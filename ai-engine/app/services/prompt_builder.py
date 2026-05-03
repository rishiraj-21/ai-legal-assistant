def build_pathway_prompt(issue: str, case_type: str, context: str) -> str:
    return f"""You are an expert Indian legal advisor. Based on the user's legal issue and relevant legal provisions, generate a step-by-step legal pathway.

USER'S ISSUE:
{issue}

CASE TYPE: {case_type}

RELEVANT LEGAL PROVISIONS:
{context}

Generate a JSON response with this EXACT structure:
{{
  "steps": [
    {{
      "icon": "<icon_name>",
      "title": "<step title>",
      "detail": "<1-2 sentence description of this step>"
    }}
  ],
  "documents": ["<document 1>", "<document 2>", ...]
}}

RULES:
- Generate 4-6 steps that are SPECIFIC to this case (not generic)
- Each step must have a concrete, actionable title and detail
- icon MUST be one of: "file-text", "shield-check", "scale", "handshake", "gavel"
- Use icons contextually (e.g. "file-text" for documentation, "shield-check" for legal notice, "scale" for court filing, "handshake" for mediation, "gavel" for verdict)
- documents should list 4-6 specific documents the user needs to prepare
- Base your advice on the relevant legal provisions provided
- Be specific to Indian law and jurisdiction"""


def build_risk_prompt(issue: str, case_type: str, context: str) -> str:
    return f"""You are an expert Indian legal risk analyst. Analyze the user's legal issue and provide a risk assessment.

USER'S ISSUE:
{issue}

CASE TYPE: {case_type}

RELEVANT LEGAL PROVISIONS:
{context}

Generate a JSON response with this EXACT structure:
{{
  "risk_score": <integer 0-100>,
  "settlement_probability": <integer 0-100>,
  "factors": [
    ["<factor label>", <value 0-100>],
    ["<factor label>", <value 0-100>]
  ],
  "summary": "<2-3 sentence summary of the risk assessment>"
}}

RULES:
- risk_score: 0 = no risk, 100 = extreme risk. Assess based on evidence, precedent, and complexity.
- settlement_probability: likelihood of out-of-court resolution (0-100)
- factors: provide 3-5 risk factors as [string, number] tuples
  - Good factor labels: "Evidence strength", "Precedent favorability", "Procedural complexity", "Time sensitivity", "Financial exposure", "Jurisdiction clarity", "Opposition strength", "Statutory protection"
  - Each factor value is 0-100 where higher = more favorable to user
- summary: concise assessment specific to this case
- Base analysis on the relevant legal provisions provided
- Be realistic and balanced in your assessment"""
