# H1 Short Description Prompt

**Purpose:** Generate concise, informative short descriptions for H1 (Heading Level 1) sections in technical documentation.

---

## Instructions

1. **Read the provided H1 section content** carefully
2. **Identify all topics** covered within the H1 section
3. **Write a short description** following the rules below
4. **Output format:**
   ```
   **Short description**: {{Your generated short description}}
   ```

---

## H1 Short Description Rules

- **Length:** 1–2 sentences (20–50 words)
- **Start with:** Active verbs such as "Introduces", "Outlines", "Guides", "Details", "Provides instructions"
- **Content:** Ensure all topics within the H1 section are considered in the summary
- **Scope:** More specific than Chapter, covering the immediate subsection
- **Tone:** Succinct and informative

---

## Examples

### Example 1
**H1 Section:** Configure Network Devices
**Content:** [Instructions for configuring network devices and establishing connectivity between controller and access points]

**Output:**
```
**Short description**: Provides instructions for configuring network devices and establishing connectivity between the controller and access points.
```

### Example 2
**H1 Section:** Troubleshoot OSPF Routing
**Content:** [Guidance on diagnosing OSPF issues, checking neighbor relationships, and verifying routing tables]

**Output:**
```
**Short description**: Guides you through troubleshooting OSPF routing issues, including neighbor relationship verification and routing table analysis.
```

---

## Best Practices

1. **Be Concise:** Stick to the 20-50 word count limit
2. **Be Specific:** Avoid vague language like "information about" or "details on"
3. **Use Active Voice:** Write in present tense with active verbs
4. **Focus on Value:** Communicate what the user will learn or accomplish
5. **Cover All Topics:** Ensure the description encompasses all subsections within the H1
6. **Avoid Redundancy:** Don't repeat the H1 title verbatim
7. **Consider the Audience:** Write for technical users who need quick understanding

---

## Common Mistakes to Avoid

❌ **Too Vague:** "Covers various networking topics."  
✅ **Better:** "Introduces BGP routing protocols and their configuration on Cisco routers."

❌ **No Action Verb:** "Information about SNMP configuration."  
✅ **Better:** "Details the SNMP configuration process for network monitoring."

❌ **Too Long:** "This comprehensive section provides detailed information about the various aspects of configuring, managing, and troubleshooting..."  
✅ **Better:** "Outlines the configuration and troubleshooting procedures for network management."

❌ **Missing Topics:** "Describes device configuration." (when section also covers connectivity and troubleshooting)  
✅ **Better:** "Describes device configuration, connectivity setup, and troubleshooting procedures."
