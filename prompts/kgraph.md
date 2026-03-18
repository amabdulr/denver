# Gen AI Prompt: Extract RDF Triples from Documentation

## Goal:
Extract structured RDF triples (Subject, Predicate, Object) from a given documentation chapter.
**If any field would contain a comma, replace internal commas with semicolons to ensure the CSV always has exactly five columns.**

## Instructions to Model:

You are an AI agent analyzing a Cisco networking product's documentation, for example, a configuration chapter, installation chapter, user guide chapter, troubleshooting guide, etc. Your task is to parse the content and extract structured **RDF triples** following the below rules. The output must be a pipe-delimited table with the columns:

```
Subject|Predicate|Object|CategoryType|SourceTrace
```

Use controlled vocabulary for **predicates**, generate **canonical nodes & phrases**, decompose long ideas into **multiple triples**, and ensure **soft categorization** of all subject and object nodes.

### SourceTrace Field (Traceability Column)

The fifth column **SourceTrace** captures grounding information from the source document.

Format:

SourceFileName :: Container Section Title :: First Five Words of source sentence...

Example:

Implementing-bgp :: Configure BGP-LU over RSVP-TE :: This example shows how to...

Rules:
- Use **double-colon `::`** as the internal delimiter within this column.
- The main CSV delimiter **remains the pipe `|`**.
- Always extract the **first five words** from the sentence where the fact originates.
- The container section title must match the nearest section heading in the topic/content hierarchy.
- Use the chapter or document filename (without extension) as SourceFileName. No page numbers needed.

---

## 1. Feature History Table Handling and Analysis (Neutralized)

- If a **Feature History Table** is present, treat it as a **high-confidence source** of introduced/enhanced/deprecated feature data.  
- If no Feature History Table exists, continue extraction from section headers, descriptive sentences, and other structural cues (for example, "New in Release X.Y.Z").  
- Do **not assume** a Feature History Table must exist in every document. If absent, skip this priority step gracefully.  

