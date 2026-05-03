import re

from pydantic import BaseModel, Field, field_validator

ALLOWED_CASE_TYPES = {
    "civil", "criminal", "family", "property", "corporate",
    "consumer", "ip", "employment", "tax", "other",
}


class AnalyzeRequest(BaseModel):
    issue: str = Field(..., min_length=10, max_length=5000, description="User's legal issue description")
    case_type: str = Field(default="Civil", description="Type of legal case")

    @field_validator("issue")
    @classmethod
    def sanitize_issue(cls, v: str) -> str:
        # Strip HTML tags
        v = re.sub(r"<[^>]*>", " ", v)
        # Collapse whitespace
        v = re.sub(r"\s+", " ", v).strip()
        if len(v) < 10:
            raise ValueError("Issue must be at least 10 characters after removing HTML tags.")
        return v

    @field_validator("case_type")
    @classmethod
    def validate_case_type(cls, v: str) -> str:
        if v.lower() not in ALLOWED_CASE_TYPES:
            allowed = ", ".join(sorted(ALLOWED_CASE_TYPES))
            raise ValueError(f"case_type must be one of: {allowed}")
        return v


class PathwayStep(BaseModel):
    icon: str
    title: str
    detail: str


class PathwayResult(BaseModel):
    steps: list[PathwayStep]
    documents: list[str]


class RiskResult(BaseModel):
    risk_score: int = Field(ge=0, le=100)
    settlement_probability: int = Field(ge=0, le=100)
    factors: list[list] = Field(description="List of [label, value] tuples")
    summary: str


class AdvocateResult(BaseModel):
    points: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    key_precedents: list[str] = Field(default_factory=list)


class OpponentResult(BaseModel):
    points: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    key_precedents: list[str] = Field(default_factory=list)


class AdversarialResult(BaseModel):
    advocate: AdvocateResult
    opponent: OpponentResult
    vulnerabilities: list[str] = Field(default_factory=list)


class RiskFactor(BaseModel):
    label: str
    value: int = Field(ge=0, le=100)
    explanation: str


class SettlementResult(BaseModel):
    probability: int = Field(ge=0, le=100)
    recommendation: str = Field(description="Negotiate, Litigate, or Settle")
    reasoning: str


class EnhancedRiskResult(BaseModel):
    risk_score: int = Field(ge=0, le=100)
    settlement_probability: int = Field(ge=0, le=100)
    factors: list[list] = Field(default_factory=list, description="Legacy [label, value] tuples")
    summary: str = ""
    risk_label: str = ""
    detailed_factors: list[RiskFactor] = Field(default_factory=list)
    settlement: SettlementResult | None = None


class AnalyzeResponse(BaseModel):
    pathway: PathwayResult | None = None
    risk: EnhancedRiskResult | None = None
    adversarial: AdversarialResult | None = None
    errors: list[str] = Field(default_factory=list)
