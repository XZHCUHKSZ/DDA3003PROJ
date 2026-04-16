using System.Diagnostics;
using System.Text.RegularExpressions;

namespace AQDeskShell.Services;

public record BootstrapProgressEvent(int Progress, string Message);

public class BootstrapService
{
    private readonly string _projectRoot;
    private Process? _bootstrapProc;

    public event EventHandler<BootstrapProgressEvent>? ProgressChanged;
    public event EventHandler<bool>? Completed;

    public BootstrapService(string projectRoot)
    {
        _projectRoot = projectRoot;
    }

    public bool IsRunning => _bootstrapProc is { HasExited: false };

    public async Task<bool> RunPrepareAsync(CancellationToken cancellationToken = default)
    {
        if (IsRunning) return false;
        var psi = new ProcessStartInfo("powershell")
        {
            WorkingDirectory = _projectRoot,
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            CreateNoWindow = true,
            Arguments = "-NoProfile -ExecutionPolicy Bypass -File .\\bootstrap_env.ps1 -Mode prepare",
        };

        _bootstrapProc = new Process { StartInfo = psi, EnableRaisingEvents = true };
        _bootstrapProc.OutputDataReceived += (_, e) => ParseProgress(e.Data);
        _bootstrapProc.ErrorDataReceived += (_, e) =>
        {
            if (!string.IsNullOrWhiteSpace(e.Data))
            {
                ProgressChanged?.Invoke(this, new BootstrapProgressEvent(0, e.Data.Trim()));
            }
        };

        _bootstrapProc.Start();
        _bootstrapProc.BeginOutputReadLine();
        _bootstrapProc.BeginErrorReadLine();
        await _bootstrapProc.WaitForExitAsync(cancellationToken);
        var ok = _bootstrapProc.ExitCode == 0;
        Completed?.Invoke(this, ok);
        return ok;
    }

    private void ParseProgress(string? line)
    {
        if (string.IsNullOrWhiteSpace(line)) return;
        var text = line.Trim();
        var progress = text switch
        {
            var t when t.Contains("Workspace:") => 5,
            var t when t.Contains("Using Python launcher") => 15,
            var t when t.Contains("Creating .venv") => 30,
            var t when t.Contains("Upgrading pip") => 45,
            var t when t.Contains("Installing locked dependencies") => 65,
            var t when t.Contains("Verifying dependency imports") => 85,
            var t when t.Contains("Environment is ready") => 100,
            _ => InferProgressFromInstall(text),
        };
        ProgressChanged?.Invoke(this, new BootstrapProgressEvent(progress, text));
    }

    private static int InferProgressFromInstall(string line)
    {
        var m = Regex.Match(line, @"(\d+)%");
        if (m.Success && int.TryParse(m.Groups[1].Value, out var p))
        {
            return Math.Clamp(p, 10, 90);
        }
        return 0;
    }
}
