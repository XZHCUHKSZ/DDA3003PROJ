using System.Net.Http;

namespace AQDeskShell.Services;

public class HealthService
{
    private static readonly HttpClient Http = new() { Timeout = TimeSpan.FromSeconds(2.5) };

    public async Task<bool> IsHealthyAsync(string url, CancellationToken ct = default)
    {
        try
        {
            using var resp = await Http.GetAsync(url, ct);
            return resp.IsSuccessStatusCode;
        }
        catch
        {
            return false;
        }
    }

    public async Task<(bool map, bool ai, bool heatmap)> CheckAllAsync(CancellationToken ct = default)
    {
        var ai = await IsHealthyAsync("http://127.0.0.1:8787/health", ct);
        var ctrl = await IsHealthyAsync("http://127.0.0.1:8790/health", ct);
        var heat = await IsHealthyAsync("http://127.0.0.1:8791/health", ct);
        return (ctrl, ai, heat);
    }
}
