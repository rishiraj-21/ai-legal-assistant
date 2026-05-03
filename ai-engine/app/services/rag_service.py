import asyncio
import logging

from app.models.schemas import AnalyzeResponse, PathwayResult, PathwayStep
from app.retrieval.hybrid_retriever import hybrid_retriever
from app.services.adversarial_service import adversarial_service
from app.services.gemini_service import gemini_service
from app.services.prompt_builder import build_pathway_prompt
from app.services.risk_scoring_service import risk_scoring_service

logger = logging.getLogger(__name__)


class RAGService:
    def _format_context(self, results: list[dict]) -> str:
        if not results:
            return "No specific legal provisions found. Use general Indian legal knowledge."

        chunks = []
        for i, r in enumerate(results, 1):
            meta = r.get("metadata", {})
            # Support both seed-format (act/section/title) and DB-format (type/case_name/court)
            doc_type = meta.get("type", "section")
            if doc_type == "case":
                case_name = meta.get("case_name", "Unknown Case")
                court = meta.get("court", "")
                header = f"[{i}] {case_name} ({court})"
            else:
                act = meta.get("act", "Unknown Act")
                section = meta.get("section", "")
                title = meta.get("title", "")
                header = f"[{i}] {act}, Section {section} — {title}"
            chunks.append(f"{header}\n{r['text']}")
        return "\n\n".join(chunks)

    def _parse_pathway(self, data: dict) -> PathwayResult | None:
        try:
            steps = []
            valid_icons = {"file-text", "shield-check", "scale", "handshake", "gavel"}
            for s in data.get("steps", []):
                icon = s.get("icon", "file-text")
                if icon not in valid_icons:
                    icon = "file-text"
                steps.append(PathwayStep(
                    icon=icon,
                    title=s["title"],
                    detail=s["detail"],
                ))
            documents = data.get("documents", [])
            if not steps:
                return None
            return PathwayResult(steps=steps, documents=documents)
        except Exception as e:
            logger.warning("Failed to parse pathway response: %s", e)
            return None

    async def analyze(self, issue: str, case_type: str) -> AnalyzeResponse:
        errors: list[str] = []

        # 1. Retrieve relevant legal chunks via hybrid retrieval
        results = hybrid_retriever.search(issue)
        context = self._format_context(results)
        logger.info("Retrieved %d relevant chunks for query", len(results))

        # 2. Phase A — 3 parallel Gemini calls: pathway + advocate + opponent
        pathway_prompt = build_pathway_prompt(issue, case_type, context)
        pathway_task = gemini_service.generate(pathway_prompt)
        adversarial_task = adversarial_service.analyze(issue, case_type, context)

        phase_a = await asyncio.gather(pathway_task, adversarial_task, return_exceptions=True)

        # 3. Parse pathway
        pathway = None
        if isinstance(phase_a[0], Exception):
            logger.error("Pathway generation failed: %s", phase_a[0])
            errors.append(f"Pathway generation failed: {phase_a[0]}")
        elif phase_a[0] is not None:
            pathway = self._parse_pathway(phase_a[0])
            if pathway is None:
                errors.append("Failed to parse pathway response from AI")
        else:
            errors.append("Pathway generation returned no result")

        # 4. Parse adversarial result
        adversarial = None
        advocate_confidence = 0.5
        opponent_confidence = 0.5
        if isinstance(phase_a[1], Exception):
            logger.error("Adversarial analysis failed: %s", phase_a[1])
            errors.append(f"Adversarial analysis failed: {phase_a[1]}")
        else:
            adversarial, adv_errors = phase_a[1]
            errors.extend(adv_errors)
            if adversarial is not None:
                advocate_confidence = adversarial.advocate.confidence
                opponent_confidence = adversarial.opponent.confidence

        # 5. Phase B — Enhanced risk scoring (uses adversarial confidence)
        risk, risk_errors = await risk_scoring_service.analyze(
            issue, case_type, context, advocate_confidence, opponent_confidence
        )
        errors.extend(risk_errors)

        return AnalyzeResponse(
            pathway=pathway,
            risk=risk,
            adversarial=adversarial,
            errors=errors,
        )


rag_service = RAGService()