- **Locate tables titled** `Feature History Table`. These are 3-column tables.
- For each row in the table:
  - Extract the **feature name** (from *Feature Name* column)and create a **canonical label** if multiple synonyms are detected. Link synonyms using `altLabel`.
    - → `Feature, isA, Feature`
	- → `Avoiding Congestion, altLabel, Congestion Avoidance														   
  - **Determine the earliest IOS XR release version from the bottom-most row**:
    - → `Feature, introducedIn, IOS-XR version` for example, 7.5.1.
  - **For any and all subsequent releases (rows above), use**:
    - → `Feature, enhancedIn, IOS-XR version` for example, 7.5.3 or 24.4.1.
  - Do **not** infer enhancements from description phrases like "Earlier" or "Previously" in the *Feature Description* column—only use the table’s *Release Information* column in order to determine introduction vs. enhancement for a feature.
   
  - When comparing release version numbers, always split the version into its numeric components and compare each segment from left to right as an integer. For example:
   - For versions "7.11.1" and "24.1.1":
    - Compare the first segment: 7 vs. 24 (since 7 < 24, "7.11.1" is older).
    - If the first segment is equal, compare the second segment, and so on.
   - This ensures that "7.11.1" is always treated as an **older** release than "24.1.1", regardless of string sorting order.

  - If the *Description* column includes benefits (e.g., "supports lossless Ethernet"):
    - → `Feature, hasBenefit, [summarized benefit text]`
  - If it mentions additional hardware support (e.g., “introduced in this release on…”):
    - → `Feature, availableOn, [platforms]`
  - If it says “select variants only”:
    - → `Feature, availableOn, [hardware model]`
  - If it says “not supported on…”:
    - → `Feature, notSupportedOn, [platforms]`


### 1.1 Section Priority Logic

- Prioritize **section titles** and **explicit markers** (for example: *Limitations*, *Restrictions*, *Benefits*, *Guidelines*, *Concepts*, *Usage Guidelines*).  
- For docs **without Feature History Tables** (e.g., Hyperfabric):  
  - Extract features, concepts, limitations, and guidelines **based on section headers** rather than expecting structured tabular history.  
  - Look for phrasing like "Hyperfabric supports …", "This feature allows …", "Limitations include …" as evidence.  
- For docs **with Feature History Tables** (e.g., IOS-XR guides):  
  - Continue structured extraction using the Feature History Table and other related sections.  

---

## 2. Main Body Analysis (Core Content)

- Identify and extract relationships involving:
  - **Features**:
    - `RED, isA, [Technology] Feature` (e.g., "RED, isA, QoS Feature")
    - `RED, enables, Congestion Avoidance`
  - **Concepts**:
    - `Congestion Avoidance, isA, [Technology] Concept`
  - **Verification CLI commands** (highlighted code or CLI lines):
    - `Feature, verifiedBy, show [command]`
  - **Mandatory behaviors or defaults**:
    - `Feature, enables, [Functionality]`
	- `Feature, isFunctionOf, [Solution Domain]`
  - **Mandatory attributes or capabilities of a feature**:
    - `Feature, hasKeyAttribute, [Attribute]`
  - **Usage limitations**:
    - `Feature, hasLimitation, [text]`
  - **Platform support**:
    - `Feature, availableOn, Cisco 8000`
  - **Unsupported platforms**:
    - `Feature, notSupportedOn, [platform]`
  - **Relationships between CLI entities and config frameworks (e.g., MQC)**:
    - `MQC, usesComponent, Class-Map`
	
## 2A. Configuration Task Extraction Rules

Configuration tasks represent the primary procedural method used to configure a feature using CLI, GUI, templates, or automation interfaces.

Detect configuration tasks using structural cues such as:

- Section titles beginning with **"Configure"**
- Titles containing **"Using CLI"**, **"Using CLIs"**, **"Using GUI"**, **"Configuration Example"**
- Sections containing **"Before you begin"** followed by **"Procedure"**
- Sections describing explicit configuration workflows for a feature

### Extraction Rules

For each detected configuration task:

1. Create a **Configuration node** using the exact task title and assign the correct category type based on configuration method.

Example: Configure path limit using CLI commands


2. Link the feature to the configuration task using:

Feature|usesProcedure|Configuration Task Title|CLIConfiguration
Feature|usesProcedure|Configure Application-Aware Routing using the dashboard|GUIConfiguration


3. Extract **prerequisites** from sections such as **"Before you begin"** using:

Configuration Task|requires|<prerequisite text>|Configuration


4. Extract **verification commands** if present using:

Configuration Task|verifiedBy|show <command>|CLICommand


5. Extract a **single concise task purpose** from the task introduction or explanatory sentence using:

Configuration Task|enables|<task purpose>|Functionality

### Configuration Type Classification

Each configuration task must be classified as either **CLIConfiguration** or **GUIConfiguration**.

Determine the configuration type using the following cues:

CLIConfiguration
- Section titles containing phrases such as:
  - "Using CLI"
  - "Using CLIs"
  - "Using the CLI"
  - "Configure using commands"
- Presence of command syntax blocks or CLI prompts such as:
  - router(config)
  - show commands
  - configuration mode syntax
- Tasks that primarily use command-line interface instructions.

GUIConfiguration
- Section titles containing phrases such as:
  - "Using GUI"
  - "Using the web UI"
  - "Using the dashboard"
  - "Using the management interface"
  - "Using configuration groups"
- Tasks that involve clicking menus, selecting options, or interacting with graphical controls.

If both CLI and GUI workflows exist for the same feature, extract **two separate configuration task nodes**, each linked to the feature.


### Important Constraint

Do **NOT** extract each numbered procedural step as an RDF triple.

Only represent the configuration task title itself and classify it as either:

CLIConfiguration
GUIConfiguration

Include:
- task prerequisites
- verification commands
- task purpose

Do not model individual steps inside the procedure.

Reason:
- Procedural steps are often reused across procedures
- Individual steps lose semantic context when isolated
- Step-level triples significantly increase graph noise

Only represent the **configuration task itself**, its **prerequisites**, **verification**, and **purpose**.

---

## 2B. Task-Intent Extraction (RAG Query Bridging)

Users ask questions like *"How do I configure NAT64?"*, *"How do I set up OSPF over SD-WAN?"*, or *"What are the steps for upgrading firmware?"*. Standard `isA` / `enables` triples do not bridge these **task-intent queries** to features or procedures.

### Goal

Create triples that map a **user's likely question or task intent** to the feature, configuration procedure, or concept that answers it.

### Detection Cues

- Section titles starting with **"Configure"**, **"Set Up"**, **"Enable"**, **"Deploy"**, **"Provision"**, **"Create"**, **"Migrate"**
- Introductory sentences like *"Use this procedure to …"*, *"To configure X, perform …"*, *"This section describes how to …"*
- Sections titled **"Before You Begin"**, **"Prerequisites"**, **"Workflow"**

### Extraction Rules

For each detected task-intent section:

1. **Create a TaskIntent node** using a natural-language question form:

```
Configure NAT64|answersQuestion|How do I configure NAT64 on SD-WAN?|TaskIntent
```

2. **Link the task intent to the feature it configures:**

```
How do I configure NAT64 on SD-WAN?|relatesTo|NAT64|Feature
```

3. **Link the task intent to the procedure:**

```
How do I configure NAT64 on SD-WAN?|addressedBy|Configure NAT64 Using CLI|CLIConfiguration
```

4. **Extract prerequisite context for the task:**

```
How do I configure NAT64 on SD-WAN?|requires|NAT must be enabled on the device|Prerequisite
```

### Important Constraints

- Generate 1–3 task-intent questions per configuration section. Focus on the most likely user phrasing.
- Use **short, natural question forms** — the kind a network engineer would type into a search box.
- Do NOT generate task-intents for purely conceptual/overview sections that have no actionable procedure.

---

## 2C. Troubleshooting & Symptom Extraction

Users ask *"Why is my BFD session flapping?"*, *"NAT DIA failover not working"*, or *"OMP routes not propagating"*. The knowledge graph must link **symptoms and error conditions** to **features, causes, and resolution procedures**.

### Detection Cues

- Sections titled **"Troubleshoot"**, **"Troubleshooting"**, **"Common Issues"**, **"Known Issues"**, **"Error Messages"**, **"FAQ"**, **"Workaround"**
- Sentences containing: *"If you see …"*, *"When X fails …"*, *"This error occurs when …"*, *"Workaround:"*, *"Resolution:"*

### Extraction Rules

1. **Extract symptom/problem nodes:**

```
BFD Session Flapping|isA|Symptom|Troubleshooting
OMP Routes Not Propagating|isA|Symptom|Troubleshooting
```

2. **Link symptom to the feature or component it affects:**

```
BFD Session Flapping|affects|BFD|Feature
OMP Routes Not Propagating|affects|OMP|Feature
```

3. **Link symptom to its cause (if stated):**

```
BFD Session Flapping|causedBy|MTU mismatch on transport interface|Cause
```

4. **Link symptom to resolution or workaround:**

```
BFD Session Flapping|resolvedBy|Verify and match MTU on both endpoints|Resolution
OMP Routes Not Propagating|resolvedBy|Check vSmart reachability and OMP timers|Resolution
```

5. **Link symptom to verification command:**

```
BFD Session Flapping|verifiedBy|show bfd sessions|CLICommand
```

### Important Constraints

- Only extract from sections that are explicitly about troubleshooting, workarounds, known issues, or error conditions.
- Do NOT convert general negative statements (e.g., "Feature X does not support Y") into symptoms — those belong under `hasRestriction` or `hasLimitation` per Section 8B rules.
- Keep symptom descriptions short and recognizable — the kind of phrase an engineer would search for.

---

## 2D. Concept-to-Concept and Synonym Linking (RAG Recall Improvement)

RAG retrieval fails when users use **different terminology** than what appears in the documentation. For example, a user searching *"tunnel failover"* should find content about *"High Availability"* and *"Disaster Recovery"*.

### Rules

1. **Link related concepts that a user might confuse or use interchangeably:**

```
Tunnel Failover|relatedTo|High Availability|Concept
SD-WAN Fabric|relatedTo|Overlay Network|Concept
Zero Touch Provisioning|altLabel|ZTP|Concept
vManage|altLabel|Cisco SD-WAN Manager|Platform
```

2. **Link parent-child technology relationships:**

```
Application-Aware Routing|isPartOf|SD-WAN Policies|Technology
NAT64|isPartOf|NAT|Technology
OSPFv3|isPartOf|OSPF|Technology
```

3. **Link features to the book/guide they belong to:**

```
NAT64|definedInChapter|Configure NAT64|Documentation
High Availability|definedInChapter|High Availability Configuration Guide|Documentation
```

### Detection Cues

- Introductory paragraphs that mention *"also known as"*, *"formerly called"*, *"sometimes referred to as"*
- Sections that cross-reference other guides or chapters
- Abbreviations and their expansions
- Feature names that are subsets of broader technology areas

### Important Constraints

- Generate `altLabel` triples for **every abbreviation** you encounter (e.g., AAR, BFD, OMP, TLOC, VPN, vSmart).
- Generate `isPartOf` triples to place features within their technology hierarchy.
- Generate `relatedTo` triples conservatively — only for concepts that a user would reasonably confuse or use as alternative search terms.

---

## 2E. Graph Connectivity Rule (No Orphan Entities)

Every entity you introduce as a **Subject** must appear in **at least two triples** — either as Subject or Object — so that it is connected to the chapter's knowledge graph. Specifically:

1. **Hub entity**: Identify the chapter's primary feature or technology (e.g., AppNav-XE, DRE, BFD). This is the **hub** of the chapter graph.
2. **Satellite rule**: Any non-hub entity you introduce as a Subject MUST have at least one triple connecting it back to the hub (directly or through another satellite). Use `isPartOf`, `usesComponent`, `relatedTo`, or any appropriate predicate from Section 8.
3. **No standalone `isA`-only nodes**: Do not emit an entity with only a single `isA` triple and no other connections. Either add a connecting predicate or omit the entity.
4. **Platform/technology scaffolding**: Generic platform or technology entities (e.g., "Cisco Catalyst SD-WAN|isA|SD-WAN Technology") are permitted **only if** they also appear as an Object in another triple from the same chapter (e.g., "AppNav-XE|availableOn|Cisco Catalyst SD-WAN").

**Example — WRONG (orphan):**
```
Asymmetric flow|isA|Network Concept|Concept|...
```
(No other triple references "Asymmetric flow" — this is a dead-end node.)

**Example — CORRECT (connected):**
```
Asymmetric flow|isA|Network Concept|Concept|...
AppNav-XE|supports|Asymmetric flow|Functionality|...
```
(Now "Asymmetric flow" is reachable from the hub.)

---

## 3. Inferring Technology Affiliation for Features (If Not Explicit in Feature History Table)

If a feature's technology affiliation (e.g., QoS, MPLS, SRv6) is **not explicitly mentioned** in the Feature History Table, use the following inference strategies:

1. **Chapter or Section Title Context**
   - If the chapter or section is titled with a known technology, assign that as the parent technology.
   - **Example:**
     - Chapter title: `Congestion Management` → classify features as `QoS Feature`

2. **Introductory Paragraph Heuristics**
   - Scan leading paragraphs for phrases like:
     - “This feature enhances MPLS traffic engineering...”
     - “Used in SRv6 flow classification...”
   - Use NLP or regex to extract technology references.

3. **CLI or Configuration Context**
   - Analyze associated CLI syntax:
     - `class-map`, `policy-map` → `QoS Feature`
     - `mpls traffic-eng` → `MPLS Feature`
     - `segment-routing srv6` → `SRv6 Feature`

---
Use controlled vocabulary for **predicates** and ensure **soft categorization** of all subject and object nodes.

## 4. Rule for `isFunctionOf` Predicate Extraction

When extracting RDF triples, always attempt to associate each feature, capability, or outcome with its solution domain or functional theme using the `isFunctionOf` predicate.

- **If the solution domain (functional category) is explicit** in the chapter/section title, heading, or table title, map the feature or functionality directly to that domain.  
  *Example:*  
  `RED,isFunctionOf,Congestion Avoidance`
- **If not explicit**, apply the following logic:
  1. **Analyze feature descriptions, benefits, limitations, or overview sentences** for keywords that match known solution domain categories.
  2. **Compare against a controlled vocabulary** (such as: Congestion Management, Traffic Engineering, Classification, Policing, Lossless Ethernet, Queue Management).
  3. **Review CLI/configuration examples** for technology hints (e.g., `policy-map` or `mpls traffic-eng`).
  4. **If still ambiguous**, default to the parent section or guide’s primary technology category.

**Example triples:**

```
WRED,isFunctionOf,Congestion Avoidance
Priority Propagation on Egress Queues isFunctionOf Congestion Management
Tail Drop,isFunctionOf,Congestion Avoidance
```


**Controlled vocabulary for solution domains:**
- Congestion Management
- Congestion Avoidance
- Traffic Engineering
- Classification
- Policing
- Lossless Ethernet
- Queue Management

*Expand this list as your content model evolves.*

---

## 5. Canonicalization & Summarization

- If multiple names/labels refer to the same concept, pick one as the **canonical label** and link others with `altLabel`.
  - → `Avoiding Congestion, altLabel, Congestion Avoidance`
- For long, descriptive benefits/limitations/etc., create a **short, meaningful canonical phrase in active voice**.
  - → Long text: “This feature enables significant throughput improvement by proactively dropping low-priority packets…”  
    → Canonical phrase: “Improves throughput and fairness”

---

## 6. Decompose into Multiple Triples (MANDATORY & STRICT)

- If a sentence encodes more than one fact (multiple benefits, limitations, relationships, platforms, or releases), **split into multiple rows** so that **each row contains exactly one atomic triple**.
- **Never** concatenate multiple objects with commas in a single row. If you detect a list (e.g., “benefits A, B, and C”), **emit three separate rows**—one per benefit.
- **Do not** include coordinating phrases like “and”, “as well as” inside the same triple when they indicate multiple facts. Split them.
- **Micro-checklist per sentence** (must pass all before output):  
  1. Is there **only one subject, one predicate, one object**?  
  2. Does the **object** contain **no commas** introduced by list-like phrasing?  
  3. If multiple platforms/versions are mentioned, did you **emit multiple triples** (one per platform/version)?  
  4. If multiple relationships are implied, did you **emit multiple triples**?
- **Example (correct)**:
    ```
    Feature,hasBenefit,Improves throughput,Benefit
	Feature,hasBenefit,Improves fairness,Benefit
    Feature,hasBenefit,Prevents buffer exhaustion,Benefit
	```
---

## 7. Mandatory Enables Predicate

- Every **Feature** must include an `enables` predicate that explicitly links it to a **Functionality** or **Business Outcome**.
  - This outcome is usually present in the *Feature History Table*, under the *Description* column.
  - If no clear outcome is present, use the closest reasonable functionality inferred from the chapter content or table.
  - Use NLP or human judgment to summarize the outcome into a concise, canonical phrase.
  - Example:
    ```
    LLQ,enables,Guaranteed Bandwidth,Functionality
    WRED,enables,Congestion Avoidance,Functionality
    PFC,enables,Lossless Ethernet,Functionality
    ```

---

## 8. Controlled Predicate List (Use ONLY These Predicates — STRICT)

**This is a closed list.** Use ONLY the predicates below. If a fact does not fit any predicate, use `relatedTo` as the fallback. Do NOT invent new predicates, and do NOT use descriptions, sentences, or free-text as predicates.

If a potential new predicate emerges, note it at the end of your output under a section titled `## Suggested New Predicates` but do NOT use it in the triples.

