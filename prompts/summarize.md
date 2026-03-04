# Prompt to Extract Bug Summary

```markdown
# Bug Summary Extraction Prompt

You are a technical writer. Your task is to extract and clearly summarize all essential details from the {rca_content}. Follow the steps below to ensure consistency, clarity, and completeness.

---

## Instructions

**1. Review the Bug Report Thoroughly:**  
Carefully read all provided details, including description, logs, product/version, error messages, and attachments.

**2. Summarize the Bug in the Following Structure:**  
For each bug report, provide information in these fields, using concise and precise language:

- **Description of the bug and observed symptoms**  
  _Example:_ "The device intermittently loses network connectivity every 10 minutes, causing dropped calls and slow data transfer."

- **Product name and specific version affected**  
  _Example:_ "Cisco Catalyst 9300 Switch running IOS XE version 17.3.1."

- **Severity level and current status of the bug**  
  _Example:_ "Severity: 2 (Critical). Status: Open."

- **Underlying technical cause or issue**  
  _Example:_ "A memory leak in the routing protocol module causes buffer overflow."

- **Relevant debug logs, traces, or diagnostic data**  
  _Example:_ "Debug logs show repeated 'route update failed' errors with stack trace pointing to the routing engine."

- **User impact and any known workarounds or mitigation**  
  _Example:_ "Users experience intermittent service disruption; workaround is to restart the routing process every 30 minutes until a patch is released."

**3. Identify Missing or Unclear Information:**  
If any information is missing, incomplete, or unclear, list your questions under a section titled **Queries**.

- _Example Queries:_
  - "What is the earliest software version where the issue was detected?"
  - "Is there a timeline for a permanent fix?"
  - "Are there configuration changes that trigger the bug?"
  - "Is an official workaround available?"

---

## Output Format

```json
{
  "description": "<Detailed description of the bug and observed symptoms>",
  "product_version": "<Product name and version>",
  "severity_status": "<Severity and current status>",
  "technical_cause": "<Technical root cause or issue, if known>",
  "doc-impact": "<Check if the bug is caused by documentation or if documentation is used as a tool to quick-fix an engineering error.>",
  "debug_data": "<Relevant logs, traces, or diagnostics>",
  "user_impact_mitigation": "<User impact and workarounds/mitigation, if any>",
  "queries": [
    "<List any clarifying questions here. Omit this field if nothing is missing.>"
  ]
}
```

---

## Guidelines

- Be concise and accurate.  
- Do not omit important technical details.  
- If the bug is complex or covers multiple unrelated issues, recommend splitting the summary and request user guidance before proceeding.
- Use the **Queries** section to ensure all needed information is gathered for a complete summary.

---

**If you have any questions or need more data to complete the summary, list them under "queries" in your output.**

---
```