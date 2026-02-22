"""
Helper functions for the Streamlit app
Contains all the business logic and agent operations

ANALOGY: Think of this module as the "ENGINE ROOM" of a ship 🚢
- streamlit_app.py is the BRIDGE (controls and displays)
- app_functions.py is the ENGINE ROOM (does all the heavy work)
- first_draft_tab.py is a SPECIALIZED DECK (handles specific operations)

The captain (user) gives orders on the bridge, but all the power and processing
happens down in the engine room where the real work gets done.

FUNCTIONS OVERVIEW:
├── get_product_info()      : 🔍 RAG search tool - Queries vector database for product documentation
├── run_agent()             : 🤖 AI Agent orchestrator - Runs LangChain agent with tools and prompts
├── format_output()         : 📋 Output formatter - Converts agent responses to readable markdown
└── apply_prompt_file()     : 📝 Prompt template engine - Reads .md files and populates placeholders

This module handles:
- Vector database queries (Chroma + HuggingFace embeddings)
- LangChain agent execution (OpenAI Functions Agent)
- LLM invocations (via utils.get_llm())
- Template-based prompt generation
"""

from typing import List
import math
import time
import re
import json
import os
from urllib.parse import urlparse
from langchain.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.tools import tool
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from utils import get_llm
import streamlit as st


def _load_networking_terms() -> dict:
    """Load networking technology terms from networking_terms.json.
    Returns a dict with category -> list of terms.
    Caches in module-level variable; auto-refreshes if file has been modified.
    """
    global _networking_terms_cache, _networking_terms_mtime
    
    terms_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "networking_terms.json")
    
    # Check file modification time to auto-refresh cache
    try:
        current_mtime = os.path.getmtime(terms_file)
    except OSError:
        current_mtime = 0
    
    if _networking_terms_cache is not None and current_mtime == _networking_terms_mtime:
        return _networking_terms_cache
    
    try:
        with open(terms_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Remove the comment key
        data.pop("_comment", None)
        _networking_terms_cache = data
        _networking_terms_mtime = current_mtime
        if current_mtime != 0:
            print(f"📖 Loaded networking_terms.json ({sum(len(v) for v in data.values() if isinstance(v, list))} terms)")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"⚠️ Could not load networking_terms.json: {e}")
        _networking_terms_cache = {}
        _networking_terms_mtime = 0
    return _networking_terms_cache

_networking_terms_cache = None
_networking_terms_mtime = 0


def _scan_for_networking_terms(text: str) -> tuple:
    """
    Scan bug/RCA text for known networking technology terms from networking_terms.json.
    Returns (found, frequencies) where:
      - found: deduplicated list of (category, term) tuples
      - frequencies: {term_lower: count} — how many times each term appears in the text
    
    Multi-word terms (e.g. 'segment routing') are matched first, then single-word terms.
    All matching is case-insensitive and uses word boundary checks.
    Also scans a normalized version of the text where underscores/hyphens become spaces,
    so component fields like 'cnbng_nal' can match the term 'cnbng'.
    """
    terms_db = _load_networking_terms()
    if not terms_db:
        return [], {}
    
    text_lower = text.lower()
    # Also create a normalized version where underscores/hyphens become spaces
    # This lets 'cnbng_nal' match 'cnbng', 'ap-qos' match 'qos', etc.
    text_normalized = re.sub(r'[_\-./]', ' ', text_lower)
    combined_text = text_lower + " " + text_normalized
    
    found = []  # list of (category, term)
    frequencies = {}  # term -> count of occurrences in original text
    seen = set()
    
    # Build a flat list: multi-word terms first (greedy match), then single-word
    all_terms = []
    for category, terms in terms_db.items():
        for term in terms:
            all_terms.append((category, term.lower()))
    
    # Sort by term length descending so multi-word matches come first
    all_terms.sort(key=lambda x: len(x[1]), reverse=True)
    
    for category, term in all_terms:
        if term in seen:
            continue
        # Use word boundary regex for accurate matching
        # For terms with special chars like "ios-xe", escape them
        pattern = r'\b' + re.escape(term) + r'\b'
        matches = re.findall(pattern, combined_text)
        if matches:
            found.append((category, term))
            seen.add(term)
            frequencies[term] = len(matches)
    
    return found, frequencies


    # ── Load guide mappings from JSON (editable without touching code) ──
_GUIDE_MAPPINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "guide_mappings.json")

