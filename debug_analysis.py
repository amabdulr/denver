#!/usr/bin/env python3
"""
Debug script that replicates the Analysis tab flow from sidebar_app.py
WITHOUT needing Streamlit.  Traces every step so you can see exactly
what the LLM will receive in {{RECOMMENDED_GUIDE}}, {{RECOMMENDED_SECTION}},
and {{RECOMMENDED_FORMAT}}.

Usage:
    python3 debug_analysis.py                   # default RCA (mss_clamping)
    python3 debug_analysis.py --rca template    # template negotiation RCA
    python3 debug_analysis.py --rca policy      # policy configuration RCA
    python3 debug_analysis.py --no-llm          # skip the actual LLM call
    python3 debug_analysis.py --rca policy --no-llm   # combine flags
"""

import importlib
import json
import sys
import os
import textwrap

# ── Ensure we're in the right directory ──
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ── Reload app_functions fresh ──
import app_functions
importlib.reload(app_functions)
from app_functions import (
    extract_doc_clues_data,
    match_terms_to_guides,
    format_doc_clues_for_prompt,
    _scan_for_networking_terms,
)

# ═══════════════════════════════════════════════════════════════════
# TEST RCAs — add more here as needed
# ═══════════════════════════════════════════════════════════════════

TEST_RCAS = {
    "mss_clamping": {
        "product": "Cisco SD-WAN",
        "description": "TCP MSS Clamping on cEdge C8300",
        "content": """\
Executive Summary:
This case addressed a customer inquiry regarding the behavior and configuration of TCP MSS (Maximum Segment Size) Clamping on Cisco Catalyst C8300-1N1S-4T2X routers running IOS-XE SD-WAN (cEdge) in controller mode. The customer specifically sought clarification on whether MSS clamping applies equally on both ingress and egress directions, and whether it affects both SYN and SYN+ACK packets. Additionally, they wanted to know if configuring MSS clamping only on the LAN-side interface is sufficient, or if it must also be set on tunnel interfaces. The root cause of the confusion stemmed from platform-dependent behavior and ambiguous documentation, leading to uncertainty in best practices for configuration.

Steps to Reproduce:
1. Configure `ip tcp adjust-mss` on both a tunnel interface and a LAN-side interface on a Cisco Catalyst C8300-1N1S-4T2X router.
2. Initiate TCP connections traversing both interfaces.
3. Observe MSS values in SYN and SYN+ACK packets using packet captures on both ingress and egress directions.
4. Repeat the test with MSS clamping configured only on the LAN-side interface.
5. Repeat the test with MSS clamping configured only on the tunnel interface.
6. Compare MSS values and connection behavior in all scenarios.

Condition:
- Device: Cisco Catalyst C8300-1N1S-4T2X (also referenced: C8200-1N-4T, C8000V)
- Software: IOS-XE SD-WAN (cEdge), version not explicitly stated but references to 17.x and 17.09.05 in related cases.
- Configuration:
  - `ip tcp adjust-mss <value>` applied on either or both of:
    - interface Tunnel X
    - interface XGigabitEthernet X (LAN-side)
- Traffic: TCP connections traversing the device, including both SYN and SYN+ACK packets.

Workarounds:
- If only one LAN interface is used for all tunnel traffic, apply `ip tcp adjust-mss` on the LAN interface to ensure all relevant traffic is clamped.

Procedure (Solution):
1. Identify all interfaces through which TCP traffic will traverse, especially those entering or exiting VPN tunnels.
2. Apply the MSS clamping configuration.
7. Reference official documentation for further details:
   - https://www.cisco.com/c/en/us/td/docs/routers/sdwan/configuration/system-interface/ios-xe-17/systems-interfaces-book-xe-sdwan/configure-interfaces.html#Cisco_Concept.dita_7e3ad6c7-1784-4beb-949b-a124ab4bc7f6

Root Cause:
The root cause of the confusion was the platform-dependent behavior of the `ip tcp adjust-mss` command and the lack of explicit documentation regarding its directionality (ingress/egress) on different Cisco hardware and software versions.
""",
    },

    "template": {
        "product": "Cisco SD-WAN",
        "description": "Feature template negotiation failure on vEdge",
        "content": """\
Executive Summary:
Customer reported that after upgrading vManage to 20.12.2, pushing a feature template to vEdge 2000 devices fails with error "Template negotiation failed - device unreachable". The template push worked fine on the previous vManage version 20.9.4. The issue affects all vEdge 2000 routers across the SD-WAN overlay, but Catalyst 8000v (cEdge) devices accept templates normally.

Steps to Reproduce:
1. Upgrade vManage from 20.9.4 to 20.12.2.
2. Open vManage Configuration > Templates.
3. Select an existing device feature template attached to a vEdge 2000.
4. Push the template to the vEdge 2000 device.
5. Observe the error "Template negotiation failed - device unreachable" in the task status.
6. Verify the same template pushes successfully to a cEdge (Catalyst 8000v) device.

Condition:
- vManage version: 20.12.2 (upgraded from 20.9.4)
- Device: vEdge 2000, software version 20.9.4
- Overlay: Full mesh topology with 150+ devices
- Control connections: All active, OMP sessions established
- Feature template: VPN 0 transport + VPN 512 management + system template

Workarounds:
- Downgrade vManage to 20.9.4 and re-push templates.
- Use CLI add-on template as a temporary workaround.

Procedure (Solution):
1. Verify control connections between vManage and vEdge devices using `show control connections`.
2. Check NETCONF session status on the vEdge device.
3. Reference: https://www.cisco.com/c/en/us/td/docs/routers/sdwan/configuration/sdwan-xe-gs-book/manage-devices.html
4. Upgrade vEdge devices to a compatible software version (20.12.x) to match vManage.

Root Cause:
The root cause was a NETCONF version mismatch between vManage 20.12.2 and vEdge 2000 running 20.9.4. The newer vManage uses NETCONF 1.1 by default, while older vEdge software only supports NETCONF 1.0, causing template push negotiation to fail.
""",
    },

    "policy": {
        "product": "Cisco SD-WAN",
        "description": "Centralized data policy not applying to traffic",
        "content": """\
Executive Summary:
Customer configured a centralized data policy on vManage to redirect traffic from VPN 10 to a service chain (firewall) for specific applications. The policy was successfully pushed to vSmart controllers, but traffic from branch sites is not being redirected according to the policy. Direct internet access (DIA) traffic bypasses the firewall entirely. The customer confirmed the policy shows as active on vSmart using `show running-config policy`.

Steps to Reproduce:
1. Create a centralized data policy in vManage under Configuration > Policies.
2. Define a match condition for VPN 10, matching application "Office365" traffic.
3. Define an action to redirect matching traffic to a service chain (Firewall at site 100).
4. Apply the policy to the target site list containing branch site IDs 200-210.
5. Activate the policy on vSmart controllers.
6. Generate Office365 traffic from a host in VPN 10 at branch site 200.
7. Observe that traffic takes the direct path instead of being redirected to the firewall.

Condition:
- vManage/vSmart version: 20.11.1
- Branch routers: Catalyst 8300 (cEdge), IOS-XE 17.11.1a
- Topology: Hub-and-spoke with regional hubs
- VPN 10: Corporate LAN, internet exit via DIA at branch
- Service chain: Palo Alto firewall at hub site 100
- Policy type: Centralized data policy with app-route match

Workarounds:
- Apply a localized data policy directly on the cEdge router as a temporary measure.
- Use access-list based PBR on the cEdge as a fallback.

Procedure (Solution):
1. Verify the policy is active on vSmart: `show running-config policy`.
2. Check that OMP routes include the policy from vSmart to cEdge: `show sdwan policy from-vsmart`.
3. Verify the service chain is reachable: `show sdwan service-chain database`.
4. Reference: https://www.cisco.com/c/en/us/td/docs/routers/sdwan/configuration/policies/ios-xe-17/policies-book-xe/centralized-policy.html
5. Ensure the site-list in the policy apply section includes the correct site IDs.

Root Cause:
The root cause was that the policy apply direction was set to "from-service" instead of "from-tunnel". Since branch traffic enters the SD-WAN fabric through the tunnel interface, the policy must be applied in the "from-tunnel" direction to match ingress traffic at the branch. With "from-service" direction, the policy only matches traffic originating from the local service-side (LAN) at the hub, not traffic arriving from remote branches.
""",
    },
}

