using System.Diagnostics;

namespace AQDeskShell.Services;

public record ProcessProgressEvent(int Progress, string Message);

public class ProcessService
{
    private readonly string _projectRoot;
    private Process? _activeProc;

    public event EventHandler<ProcessProgressEvent>? ProgressChanged;
    public event EventHandler<int>? ProcessCompleted;

    public ProcessService(string projectRoot)
    {
        _projectRoot = projectRoot;
    }

    public bool IsRunning => _activeProc is { HasExited: false };

    public Task<int> StartAllAsync(CancellationToken cancellationToken = default)
    {
        return RunHiddenAsync(
            "powershell",
            "-NoProfile -ExecutionPolicy Bypass -File .\\bootstrap_env.ps1 -Mode all",
            cancellationToken
        );
    }

    public Task<int> StartAiOnlyAsync(CancellationToken cancellationToken = default)
    {
        return RunHiddenAsync(
            "powershell",
            "-NoProfile -ExecutionPolicy Bypass -File .\\bootstrap_env.ps1 -Mode ai",
            cancellationToken
        );
    }

    private async Task<int> RunHiddenAsync(string fileName, string args, CancellationToken cancellationToken)
    {
        if (IsRunning) return -2;

        var psi = new ProcessStartInfo(fileName, args)
        {
            WorkingDirectory = _projectRoot,
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            CreateNoWindow = true,
        };

        _activeProc = Process.Start(psi) ?? throw new InvalidOperationException("Failed to start process.");
        _activeProc.OutputDataReceived += (_, e) => ParseLine(e.Data);
        _activeProc.ErrorDataReceived += (_, e) => ParseLine(e.Data);
        _activeProc.BeginOutputReadLine();
        _activeProc.BeginErrorReadLine();

        await _activeProc.WaitForExitAsync(cancellationToken);
        var code = _activeProc.ExitCode;
        ProcessCompleted?.Invoke(this, code);
        return code;
    }

    private void ParseLine(string? line)
    {
        if (string.IsNullOrWhiteSpace(line)) return;
        var text = line.Trim();
        var p = text switch
        {
            var t when t.Contains("[BOOT] Workspace") => 5,
            var t when t.Contains("Using Python launcher") => 12,
            var t when t.Contains("Creating .venv") => 22,
            var t when t.Contains("Upgrading pip") => 32,
            var t when t.Contains("Installing locked dependencies") => 48,
            var t when t.Contains("Verifying dependency imports") => 62,
            var t when t.Contains("Environment is ready") => 70,
            var t when t.Contains("[AI-CTRL][OK]") => 76,
            var t when t.Contains("[AI][OK]") || t.Contains("[AI-WARMUP][OK]") => 82,
            var t when t.Contains("[HEATMAP][OK]") => 88,
            var t when t.Contains("Program finished") => 100,
            _ => InferPercent(text),
        };
        ProgressChanged?.Invoke(this, new ProcessProgressEvent(p, text));
    }

    private static int InferPercent(string text)
    {
        var idx = text.IndexOf('%');
        if (idx > 0)
        {
            var start = idx - 1;
            while (start >= 0 && char.IsDigit(text[start])) start--;
            var s = text[(start + 1)..idx];
            if (int.TryParse(s, out var val))
            {
                return Math.Clamp(val, 5, 95);
            }
        }
        return 0;
    }
}
