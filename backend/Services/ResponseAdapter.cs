using System.Text.Json;
using Backend.Models;

namespace Backend.Services;

internal static class ResponseAdapter
{
    internal static AnalysisResult Adapt(PythonAnalysisResponse? python, AnalysisResult mockFallback)
    {
        // Steps: use AI-generated if available, else mock
        var steps = mockFallback.Steps;
        if (python?.Pathway?.Steps is { Length: > 0 } aiSteps)
        {
            steps = aiSteps.Select(s => new LegalStep(s.Title, s.Detail)).ToArray();
        }

        // Risk score: use AI-generated if available, else mock
        var riskScore = mockFallback.RiskScore;
        var settlementProbability = mockFallback.SettlementProbability;
        if (python?.Risk is { } aiRisk)
        {
            riskScore = Math.Clamp(aiRisk.RiskScore, 0, 100);
            settlementProbability = Math.Clamp(aiRisk.SettlementProbability, 0, 100);
        }

        // Settlement from AI
        if (python?.Risk?.Settlement is { } settlement)
        {
            settlementProbability = Math.Clamp(settlement.Probability, 0, 100);
        }

        // Risk factors: extract from Python response if available
        string[]? riskFactors = null;
        if (python?.Risk?.Factors is { Length: > 0 } factors)
        {
            riskFactors = factors.Select(f =>
            {
                var label = f.Length > 0 ? f[0]?.ToString() ?? "" : "";
                var value = f.Length > 1 ? f[1]?.ToString() ?? "0" : "0";
                return $"{label}:{value}";
            }).ToArray();
        }

        // Detailed factors from AI
        DetailedFactor[]? detailedFactors = null;
        if (python?.Risk?.DetailedFactors is { Length: > 0 } df)
        {
            detailedFactors = df.Select(f => new DetailedFactor(f.Label, f.Value, f.Explanation)).ToArray();
        }

        // Adversarial from AI
        var advocatePoints = python?.Adversarial?.Advocate.Points ?? mockFallback.AdvocatePoints;
        var opponentPoints = python?.Adversarial?.Opponent.Points ?? mockFallback.OpponentPoints;
        var vulnerabilities = python?.Adversarial?.Vulnerabilities ?? mockFallback.Vulnerabilities;
        var advocateConfidence = python?.Adversarial?.Advocate.Confidence ?? mockFallback.AdvocateConfidence;
        var opponentConfidence = python?.Adversarial?.Opponent.Confidence ?? mockFallback.OpponentConfidence;

        // Documents from pathway
        var documents = python?.Pathway?.Documents;

        return new AnalysisResult(
            RiskScore: riskScore,
            SettlementProbability: settlementProbability,
            AdvocatePoints: advocatePoints,
            OpponentPoints: opponentPoints,
            Vulnerabilities: vulnerabilities,
            Steps: steps,
            RiskFactors: riskFactors,
            RiskSummary: python?.Risk?.Summary,
            AdvocateConfidence: advocateConfidence,
            OpponentConfidence: opponentConfidence,
            RiskLabel: python?.Risk?.RiskLabel,
            DetailedFactors: detailedFactors,
            SettlementRecommendation: python?.Risk?.Settlement?.Recommendation,
            SettlementReasoning: python?.Risk?.Settlement?.Reasoning,
            Documents: documents
        );
    }
}
