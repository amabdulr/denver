# Chapter Short Description Prompt

**Purpose:** Generate concise, informative short descriptions for chapters in technical documentation.

---

## Instructions

1. **Read the provided chapter content** carefully
2. **Identify what the chapter covers** at a high level
3. **Write a short description** following the rules below
4. **Output format:**
   ```
   **Short description**: {{Your generated short description}}
   ```

---

## Chapter Short Description Rules

- **Length:** 1–2 sentences (20–50 words)
- **Start with:** Active verbs such as "Introduces", "Outlines", "Guides", "Details", "Provides"
- **Content:** Summarize what the chapter covers at a high level
- **Scope:** Broader than H1 sections but more focused than the entire book
- **Tone:** Succinct and informative

---

## Examples

### Example 1
**Chapter:** Getting Started with Catalyst Center
**Content:** [Key concepts, architecture, and initial setup process]

**Output:**
```
**Short description**: Introduces the key concepts and architecture of the Catalyst Center platform and outlines the initial setup process.
```

### Example 2
**Chapter:** Advanced Security Features
**Content:** [Encryption methods, authentication protocols, access control lists, and security best practices]

**Output:**
```
**Short description**: Details encryption methods, authentication protocols, and access control mechanisms for securing network infrastructure.
```

### Example 3
**Chapter:** Network Monitoring and Analytics
**Content:** [Performance metrics, health monitoring, alerting systems, and reporting tools]

**Output:**
```
**Short description**: Provides an overview of performance monitoring tools, health analytics, and alerting mechanisms for maintaining network operations.
```

---

## Best Practices

1. **Be Concise:** Stick to the 20-50 word count limit
2. **Be Specific:** Avoid vague language like "information about" or "details on"
3. **Use Active Voice:** Write in present tense with active verbs
4. **Focus on Value:** Communicate what the user will learn or accomplish
5. **High-Level Summary:** Capture the chapter's main themes without listing every detail
6. **Avoid Redundancy:** Don't repeat the chapter title verbatim
7. **Consider the Audience:** Write for technical users who need quick understanding

---

## Common Mistakes to Avoid

❌ **Too Long:** "This chapter provides comprehensive coverage of all aspects of installation, including hardware setup, software configuration, and troubleshooting..."  
✅ **Better:** "Guides you through hardware installation, software setup, and initial configuration procedures."

❌ **No Action Verb:** "Information about network protocols."  
✅ **Better:** "Introduces network protocols and their implementation on Cisco devices."

❌ **Too Vague:** "Covers various topics related to security."  
✅ **Better:** "Details encryption, authentication, and access control mechanisms for network security."

❌ **Too Detailed:** "Explains how to configure SNMP v2c, v3, enable traps, set community strings, and verify settings."  
✅ **Better:** "Outlines SNMP configuration and management for network monitoring."