# ═══════════════════════════════════════════════════════════════════
# Parse arguments
# ═══════════════════════════════════════════════════════════════════
SKIP_LLM = "--no-llm" in sys.argv

# Pick the RCA to test
rca_key = "mss_clamping"  # default
if "--rca" in sys.argv:
    idx = sys.argv.index("--rca")
    if idx + 1 < len(sys.argv):
        rca_key = sys.argv[idx + 1]

if rca_key not in TEST_RCAS:
    print(f"❌ Unknown RCA '{rca_key}'. Available: {', '.join(TEST_RCAS.keys())}")
    sys.exit(1)

selected_rca = TEST_RCAS[rca_key]
PRODUCT_NAME = selected_rca["product"]
RCA_CONTENT = selected_rca["content"]

print(f"🧪 Test RCA: {rca_key} — {selected_rca['description']}")
print(f"   Product: {PRODUCT_NAME}")
print(f"   Content: {len(RCA_CONTENT):,} chars\n")

def section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


# ═══════════════════════════════════════════════════════════════════
# STEP 1: Term detection (what the "Detect" button does)
# ═══════════════════════════════════════════════════════════════════
section("STEP 1: Technology Term Detection")

clues_data = extract_doc_clues_data(RCA_CONTENT)
all_detected_terms = [term for _, term in clues_data.get('tech_terms', [])]
url_clues = clues_data.get('url_clues', [])

