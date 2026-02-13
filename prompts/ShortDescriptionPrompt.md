# Short Description Writing Prompt

**Purpose:** Generate concise, informative short descriptions for technical documentation based on information type.

---

## Instructions

1. **Read the provided content** and identify its information type from the parentheses (e.g., *Configure a device (Task)*).
2. **Identify the information type:** Task, Concept, Process, Reference, Principle, Book, Chapter, or H1.
3. **Write a short description** following the rules specific to that information type.
4. **Output format:**
   ```
   **Short description**: {{Your generated short description}}
   ```

---

## Short Description Rules by Information Type

### Basic Information Types

#### Task
- **Length:** 1–2 sentences (20–50 words)
- **Start with:** Action verbs such as "Configure", "Verify", "Create", "Deploy", "Enable"
- **Content:** Briefly state what the task accomplishes
- **Example:** Enroll Crosswork Data Gateway into Crosswork Cloud using a registration file.

---

#### Concept
- **Length:** 1–2 sentences (20–50 words)
- **Start with:** "Explains" or "Describes"
- **Content:** Summarize what concept is being defined or explained
- **Example:** Explains the disk encryption mechanism that protects sensitive customer information and ensures compliance with security requirements.

---

#### Process
- **Length:** 1–2 sentences (20–50 words)
- **Start with:** "Describes" followed by the process name
- **Content:** State what process is being described and mention key components or stages
- **Example:** Describes how DHCP servers automate network configuration. It describes the key components involved and the various stages.

---

#### Reference
- **Length:** 1–2 sentences (20–50 words)
- **Start with:** "Lists", "Provides", "Outlines", "Summarizes"
- **Content:** Indicate what reference information is provided
- **Example:** Lists the available device configuration modes and their specific use cases for network administrators.

---

#### Principle
- **Length:** 1–2 sentences (20–50 words)
- **Start with:** "Outlines", "Provides", "Recommends", "Details"
- **Content:** Briefly state the advisory nature of the content
- **Example:** Outlines the best practices for using the included Torx screwdriver during hardware installation.

---

### Container Information Types

#### Book
- **Format:** Start with **"This guide provides"**
- **Length:** 2–3 sentences
- **Content:** Summarize the overall purpose and scope of the entire guide
- **Tone:** Succinct and informative
- **Example:** This guide provides instructions for deploying, configuring, and managing Catalyst Center Global Manager, a platform designed to oversee multiple Catalyst Centers from a unified interface.

---

#### Chapter
- **Length:** 1–2 sentences (20–50 words)
- **Start with:** Active verbs such as "Introduces", "Outlines", "Guides", "Details", "Provides"
- **Content:** Summarize what the chapter covers at a high level
- **Example:** Introduces the key concepts and architecture of the Catalyst Center platform and outlines the initial setup process.

---

#### H1 (Heading Level 1)
- **Length:** 1–2 sentences (20–50 words)
- **Start with:** Active verbs such as "Introduces", "Outlines", "Guides", "Details", "Provides instructions"
- **Content:** Ensure all topics within the H1 section are considered in the summary
- **Scope:** More specific than Chapter, covering the immediate subsection
- **Example:** Provides instructions for configuring network devices and establishing connectivity between the controller and access points.

---

## Quick Reference Table

| Information Type | Length | Starting Verbs | Focus |
|-----------------|--------|----------------|-------|
| **Task** | 1-2 sentences (20-50 words) | Configure, Verify, Create, Deploy, Enable | What the task accomplishes |
| **Concept** | 1-2 sentences (20-50 words) | Explains, Describes | What concept is defined |
| **Process** | 1-2 sentences (20-50 words) | Describes | What process and its components |
| **Reference** | 1-2 sentences (20-50 words) | Lists, Provides, Outlines, Summarizes | What information is provided |
| **Principle** | 1-2 sentences (20-50 words) | Outlines, Provides, Recommends, Details | What guidance is given |
| **Book** | 2-3 sentences | This guide provides | Overall guide purpose and scope |
| **Chapter** | 1-2 sentences (20-50 words) | Introduces, Outlines, Guides, Details, Provides | Chapter-level summary |
| **H1** | 1-2 sentences (20-50 words) | Introduces, Outlines, Guides, Details, Provides instructions | Section-specific summary |

---

## Usage Examples

### Example 1: Task
**Input:**
```
Configure SNMP settings (Task)
[Content about configuring SNMP...]
```

**Output:**
```
**Short description**: Configure SNMP v2c and v3 settings to enable network monitoring and device management.
```

---

### Example 2: Concept
**Input:**
```
Smart licensing using policy (Concept)
[Content explaining smart licensing...]
```

**Output:**
```
**Short description**: Explains the policy-based licensing mechanism that automates license management and ensures compliance with Cisco's default policies.
```

---

### Example 3: Book
**Input:**
```
Cisco Catalyst 9000 Configuration Guide (Book)
[Multiple chapters covering installation, configuration, troubleshooting...]
```

**Output:**
```
**Short description**: This guide provides comprehensive instructions for installing, configuring, and managing Cisco Catalyst 9000 series switches. It covers initial setup, advanced features, security configurations, and troubleshooting procedures.
```

---

## Best Practices

1. **Be Concise:** Stick to the word count limits
2. **Be Specific:** Avoid vague language like "information about" or "details on"
3. **Use Active Voice:** Write in present tense with active verbs
4. **Focus on Value:** Communicate what the user will learn or accomplish
5. **Avoid Redundancy:** Don't repeat the title verbatim
6. **Match the Tone:** Align with the information type's purpose
7. **Consider the Audience:** Write for technical users who need quick understanding

---

## Common Mistakes to Avoid

❌ **Too Long:** "This comprehensive section provides detailed information about the various aspects of..."  
✅ **Better:** "Describes the configuration process for network interfaces."

❌ **No Action Verb:** "Information about SNMP configuration."  
✅ **Better:** "Explains how to configure SNMP for network monitoring."

❌ **Too Vague:** "Covers various topics related to networking."  
✅ **Better:** "Introduces BGP routing protocols and their configuration on Cisco routers."

❌ **Wrong Starting Verb:** "Configure the DHCP settings" (for a Concept)  
✅ **Better:** "Explains DHCP server functionality and address allocation."
