using System.Text.Json.Serialization;

namespace Backend.Models;

public record PythonAnalyzeRequest(
    [property: JsonPropertyName("issue")] string Issue,
    [property: JsonPropertyName("case_type")] string CaseType
);

public record PythonAnalysisResponse(
    [property: JsonPropertyName("pathway")] PythonPathway? Pathway,
    [property: JsonPropertyName("risk")] PythonRisk? Risk,
    [property: JsonPropertyName("adversarial")] PythonAdversarial? Adversarial,
    [property: JsonPropertyName("errors")] string[] Errors
);

public record PythonPathway(
    [property: JsonPropertyName("steps")] PythonStep[] Steps,
    [property: JsonPropertyName("documents")] string[] Documents
);

public record PythonStep(
    [property: JsonPropertyName("icon")] string Icon,
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("detail")] string Detail
);

public record PythonRisk(
    [property: JsonPropertyName("risk_score")] int RiskScore,
    [property: JsonPropertyName("settlement_probability")] int SettlementProbability,
    [property: JsonPropertyName("factors")] object[][] Factors,
    [property: JsonPropertyName("summary")] string Summary,
    [property: JsonPropertyName("risk_label")] string? RiskLabel,
    [property: JsonPropertyName("detailed_factors")] PythonDetailedFactor[]? DetailedFactors,
    [property: JsonPropertyName("settlement")] PythonSettlement? Settlement
);

public record PythonDetailedFactor(
    [property: JsonPropertyName("label")] string Label,
    [property: JsonPropertyName("value")] int Value,
    [property: JsonPropertyName("explanation")] string Explanation
);

public record PythonSettlement(
    [property: JsonPropertyName("probability")] int Probability,
    [property: JsonPropertyName("recommendation")] string Recommendation,
    [property: JsonPropertyName("reasoning")] string Reasoning
);

public record PythonAdvocateOpponent(
    [property: JsonPropertyName("points")] string[] Points,
    [property: JsonPropertyName("confidence")] double Confidence,
    [property: JsonPropertyName("key_precedents")] string[] KeyPrecedents
);

public record PythonAdversarial(
    [property: JsonPropertyName("advocate")] PythonAdvocateOpponent Advocate,
    [property: JsonPropertyName("opponent")] PythonAdvocateOpponent Opponent,
    [property: JsonPropertyName("vulnerabilities")] string[] Vulnerabilities
);
