# Book Short Description Prompt

**Purpose:** Generate concise, informative short descriptions for entire technical documentation guides (books).

---

## Instructions

1. **Read the provided book/guide content** carefully (or review the table of contents and key chapters)
2. **Identify the overall purpose and scope** of the entire guide
3. **Write a short description** following the rules below
4. **Output format:**
   ```
   **Short description**: {{Your generated short description}}
   ```

---

## Book Short Description Rules

- **Format:** Start with an action verb (e.g., "Provides", "Introduces", "Outlines", "Guides", "Details")
- **Length:** 2–3 sentences
- **Content:** Summarize the overall purpose and scope of the entire guide
- **Scope:** Cover the main themes and intended use cases of the complete documentation
- **Tone:** Succinct and informative
- **Acronyms:** Do not abbreviate acronyms

---

## Examples

### Example 1
**Book:** Catalyst Center Global Manager Configuration Guide
**Content:** [Multiple chapters covering deployment, configuration, management, and troubleshooting]

**Output:**
```
**Short description**: Provides instructions for deploying, configuring, and managing Catalyst Center Global Manager, a platform designed to oversee multiple Catalyst Centers from a unified interface.
```

### Example 2
**Book:** Cisco Catalyst 9000 Series Configuration Guide
**Content:** [Installation, basic configuration, advanced features, security, and troubleshooting]

**Output:**
```
**Short description**: Provides comprehensive instructions for installing, configuring, and managing Cisco Catalyst 9000 series switches. It covers initial setup, advanced features, security configurations, and troubleshooting procedures.
```

### Example 3
**Book:** SD-WAN Deployment and Operations Guide
**Content:** [Architecture overview, deployment planning, configuration workflows, operations, and optimization]

**Output:**
```
**Short description**: Provides detailed instructions for planning, deploying, and operating Cisco SD-WAN solutions. It covers architecture fundamentals, configuration procedures, policy management, and operational best practices.
```

---

## Best Practices

1. **Always Start with an Action Verb:** Use active verbs such as "Provides", "Introduces", "Outlines", "Guides", or "Details" to begin descriptions
2. **Be Comprehensive:** Capture the full scope of the guide in 2-3 sentences
3. **Be Specific:** Mention key features, use cases, or target audience
4. **Use Active Voice:** Write in present tense with active verbs
5. **Focus on Value:** Communicate what the reader will accomplish with this guide
6. **List Key Areas:** Briefly mention the main topics covered (e.g., "deployment, configuration, troubleshooting")
7. **Consider the Audience:** Write for technical users who need to understand the guide's full value

---

## Common Mistakes to Avoid

❌ **Wrong Format:** "This guide provides information about network configuration."  
✅ **Better:** "Provides comprehensive instructions for configuring Cisco network devices, including routing protocols, security features, and quality of service settings."

❌ **Too Brief:** "Covers network configuration."  
✅ **Better:** "Provides comprehensive instructions for configuring Cisco network devices, including routing protocols, security features, and quality of service settings."

❌ **Too Long:** "Provides detailed information about every aspect of the Cisco ASR 9000 router including hardware installation, initial software setup, basic and advanced routing protocols, multicast configuration, MPLS implementation, security features including..."  
✅ **Better:** "Provides instructions for deploying and configuring Cisco ASR 9000 routers. It covers hardware installation, software setup, routing protocols, MPLS, and security features."

❌ **Too Vague:** "Provides information for network administrators."  
✅ **Better:** "Provides configuration and troubleshooting procedures for managing enterprise network infrastructure using Cisco Catalyst switches."

---

## Structure Template

Use this template when writing book short descriptions:

```
Provides [main purpose] for [product/platform name], [brief descriptor/purpose]. 
It covers [key area 1], [key area 2], [key area 3], and [key area 4].
```

**Example:**
```
Provides instructions for deploying, configuring, and managing Catalyst Center Global Manager, 
a platform designed to oversee multiple Catalyst Centers from a unified interface.
```