Predicate          | Description                                                   | Example
-------------------|---------------------------------------------------------------|---------------------------------------------------------------
isA                | Declares the entity type                                      | RED, isA, QoS Feature
isFunctionOf       | Maps a feature or outcome to its solution domain              | OMP, isFunctionOf, Network Control
isPartOf           | Places a feature within a broader technology hierarchy         | NAT64, isPartOf, NAT
supports           | Platform/product is compatible with a feature or technology    | Cisco 8000, supports, MACsec
enables            | Indicates functional enablement                               | PFC, enables, Congestion Management
disables           | Specifies what a feature inhibits or disables                 | Queue Watchdog, disables, Tail Drop
enhances           | Shows evolutionary improvement of a feature                   | WRED, enhances, RED
introducedIn       | Release version where a feature was first introduced          | Tail Drop, introducedIn, XR 7.0.1
enhancedIn         | Release version where a feature was improved                  | Tail Drop, enhancedIn, XR 7.1.0
deprecatedIn       | Marks a feature deprecated in a specific release              | Legacy Policing, deprecatedIn, XR 6.5.3
notSupportedOn     | Platform(s) where a feature is not available                  | WRED, notSupportedOn, Cisco 8802
availableOn        | Platform(s) where a feature is supported                      | RED, availableOn, Cisco 8801
extendedTo         | Hardware or platform support added in a later release         | PFC, extendedTo, Cisco 8808
usedInPlatform     | Associates a feature with the overall platform                | RED, usedInPlatform, Cisco 8000
definedInChapter   | Points to the section/chapter where it's described            | RED, definedInChapter, Congestion Avoidance
hasBenefit         | Highlights technical or business value of a feature           | VOQ, hasBenefit, Minimizes Egress Congestion
hasLimitation      | Functional or environmental limitations (Section 8B rules)    | VOQ, hasLimitation, High Buffer Memory Use
hasRestriction     | Specific conditions under which the feature is limited (8B)   | RED, hasRestriction, Not available on bundle interfaces
hasGuideline       | Recommended practices or operational guidance                 | WRED, hasGuideline, Avoid enabling with LLC when latency exceeds 100 ms
hasKeyAttribute    | Core operational aspects or traits of a feature               | Token Bucket, hasKeyAttribute, Dual rate with single bucket
isCategoryType     | Maps a feature to a broader technology category               | RED, isCategoryType, Congestion Avoidance
requires           | States prerequisites for feature enablement                   | Policing, requires, Class Map
supportsInterface  | Indicates supported interface types                           | QoS, supportsInterface, Bundle-Ether
usesCriterion      | Criteria used for classification                              | Classification, usesCriterion, DSCP
usesComponent      | MQC or CLI elements like class-map, policy-map                | MQC, usesComponent, Policy-Map
verifiedBy         | CLI commands used to verify functionality                     | Queue Monitoring, verifiedBy, show policy-map interface
hasProcessStep     | Procedural sub-steps within a feature's operation             | Policing, hasProcessStep, Apply committed rate
relatedTo          | General link for soft associations between concepts           | WRED, relatedTo, ECN
altLabel           | Synonym or alternate label for canonical node                 | Avoiding Congestion, altLabel, Congestion Avoidance
usesProcedure      | Links a feature to its configuration procedure                | BGP PIC Edge, usesProcedure, Configure BGP PIC Edge using CLI
answersQuestion    | Links a feature/procedure to a natural-language user query    | Configure NAT64, answersQuestion, How do I configure NAT64 on SD-WAN?
addressedBy        | Links a user question or task intent to a procedure           | How do I configure NAT64?, addressedBy, Configure NAT64 Using CLI
affects            | Links a symptom/problem to the feature it impacts             | BFD Session Flapping, affects, BFD
causedBy           | Links a symptom to its root cause                             | BFD Session Flapping, causedBy, MTU mismatch on transport interface
resolvedBy         | Links a symptom to its resolution or workaround               | BFD Session Flapping, resolvedBy, Match MTU on both endpoints

