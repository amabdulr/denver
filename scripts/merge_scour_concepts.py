#!/usr/bin/env python3
"""
merge_scour_concepts.py
=======================
Properly merges ALL scour-discovered concepts into:
  1. networking_terms.json  (vocabulary)
  2. guide_mappings.json    (concept_to_guide.ASR9000)

The original merge only picked up terms already in the vocabulary (11%).
This script promotes scour-discovered terms INTO the vocabulary first,
then maps them to their guides.

Usage:
  python3 merge_scour_concepts.py --dry-run     # preview only
  python3 merge_scour_concepts.py               # apply changes
"""

import json, re, sys, copy
from pathlib import Path

DRY_RUN = "--dry-run" in sys.argv
PRODUCT_CODE = "ASR9000"

BASE = Path(__file__).parent
SCOUR_FILE      = BASE / "scour_output" / "raw_results.json"
VOCAB_FILE      = BASE / "networking_terms.json"
GUIDE_MAP_FILE  = BASE / "guide_mappings.json"

# ═══════════════════════════════════════════════════════════════════
# NOISE FILTERS
# ═══════════════════════════════════════════════════════════════════

# Reference guides — terms ONLY found in these are excluded
REFERENCE_GUIDE_PATTERNS = ["rcsi-0350", "vsmig", "asr9k-overview-reference"]

# Product noise — these are platform names, not networking concepts
PRODUCT_NOISE = {
    "asr9000", "asr9k", "asr 9000", "asr 9k", "cisco asr 9000",
    "cisco asr9000", "cisco asr 9k", "ios xr", "iosxr", "xr",
    "ncs", "ncs5500", "cisco 8000", "asr9902", "asr9903",
    "asr-9010", "asr-9006", "asr-9001", "asr-9904", "asr-9912",
    "asr-9922", "a99", "a9k", "rsp5", "rp3",
    "cisco ios xr", "cisco ios", "cisco asr 9000",
}

# Generic English words that are too broad to be useful as search terms
GENERIC_NOISE = {
    "configuration", "overview", "description", "system", "feature",
    "features", "example", "examples", "summary", "troubleshooting",
    "introduction", "chapter", "table", "figure", "section", "page",
    "command", "commands", "show", "configure", "verify", "display",
    "enable", "disable", "default", "general", "basic", "advanced",
    "information", "document", "guide", "reference", "manual",
    "warning", "warnings", "note", "notes", "caution", "tip",
    "important", "restriction", "restrictions", "limitation",
    "limitations", "prerequisites", "requirements", "requirement",
    "support", "supported", "status", "state", "mode", "type",
    "name", "value", "values", "number", "address", "port",
    "module", "card", "slot", "node", "device", "router", "switch",
    "server", "client", "host", "process", "service", "services",
    "interface", "interfaces", "connection", "session", "packet",
    "frame", "message", "event", "error", "errors", "failure",
    "log", "logs", "logging", "monitor", "monitoring",
    "update", "upgrade", "install", "version", "release",
    "user", "admin", "management", "control", "data", "plane",
    "active", "standby", "primary", "secondary", "backup",
    "local", "remote", "global", "static", "dynamic",
    "input", "output", "ingress", "egress", "inbound", "outbound",
    "source", "destination", "next", "previous", "first", "last",
    "new", "old", "current", "format", "content", "field",
    "parameter", "option", "options", "method", "rule", "rules",
    "policy", "list", "group", "class", "level", "size",
    "count", "counter", "counters", "rate", "limit", "maximum",
    "minimum", "timeout", "timer", "interval", "threshold",
    "path", "route", "entry", "record", "profile", "template",
    "map", "mapping", "table", "database", "cache", "buffer",
    "queue", "priority", "weight", "cost", "metric",
    "id", "identifier", "tag", "label", "key",
    "enable", "disable", "add", "remove", "delete", "create",
    "modify", "change", "set", "clear", "reset", "start", "stop",
    "open", "close", "up", "down", "on", "off", "yes", "no",
    "true", "false", "all", "none", "any", "each", "both",
    "same", "different", "specific", "particular", "certain",
    "multiple", "single", "dual", "redundancy", "compliance",
    "compatibility", "license", "licenses", "licensing",
}