def _load_guide_mappings():
    """Load guide matching configuration from guide_mappings.json"""
    try:
        with open(_GUIDE_MAPPINGS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Could not load guide_mappings.json: {e}")
        return {}

def match_terms_to_guides(detected_terms: list, product_name: str, term_frequencies: dict = None) -> tuple:
    """
    Match detected technology terms against actual PDF guide filenames
    in the knowledge_docs folder for a given product.
    
    Args:
        detected_terms: List of term strings (e.g. ['cnbng', 'bng', 'pppoe'])
        product_name: UI product name (e.g. 'ASR 9000') — will be mapped to folder name
        term_frequencies: Optional {term: count} from _scan_for_networking_terms.
                          When provided, each term's score is multiplied by
                          log2(frequency) + 1.  A term appearing 16× gets 5× the
                          weight of a term appearing once.  This ensures that
                          heavily-discussed topics dominate the guide ranking.
    
    Returns:
        (matched_dict, all_guides) where:
        - matched_dict: {term: [guide_filename, ...]} for terms that match a guide title
        - all_guides: list of all guide filenames in the product folder
    
    Also stores guide_scores in the returned matched_dict under a special key '_guide_scores':
        {'guide_filename': score, ...} — higher score = stronger match
    """
    # Map UI product names to folder names (same mapping as sidebar_app.py)
    product_mapping = {
        "Cisco SD-WAN": "sdwan",
        "Cisco 9800": "9800",
        "ASR 9000": "ASR9000",
        "Cisco 8000": "Cisco8000",
        "cisco_generic": "cisco_generic"
    }
    product_code = product_mapping.get(product_name, product_name)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    knowledge_dir = os.path.join(base_dir, "knowledge_docs", product_code)
    
    if not os.path.isdir(knowledge_dir):
        return {}, []
    
    guide_files = sorted([f for f in os.listdir(knowledge_dir) if f.lower().endswith('.pdf')])
    if not guide_files:
        return {}, []
    
    # ── Load all configuration from guide_mappings.json ──
    mappings = _load_guide_mappings()
    
    install_cfg = mappings.get('install_upgrade_terms', {})
    install_terms = set(install_cfg.get('terms', []))
    install_patterns = install_cfg.get('guide_patterns', [])
    
    concept_map = {k: v for k, v in mappings.get('concept_to_guide', {}).items() if k != '_comment'}
    
    product_noise_cfg = mappings.get('product_noise', {})
    filename_noise = set(mappings.get('filename_noise_words', {}).get('words', []))
    stop_words = set(mappings.get('stop_words', {}).get('words', []))
    
    matched = {}  # term -> [guide filenames]
    
    # Build a set of product-name terms to SKIP — these are too generic
    product_noise = set()
    for word in product_name.lower().replace("-", " ").split():
        product_noise.add(word)
    product_noise.add(product_code.lower())
    for noise_term in product_noise_cfg.get(product_code, []):
        product_noise.add(noise_term)

    for term in detected_terms:
        term_lower = term.lower()
        
        # Skip terms that are just the product name — they'd match every guide
        if term_lower in product_noise:
            continue
        
        # Skip terms that are substrings of common guide-type words
        # (e.g. "gui" matches every filename containing "guide")
        if any(term_lower in noise_word for noise_word in filename_noise):
            continue
        
        # Create variants for flexible matching
        # Strip stop words that filenames often omit
        # e.g. "monitor and maintain" → "monitor maintain" → matches "monitor-maintain-book.pdf"
        term_no_stops = " ".join(w for w in term_lower.split() if w not in stop_words)
        
        term_variants = [
            term_lower,                          # exact: "cnbng"
            term_lower.replace(" ", "-"),        # spaces→hyphens
            term_lower.replace(" ", "_"),        # spaces→underscores
            term_lower.replace(" ", ""),          # no spaces
        ]
        # Add stop-word-stripped variants if different from original
        if term_no_stops and term_no_stops != term_lower:
            term_variants.extend([
                term_no_stops,
                term_no_stops.replace(" ", "-"),
                term_no_stops.replace(" ", ""),
            ])
        
        for guide in guide_files:
            guide_lower = guide.lower()
            guide_normalized = guide_lower.replace(".pdf", "").replace("-", "").replace("_", "")
            
            for variant in term_variants:
                variant_normalized = variant.replace("-", "").replace("_", "")
                if variant_normalized in guide_normalized or variant in guide_lower:
                    if term_lower not in matched:
                        matched[term_lower] = []
                    if guide not in matched[term_lower]:
                        matched[term_lower].append(guide)
                    break

    # ── Install / Upgrade guide injection ──
    install_terms_found = [t for t in detected_terms if t.lower() in install_terms]
    if install_terms_found:
        trigger_term = install_terms_found[0].lower()
        for guide in guide_files:
            guide_lower = guide.lower()
            if any(pat in guide_lower for pat in install_patterns):
                if trigger_term not in matched:
                    matched[trigger_term] = []
                if guide not in matched[trigger_term]:
                    matched[trigger_term].append(guide)

    # ── Concept-to-guide injection ──
    # If a detected term is in the concept map, also match guides
    # whose filenames contain the mapped patterns.
    for term in detected_terms:
        term_lower = term.lower()
        if term_lower in concept_map:
            guide_patterns = concept_map[term_lower]
            for guide in guide_files:
                guide_lower = guide.lower()
                guide_normalized = guide_lower.replace(".pdf", "").replace("-", "").replace("_", "")
                if any(pat in guide_normalized or pat in guide_lower for pat in guide_patterns):
                    if term_lower not in matched:
                        matched[term_lower] = []
                    if guide not in matched[term_lower]:
                        matched[term_lower].append(guide)
    
    # ── Build guide scores with inverse breadth × frequency × specificity ──
    #
    # Three scoring factors per term:
    #
    # 1. Inverse breadth: 1 guide → 1.0;  5 guides → 0.2 each.
    #    Rewards laser-targeted terms over spray terms.
    #
    # 2. Frequency boost: log2(occurrences) + 1, capped at 3.0.
    #    A term mentioned 8× matters more than one mentioned once,
    #    but the cap prevents "dns" ×32 from running away.
    #
    # 3. Specificity bonus: multi-word terms get a 2× multiplier.
    #    "dns security" (2 words) is far more informative than "dns" alone.
    #    This rewards compound technology phrases that precisely identify
    #    the topic over generic single-word noise like "template" or "process".
    #
    # After per-term scoring, we apply diminishing returns per guide:
    #    final_score = raw_score ^ 0.7
    # This compresses high scores and narrows the gap between a guide that
    # hoards 8 generic exclusive terms and one with 3 highly relevant terms.
    # Without this, "catch-all" guides like systems-interfaces dominate just
    # by accumulating many low-value exclusive mappings.
    #
    FREQ_BOOST_CAP = 3.0
    MULTIWORD_BONUS = 2.0
    DIMINISHING_EXPONENT = 0.7  # <1.0 compresses; 1.0 = linear (no diminishing)
    freq = term_frequencies or {}
    guide_scores = {}  # guide_filename -> weighted score
    for term, guides in matched.items():
        breadth_weight = 1.0 / len(guides) if guides else 0
        term_freq = freq.get(term, 1)
        freq_boost = min(math.log2(term_freq) + 1, FREQ_BOOST_CAP) if term_freq >= 1 else 1
        specificity = MULTIWORD_BONUS if ' ' in term or '-' in term else 1.0
        weight = breadth_weight * freq_boost * specificity
        for guide in guides:
            guide_scores[guide] = guide_scores.get(guide, 0) + weight
    
    # Apply diminishing returns so "catch-all" guides don't run away
    guide_scores = {g: round(s ** DIMINISHING_EXPONENT, 2) for g, s in guide_scores.items()}
    
    # Attach scores to the matched dict under a special key
    matched['_guide_scores'] = guide_scores
    
    return matched, guide_files


### ── Component abbreviation expansions ────────────────────────────
_component_abbreviations = {
    'cfg': 'configuration', 'cfg2': 'configuration group',
    'mgmt': 'management', 'mon': 'monitor', 'sec': 'security',
    'pol': 'policy', 'cert': 'certificate', 'topo': 'topology',
    'deploy': 'deployment', 'intf': 'interface', 'rte': 'route',
    'rtng': 'routing', 'acl': 'access control list', 'vpn': 'VPN',
    'wan': 'WAN', 'tun': 'tunnel', 'bfd': 'BFD', 'omp': 'OMP',
    'ntp': 'NTP', 'snmp': 'SNMP', 'aaa': 'AAA authentication',
    'qos': 'QoS', 'nat': 'NAT', 'dhcp': 'DHCP', 'bgp': 'BGP',
    'ospf': 'OSPF', 'isis': 'IS-IS', 'mpls': 'MPLS',
    'multicast': 'multicast', 'ha': 'high availability', 'sso': 'SSO',
    'rrm': 'RRM radio resource management',
    'ewlc': 'embedded wireless controller',
    'cnbng': 'cloud native BNG', 'bng': 'BNG broadband network gateway',
    'xe': 'IOS-XE', 'xr': 'IOS-XR',
    'vmanage': 'vManage', 'vedge': 'vEdge', 'vsmart': 'vSmart',
    'pref': 'prefix', 'tmpl': 'template', 'tmpt': 'template',
    'ctrl': 'control', 'svc': 'service', 'svcs': 'services',
    'app': 'application', 'dash': 'dashboard',
}
_component_noise = {
    'basic', 'ui', 'nal', 'docs', 'doc', 'system', 'test', 'core',
    'main', 'page', 'view', 'module', 'lib', 'util', 'utils',
}


def _extract_search_hints(text: str) -> dict:
    """
    Mine bug/RCA content for explicit search query suggestions.
    
    Extracts:
    - Component sub-parts (expanded abbreviations)
    - UI navigation paths from Description ("navigate to X → Y")
    - Specific feature/object nouns from Description
    - Action verbs (edit, delete, create, etc.)
    
    Returns a dict with 'suggested_queries' list ready for the LLM to use directly.
    """
    result = {
        'component_keywords': [],   # Expanded component sub-parts
        'nav_endpoints': [],        # Terminal destinations from UI navigation paths
        'description_nouns': [],    # Specific features/objects from description
        'actions': [],              # Action verbs
        'suggested_queries': [],    # Ready-to-use search queries for the LLM
    }

    if not text or not text.strip():
        return result

    # ── Extract Component field ──────────────────────────────────────
    # Find ALL Component fields and pick the most meaningful one.
    # Bugs can have multiple Component values (e.g. "documentation" then "ap-qos")
    # and the first one is often generic. We want the most specific.
    _generic_components = {'documentation', 'general', 'other', 'none', 'unknown', 'docs', 'doc'}
    comp_matches = re.findall(r'\*\*Component:?\*\*[:\s]*(\S+)', text, re.IGNORECASE)
    best_component = None
    for comp_val in comp_matches:
        comp_val = comp_val.strip()
        if comp_val.lower() in _generic_components:
            if best_component is None:
                best_component = comp_val  # keep as fallback
            continue
        # Prefer non-generic components
        best_component = comp_val
        break  # first non-generic wins

    if best_component:
        component = best_component
        parts = re.split(r'[-_]+', component)
        expanded = []
        for part in parts:
            p = part.lower().strip()
            if not p or p in _component_noise or p.isdigit():
                continue
            # Remove trailing digits (e.g., cfg2 → cfg)
            p_base = re.sub(r'\d+$', '', p)
            if p_base in _component_abbreviations:
                expanded.append(_component_abbreviations[p_base])
            elif p in _component_abbreviations:
                expanded.append(_component_abbreviations[p])
            elif len(p) > 2:
                expanded.append(p)
        result['component_keywords'] = expanded

    # ── Extract Description field (or fall back to full text) ────────
    desc_text = text
    desc_match = re.search(
        r'\*\*Description:?\*\*[:\s]*(.*?)(?=\n\*\*[A-Z]|\Z)',
        text, re.DOTALL | re.IGNORECASE
    )
    if desc_match:
        desc_text = desc_match.group(1)

    # ── Extract UI navigation paths ──────────────────────────────────
    # Only look for explicit "navigate to" / "go to" patterns with arrows
    nav_patterns = [
        r'(?:navigate|go|goes?|navigating)\s+to\s+(.+?)(?:\.|,|$|\n)',
        r'(?:under|within)\s+(?:the\s+)?(.+?[→>].+?)(?:\.|,|$|\n)',
    ]

    # Noise words to strip from the endpoints
    nav_noise = {'section', 'page', 'tab', 'menu', 'screen', 'window', 'panel', 'area', 'the', 'a', 'an'}

    nav_endpoints = []
    for pattern in nav_patterns:
        matches = re.findall(pattern, desc_text, re.IGNORECASE)
        for match in matches:
            # Split on arrows/greater-than
            parts = re.split(r'[→>]+', match)
            parts = [p.strip().strip('"\'()[]') for p in parts if p.strip()]
            # Clean noise words from each part
            cleaned_parts = []
            for p in parts:
                words = p.split()
                cleaned = ' '.join(w for w in words if w.lower() not in nav_noise)
                if cleaned and len(cleaned) > 2:
                    cleaned_parts.append(cleaned)
            if cleaned_parts:
                # The last part is the most specific destination
                nav_endpoints.append(cleaned_parts[-1])
                # Also keep last two parts joined (for broader search)
                if len(cleaned_parts) > 1:
                    full_path = ' '.join(cleaned_parts[-2:])
                    nav_endpoints.append(full_path)

    result['nav_endpoints'] = list(dict.fromkeys(nav_endpoints))  # Dedupe, preserve order

    # ── Extract specific nouns/features from description ─────────────
    noun_patterns = [
        r'\b(prefix(?:es)?(?:\s+list(?:s)?)?)\b',
        r'\b(policy\s+object(?:s)?)\b',
        r'\b(object(?:s)?\s+and\s+profile(?:s)?)\b',
        r'\b(profile(?:s)?)\b',
        r'\b(feature\s+template(?:s)?)\b',
        r'\b(device\s+template(?:s)?)\b',
        r'\b(configuration\s+group(?:s)?)\b',
        r'\b(config(?:uration)?\s+profile(?:s)?)\b',
        r'\b(cloud\s+service(?:s)?)\b',
        r'\b(certificate(?:s)?)\b',
        r'\b(security\s+polic(?:y|ies))\b',
        r'\b(access[\s-](?:control[\s-])?list(?:s)?)\b',
        r'\b(route\s+polic(?:y|ies))\b',
        r'\b(localized\s+polic(?:y|ies))\b',
        r'\b(centralized\s+polic(?:y|ies))\b',
        r'\b(data\s+polic(?:y|ies))\b',
        r'\b(app(?:lication)?[\s-]aware\s+routing)\b',
        r'\b(SLA\s+class(?:es)?)\b',
        r'\b(color\s+list(?:s)?)\b',
        r'\b(site\s+list(?:s)?)\b',
        r'\b(TLOC(?:\s+list(?:s)?)?)\b',
        r'\b(VPN\s+list(?:s)?)\b',
        r'\b(community\s+list(?:s)?)\b',
        r'\b(prefix\s+list(?:s)?)\b',
        r'\b(deployment(?:s)?)\b',
        r'\b(dashboard(?:s)?)\b',
        r'\b(topology(?:ies)?)\b',
        r'\b(system[\s-]generated)\b',
        r'\b(alarm(?:s)?)\b',
    ]

    desc_nouns = []
    for pattern in noun_patterns:
        matches = re.findall(pattern, desc_text, re.IGNORECASE)
        desc_nouns.extend(m.lower().strip() for m in matches)

    result['description_nouns'] = list(dict.fromkeys(desc_nouns))

    # ── Extract action verbs ─────────────────────────────────────────
    action_match = re.findall(
        r'\b(edit(?:ing|ed)?|delet(?:e|ing|ed)|remov(?:e|ing|ed)|creat(?:e|ing|ed)|'
        r'add(?:ing|ed)?|configur(?:e|ing|ed)|deploy(?:ing|ed|ment)?|'
        r'attach(?:ing|ed)?|detach(?:ing|ed)?|modif(?:y|ying|ied)|'
        r'updat(?:e|ing|ed)|system[\s-]generated)\b',
        desc_text, re.IGNORECASE
    )
    result['actions'] = list(dict.fromkeys(a.lower() for a in action_match))

    # ── Build suggested search queries ───────────────────────────────
    # IMPORTANT: Shorter, more specific queries perform BETTER in vector search.
    # Long queries like "configuration group objects and profiles prefix" get
    # pulled back to intro chapters. Keep queries focused and concise.
    queries = []

    # Priority 1: Most-specific nav endpoint + description noun
    # Use only the FIRST (most specific) endpoint, not the full path
    best_endpoint = result['nav_endpoints'][0] if result['nav_endpoints'] else None
    if best_endpoint:
        for noun in result['description_nouns'][:3]:
            if noun.lower() not in best_endpoint.lower():
                combo = f"{best_endpoint} {noun}"
                if combo not in queries:
                    queries.append(combo)
        # Nav endpoint alone if no nouns overlap
        if not queries:
            queries.append(best_endpoint)

    # Priority 2: Description noun + action (targets specific behavior)
    for noun in result['description_nouns'][:2]:
        for action in result['actions'][:2]:
            if action != noun:
                combo = f"{noun} {action}"
                if combo not in queries:
                    queries.append(combo)

    # Priority 3: Standalone description nouns (specific features)
    for noun in result['description_nouns'][:3]:
        if noun not in queries and not any(noun in q for q in queries):
            queries.append(noun)

    # Priority 4: Component keyword + description noun (only if short)
    for kw in result['component_keywords'][:2]:
        for noun in result['description_nouns'][:2]:
            combo = f"{kw} {noun}"
            # Skip combos that are too long — they dilute vector search
            if len(combo) <= 50 and noun.lower() not in kw.lower() and kw.lower() not in noun.lower():
                if combo not in queries:
                    queries.append(combo)

    # Fallback: component keywords alone if nothing better found
    if not queries:
        for kw in result['component_keywords'][:3]:
            if kw not in queries:
                queries.append(kw)

    result['suggested_queries'] = queries[:6]  # Cap at 6

    return result


def extract_doc_clues_data(text: str) -> dict:
    """
    Extract structured data from RCA/bug content: URLs, book names, chapter clues,
    networking technology terms, and search query suggestions from Description mining.
    Returns raw data (not formatted string) so the UI can display it for user selection.
    
    Returns:
        {
            'url_clues': [{'url': str, 'book_pdf': str, 'book_id': str, 'chapter_clues': [str]}],
            'tech_terms': [(category, term), ...],   # all detected terms
            'tech_terms_by_category': {category: [term, ...]}  # grouped
            'search_hints': {                        # from Description mining
                'component_keywords': [str],
                'nav_endpoints': [str],
                'description_nouns': [str],
                'actions': [str],
                'suggested_queries': [str],
            }
        }
    """
    result = {'url_clues': [], 'tech_terms': [], 'tech_terms_by_category': {}, 'search_hints': {}}
    
    if not text or not text.strip():
        return result
    
    # ── PART 1: URL extraction ──────────────────────────────────────
    url_pattern = r'https?://(?:www\.)?cisco\.com/c/en/us/(?:td|support)/docs/[^\s\)\]\"\'<>]+'
    urls = re.findall(url_pattern, text, re.IGNORECASE)
    
    noise_tokens = {
        'm', 'b', 'c', 'a', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'n', 'o', 'p',
        'from', 'onwards', 'cg', 'config', 'guide', 'chapter', 'book', 'later',
        'the', 'and', 'for', 'with', 'on', 'in', 'to', 'of', 'html', 'htm',
    }
    
    seen_books = set()
    for url in urls:
        try:
            url = url.rstrip('.,;:')
            parsed = urlparse(url)
            path_parts = [p for p in parsed.path.split('/') if p]
            if len(path_parts) < 2:
                continue
            html_filename = path_parts[-1]
            book_identifier = path_parts[-2]
            if not html_filename.endswith(('.html', '.htm')):
                book_identifier = html_filename
                html_filename = ""
            book_pdf = f"{book_identifier}.pdf"
            if book_pdf in seen_books:
                continue
            seen_books.add(book_pdf)
            chapter_clues = []
            if html_filename:
                name_no_ext = re.sub(r'\.html?$', '', html_filename, flags=re.IGNORECASE)
                tokens = re.split(r'[_\-]', name_no_ext)
                for token in tokens:
                    t = token.lower().strip()
                    if not t or t in noise_tokens or t.isdigit():
                        continue
                    if re.match(r'^[a-z]+\d+$', t) and len(t) <= 8:
                        continue
                    chapter_clues.append(t)
            result['url_clues'].append({
                'url': url, 'book_pdf': book_pdf,
                'book_id': book_identifier, 'chapter_clues': chapter_clues
            })
        except Exception:
            continue
    
    # ── PART 2: Networking technology term scan ─────────────────────
    net_terms, term_frequencies = _scan_for_networking_terms(text)
    result['tech_terms'] = net_terms
    result['term_frequencies'] = term_frequencies
    by_cat = {}
    for cat, term in net_terms:
        by_cat.setdefault(cat, []).append(term)
    result['tech_terms_by_category'] = by_cat

    # ── PART 3: Description mining for search query suggestions ────
    result['search_hints'] = _extract_search_hints(text)
    
    return result


def format_doc_clues_for_prompt(clues_data: dict, selected_terms: List[str] = None, product_name: str = None) -> str:
    """
    Format the extracted clues data into a structured block for the LLM prompt.
    
    Args:
        clues_data: Output from extract_doc_clues_data()
        selected_terms: Optional list of user-selected technology terms.
                        If provided, only these terms are included.
                        If None, all detected terms are included.
        product_name: Optional UI product name (e.g. 'ASR 9000').
                      If provided, matches terms to actual PDF guide filenames.
    
    Returns:
        Formatted string block for injection into the agent prompt.
    """
    sections = []
    
    # ── URL clues ───────────────────────────────────────────────────
    for clue in clues_data.get('url_clues', []):
        entry = f"  📎 URL found: {clue['url']}\n"
        entry += f"     Book PDF: {clue['book_pdf']}\n"
        entry += f"     Book identifier (for source filter): {clue['book_id']}\n"
        if clue['chapter_clues']:
            entry += f"     Chapter clue keywords: {', '.join(clue['chapter_clues'])}\n"
            entry += f"     → This likely references a chapter about: {', '.join(c.upper() for c in clue['chapter_clues'])}\n"
        else:
            entry += f"     Chapter clue keywords: (none extracted - use bug content keywords)\n"
        sections.append(entry)
    
    if sections:
        sections.insert(0, "📎 CISCO DOCUMENTATION URLs DETECTED:")
        sections.insert(1, "-" * 50)
    
    # ── Technology terms (filtered by user selection) ───────────────
    all_terms = clues_data.get('tech_terms', [])
    if selected_terms is not None:
        # Only include terms the user selected
        selected_set = {t.lower() for t in selected_terms}
        filtered = [(cat, term) for cat, term in all_terms if term.lower() in selected_set]
    else:
        filtered = all_terms
    
    if filtered:
        by_cat = {}
        for cat, term in filtered:
            by_cat.setdefault(cat, []).append(term)
        
        sections.append("🔧 NETWORKING TECHNOLOGY TERMS (user-selected):")
        sections.append("-" * 50)
        for cat, terms in by_cat.items():
            label = cat.replace("_", " ").title()
            sections.append(f"  {label}: {', '.join(t.upper() for t in terms)}")
        
        terms_flat = [t for _, t in filtered]
        sections.append(f"\n  → Use these as ADDITIONAL search keywords: {', '.join(terms_flat)}")
    
    # ── Guide matching (match terms to actual PDF filenames) ────────
    if product_name and filtered:
        terms_for_matching = [t for _, t in filtered]
        term_frequencies = clues_data.get('term_frequencies', {})
        matched_guides, all_guides = match_terms_to_guides(terms_for_matching, product_name, term_frequencies)
        
        if matched_guides:
            # Extract guide scores for ranking
            guide_scores = matched_guides.pop('_guide_scores', {})
            
            sections.append("")
            sections.append("📚 MATCHED GUIDES (detected terms matched against available PDF guide filenames):")
            sections.append("-" * 50)
            sections.append("  ⚠️  THESE ARE YOUR HIGHEST-PRIORITY GUIDES — search these FIRST!")
            for term, guides in matched_guides.items():
                if term.startswith('_'):
                    continue
                for guide in guides:
                    sections.append(f"  ✅ Term '{term.upper()}' → Guide: {guide}")
            
            # Rank guides by score (highest first)
            all_matched = sorted(
                set(g for term, guides in matched_guides.items() if not term.startswith('_') for g in guides),
                key=lambda g: guide_scores.get(g, 0),
                reverse=True
            )
            
            # Show ranked primary guides with scores
            sections.append(f"\n  🎯 PRIMARY GUIDES TO SEARCH (ranked by relevance):")
            for i, g in enumerate(all_matched, 1):
                score = guide_scores.get(g, 0)
                marker = " ← TOP PRIORITY" if i <= 2 else ""
                sections.append(f"    {i}. {g}  (score={score}){marker}")
            
            sections.append("  → Search the TOP-RANKED guides FIRST — they have the strongest term matches")
            sections.append("  → Filter your vector store searches to these guides using source metadata")
        
        if all_guides:
            sections.append(f"\n  📋 All available guides in '{product_name}' docset ({len(all_guides)} total):")
            for g in all_guides:
                if matched_guides:
                    score = guide_scores.get(g, 0) if guide_scores else 0
                    marker = f" ⭐ score={score}" if score > 0 else ""
                else:
                    marker = ""
                sections.append(f"     - {g}{marker}")
    
    # ── Suggested search queries (from Description mining) ──────────
    search_hints = clues_data.get('search_hints', {})
    suggested_queries = search_hints.get('suggested_queries', [])
    
    if suggested_queries:
        sections.append("")
        sections.append("🔍 SUGGESTED SEARCH QUERIES (mined from Component + Description by system):")
        sections.append("-" * 50)
        sections.append("  ⚠️  USE THESE EXACT QUERIES — they target the correct chapter/section,")
        sections.append("      not just the guide overview or introduction.")
        for i, query in enumerate(suggested_queries, 1):
            sections.append(f"  {i}. \"{query}\"")
        
        # Show reasoning
        if search_hints.get('component_keywords'):
            sections.append(f"\n  📦 Component sub-parts expanded: {', '.join(search_hints['component_keywords'])}")
        if search_hints.get('nav_endpoints'):
            sections.append(f"  🧭 UI navigation destinations: {', '.join(search_hints['nav_endpoints'])}")
        if search_hints.get('description_nouns'):
            sections.append(f"  📝 Specific features mentioned: {', '.join(search_hints['description_nouns'])}")
        if search_hints.get('actions'):
            sections.append(f"  🔧 Actions: {', '.join(search_hints['actions'])}")
    
    # ── Build final block ───────────────────────────────────────────
    if not sections:
        return ""
    
    block = "\n\n🔗 PRE-EXTRACTED DOCUMENTATION REFERENCES (extracted by system, NOT by LLM):\n"
    block += "=" * 70 + "\n"
    block += "\n".join(sections)
    block += "\n" + "=" * 70 + "\n"
    block += "🚨 MANDATORY FIRST ACTIONS:\n"
    block += "1. If SUGGESTED SEARCH QUERIES (🔍) are listed above, use THOSE as your get_product_info queries\n"
    block += "   — DO NOT simplify them. They are pre-built to target the RIGHT chapter, not just the intro.\n"
    block += "2. If MATCHED GUIDES (⭐) are listed, filter searches to THOSE guides first\n"
    block += "3. If a Book PDF name was detected from a URL, use that as primary search source\n"
    block += "4. Use networking terms as ADDITIONAL search keywords after the suggested queries\n"
    block += "5. For EACH suggestion, specify the EXACT guide name and chapter/section\n"
    block += "⚠️ Do NOT just search for a high-level topic like 'configuration group' — that returns the Introduction.\n"
    block += "   Use the SPECIFIC sub-feature queries listed above instead.\n"
    
    return block

# Rate limiting: Track last call time to avoid API throttling
_last_tool_call_time = 0
_min_call_interval = 4.5  # Minimum 4.5 seconds between calls (15 calls per 60 seconds = ~4s each)


@tool
def get_product_info(product: str, query: str) -> str:
    """given a Cisco product name and a query, return the product context with metadata
    Args:
        product: Cisco product name. Valid products are: "sdwan", "cisco_generic", "9800", "ASR9000", "Cisco8000"
        query: user query about the product
    Returns:
        Formatted string with content and metadata (page, section) for each chunk
    
    Note: If guides have been selected by the user, results will be automatically filtered to those guides
    """
    global _last_tool_call_time
    
    # Rate limiting: Ensure minimum interval between calls
    current_time = time.time()
    time_since_last_call = current_time - _last_tool_call_time
    if time_since_last_call < _min_call_interval:
        sleep_time = _min_call_interval - time_since_last_call
        print(f"⏱️ Rate limiting: Waiting {sleep_time:.1f}s before next API call...")
        time.sleep(sleep_time)
    
    _last_tool_call_time = time.time()
    
    # Get selected guides from session state if available
    guides = None
    try:
        import streamlit as st
        guides = st.session_state.get('selected_guides_for_search', None)
    except:
        pass  # Session state not available, search all guides
    
    metadata_field_info = [
        AttributeInfo(
            name="source",
            description="The source file the information came from",
            type="string",
        ),
        AttributeInfo(
            name="product",
            description='Cisco product name. Valid products are: "sdwan", "cisco_generic", "9800", "ASR9000", "Cisco8000"',
            type="string",
        ),
    ]
    document_content_description = "Cisco Product information"
    _model = st.session_state.get('selected_model', 'gpt-4o')
    llm = get_llm(model_name=_model)
    
    # IMPORTANT: Using shared in-memory ChromaDB due to SQLite 3.26.0 constraint
    # Vector store is initialized at app startup via vector_store_manager
    from vector_store_manager import get_vector_store, initialize_vector_store
    
    try:
        vectorstore = get_vector_store()
    except RuntimeError:
        # Fallback: Initialize if not already done
        # This shouldn't happen if startup initialization worked
        import streamlit as st
        if st.session_state.get('vector_store_init_attempted', False):
            # Don't show warning again if we already tried at startup
            vectorstore = initialize_vector_store()
        else:
            st.warning("⚠️ Vector store not initialized. Initializing now...")
            vectorstore = initialize_vector_store()
            st.session_state.vector_store_init_attempted = True
    
    # ── BOOST: Inject pre-extracted suggested queries on the FIRST tool call ──
    # The LLM consistently ignores our suggested search queries in the prompt,
    # so we intercept the tool and run them ourselves, merging with the LLM's query.
    boosted_queries = []
    try:
        import streamlit as st
        pending = st.session_state.pop('_pending_search_queries', None)
        if pending:
            boosted_queries = pending
            print(f"🚀 BOOST: Injecting {len(boosted_queries)} pre-extracted search queries")
    except:
        pass
    
    # If guides are selected, use direct similarity search instead of SelfQueryRetriever
    # SelfQueryRetriever doesn't work well with source file filtering
    if guides and len(guides) > 0:
        # Build filter for selected guides
        guide_paths = [f"knowledge_docs/{product.lower()}/{guide}" if '/' not in guide else guide 
                      for guide in guides]
        
        # Map UI product names to internal codes if needed
        product_mapping = {
            "Cisco SD-WAN": "sdwan",
            "Cisco 9800": "9800",
            "ASR 9000": "ASR9000",
            "Cisco 8000": "Cisco8000",
            "cisco_generic": "cisco_generic"
        }
        product_code = product_mapping.get(product, product)
        
        # Update paths with correct product code
        guide_paths = [f"knowledge_docs/{product_code}/{guide}" for guide in guides]
        
        # ── Priority-weighted search: top guides get more search slots ──
        # Get guide scores from session state (set by match_terms_to_guides)
        guide_scores = {}
        try:
            import streamlit as st
            guide_scores = st.session_state.get('_guide_scores', {})
        except:
            pass
        
        # Rank guides by score; top 3 get dedicated search slots
        scored_guides = sorted(guides, key=lambda g: guide_scores.get(g, 0), reverse=True)
        top_guides = [g for g in scored_guides if guide_scores.get(g, 0) > 0][:3]
        
        # For single guide, use direct filter
        if len(guides) == 1:
            search_filter = {
                "$and": [
                    {"product": product_code},
                    {"source": guide_paths[0]}
                ]
            }
        else:
            # For multiple guides, use $or
            search_filter = {
                "$and": [
                    {"product": product_code},
                    {"$or": [{"source": path} for path in guide_paths]}
                ]
            }
        
        result = []
        seen_pages = set()
        
        # PHASE 1: Dedicated search on top-ranked guides (5 results each for top 2)
        if top_guides and len(guides) > 1:
            for i, tg in enumerate(top_guides[:2]):
                tg_path = f"knowledge_docs/{product_code}/{tg}"
                tg_filter = {
                    "$and": [
                        {"product": product_code},
                        {"source": tg_path}
                    ]
                }
                try:
                    tg_results = vectorstore.similarity_search(
                        query=query,
                        k=5,
                        filter=tg_filter
                    )
                    for doc in tg_results:
                        page_key = (doc.metadata.get('source', ''), doc.metadata.get('page', ''), doc.page_content[:80])
                        if page_key not in seen_pages:
                            result.append(doc)
                            seen_pages.add(page_key)
                except Exception as e:
                    print(f"⚠️ Priority search for '{tg}' failed: {e}")
            
            if result:
                print(f"🎯 PRIORITY: Got {len(result)} chunks from top {min(2, len(top_guides))} guides: {top_guides[:2]}")
        
        # PHASE 2: Broad search across ALL selected guides (fills remaining slots)
        broad_results = vectorstore.similarity_search(
            query=query,
            k=10,
            filter=search_filter
        )
        for doc in broad_results:
            page_key = (doc.metadata.get('source', ''), doc.metadata.get('page', ''), doc.page_content[:80])
            if page_key not in seen_pages:
                result.append(doc)
                seen_pages.add(page_key)
        
        # PHASE 3: BOOST with pre-extracted suggested queries
        if boosted_queries:
            boost_results = []
            for bq in boosted_queries:
                try:
                    bq_results = vectorstore.similarity_search(
                        query=bq,
                        k=5,
                        filter=search_filter
                    )
                    for doc in bq_results:
                        page_key = (doc.metadata.get('source', ''), doc.metadata.get('page', ''), doc.page_content[:80])
                        if page_key not in seen_pages:
                            boost_results.append(doc)
                            seen_pages.add(page_key)
                except Exception as e:
                    print(f"⚠️ Boost query '{bq}' failed: {e}")
            
            if boost_results:
                print(f"🚀 BOOST: Added {len(boost_results)} new chunks from suggested queries")
                # Prepend boost results so they appear FIRST (higher priority)
                result = boost_results + result
    else:
        # Use SelfQueryRetriever for normal searches without guide filtering
        retriever = SelfQueryRetriever.from_llm(
            llm,
            vectorstore,
            document_content_description,
            metadata_field_info,
            enable_limit=True,
            verbose=True,
        )
        
        result = retriever.invoke(f"Product: {product}\nQuery: {query}")
    
    # Filter out unwanted content (e.g., Cisco Bug Search Tool references)
    excluded_keywords = [
        "cisco bug search tool",
        "bug search tool",
        "bst",
        "cisco bug tracker"
    ]
    
    filtered_result = []
    for doc in result:
        content_lower = doc.page_content.lower()
        section_lower = doc.metadata.get('section', '').lower()
        
        # Skip if any excluded keyword is found in content or section
        if any(keyword in content_lower or keyword in section_lower for keyword in excluded_keywords):
            continue
        
        filtered_result.append(doc)
    
    # Use filtered results
    result = filtered_result
    
    # Check if we got any results
    if not result or len(result) == 0:
        return f"""
❌ NO DOCUMENTS FOUND ❌

The search for "{query}" in product "{product}" returned ZERO results.

POSSIBLE REASONS:
1. The product name might be incorrect. Available products: "sdwan", "cisco_generic", "9800", "ASR9000", "Cisco8000"
2. The search query might be too specific or use terms not in the documentation
3. The relevant documentation might not be loaded into the database

⚠️ CRITICAL INSTRUCTION: Do NOT invent or fabricate any documents, sections, page numbers, or quotes.
You MUST tell the user that no documents were found and cannot provide recommendations without actual source material.
"""
    
    # Format the result to include metadata explicitly
    formatted_chunks = []
    for i, doc in enumerate(result, 1):
        chunk_info = f"\n--- CHUNK {i} ---"
        chunk_info += f"\nSource: {doc.metadata.get('source', 'Unknown')}"
        
        # Prefer page_label (printed page number) over page (file index)
        page_num = doc.metadata.get('page_label') or doc.metadata.get('page')
        chunk_info += f"\nPage: {page_num if page_num is not None else 'Not available'}"
        
        chunk_info += f"\nSection: {doc.metadata.get('section', 'Not available')}"
        chunk_info += f"\n\nCONTENT:\n{doc.page_content}\n"
        formatted_chunks.append(chunk_info)
    
    return "\n".join(formatted_chunks)


def run_agent(product_name: str, question: str, rca_content: str, selected_guides: List[str] = None, selected_tech_terms: List[str] = None):
    """Run the agent with the given inputs
    
    Args:
        product_name: Cisco product name
        question: User's question/task
        rca_content: Bug report or RCA content
        selected_guides: Optional list of guide filenames to limit search scope
        selected_tech_terms: Optional list of user-selected technology terms to focus search on.
                             If None, all auto-detected terms are used.
    """
    
    # Store selected guides in session state for tool access
    if selected_guides:
        import streamlit as st
        st.session_state.selected_guides_for_search = selected_guides
    
    # Pre-extract Cisco documentation references from the content FIRST
    # so URL clues can override guide/section with highest priority
    clues_data = extract_doc_clues_data(rca_content)
    url_clues = clues_data.get('url_clues', [])
    
    # Inject the top-scored guide and section hints into the prompt at runtime
    # Priority chain: URL clue > term-based scoring > fallback
    import streamlit as st
    guide_scores = st.session_state.get('_guide_scores', {})
    
    recommended_label = None
    section_label = None
    
    # HIGHEST PRIORITY: URL clue in the RCA — deterministic, most specific
    if url_clues:
        url_book = url_clues[0]['book_pdf']  # e.g. systems-interfaces-book-xe-sdwan.pdf
        chapter_tokens = url_clues[0].get('chapter_clues', [])  # e.g. ['configure', 'interfaces']
        url_score = guide_scores.get(url_book, 'n/a')
        recommended_label = f"{url_book} (from URL reference, score: {url_score})"
        if chapter_tokens:
            # Turn ['configure', 'interfaces'] into "Configure Interfaces"
            section_label = " ".join(t.title() for t in chapter_tokens)
    
    # FALLBACK: term-based scoring (no URL found)
    if not recommended_label:
        if guide_scores:
            top_guide = max(guide_scores, key=guide_scores.get)
            top_score = guide_scores[top_guide]
            recommended_label = f"{top_guide} (confidence score: {top_score})"
        else:
            top_guide = None
            recommended_label = "(no guide scores available — use your best judgment from search results)"
    else:
        top_guide = url_clues[0]['book_pdf'] if url_clues else None
    
    # Section fallback: term-based hints if URL didn't provide chapter clues
    if not section_label:
        matched_term_guides = st.session_state.get('_matched_term_guides', {})
        effective_guide = top_guide or (max(guide_scores, key=guide_scores.get) if guide_scores else None)
        if effective_guide and matched_term_guides:
            term_weights = []
            for term, guides in matched_term_guides.items():
                if term.startswith('_'):
                    continue
                if effective_guide in guides:
                    weight = 1.0 / len(guides)
                    term_weights.append((term, weight))
            term_weights.sort(key=lambda x: -x[1])
            top_terms = [t.title() for t, _ in term_weights[:5]]
            section_label = ", ".join(top_terms) if top_terms else "(see location recommendations above)"
        else:
            section_label = "(see location recommendations above)"
    
    question = question.replace('{{RECOMMENDED_GUIDE}}', recommended_label)
    question = question.replace('{{RECOMMENDED_SECTION}}', section_label)
    
    # Build a pinned Location Recommendation #1 from code-derived signals
    # so the LLM's first recommendation always points to the right chapter
    # Then pin #2 and #3 from the next-highest-scored guides.
    # The user still reviews/edits all of these — we're pre-populating, not dictating.
    
    matched_term_guides = st.session_state.get('_matched_term_guides', {})
    
    def _section_hints_for_guide(guide_name):
        """Get the top term-based section hints for a specific guide."""
        if not matched_term_guides:
            return None
        tw = []
        for term, guides in matched_term_guides.items():
            if term.startswith('_'):
                continue
            if guide_name in guides:
                w = 1.0 / len(guides)
                tw.append((term, w))
        tw.sort(key=lambda x: -x[1])
        top = [t.title() for t, _ in tw[:5]]
        return ", ".join(top) if top else None
    
    # Sort all guides by score descending
    sorted_guides = sorted(guide_scores.items(), key=lambda x: -x[1]) if guide_scores else []
    
    # ── PINNED REC #1 ──
    pinned_rec_section = ""
    rec1_guide = None  # track which guide is #1 so we skip it for #2/#3
    
    if url_clues and section_label and section_label != "(see location recommendations above)":
        # Strong signal: URL gave us both guide and chapter
        rec1_guide = url_clues[0]['book_pdf']
        chapter_query = ' '.join(url_clues[0].get('chapter_clues', []))
        pinned_rec_section = f"""
    
    🔒 MANDATORY LOCATION RECOMMENDATION #1 (from documentation URL — DO NOT SKIP OR REPLACE):
    ══════════════════════════════════════════════════════════════════════
    Document name: {rec1_guide}
    Chapter/Section: {section_label}
    Page number: <SEARCH THIS GUIDE and fill in>
    Actual content location indicator: <SEARCH THIS GUIDE and quote 8-15 words>
    Detailed reasoning: The bug/RCA explicitly references this document and chapter via URL.
    ══════════════════════════════════════════════════════════════════════
    🔍 REQUIRED SEARCH: call get_product_info with query targeting "{chapter_query}" in {rec1_guide}
    """
    elif top_guide and section_label and section_label != "(see location recommendations above)":
        # Moderate signal: term scoring gave us guide + section hints (no URL)
        rec1_guide = top_guide
        pinned_rec_section = f"""
    
    🔒 MANDATORY LOCATION RECOMMENDATION #1 (highest scoring guide — DO NOT SKIP OR REPLACE):
    ══════════════════════════════════════════════════════════════════════
    Document name: {rec1_guide}
    Likely section topics: {section_label}
    Page number: <SEARCH THIS GUIDE and fill in>
    Actual content location indicator: <SEARCH THIS GUIDE and quote 8-15 words>
    Detailed reasoning: This guide scored highest ({guide_scores.get(rec1_guide, 'n/a')}) based on detected technology terms.
    ══════════════════════════════════════════════════════════════════════
    🔍 REQUIRED SEARCH: call get_product_info with query targeting "{section_label}" in {rec1_guide}
    """
    
    # ── MANDATORY RECS #2 and #3 — next highest-scored guides ──
    remaining_guides = [(g, s) for g, s in sorted_guides if g != rec1_guide]
    for rank, (guide_name, score) in enumerate(remaining_guides[:2], start=2):
        hints = _section_hints_for_guide(guide_name)
        hint_text = hints if hints else "(search this guide for relevant sections)"
        pinned_rec_section += f"""
    
    🔒 MANDATORY LOCATION RECOMMENDATION #{rank} (DO NOT SKIP — search this DIFFERENT guide):
    ══════════════════════════════════════════════════════════════════════
    Document name: {guide_name}
    Likely section topics: {hint_text}
    Page number: <SEARCH THIS GUIDE and fill in>
    Actual content location indicator: <SEARCH THIS GUIDE and quote 8-15 words>
    Detailed reasoning: This guide scored #{rank} ({score}) based on detected technology terms matching: {hint_text}
    ══════════════════════════════════════════════════════════════════════
    🔍 REQUIRED SEARCH: call get_product_info with query targeting "{hint_text}" in {guide_name}
    """
    
    if pinned_rec_section:
        pinned_rec_section += """
    🚫 STRICT RULES FOR LOCATION RECOMMENDATIONS:
    1. You MUST output EXACTLY the 3 mandatory recommendations above as your Location Recommendations #1, #2, #3.
    2. Each recommendation MUST use a DIFFERENT guide — do NOT repeat the same guide.
    3. For EACH recommendation, you MUST make a SEPARATE get_product_info search call targeting that specific guide.
    4. Fill in page numbers and content indicators ONLY from actual search results for that guide.
    5. If a search for a guide returns no results, still include it but note "No matching content found in search results."
    6. You MAY add a 4th recommendation from your own analysis, but recommendations #1-#3 are locked.
    """
    
    # Append RCA content to the question
    full_question = question + rca_content
    doc_clues = format_doc_clues_for_prompt(clues_data, selected_terms=selected_tech_terms, product_name=product_name)
    
    # Store suggested search queries in session state so get_product_info can
    # inject them on the FIRST tool call — this bypasses the LLM ignoring our queries
    suggested_queries = clues_data.get('search_hints', {}).get('suggested_queries', [])
    if suggested_queries:
        import streamlit as st
        st.session_state._pending_search_queries = suggested_queries[:4]  # Top 4
    
    # Build the clues as a SEPARATE top-level section in the agent prompt
    # (NOT buried inside the question blob where it gets lost)
    doc_clues_section = ""
    if doc_clues:
        doc_clues_section = f"""
    
    {doc_clues}
    """
    
    # Build guide filter message for prompt
    guide_filter_message = ""
    if selected_guides and len(selected_guides) > 0:
        guides_list = ', '.join(selected_guides)
        guide_filter_message = f"""
    
    🎯 SEARCH SCOPE LIMITATION:
    The user has selected specific guides to search. You MUST limit your search to these guides only:
    {guides_list}
    
    When calling get_product_info, the results will automatically be filtered to these guides.
    """
    
    product_version_prompt_template = f"""
    given a Cisco product name and a question from a user, return the answer.
    Use your tools to fetch context to answer the question to provide a more accurate answer.
    
    Cisco product: {{product_name}}
    {doc_clues_section}
    {pinned_rec_section}
    question: {{question}}
    {guide_filter_message}
    
    🚨 MANDATORY FIRST ACTIONS (before anything else):
    1. If � MANDATORY LOCATION RECOMMENDATIONS appear above, you MUST make a SEPARATE get_product_info call
       for EACH of the 3 guides listed. Do NOT skip any. Do NOT combine searches. 3 guides = 3 separate searches.
    2. Your final Location Recommendations #1, #2, #3 MUST match the 3 mandatory guides above — same order, same guides.
    3. If SUGGESTED SEARCH QUERIES (🔍) are listed, use THOSE EXACT queries in your get_product_info calls
       — They are pre-built from the bug Description to target the correct chapter, not just the intro
       — Example: call get_product_info(product="sdwan", query="objects and profiles prefix")
    3. Use the "Book PDF" name as your primary search source filter
    4. Only AFTER exhausting the suggested queries, try your own search terms
    ⚠️ Do NOT simplify or generalize the suggested queries. "configuration group" alone will return the wrong chapter.
    
    ⚠️ CRITICAL ANTI-HALLUCINATION RULES:
    1. ONLY use information that the get_product_info tool actually returned
    2. If the tool returns "❌ NO DOCUMENTS FOUND ❌", you MUST tell the user no documentation was found
    3. DO NOT invent document names, page numbers, sections, or quotes
    4. DO NOT make up plausible-sounding information
    5. When referencing content, quote EXACT text from the retrieved chunks
    6. When stating page numbers or sections, copy EXACTLY from the chunk metadata
    7. If metadata is "Not available", say so - don't guess or invent
    
    ⚠️ IMPORTANT: Be efficient with tool calls to avoid rate limiting (max 15 calls per minute)
    - Call get_product_info only when you need NEW information
    - Don't repeat searches with similar queries
    - Use the information from previous tool calls when possible
    
    answer:
    """

    product_prompt_template = PromptTemplate(
        input_variables=["product_name", "question"],
        template=product_version_prompt_template,
    )

    # Use the user-selected model (from sidebar dropdown)
    _model = st.session_state.get('selected_model', 'gpt-4o')
    llm = get_llm(model_name=_model)

    # Model-agnostic agent: works with GPT, Claude, Gemini — any model
    # that supports tool/function calling via LangChain
    agent_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful technical writing assistant that analyzes Cisco documentation."),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(
        llm=llm, tools=[get_product_info], prompt=agent_prompt
    )

    agent_executor = AgentExecutor(
        agent=agent, tools=[get_product_info], verbose=False, stream_runnable=False
    )
    
    res = agent_executor.invoke(
        input={
            "input": product_prompt_template.format_prompt(
                product_name=product_name,
                question=full_question,
            )
        }
    )

    return res


