def build_enhanced_risk_prompt(
    issue: str,
    case_type: str,
    context: str,
    advocate_confidence: float,
    opponent_confidence: float,
) -> str:
    return f"""You are an expert Indian legal risk analyst. Analyze the user's legal issue across 5 specific risk factors and provide a settlement recommendation.

USER'S ISSUE:
{issue}

CASE TYPE: {case_type}

RELEVANT LEGAL PROVISIONS:
{context}

ADVERSARIAL ANALYSIS CONTEXT:
- Advocate confidence (how strong the user's case is): {advocate_confidence:.2f}
- Opponent confidence (how strong the opposition's case is): {opponent_confidence:.2f}

Generate a JSON response with this EXACT structure:
{{
  "factors": [
    {{
      "label": "Evidence Strength",
      "value": <int 0-100>,
      "explanation": "<1-2 sentence explanation>"
    }},
    {{
      "label": "Precedent Alignment",
      "value": <int 0-100>,
      "explanation": "<1-2 sentence explanation>"
    }},
    {{
      "label": "Financial Exposure",
      "value": <int 0-100>,
      "explanation": "<1-2 sentence explanation>"
    }},
    {{
      "label": "Case Complexity",
      "value": <int 0-100>,
      "explanation": "<1-2 sentence explanation>"
    }},
    {{
      "label": "Jurisdiction History",
      "value": <int 0-100>,
      "explanation": "<1-2 sentence explanation>"
    }}
  ],
  "settlement": {{
    "recommendation": "<Negotiate or Litigate or Settle>",
    "reasoning": "<2-3 sentence reasoning for the recommendation>"
  }},
  "summary": "<2-3 sentence overall risk assessment>"
}}

RULES:
- Each factor value is 0-100 where higher = MORE FAVORABLE to the user
  - Evidence Strength: how strong is the user's available evidence
  - Precedent Alignment: how well established case law supports the user
  - Financial Exposure: financial risk level (100 = minimal financial risk, 0 = extreme exposure)
  - Case Complexity: procedural simplicity (100 = straightforward, 0 = extremely complex)
  - Jurisdiction History: how favorable the relevant court/forum has been for similar cases
- settlement.recommendation MUST be exactly one of: "Negotiate", "Litigate", "Settle"
- Consider the adversarial analysis confidence scores when forming your assessment
- Be realistic and balanced — base analysis on the legal provisions provided"""