---

## 8A. CSV Hygiene & Delimiter Rules (STRICT)

- **No raw commas** inside any field value. If the source text includes commas, **replace internal commas with semicolons (`;`)** or **rephrase**.  
- Example: source = “reduces drops, increases fairness”  
  → `"Feature","hasBenefit","Reduces drops; increases fairness","Benefit"`
- **No line breaks** inside fields; strip or replace with spaces.
- **No extra columns beyond the defined five columns** and **no trailing commas** at end of line.
- The output must contain **exactly five columns**:
  Subject|Predicate|Object|CategoryType|SourceTrace

## 8B. Limitations/Restrictions Extraction Rules (STRICT)

**Goal:** Prevent false positives where negative wording (e.g., “does not…”) is incorrectly labeled as a limitation.  
**Action:** Only mark limitations/restrictions when the text is **inside a clearly titled section**.

### 8B.1 Allowed Section Titles (case-insensitive, singular/plural accepted)

Treat a sentence as a **Limitation/Restriction** **only if** it is located *within* a section whose heading matches **one** of:
- `Limitations`
- `Limitation`
- `Restrictions`
- `Restriction`
- `Caveats`
- `Unsupported`
- `Not Supported`

> **Heuristic for PDFs without explicit heading markup:**  
> If the line starts with or contains a bold/uppercase cue like `LIMITATIONS:`, `RESTRICTIONS:`, `CAVEATS:`, or a standalone heading line followed by bullet points, consider the following lines **within** that section until the next heading-styled line.