def format_output(result: dict) -> str:
    """Format the agent output in a readable way"""
    if 'output' in result:
        output_text = result['output']
        
        # Format the output with markdown
        formatted = f"""## 📋 Documentation Recommendation

{output_text}

---
### 🔍 Query Details
**Product:** {st.session_state.product_name}
**Status:** ✅ Analysis Complete
"""
        return formatted
    return "No output received from agent."


def apply_prompt_file(prompt_file_path: str, rca_content: str, product_name: str = "") -> str:
    """
    Apply a prompt from a markdown file to the RCA content
    
    Args:
        prompt_file_path: Path to the prompt.md file
        rca_content: The RCA/bug content to analyze
        product_name: Optional product name for context
    
    Returns:
        LLM response as string
    """
    # Read the prompt file
    with open(prompt_file_path, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    # Pre-extract Cisco documentation references from the content
    clues_data = extract_doc_clues_data(rca_content)
    doc_clues = format_doc_clues_for_prompt(clues_data, product_name=product_name)
    enriched_rca = rca_content
    if doc_clues:
        enriched_rca = doc_clues + "\n\n" + rca_content
    
    # Replace placeholders with actual content (use enriched version with doc clues)
    full_prompt = prompt_template.replace("{rca_content}", enriched_rca)
    full_prompt = full_prompt.replace("{extracted_text}", enriched_rca)
    full_prompt = full_prompt.replace("{product_name}", product_name)
    full_prompt = full_prompt.replace("{product}", product_name)
    
    # Get LLM and invoke (use selected model)
    _model = st.session_state.get('selected_model', 'gpt-4o')
    llm = get_llm(model_name=_model)
    result = llm.invoke(full_prompt)
    
    return result.content if hasattr(result, 'content') else str(result)


def run_agent_with_prompt_file(prompt_file_path: str, rca_content: str, product_name: str, selected_tech_terms: List[str] = None) -> str:
    """
    Run the agent with a custom prompt file and RAG capabilities
    
    This function is similar to run_agent() but allows using custom prompt files
    like ChapterFinder.md and ContentWriter.md while maintaining RAG functionality.
    
    Args:
        prompt_file_path: Path to the prompt.md file (e.g., "ChapterFinder.md")
        rca_content: The RCA/bug content to analyze
        product_name: Cisco product name for context
        selected_tech_terms: Optional list of user-selected technology terms to focus search on.
    
    Returns:
        Agent's response as string
    """
    # Read the prompt file
    with open(prompt_file_path, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    # Pre-extract Cisco documentation references from the content
    clues_data = extract_doc_clues_data(rca_content)
    doc_clues = format_doc_clues_for_prompt(clues_data, selected_terms=selected_tech_terms, product_name=product_name)
    
    # Store suggested search queries in session state for tool-level boost
    suggested_queries = clues_data.get('search_hints', {}).get('suggested_queries', [])
    if suggested_queries:
        import streamlit as st
        st.session_state._pending_search_queries = suggested_queries[:4]
    
    # Build the full question with RCA content (clues go in agent template, NOT here)
    full_question = f"""
{prompt_template}

---

### BUG/RCA CONTENT TO ANALYZE:

{rca_content}

---

Cisco Product: {product_name}
"""
    
    # Build the clues as a top-level section in the agent template
    doc_clues_section = ""
    if doc_clues:
        doc_clues_section = doc_clues
    
    # Create the agent prompt template
    agent_prompt_template = f"""
    Given a Cisco product name and analysis instructions, provide the requested analysis.
    Use your tools to fetch context from documentation to provide accurate recommendations.
    
    Cisco product: {{product_name}}
    {doc_clues_section}
    
    🚨 MANDATORY FIRST ACTIONS (before anything else):
    If PRE-EXTRACTED DOCUMENTATION REFERENCES appear above, you MUST:
    1. If SUGGESTED SEARCH QUERIES (🔍) are listed, use THOSE EXACT queries in your get_product_info calls
       — They are pre-built from the bug Description to target the correct chapter, not just the intro
       — Example: call get_product_info(product="sdwan", query="objects and profiles prefix")
    2. Use the "Book PDF" name as your primary search source filter
    3. Only AFTER exhausting the suggested queries, try your own search terms
    ⚠️ Do NOT simplify or generalize the suggested queries. "configuration group" alone will return the wrong chapter.
    
    Analysis request and content:
    {{question}}
    
    ⚠️ CRITICAL ANTI-HALLUCINATION RULES:
    1. ONLY use information that the get_product_info tool actually returned
    2. If the tool returns "❌ NO DOCUMENTS FOUND ❌", you MUST tell the user no documentation was found
    3. DO NOT invent document names, page numbers, sections, or quotes
    4. DO NOT make up plausible-sounding information
    5. When referencing content, quote EXACT text from the retrieved chunks
    6. When stating page numbers or sections, copy EXACTLY from the chunk metadata
    7. If metadata is "Not available", say so - don't guess or invent
    
    ⚠️ IMPORTANT: Be efficient with tool calls to avoid rate limiting (max 15 calls per minute)
    - Call get_product_info only when you need NEW information
    - Don't repeat searches with similar queries
    - Use the information from previous tool calls when possible
    
    analysis:
    """
    
    product_prompt_template = PromptTemplate(
        input_variables=["product_name", "question"],
        template=agent_prompt_template,
    )
    
    # Use the user-selected model (from sidebar dropdown)
    _model = st.session_state.get('selected_model', 'gpt-4o')
    llm = get_llm(model_name=_model)
    
    # Model-agnostic agent: works with GPT, Claude, Gemini
    agent_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful technical writing assistant that analyzes Cisco documentation."),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(
        llm=llm, tools=[get_product_info], prompt=agent_prompt
    )
    
    agent_executor = AgentExecutor(
        agent=agent, tools=[get_product_info], verbose=False, stream_runnable=False
    )
    
    res = agent_executor.invoke(
        input={
            "input": product_prompt_template.format_prompt(
                product_name=product_name,
                question=full_question,
            )
        }
    )
    
    # Extract the output
    if isinstance(res, dict) and 'output' in res:
        return res['output']
    return str(res)