print(f"Detected {len(all_detected_terms)} terms, {len(url_clues)} URL(s)")
print(f"\nURL Clues:")
for c in url_clues:
    print(f"  book_pdf:       {c['book_pdf']}")
    print(f"  book_id:        {c['book_id']}")
    print(f"  chapter_clues:  {c['chapter_clues']}")
    print(f"  url:            {c['url'][:100]}...")

print(f"\nDetected Terms ({len(all_detected_terms)}):")
for cat, term in clues_data.get('tech_terms', []):
    print(f"  [{cat:12s}] {term}")

# In the real UI, all terms start selected
selected_raw_terms = all_detected_terms  # user hasn't deselected any


# ═══════════════════════════════════════════════════════════════════
# STEP 2: Guide matching & scoring (what the checkbox expander does)
# ═══════════════════════════════════════════════════════════════════
section("STEP 2: Guide Matching & Scoring")

matched, available_guides = match_terms_to_guides(selected_raw_terms, PRODUCT_NAME)
guide_scores = matched.pop('_guide_scores', {})
matched_term_guides = dict(matched)  # what sidebar stores in session_state

print(f"\nGuide Scores (top 10):")
for g, s in sorted(guide_scores.items(), key=lambda x: -x[1])[:10]:
    terms_for_guide = [t for t, gl in matched_term_guides.items() if not t.startswith('_') and g in gl]
    print(f"  score={s:6.2f}  {g}")
    if terms_for_guide:
        print(f"          terms: {', '.join(terms_for_guide[:8])}")

print(f"\nMatched term → guide mapping ({len(matched_term_guides)} terms):")
for term, guides in sorted(matched_term_guides.items()):
    if term.startswith('_'):
        continue
    print(f"  {term:25s} → {guides}")

# Simulate auto-checked guides (what the UI does)
auto_matched_guides = set()
for term, guide_list in matched_term_guides.items():
    if term.startswith('_'):
        continue
    for g in guide_list:
        auto_matched_guides.add(g)

selected_guides = list(auto_matched_guides)
print(f"\nAuto-selected guides ({len(selected_guides)}):")
for g in sorted(selected_guides, key=lambda g: guide_scores.get(g, 0), reverse=True):
    print(f"  {'✅':2s} {g} (score={guide_scores.get(g, 0)})")


# ═══════════════════════════════════════════════════════════════════
# STEP 3: Simulate run_agent replacement logic
# ═══════════════════════════════════════════════════════════════════
section("STEP 3: run_agent() Replacement Logic")

# Load BugAnalyze.md (what the text area holds)
with open("BugAnalyze.md", "r") as f:
    question = f.read()

# --- Replicate run_agent logic exactly ---

# Pre-extract URL clues from RCA
clues_data_agent = extract_doc_clues_data(RCA_CONTENT)
url_clues_agent = clues_data_agent.get('url_clues', [])

recommended_label = None
section_label = None

# HIGHEST PRIORITY: URL clue
if url_clues_agent:
    url_book = url_clues_agent[0]['book_pdf']
    chapter_tokens = url_clues_agent[0].get('chapter_clues', [])
    url_score = guide_scores.get(url_book, 'n/a')
    recommended_label = f"{url_book} (from URL reference, score: {url_score})"
    if chapter_tokens:
        section_label = " ".join(t.title() for t in chapter_tokens)
    print(f"URL override active:")
    print(f"  url_book:        {url_book}")
    print(f"  chapter_tokens:  {chapter_tokens}")
    print(f"  url_score:       {url_score}")