### 8B.2 Disallowed Outside These Sections

- **Do NOT** classify statements as limitations/restrictions **solely** because they contain negative constructs (e.g., “not”, “does not”, “cannot”, “isn’t”, “no”, “except”, “unless”, “unsupported”) **when they are outside** the allowed sections above.
- Outside those sections, such sentences should be mapped to other categories when appropriate, e.g.:
  - **Prerequisite** (e.g., “Feature X is not available unless Y is enabled.” → represent as a dependency/condition, *not* limitation)
  - **Guideline** / **UsageNote** (e.g., “Do not enable X with Y in high-latency links.” → usage guidance, *not* limitation)
  - **Compatibility** (e.g., “Feature X is not compatible with mode Z.” → compatibility relation, *not* limitation, unless under an allowed section)
  - **Scope** (e.g., “This procedure does not apply to platform A.” → scope note)

### 8B.3 Predicates to Use (inside allowed sections only)

- Use **`hasLimitation`** or **`hasRestriction`** predicates **only** for triples extracted from within the allowed sections.
- Outside allowed sections, **do not** use these predicates. Prefer:
  - `requires` (for prerequisites/dependencies)
  - `incompatibleWith` (for incompatibilities outside explicit limitation sections)
  - `guides` / `hasGuideline` (for recommended or discouraged practice)
  - `appliesTo` / `doesNotApplyTo` (scope notes) — if `doesNotApplyTo` is used, ensure it is **not** labeled as a limitation unless under an allowed section.