# Physical/safety/hardware-only terms — won't appear in software bugs
PHYSICAL_NOISE = {
    # Compliance & safety
    "guide rails", "status leds", "shutdown button", "lifting chassis",
    "chassis lifting", "installing unit", "replacing unit", "unit installation",
    "unit replacement", "laser radiation", "class 1 laser", "class 1m laser",
    "unterminated fiber", "fiber cable", "unterminated fiber cable",
    "user-serviceable parts", "serviceable parts", "user serviceable parts",
    "user serviceable", "electrical codes", "local electrical codes",
    "national electrical codes", "national electrical code", "local electrical code",
    "power terminals", "terminal cover", "instructed person", "skilled person",
    "installation by skilled person", "installation by instructed person",
    "lifting requirement", "lifting requirements", "system power supply",
    "grounded outlet", "grounded equipment", "class a warning",
    "lightning surge", "ac power fault", "equipment interfacing",
    "ce mark", "product disposal", "disposal", "battery handling", "battery",
    "earthing", "earth", "restricted access", "repair",
    "electrical safety", "qualified person", "trained person", "lifting",
    "system power", "power connection", "terminals", "waste",
    "cispr22", "en55022", "cispr32", "en55032", "emc",
    "electromagnetic compatibility", "fcc", "ul", "iec",
    "blank faceplate", "cover panel", "blank panel", "blank panels",
    "blank faceplates", "cover panels", "blind covers",
    "aggregation router", "power disconnect", "dc power disconnect",
    "power terminal", "power source", "multiple power sources",
    "multiple power supply", "fuse", "chassis mounting",
    "optical cable", "electrical code", "electrical compliance",
    "qualified personnel", "trained personnel",
    "fiber optic safety", "fiber safety", "chassis handling",
    "dc power disconnection", "power disconnection", "circuit breaker",
    "breaker", "chassis warning", "rack-mounting", "servicing",
    "restricted area", "disconnect device", "ground conductor", "ground",
    "battery safety", "electrical terminals", "no user serviceable parts",
    "system power source", "emc compliance", "waste disposal", "recycling",
    "power", "dc", "fiber", "regulatory compliance", "safety information",
    "regulatory", "restricted access", "access control",
    "vcci", "vcci class a",
    # Hardware physical — won't appear in software/protocol bugs
    "led", "leds", "status led", "power supply", "power supplies",
    "ac power", "dc power", "grounding", "ground lug",
    "fan tray", "fan trays", "fan module", "air filter", "air filters",
    "cable management", "cable management bracket",
    "rack mounting", "rack mount", "rack-mount",
    "console port", "console cable", "serial port",
    "esd", "electrostatic discharge", "esd strap", "esd wrist strap",
    "hot swap", "hot swappable", "hot-swappable",
    "fiber optic", "fiber optics",
    "power cord", "power cords", "power cable", "power cables",
    "chassis ground", "chassis grounding",
    "screw", "screws", "captive screw", "captive screws",
    "torque", "torx", "phillips",
    "rj-45", "rj45", "db-9", "db9",
    "front panel", "rear panel", "faceplate",
    "2-post rack", "4-post rack", "19-inch rack",
    "airflow", "air flow", "cooling", "temperature",
    "weight", "dimensions", "height", "width", "depth",
    "watts", "amps", "volts", "btu",
    "xfp", "sfp+", "sfp", "qsfp", "qsfp+", "qsfp28", "qsfp-dd",
    "cfp", "cfp2", "cfp4", "cpak",
    # ISM/VSM hardware-specific
    "vsm card", "vsm installation", "vsm configuration", "vsm troubleshooting",
    "a9k-vsm-500", "virtualized services", "services module",
    "card installation", "card removal", "card status", "led status",
    "ova package", "vm activation", "show tech vsm",
    "tech support", "fabric counters", "np counters",
    "interlaken", "fabric interface", "crossbar",
    "fia", "fabric interface asic", "cbc", "can bus controller",
    "boot loader", "bmc", "board management controller",
    "fpga", "field programmable gate array", "calvados",
    "show controllers", "controller diagnostics",
    "crashinfo", "crash dump", "np crashinfo",
    "driver log", "np drvlog",
    # Very low-level counter/interface stats (from vsmig)
    "interlaken tx", "interlaken rx", "interlaken packets", "interlaken bytes",
    "interlaken bad packets", "interlaken crc error", "interlaken alignment error",
    "interlaken alignment failure", "interlaken block type error",
    "interlaken diag crc error", "interlaken word sync error",
    "fabric stats", "fabric fia", "xbar", "unicast xbar", "multicast xbar",
    "ingress drop", "egress drop", "fabric drop",
    "np ports", "np bridge", "tengige", "ten gig",
    "interface counters", "interface statistics", "mdf", "parse",
    "punt statistics", "netio", "diags", "health monitor",
    "frame type", "packet drops", "input drops", "output drops",
    "crc errors", "interface errors", "underruns", "overruns",
    "runts", "giants", "throttles", "parity", "frame errors",
    "abort", "ignored", "applique", "buffer failures",
    "carrier transitions", "full duplex", "link type", "force up",
    "reliability", "txload", "rxload", "arpa",
    "broadcast packets", "multicast packets",
    "input rate", "output rate", "packets per second",
    "ten gigabit ethernet", "show interface",
    "administratively down", "line protocol", "full-duplex",
    "packets input", "packets output", "input errors", "crc", "frame",
    "overrun", "output errors", "resets", "switch", "data-path",
    "xaui", "rxaui", "pve", "switch statistics", "mac counters",
    "good octets", "good packets", "bad octets",
    "unicast packets", "excessive collisions", "collisions",
    "undersize packets", "oversized packets", "jabber packets",
    "mac receive error", "bad crc", "dropped packets",
    "late collisions", "deferred packets",
    "show drops", "np drops", "bridge drops", "fia drops",
    "crc error", "align fail", "bad code", "prot err", "protocol error",
    "network processor counters", "parse error",
    "ingress drops", "crc err", "alignment failure",
    "sgmii counters", "sgmii", "serial gigabit media independent interface",
    "punt path counters", "punt counters", "punting",
    "frame counters", "fcs error", "fcs err", "frame check sequence",
    "length error", "oversize frames", "jabber frames",
    "undersize frames", "fragment frames",
    "multicast frames", "broadcast frames", "control frames", "pause frames",
    "spp stats", "spp", "shared port processor",
    "sid stats", "stream id", "netio drops", "network io",
    "interface drops", "unknown protocol", "pifib",
    "platform independent forwarding information base",
    "hardware entry statistics", "node counters",
    "inject", "injection", "packet injection",
    "fabric receive", "fabric transmit",
    "parse counters", "modify punt", "diag", "tm loop", "traffic manager",
    "punt reason", "exceed max frame", "code error",
    "config register", "show diag", "show version", "show tech-support",
    "clns", "icmp6", "node drop counts", "drop statistics",
    "hardware statistics", "ucode", "microcode", "cpld",
    "system bootstrap", "asr-9010",
    # ISM-specific
    "ism", "integrated service module", "ism line card",
    "integrated service module line card",
    "service acceleration module", "service acceleration modules",
    "line card installation", "line card removal",
    "system recovery mode", "recovery mode",
    "service-management interface", "service-mgmt",
    "service management interface", "service engine interface", "service-engine",
    "cds", "content delivery system", "cds-tv", "content delivery system tv",
    "iso image", "avsm", "advanced video services module",
    "cdsinstall", "cdsconfig", "vvim", "video virtual infrastructure manager",
    "cdsm", "content delivery system manager", "stream manager",
    "show hw-module", "interface connector",
    # Licensing-specific (separate product domain)
    "flexible consumption model", "fcm", "flexible consumption",
    "consumption model", "right to use", "rtu", "rtu licenses",
    "per-system license", "per-port license",
    "à la carte license", "a la carte license", "alacarte license",
    "non-consumption model", "software innovation access", "sia",
    "sia licenses", "license consumption", "license compliance",
    "compliance status", "license entitlements", "entitlements",
    "license term", "license offerings", "licensing solutions",
    "smart software manager", "smart software manager on-prem",
    "ssm on-prem", "cisco smart licensing utility", "cslu",
    "direct deployment", "on-premises deployment", "offline deployment",
    "air-gapped", "specific license reservation",
    "rum reports", "rum", "resource utilization measurement",
    "perpetual mode", "smart licensing perpetual",
    "license activation", "license upgrade", "license downgrade",
    "license migration",
}