else:
    print("No URL clues found — falling back to term scoring")

# FALLBACK: term-based scoring
if not recommended_label:
    if guide_scores:
        top_guide = max(guide_scores, key=guide_scores.get)
        top_score = guide_scores[top_guide]
        recommended_label = f"{top_guide} (confidence score: {top_score})"
    else:
        top_guide = None
        recommended_label = "(no guide scores available — use your best judgment from search results)"
else:
    top_guide = url_clues_agent[0]['book_pdf'] if url_clues_agent else None

# Section fallback
if not section_label:
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

print(f"\n--- FINAL REPLACEMENTS ---")
print(f"  {{{{RECOMMENDED_GUIDE}}}}   => {recommended_label}")
print(f"  {{{{RECOMMENDED_SECTION}}}} => {section_label}")

# Apply replacements
question = question.replace('{{RECOMMENDED_GUIDE}}', recommended_label)
question = question.replace('{{RECOMMENDED_SECTION}}', section_label)

# Check for any remaining unresolved placeholders
import re
remaining = re.findall(r'\{\{[^}]+\}\}', question)
if remaining:
    print(f"\n⚠️  UNRESOLVED PLACEHOLDERS ({len(remaining)}):")
    for p in remaining:
        print(f"    {p}")
else:
    print(f"\n✅ All placeholders resolved!")


# ═══════════════════════════════════════════════════════════════════
# STEP 4: Show the key lines the LLM will see
# ═══════════════════════════════════════════════════════════════════
section("STEP 4: Key Lines the LLM Sees (from BugAnalyze.md)")

for i, line in enumerate(question.split('\n'), 1):
    stripped = line.strip()
    if any(k in stripped for k in ['Recommended Guide:', 'Recommended Section:', 'Recommended Format:']):
        print(f"  Line {i}: {stripped}")


# ═══════════════════════════════════════════════════════════════════
# STEP 5: Build full_question (question + RCA)
# ═══════════════════════════════════════════════════════════════════
section("STEP 5: full_question Construction")

full_question = question + RCA_CONTENT
print(f"  question length:      {len(question):,} chars")
print(f"  rca_content length:   {len(RCA_CONTENT):,} chars")
print(f"  full_question length: {len(full_question):,} chars")


# ═══════════════════════════════════════════════════════════════════
# STEP 6: Build the agent prompt template
# ═══════════════════════════════════════════════════════════════════
section("STEP 6: Agent Prompt (what the LLM actually gets)")

doc_clues = format_doc_clues_for_prompt(clues_data_agent, selected_terms=selected_raw_terms, product_name=PRODUCT_NAME)

doc_clues_section = ""
if doc_clues:
    doc_clues_section = f"\n\n{doc_clues}\n"

guide_filter_message = ""
if selected_guides:
    guides_list = ', '.join(selected_guides)
    guide_filter_message = f"""

🎯 SEARCH SCOPE LIMITATION:
The user has selected specific guides to search. You MUST limit your search to these guides only:
{guides_list}

When calling get_product_info, the results will automatically be filtered to these guides.
"""

# ── Build pinned recs (replicate run_agent logic) ──
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

sorted_guides_list = sorted(guide_scores.items(), key=lambda x: -x[1]) if guide_scores else []

pinned_rec_section = ""
rec1_guide = None

if url_clues_agent and section_label and section_label != "(see location recommendations above)":
    rec1_guide = url_clues_agent[0]['book_pdf']
    pinned_rec_section = f"""
📌 PINNED LOCATION RECOMMENDATION #1 (pre-determined from documentation URL — DO NOT REPLACE):
══════════════════════════════════════════════════════════════════════
Document name: {rec1_guide}
Chapter/Section: {section_label}
Page number: <FILL IN from your search results within this chapter>
Actual content location indicator: <FILL IN — quote 8-15 words from a chunk in this chapter>
Detailed reasoning: The bug/RCA explicitly references this document and chapter via URL.
══════════════════════════════════════════════════════════════════════
"""
elif top_guide and section_label and section_label != "(see location recommendations above)":
    rec1_guide = top_guide
    pinned_rec_section = f"""
📌 SUGGESTED LOCATION RECOMMENDATION #1 (from term-based scoring — highest confidence):
══════════════════════════════════════════════════════════════════════
Document name: {rec1_guide}
Likely section topics: {section_label}
Page number: <FILL IN from your search results>
Actual content location indicator: <FILL IN — quote 8-15 words from a relevant chunk>
Detailed reasoning: This guide scored highest ({guide_scores.get(rec1_guide, 'n/a')}) based on detected technology terms.
══════════════════════════════════════════════════════════════════════
"""