### 8B.4 Micro-Checklist (Must pass before emitting a limitation)
- Is the sentence **inside** an allowed limitation/restriction section?
- Does the triple express a **single atomic constraint**? (If multiple constraints are listed, **decompose** into multiple triples.)
- Is the **Subject** the relevant feature/capability/platform, **Predicate** one of `hasLimitation` or `hasRestriction`, and the **Object** a concise statement **without commas**?
- CSV hygiene: four columns only, quotes around each field (see Section 8A).

### 8B.5 Examples

**Correct (inside “Restrictions” section):**
 -`"SRv6 TE","hasRestriction","Not supported on platform ABC in release 7.2.x","Restriction"`
 -`"BGP Route Policy","hasLimitation","Communities are ignored on eBGP sessions in mode X","Limitation"`
 
**Incorrect (outside allowed sections — do NOT mark as limitation):**
- Source: “Do not enable WRED with LLC if latency > 100 ms.”
  - Use guideline:

   `"WRED","hasGuideline","Avoid enabling with LLC when latency exceeds 100 ms","Guideline"`

- Source: “Feature X is not available unless Feature Y is configured.”
- Use prerequisite/dependency:

  `"Feature X","requires","Feature Y","Prerequisite"`


## 9. Output Format

**Output as a pipe-delimited table in a code block:**
**Example (final form)**:
```
Subject|Predicate|Object|CategoryType|SourceTrace
RED|isA|QoS Feature|Feature|congestion-avoidance :: Congestion Avoidance :: RED randomly drops packets...
RED|enables|Congestion Avoidance|Concept|congestion-avoidance :: Congestion Avoidance :: RED randomly drops packets...
RED|introducedIn|IOS-XR 7.3.1|ReleaseVersion|qos-guide :: Congestion Avoidance :: This feature was introduced in...
RED|hasBenefit|Reduces congestion-related drops|Benefit|qos-guide :: Congestion Avoidance :: RED reduces congestion related drops...
OMP Path Limit|usesProcedure|Configure path limit using CLI commands|CLIConfiguration|routing-guide :: Configure path limit :: Configure path limit using...
Configure RED|answersQuestion|How do I configure RED for congestion avoidance?|TaskIntent|qos-guide :: Configure RED :: This section describes how to...
```