# Min term length
MIN_TERM_LENGTH = 2

# ═══════════════════════════════════════════════════════════════════
# LOAD DATA
# ═══════════════════════════════════════════════════════════════════

print("Loading data...")
with open(SCOUR_FILE) as f:
    scour_data = json.load(f)

with open(VOCAB_FILE) as f:
    vocab_data = json.load(f)

with open(GUIDE_MAP_FILE) as f:
    guide_map_data = json.load(f)

# Build existing vocab set
existing_vocab = set()
for cat in vocab_data.values():
    if isinstance(cat, list):
        existing_vocab.update(t.lower() for t in cat)

# Get existing concept map
existing_asr_map = guide_map_data.get("concept_to_guide", {}).get(PRODUCT_CODE, {})

# Get product_noise from guide_mappings too
gm_product_noise = set()
pn = guide_map_data.get("product_noise", {})
for product_terms in pn.values():
    if isinstance(product_terms, list):
        gm_product_noise.update(t.lower() for t in product_terms)

all_noise = PRODUCT_NOISE | GENERIC_NOISE | PHYSICAL_NOISE | gm_product_noise

print(f"  Scour entries: {len(scour_data)}")
print(f"  Existing vocab: {len(existing_vocab)} terms")
print(f"  Existing ASR9000 concept map: {len(existing_asr_map)} entries")
print(f"  Noise filter: {len(all_noise)} terms")

