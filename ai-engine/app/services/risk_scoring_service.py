import logging

from app.models.schemas import EnhancedRiskResult, RiskFactor, SettlementResult
from app.services.gemini_service import gemini_service
from app.services.prompt_builder_risk import build_enhanced_risk_prompt

logger = logging.getLogger(__name__)

FACTOR_WEIGHTS = {
    "Evidence Strength": 0.25,
    "Precedent Alignment": 0.25,
    "Financial Exposure": 0.20,
    "Case Complexity": 0.15,
    "Jurisdiction History": 0.15,
}

RISK_LABELS = [
    (25, "Low"),
    (50, "Medium"),
    (75, "High"),
    (100, "Critical"),
]


def _compute_risk_score(detailed_factors: list[RiskFactor]) -> int:
    favorability = 0.0
    for factor in detailed_factors:
        weight = FACTOR_WEIGHTS.get(factor.label, 0.0)
        favorability += weight * factor.value
    risk_score = 100 - favorability
    return max(0, min(100, round(risk_score)))


def _compute_risk_label(risk_score: int) -> str:
    for threshold, label in RISK_LABELS:
        if risk_score <= threshold:
            return label
    return "Critical"


def _compute_settlement_probability(
    risk_score: int, advocate_confidence: float, opponent_confidence: float
) -> int:
    settlement = (risk_score * 0.4) + ((1 - advocate_confidence) * 30) + (opponent_confidence * 30)
    return max(0, min(100, round(settlement)))


class RiskScoringService:
    def _parse_factors(self, data: dict) -> list[RiskFactor]:
        factors = []
        for f in data.get("factors", []):
            label = str(f.get("label", ""))
            value = int(f.get("value", 50))
            value = max(0, min(100, value))
            explanation = str(f.get("explanation", ""))
            factors.append(RiskFactor(label=label, value=value, explanation=explanation))
        return factors

    def _parse_settlement(self, data: dict) -> SettlementResult | None:
        s = data.get("settlement")
        if not s:
            return None
        recommendation = str(s.get("recommendation", "Negotiate"))
        if recommendation not in ("Negotiate", "Litigate", "Settle"):
            recommendation = "Negotiate"
        return SettlementResult(
            probability=0,  # will be overwritten by Python formula
            recommendation=recommendation,
            reasoning=str(s.get("reasoning", "")),
        )

    async def analyze(
        self,
        issue: str,
        case_type: str,
        context: str,
        advocate_confidence: float,
        opponent_confidence: float,
    ) -> tuple[EnhancedRiskResult | None, list[str]]:
        errors: list[str] = []

        prompt = build_enhanced_risk_prompt(
            issue, case_type, context, advocate_confidence, opponent_confidence
        )
        data = await gemini_service.generate(prompt)

        if data is None:
            errors.append("Enhanced risk analysis returned no result")
            return None, errors

        try:
            detailed_factors = self._parse_factors(data)
            settlement_from_ai = self._parse_settlement(data)
            summary = str(data.get("summary", ""))

            # Deterministic Python scoring
            risk_score = _compute_risk_score(detailed_factors)
            risk_label = _compute_risk_label(risk_score)
            settlement_prob = _compute_settlement_probability(
                risk_score, advocate_confidence, opponent_confidence
            )

            # Build settlement result with computed probability
            settlement = None
            if settlement_from_ai:
                settlement = SettlementResult(
                    probability=settlement_prob,
                    recommendation=settlement_from_ai.recommendation,
                    reasoning=settlement_from_ai.reasoning,
                )
            else:
                settlement = SettlementResult(
                    probability=settlement_prob,
                    recommendation="Negotiate",
                    reasoning="Unable to determine optimal strategy from available data.",
                )

            # Legacy factors as [label, value] tuples
            legacy_factors = [[f.label, f.value] for f in detailed_factors]

            return EnhancedRiskResult(
                risk_score=risk_score,
                settlement_probability=settlement_prob,
                factors=legacy_factors,
                summary=summary,
                risk_label=risk_label,
                detailed_factors=detailed_factors,
                settlement=settlement,
            ), errors

        except Exception as e:
            logger.warning("Failed to parse enhanced risk response: %s", e)
            errors.append("Failed to parse enhanced risk response from AI")
            return None, errors


risk_scoring_service = RiskScoringService()
