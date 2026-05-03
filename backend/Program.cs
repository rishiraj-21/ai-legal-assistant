using System.ComponentModel.DataAnnotations;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.RateLimiting;
using Backend.Models;
using Backend.Services;
using Microsoft.AspNetCore.RateLimiting;
using Microsoft.Extensions.Caching.Memory;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAngular", policy =>
    {
        policy.WithOrigins("http://localhost:4200", "http://localhost:4000")
              .AllowAnyHeader()
              .AllowAnyMethod()
              .WithExposedHeaders("X-Correlation-Id");
    });
});

builder.Services.AddMemoryCache();
builder.Services.AddHttpContextAccessor();

var rateLimitConfig = builder.Configuration.GetSection("RateLimit");
var permitLimit = rateLimitConfig.GetValue<int>("PermitLimit", 10);
var windowSeconds = rateLimitConfig.GetValue<int>("WindowSeconds", 60);

builder.Services.AddRateLimiter(options =>
{
    options.RejectionStatusCode = 429;
    options.AddFixedWindowLimiter("analysis", opt =>
    {
        opt.PermitLimit = permitLimit;
        opt.Window = TimeSpan.FromSeconds(windowSeconds);
        opt.QueueLimit = 2;
        opt.QueueProcessingOrder = QueueProcessingOrder.OldestFirst;
    });
});

var pythonUrl = builder.Configuration.GetValue<string>("PythonEngine:BaseUrl") ?? "http://localhost:8000";
builder.Services.AddHttpClient<PythonApiClient>(client =>
{
    client.BaseAddress = new Uri(pythonUrl);
    client.Timeout = TimeSpan.FromSeconds(60);
});

builder.Logging.AddJsonConsole(options =>
{
    options.IncludeScopes = true;
    options.TimestampFormat = "yyyy-MM-dd HH:mm:ss.fff ";
});

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

// ── Correlation ID middleware ────────────────────────────────
app.Use(async (context, next) =>
{
    var correlationId = context.Request.Headers["X-Correlation-Id"].FirstOrDefault()
                        ?? Guid.NewGuid().ToString("N")[..12];
    context.Items["CorrelationId"] = correlationId;
    context.Response.Headers["X-Correlation-Id"] = correlationId;

    var logger = context.RequestServices.GetRequiredService<ILogger<Program>>();
    using (logger.BeginScope(new Dictionary<string, object> { ["CorrelationId"] = correlationId }))
    {
        await next();
    }
});

// ── Global error handler middleware ──────────────────────────
app.Use(async (context, next) =>
{
    try
    {
        await next();
    }
    catch (Exception ex)
    {
        var logger = context.RequestServices.GetRequiredService<ILogger<Program>>();
        var correlationId = context.Items["CorrelationId"]?.ToString() ?? "unknown";
        logger.LogError(ex, "Unhandled exception [CorrelationId={CorrelationId}]", correlationId);

        context.Response.StatusCode = 500;
        context.Response.ContentType = "application/json";
        await context.Response.WriteAsJsonAsync(new
        {
            error = "An unexpected error occurred.",
            correlationId
        });
    }
});

app.UseHttpsRedirection();
app.UseCors("AllowAngular");
app.UseRateLimiter();

// ── Lawyers ──────────────────────────────────────────────────
var lawyers = new[]
{
    new Lawyer("Aditi Sharma", "Family & Divorce", 4.9, 1284, 25, 60, 12, true, "AS", "EN · HI"),
    new Lawyer("Rohan Mehta", "Corporate & M&A", 4.8, 932, 40, 90, 15, true, "RM", "EN"),
    new Lawyer("Nisha Verma", "Criminal Defense", 4.9, 2105, 30, 75, 18, false, "NV", "EN · HI · MR"),
    new Lawyer("Arjun Kapoor", "Property & Real Estate", 4.7, 748, 20, 55, 9, true, "AK", "EN · HI"),
    new Lawyer("Priya Nair", "Consumer & Civil", 4.8, 611, 18, 48, 7, true, "PN", "EN · ML"),
    new Lawyer("Karan Iyer", "Intellectual Property", 4.9, 489, 35, 80, 11, false, "KI", "EN · TA"),
};

app.MapGet("/api/lawyers", () => lawyers)
   .WithName("GetLawyers")
   .WithOpenApi();

// ── Analysis ─────────────────────────────────────────────────
var mockAnalysis = new AnalysisResult(
    RiskScore: 72,
    SettlementProbability: 68,
    AdvocatePoints: Array.Empty<string>(),
    OpponentPoints: Array.Empty<string>(),
    Vulnerabilities: Array.Empty<string>(),
    Steps: new[] {
        new LegalStep("Gather Evidence", "Collect contracts, emails, receipts, and any written communications."),
        new LegalStep("Send Legal Notice", "Formal notice to the opposing party outlining the grievance."),
        new LegalStep("File the Case", "Submit the petition in the appropriate court of jurisdiction."),
        new LegalStep("Mediation Phase", "Attempt a court-mandated settlement before trial."),
        new LegalStep("Hearing & Verdict", "Presentation of evidence, cross-examination, and final judgment.")
    },
    RiskFactors: null,
    RiskSummary: null,
    AdvocateConfidence: 0,
    OpponentConfidence: 0,
    RiskLabel: null,
    DetailedFactors: null,
    SettlementRecommendation: null,
    SettlementReasoning: null,
    Documents: null
);