# ═══════════════════════════════════════════════════════════════════
# BUILD SCOUR CONCEPT → GUIDE MAPPINGS
# ═══════════════════════════════════════════════════════════════════

print("\nProcessing scour concepts...")

# term → set of PDF filenames
scour_term_to_guides = {}

for item in scour_data:
    filename = item["filename"]
    concepts = item.get("concepts", {})
    if not isinstance(concepts, dict):
        continue
    
    for term in concepts:
        t = term.lower().strip()
        if t:
            scour_term_to_guides.setdefault(t, set()).add(filename)

print(f"  Total unique scour concepts: {len(scour_term_to_guides)}")

# ═══════════════════════════════════════════════════════════════════
# FILTER
# ═══════════════════════════════════════════════════════════════════

print("\nFiltering...")

filtered_out = {
    "reference_only": 0,
    "product_noise": 0,
    "generic_noise": 0,
    "too_short": 0,
    "numeric": 0,
    "already_mapped": 0,
}

new_terms = {}  # term → set of guide PDFs (to add)

for term, guides in scour_term_to_guides.items():
    # Skip if too short
    if len(term) <= MIN_TERM_LENGTH:
        filtered_out["too_short"] += 1
        continue
    
    # Skip purely numeric
    if re.match(r'^[\d\.\-]+$', term):
        filtered_out["numeric"] += 1
        continue
    
    # Skip if only found in reference guides
    non_ref_guides = {g for g in guides if not any(rp in g for rp in REFERENCE_GUIDE_PATTERNS)}
    if not non_ref_guides:
        filtered_out["reference_only"] += 1
        continue
    
    # Skip product noise
    if term in all_noise:
        filtered_out["product_noise"] += 1
        continue
    
    # Skip if already fully mapped (in both vocab AND concept map)
    if term in existing_vocab and term in existing_asr_map:
        filtered_out["already_mapped"] += 1
        continue
    
    # Use only non-reference guides for the mapping
    new_terms[term] = non_ref_guides

print(f"  Reference guide only: {filtered_out['reference_only']}")
print(f"  Product/generic noise: {filtered_out['product_noise'] + filtered_out['generic_noise']}")
print(f"  Too short/numeric: {filtered_out['too_short'] + filtered_out['numeric']}")
print(f"  Already fully mapped: {filtered_out['already_mapped']}")
print(f"  ✅ Terms to add/update: {len(new_terms)}")

# Split into: new to vocab vs already in vocab
new_to_vocab = {t: g for t, g in new_terms.items() if t not in existing_vocab}
existing_vocab_new_map = {t: g for t, g in new_terms.items() if t in existing_vocab}

print(f"\n  New to vocabulary: {len(new_to_vocab)}")
print(f"  In vocab but need map update: {len(existing_vocab_new_map)}")

# ═══════════════════════════════════════════════════════════════════
# CATEGORIZE NEW VOCAB TERMS
# ═══════════════════════════════════════════════════════════════════

# Simple heuristic: check if it's a known protocol pattern
PROTOCOL_PATTERNS = {
    "tcp", "udp", "icmp", "igmp", "pim", "rsvp", "ldp", "bgp", "ospf",
    "isis", "is-is", "rip", "eigrp", "lisp", "vrrp", "hsrp", "glbp",
    "snmp", "ssh", "telnet", "ftp", "tftp", "http", "https", "ntp",
    "ptp", "stp", "rstp", "lacp", "lldp", "cdp", "arp", "dhcp",
    "dns", "radius", "tacacs", "diameter", "grpc", "gnmi", "gnoi",
    "netconf", "restconf", "pcep", "bfd", "cfm", "oam",
    "mpls", "gre", "ipsec", "macsec", "dot1x", "eap",
    "l2tp", "pppoe", "ppp", "ipoe",
}

TECHNOLOGY_PATTERNS = {
    "vpn", "vrf", "evpn", "vpls", "vxlan", "mpls", "segment routing",
    "sr-te", "srv6", "traffic engineering", "qos", "netflow", "sflow",
    "telemetry", "multicast", "unicast", "broadcast", "anycast",
    "nat", "cgnat", "bng", "cnbng", "bfd", "nso",
    "cloud native", "sdn", "nfv", "virtualization",
}

