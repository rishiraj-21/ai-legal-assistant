using System.Text;
using System.Text.Json;
using Backend.Models;

namespace Backend.Services;

public class PythonApiClient
{
    private readonly HttpClient _http;
    private readonly ILogger<PythonApiClient> _logger;
    private readonly IHttpContextAccessor _contextAccessor;

    public PythonApiClient(HttpClient http, ILogger<PythonApiClient> logger, IHttpContextAccessor contextAccessor)
    {
        _http = http;
        _logger = logger;
        _contextAccessor = contextAccessor;
    }

    public async Task<PythonAnalysisResponse?> AnalyzeAsync(string issue, string caseType, string? correlationId = null)
    {
        try
        {
            var payload = new PythonAnalyzeRequest(issue, caseType);
            var json = JsonSerializer.Serialize(payload);

            using var request = new HttpRequestMessage(HttpMethod.Post, "/analyze")
            {
                Content = new StringContent(json, Encoding.UTF8, "application/json")
            };

            // Forward correlation ID
            var corrId = correlationId
                ?? _contextAccessor.HttpContext?.Items["CorrelationId"]?.ToString();
            if (!string.IsNullOrEmpty(corrId))
            {
                request.Headers.Add("X-Correlation-Id", corrId);
            }

            var response = await _http.SendAsync(request);

            if (!response.IsSuccessStatusCode)
            {
                _logger.LogWarning("Python engine returned {Status}", response.StatusCode);
                return null;
            }

            var result = await response.Content.ReadFromJsonAsync<PythonAnalysisResponse>(
                new JsonSerializerOptions { PropertyNameCaseInsensitive = true }
            );
            return result;
        }
        catch (TaskCanceledException)
        {
            _logger.LogWarning("Python engine request timed out");
            return null;
        }
        catch (HttpRequestException ex)
        {
            _logger.LogWarning(ex, "Failed to reach Python engine");
            return null;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unexpected error calling Python engine");
            return null;
        }
    }
}