# Pinned #2 and #3
remaining = [(g, s) for g, s in sorted_guides_list if g != rec1_guide]
for rank, (gname, gscore) in enumerate(remaining[:2], start=2):
    hints = _section_hints_for_guide(gname)
    hint_text = hints if hints else "(search this guide for relevant sections)"
    pinned_rec_section += f"""
📌 SUGGESTED LOCATION RECOMMENDATION #{rank} (from term-based scoring — score: {gscore}):
══════════════════════════════════════════════════════════════════════
Document name: {gname}
Likely section topics: {hint_text}
Page number: <FILL IN from your search results>
Actual content location indicator: <FILL IN — quote 8-15 words from a relevant chunk>
Detailed reasoning: This guide scored #{rank} ({gscore}) based on detected technology terms matching: {hint_text}
══════════════════════════════════════════════════════════════════════
"""

# Build the PromptTemplate equivalent
product_version_prompt = f"""
given a Cisco product name and a question from a user, return the answer.
Use your tools to fetch context to answer the question to provide a more accurate answer.

Cisco product: {PRODUCT_NAME}
{doc_clues_section}
{pinned_rec_section}
question: {full_question[:500]}...

[FULL QUESTION TRUNCATED — {len(full_question):,} chars total]
{guide_filter_message}

🚨 MANDATORY FIRST ACTIONS (before anything else):
1. If 📌 PINNED/SUGGESTED LOCATION RECOMMENDATIONS appear above, search within EACH of those documents
   to fill in the page numbers and content indicators. Use them as your Location Recommendations #1, #2, #3.
2. If SUGGESTED SEARCH QUERIES (🔍) are listed, use THOSE EXACT queries
3. Use the "Book PDF" name as your primary search source filter
4. Only AFTER exhausting the suggested queries, try your own search terms

answer:
"""

# Show the prompt (doc_clues section can be huge, so show separately)
print(product_version_prompt[:3000])
if len(product_version_prompt) > 3000:
    print(f"\n... [doc_clues section truncated]")

# Always show pinned recommendations clearly
if pinned_rec_section.strip():
    section("STEP 6b: Pinned Location Recommendations (sent to LLM)")
    print(pinned_rec_section)
else:
    print("\n⚠️  No pinned recommendations generated (missing URL clues and guide scores)")


# ═══════════════════════════════════════════════════════════════════
# STEP 7: (Optional) Run the actual LLM call
# ═══════════════════════════════════════════════════════════════════
if not SKIP_LLM:
    section("STEP 7: Actual LLM Call")
    print("Calling run_agent() — this will make real API calls...")
    print("(Use --no-llm flag to skip this step)\n")

    # We need to fake st.session_state since we're not in Streamlit
    import unittest.mock
    mock_session = {
        '_guide_scores': guide_scores,
        '_matched_term_guides': matched_term_guides,
        'selected_guides_for_search': selected_guides,
        'selected_model': 'gpt-4o',  # Model selection — change to test Claude/Gemini
    }

    # Patch streamlit session_state
    import streamlit as st
    for k, v in mock_session.items():
        st.session_state[k] = v

    try:
        from app_functions import run_agent
        result = run_agent(PRODUCT_NAME, open("BugAnalyze.md").read(), RCA_CONTENT, selected_guides, selected_raw_terms)

        section("STEP 8: LLM OUTPUT")
        output = result.get('output', str(result))
        print(output)

        # Check what the LLM said for Recommended Guide
        section("STEP 9: Checking LLM's Recommended Guide")
        for line in output.split('\n'):
            stripped = line.strip()
            if any(k in stripped.lower() for k in ['recommended guide', 'recommended section', 'recommended format']):
                print(f"  {stripped}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
else:
    section("STEP 7: Skipped (--no-llm)")
    print("Run without --no-llm to make actual LLM calls")

print(f"\n{'='*70}")
print("  Debug complete!")
print(f"{'='*70}")