app.MapGet("/api/analysis", () => mockAnalysis)
   .WithName("GetAnalysis")
   .WithOpenApi();

var cacheTtl = builder.Configuration.GetValue<int>("Cache:AnalysisTtlMinutes", 30);

app.MapPost("/api/analysis/submit", async (
    AnalysisRequest request,
    PythonApiClient pythonClient,
    IMemoryCache cache,
    ILogger<Program> logger) =>
{
    // ── Validation ───────────────────────────────────────────
    var context = new ValidationContext(request);
    var errors = new List<ValidationResult>();
    if (!Validator.TryValidateObject(request, context, errors, validateAllProperties: true))
    {
        var dict = errors
            .Where(e => e.MemberNames.Any())
            .GroupBy(e => e.MemberNames.First())
            .ToDictionary(g => g.Key, g => g.Select(e => e.ErrorMessage!).ToArray());
        return Results.ValidationProblem(dict);
    }

    // Sanitize issue: strip HTML tags, collapse whitespace
    var sanitizedIssue = SanitizeInput(request.Issue);
    if (sanitizedIssue.Length < 10)
    {
        return Results.ValidationProblem(new Dictionary<string, string[]>
        {
            ["Issue"] = ["Issue must be at least 10 characters after sanitization."]
        });
    }

    // ── Caching ──────────────────────────────────────────────
    var cacheKey = ComputeHash(sanitizedIssue, request.CaseType);
    if (cache.TryGetValue<AnalysisResult>(cacheKey, out var cached) && cached is not null)
    {
        logger.LogInformation("Cache HIT for key {CacheKey}", cacheKey);
        return Results.Ok(new { Issue = sanitizedIssue, request.CaseType, Analysis = cached, Cached = true });
    }

    logger.LogInformation("Cache MISS for key {CacheKey}", cacheKey);

    PythonAnalysisResponse? pythonResult = null;
    try
    {
        var correlationId = (string?)null;
        // correlationId is set via HttpContext in middleware — pass through accessor
        pythonResult = await pythonClient.AnalyzeAsync(sanitizedIssue, request.CaseType, correlationId);
    }
    catch (Exception ex)
    {
        logger.LogWarning(ex, "Python engine call failed — falling back to mock data");
    }

    var analysis = ResponseAdapter.Adapt(pythonResult, mockAnalysis);

    cache.Set(cacheKey, analysis, TimeSpan.FromMinutes(cacheTtl));

    return Results.Ok(new { Issue = sanitizedIssue, request.CaseType, Analysis = analysis, Cached = false });
})
.WithName("SubmitAnalysis")
.WithOpenApi()
.RequireRateLimiting("analysis");

app.Run();

// ── Helpers ──────────────────────────────────────────────────
static string SanitizeInput(string input)
{
    // Strip HTML tags
    var noHtml = Regex.Replace(input, "<[^>]*>", " ");
    // Collapse whitespace
    return Regex.Replace(noHtml, @"\s+", " ").Trim();
}

static string ComputeHash(string issue, string caseType)
{
    var raw = issue.ToLowerInvariant() + "|" + caseType.ToLowerInvariant();
    var bytes = SHA256.HashData(Encoding.UTF8.GetBytes(raw));
    return Convert.ToHexString(bytes)[..16].ToLowerInvariant();
}

// ── Records ──────────────────────────────────────────────────
record Lawyer(string Name, string Spec, double Rating, int Reviews,
              int Chat, int Video, int Exp, bool Online, string Initials, string Lang);

record LegalStep(string Title, string Detail);

record DetailedFactor(string Label, int Value, string Explanation);

record AnalysisResult(
    int RiskScore,
    int SettlementProbability,
    string[] AdvocatePoints,
    string[] OpponentPoints,
    string[] Vulnerabilities,
    LegalStep[] Steps,
    string[]? RiskFactors,
    string? RiskSummary,
    double AdvocateConfidence,
    double OpponentConfidence,
    string? RiskLabel,
    DetailedFactor[]? DetailedFactors,
    string? SettlementRecommendation,
    string? SettlementReasoning,
    string[]? Documents
);

// ── Validated Request ────────────────────────────────────────
class AnalysisRequest : IValidatableObject
{
    private static readonly HashSet<string> AllowedCaseTypes = new(StringComparer.OrdinalIgnoreCase)
    {
        "Civil", "Criminal", "Family", "Property", "Corporate",
        "Consumer", "IP", "Employment", "Tax", "Other"
    };

    [Required(ErrorMessage = "Issue is required.")]
    [MinLength(10, ErrorMessage = "Issue must be at least 10 characters.")]
    [MaxLength(5000, ErrorMessage = "Issue must not exceed 5000 characters.")]
    public string Issue { get; set; } = "";

    [Required(ErrorMessage = "CaseType is required.")]
    public string CaseType { get; set; } = "";

    public IEnumerable<ValidationResult> Validate(ValidationContext validationContext)
    {
        if (!AllowedCaseTypes.Contains(CaseType))
        {
            yield return new ValidationResult(
                $"CaseType must be one of: {string.Join(", ", AllowedCaseTypes)}.",
                new[] { nameof(CaseType) });
        }
    }
}