---

## 10. Categorization for Subject/Object Nodes

Apply the following `CategoryType` to each node (subject/object). **Use only these categories — do not invent new ones.**

- `Feature` — A named capability or function of the product
- `Concept` — A technical idea or principle (e.g., "Overlay Network")
- `Technology` — A broader technology area (e.g., "MPLS", "SD-WAN")
- `Platform` — A product or device (e.g., "Cisco SD-WAN Manager", "vSmart")
- `HardwareVariant` — A specific hardware model (e.g., "Cisco 8808", "ISR 1100")
- `CLICommand` — A CLI command used for configuration or verification
- `ReleaseVersion` — A software release version (e.g., "17.9.1")
- `Benefit` — A technical or business value statement
- `Attribute` — A core property or trait of a feature
- `Limitation` — A functional or environmental limitation (from allowed sections only)
- `UsageGuideline` — A recommended practice or operational guidance
- `Restriction` — A specific condition under which a feature is limited
- `Prerequisite` — A requirement that must be met before enabling a feature
- `ProcessStep` — A sub-step within a feature's operation
- `Functionality` — A capability or outcome enabled by a feature
- `Solution Domain` — A functional category (e.g., "Congestion Management")
- `CLIConfiguration` — A configuration task performed via CLI
- `GUIConfiguration` — A configuration task performed via GUI/dashboard
- `TaskIntent` — A natural-language question representing a user's task goal
- `Troubleshooting` — A troubleshooting topic, symptom, or diagnostic procedure
- `Symptom` — An observed problem or error condition
- `Cause` — A root cause of a symptom or problem
- `Resolution` — A fix, workaround, or corrective action for a symptom
- `Documentation` — A reference to a chapter, guide, or document
- `Component` — A sub-element or building block of a feature

---

## 10A. Disconnected Node Review
After generating RDF triples, perform an internal connectivity analysis.

Identify nodes that may become **disconnected or orphan nodes** in the knowledge graph.

A node is considered potentially disconnected if:

- It appears only once in the dataset
- It has only an `isA` relationship and no functional connections
- A Configuration node is not linked to a Feature
- A Benefit, Limitation, Restriction, or Guideline node lacks a parent Feature
- A Concept node has no inbound or outbound relationships beyond a single soft relation
- A CLIConfiguration or GUIConfiguration node is not linked to a Feature

### Note on Dataset Integrity

All extracted RDF triples — including those identified as **disconnected or orphan nodes** — must still be included in the **primary RDF triples output dataset**.

The **Disconnected Nodes Review** section functions only as an **audit and diagnostic report** to highlight potential graph connectivity issues and suggest remediation actions.

It **does not replace**, filter, or remove those triples from the main RDF triples list. The main dataset must remain complete so that the downstream knowledge graph and governance review processes can operate on the full set of extracted facts.

### Output Requirements

Emit a separate section titled:

Disconnected Nodes Review

Use the same output format:

Subject|Predicate|Object|CategoryType|SourceTrace

**Also include a remediation or recommendation describing how the source documentation may need to be improved to fix the orpah RDF Triple "fact".**

Example:

