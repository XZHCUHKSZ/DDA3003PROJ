using System.Diagnostics;

namespace AQDeskShell.Services;

public class ProcessService
{
    private readonly string _projectRoot;

    public ProcessService(string projectRoot)
    {
        _projectRoot = projectRoot;
    }

    public Task<int> StartAllAsync()
    {
        return RunHiddenAsync("powershell", "-NoProfile -ExecutionPolicy Bypass -File .\\bootstrap_env.ps1 -Mode all");
    }

    public Task<int> StartAiOnlyAsync()
    {
        return RunHiddenAsync("powershell", "-NoProfile -ExecutionPolicy Bypass -File .\\bootstrap_env.ps1 -Mode ai");
    }

    private async Task<int> RunHiddenAsync(string fileName, string args)
    {
        var psi = new ProcessStartInfo(fileName, args)
        {
            WorkingDirectory = _projectRoot,
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            CreateNoWindow = true,
        };
        using var p = Process.Start(psi) ?? throw new InvalidOperationException("Failed to start process.");
        await p.WaitForExitAsync();
        return p.ExitCode;
    }
}