def categorize_term(term):
    """Decide if a term is a protocol, technology, or feature."""
    t = term.lower()
    # Check protocol patterns
    for p in PROTOCOL_PATTERNS:
        if t == p or t.startswith(p + " ") or t.endswith(" " + p):
            return "protocols"
    # Check technology patterns
    for tech in TECHNOLOGY_PATTERNS:
        if tech in t:
            return "technologies"
    # Multi-word terms default to features
    return "features"

# ═══════════════════════════════════════════════════════════════════
# BUILD UPDATES
# ═══════════════════════════════════════════════════════════════════

# Vocab additions by category
vocab_additions = {"protocols": [], "technologies": [], "features": []}
for term in sorted(new_to_vocab.keys()):
    cat = categorize_term(term)
    vocab_additions[cat].append(term)

# Concept map additions/updates
concept_map_updates = {}
for term, guides in new_terms.items():
    # Merge with existing mapping if any
    existing_guides = set(existing_asr_map.get(term, []))
    merged = sorted(existing_guides | guides)
    concept_map_updates[term] = merged

# ═══════════════════════════════════════════════════════════════════
# REPORT
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("MERGE SUMMARY")
print("=" * 70)

print(f"\nVocabulary additions:")
for cat, terms in vocab_additions.items():
    print(f"  {cat}: +{len(terms)} terms")
    if len(terms) <= 20:
        for t in terms:
            print(f"    • {t}")
    else:
        for t in terms[:10]:
            print(f"    • {t}")
        print(f"    ... and {len(terms) - 10} more")

total_vocab_add = sum(len(t) for t in vocab_additions.values())
print(f"\n  TOTAL vocab additions: {total_vocab_add}")
print(f"  New vocab size: {len(existing_vocab) + total_vocab_add}")

print(f"\nConcept map updates: {len(concept_map_updates)} entries")
new_map_entries = sum(1 for t in concept_map_updates if t not in existing_asr_map)
updated_map_entries = sum(1 for t in concept_map_updates if t in existing_asr_map)
print(f"  Brand new entries: {new_map_entries}")
print(f"  Updated (added guides): {updated_map_entries}")
print(f"  New concept map size: {len(existing_asr_map) + new_map_entries}")

# Show sample of high-value multi-book terms
print(f"\n{'='*70}")
print("SAMPLE HIGH-VALUE ADDITIONS (terms mapping to 2+ guides)")
print("=" * 70)
multi_guide = {t: g for t, g in concept_map_updates.items() if len(g) >= 2 and t not in existing_asr_map}
for term, guides in sorted(multi_guide.items(), key=lambda x: -len(x[1]))[:30]:
    short = [g.replace('.pdf','').replace('b-','')[:40] for g in guides]
    print(f"  {term:40s} → {len(guides)} guides: {short[:3]}")

# ═══════════════════════════════════════════════════════════════════
# APPLY CHANGES
# ═══════════════════════════════════════════════════════════════════

if DRY_RUN:
    print(f"\n🔍 DRY RUN — no files modified. Run without --dry-run to apply.")
    sys.exit(0)

print(f"\n📝 Applying changes...")

# Update vocab
for cat, terms in vocab_additions.items():
    if cat in vocab_data and isinstance(vocab_data[cat], list):
        vocab_data[cat].extend(terms)
        vocab_data[cat] = sorted(set(vocab_data[cat]), key=str.lower)

with open(VOCAB_FILE, "w") as f:
    json.dump(vocab_data, f, indent=4, ensure_ascii=False)
print(f"  ✅ Updated {VOCAB_FILE.name} (+{total_vocab_add} terms)")

# Update concept map
if PRODUCT_CODE not in guide_map_data["concept_to_guide"]:
    guide_map_data["concept_to_guide"][PRODUCT_CODE] = {}

asr_map = guide_map_data["concept_to_guide"][PRODUCT_CODE]
for term, guides in concept_map_updates.items():
    asr_map[term] = guides

# Sort the concept map alphabetically
guide_map_data["concept_to_guide"][PRODUCT_CODE] = dict(
    sorted(asr_map.items(), key=lambda x: x[0].lower())
)

with open(GUIDE_MAP_FILE, "w") as f:
    json.dump(guide_map_data, f, indent=4, ensure_ascii=False)
print(f"  ✅ Updated {GUIDE_MAP_FILE.name} (+{new_map_entries} new, {updated_map_entries} updated)")

print(f"\n🎉 Merge complete!")