FeatureX|hasGuideline|Add relationship to parent feature section in source documentation|UsageGuideline|doc :: FeatureX Overview :: FeatureX provides enhanced routing...

## 11. Output Format & Final Self-Audit (REQUIRED)

- Emit the triples as a code block; each row must be pipe-delimited:
Subject|Predicate|Object|CategoryType|SourceTrace

- **Final Self-Audit (run mentally before emitting)**:
1. **Count columns**: Does every row parse into **exactly 5 pipe-separated fields**?
2. **Forbidden commas**: Did you **replace internal commas** in values with semicolons or rephrase?
3. **One fact per row**: Did you split list-like clauses into separate rows?
4. **Predicate whitelist**: Are ALL predicates from the approved list in Section 8? If not, replace with `relatedTo` or the closest match.
5. **CategoryType whitelist**: Are ALL CategoryTypes from the approved list in Section 10? If not, use the closest match.
6. **Configuration Category Validation**: Every configuration task must be classified as either `CLIConfiguration` or `GUIConfiguration`. Do not use the generic "Configuration" category type.
7. **Task-Intent coverage**: Did you generate at least one `answersQuestion` triple for each configuration section?
8. **Abbreviation coverage**: Did you generate `altLabel` triples for every abbreviation encountered?
9. **No hallucinated predicates**: Verify no free-text descriptions leaked into the Predicate column.
10. **No orphan entities**: Verify every Subject appears in at least 2 triples (as Subject or Object). If any entity has only a standalone `isA` with no connections, either add a connecting triple or remove it.

**Example (final form)**:
```
RED|isA|QoS Feature|Feature|congestion-avoidance :: Congestion Avoidance :: RED randomly drops packets...
RED|enables|Congestion Avoidance|Concept|congestion-avoidance :: Congestion Avoidance :: RED randomly drops packets...
RED|introducedIn|IOS-XR 7.3.1|ReleaseVersion|qos-guide :: Congestion Avoidance :: This feature was introduced in...
RED|hasBenefit|Reduces congestion-related drops|Benefit|qos-guide :: Congestion Avoidance :: RED reduces congestion related drops...
Configure RED|answersQuestion|How do I configure RED for congestion avoidance?|TaskIntent|qos-guide :: Configure RED :: This section describes how to...
BFD Session Flapping|affects|BFD|Feature|troubleshooting :: Troubleshoot BFD :: If BFD sessions are flapping...
BFD Session Flapping|resolvedBy|Verify MTU matches on both endpoints|Resolution|troubleshooting :: Troubleshoot BFD :: Resolution: verify that the MTU...
```


### New Predicates Output
- Separate CSV **if** any new predicate candidates found:
```
Predicate|Description|Example RDF Triple
```

### New Category Types Output
- Separate CSV **if** any new category type candidates found:
```
CategoryType|Description|Example Node or RDF Triple
```

---

## Other Rules

- If a feature is *deprecated*, still extract:
  - → `Feature, deprecatedIn, IOS-XR version`
- If a feature is *enhanced*, add:
  - → `Feature, enhancedIn, IOS-XR version`
- Avoid synonyms for predicates—stick to the vocabulary.
- If there is **no clear release version**, skip `introducedIn` predicate for that row.
- Do **not** exclude deprecated features—capture them clearly.


### Do Not Rules (Add to Section 6 in the Prompt)

- **Do not invent new predicates** — strictly use only the ones listed in the uploaded **predicate list CSV**. If new predicate candidates emerge from the content, list them in a **separate CSV titled `new_predicates.csv`**, including:
```
Predicate|Description|Example RDF Triple
```
- **Do not output predicates in camelCase, hyphenated, or plural form** — match exact predicate string from the list.
- **Do not extract generic statements like "QoS improves performance" unless tied to a feature.** Avoid vague, non-technical claims.
- **Do not convert UI text labels or UI configuration steps into RDF triples.** Focus only on conceptual relationships.
- **Do not use incomplete or generic terms like "feature", "device", "platform" as object values without specifics.**
- **Do not include content from unrelated guides (if any cross-reference is found).** Focus only on current document scope.
- **Do not extract examples or CLI outputs as object values unless they are verification commands.**
- **Do not assign a category type unless it maps to one of the allowed `CategoryType` entries** listed earlier.
- **Do not treat numbered list items or procedure steps as separate RDF triples unless they contain clear relationships.**
- **Do not include glossary definitions, unless they contribute to predicate-object relationships** like `isA`, `enables`, `usedInPlatform`.
- **Do not extract every numbered step inside configuration procedures as RDF triples. If it exists, only extract the **configuration task title**, its **prerequisites  **, **verification commands**, and **task purpose**.