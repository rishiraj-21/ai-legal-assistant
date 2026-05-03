import asyncio
import logging

from app.models.schemas import AdversarialResult, AdvocateResult, OpponentResult
from app.services.gemini_service import gemini_service
from app.services.prompt_builder_adversarial import (
    build_advocate_prompt,
    build_opponent_prompt,
)

logger = logging.getLogger(__name__)


class AdversarialService:
    def _parse_advocate(self, data: dict) -> AdvocateResult:
        points = [str(p) for p in data.get("points", []) if isinstance(p, str)]
        confidence = float(data.get("confidence", 0.5))
        confidence = max(0.0, min(1.0, confidence))
        precedents = [str(p) for p in data.get("key_precedents", []) if isinstance(p, str)]
        return AdvocateResult(
            points=points,
            confidence=confidence,
            key_precedents=precedents,
        )

    def _parse_opponent(self, data: dict) -> OpponentResult:
        points = [str(p) for p in data.get("points", []) if isinstance(p, str)]
        confidence = float(data.get("confidence", 0.5))
        confidence = max(0.0, min(1.0, confidence))
        precedents = [str(p) for p in data.get("key_precedents", []) if isinstance(p, str)]
        return OpponentResult(
            points=points,
            confidence=confidence,
            key_precedents=precedents,
        )

    def _extract_vulnerabilities(self, opponent: OpponentResult) -> list[str]:
        return opponent.points[:3]

    async def analyze(
        self, issue: str, case_type: str, context: str
    ) -> tuple[AdversarialResult | None, list[str]]:
        errors: list[str] = []

        advocate_prompt = build_advocate_prompt(issue, case_type, context)
        opponent_prompt = build_opponent_prompt(issue, case_type, context)

        results = await asyncio.gather(
            gemini_service.generate(advocate_prompt),
            gemini_service.generate(opponent_prompt),
            return_exceptions=True,
        )

        # Parse advocate
        advocate = None
        if isinstance(results[0], Exception):
            logger.error("Advocate generation failed: %s", results[0])
            errors.append(f"Advocate generation failed: {results[0]}")
        elif results[0] is not None:
            try:
                advocate = self._parse_advocate(results[0])
            except Exception as e:
                logger.warning("Failed to parse advocate response: %s", e)
                errors.append("Failed to parse advocate response from AI")
        else:
            errors.append("Advocate generation returned no result")

        # Parse opponent
        opponent = None
        if isinstance(results[1], Exception):
            logger.error("Opponent generation failed: %s", results[1])
            errors.append(f"Opponent generation failed: {results[1]}")
        elif results[1] is not None:
            try:
                opponent = self._parse_opponent(results[1])
            except Exception as e:
                logger.warning("Failed to parse opponent response: %s", e)
                errors.append("Failed to parse opponent response from AI")
        else:
            errors.append("Opponent generation returned no result")

        # If both failed, return None
        if advocate is None and opponent is None:
            return None, errors

        # Graceful partial: fallback empty result for failed side
        if advocate is None:
            advocate = AdvocateResult(points=[], confidence=0.5, key_precedents=[])
        if opponent is None:
            opponent = OpponentResult(points=[], confidence=0.5, key_precedents=[])

        vulnerabilities = self._extract_vulnerabilities(opponent)

        return AdversarialResult(
            advocate=advocate,
            opponent=opponent,
            vulnerabilities=vulnerabilities,
        ), errors


adversarial_service = AdversarialService()
