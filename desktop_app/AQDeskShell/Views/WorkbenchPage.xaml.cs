using AQDeskShell.Services;
using AQDeskShell.ViewModels;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Windows;
using System.Windows.Controls;

namespace AQDeskShell.Views;

public partial class WorkbenchPage : Page, INotifyPropertyChanged
{
    private readonly ShellState _state;
    private bool _autoStarted;
    private bool _webViewReady;
    private bool _isBusy;
    private int _runProgress;
    private string _runMessage = "Ready.";
    private string _workbenchStatus = "Idle";

    public event PropertyChangedEventHandler? PropertyChanged;

    public string WorkbenchStatus
    {
        get => _workbenchStatus;
        set
        {
            if (_workbenchStatus == value) return;
            _workbenchStatus = value;
            OnPropertyChanged();
        }
    }

    public int RunProgress
    {
        get => _runProgress;
        set
        {
            if (_runProgress == value) return;
            _runProgress = value;
            OnPropertyChanged();
        }
    }

    public string RunMessage
    {
        get => _runMessage;
        set
        {
            if (_runMessage == value) return;
            _runMessage = value;
            OnPropertyChanged();
        }
    }

    public bool IsBusy
    {
        get => _isBusy;
        set
        {
            if (_isBusy == value) return;
            _isBusy = value;
            OnPropertyChanged();
            BusyOverlay.Visibility = _isBusy ? Visibility.Visible : Visibility.Collapsed;
        }
    }

    public WorkbenchPage(ShellState state)
    {
        InitializeComponent();
        _state = state;
        DataContext = this;
        _state.Process.ProgressChanged += Process_ProgressChanged;
        _state.Process.ProcessCompleted += Process_ProcessCompleted;
        Loaded += WorkbenchPage_Loaded;
        Unloaded += WorkbenchPage_Unloaded;
    }

    private void WorkbenchPage_Unloaded(object sender, RoutedEventArgs e)
    {
        _state.Process.ProgressChanged -= Process_ProgressChanged;
        _state.Process.ProcessCompleted -= Process_ProcessCompleted;
    }

    private async void WorkbenchPage_Loaded(object sender, RoutedEventArgs e)
    {
        await InitializeWebViewAsync();
        TryOpenMapPage();

        if (!_autoStarted)
        {
            _autoStarted = true;
            await RunMainPipelineAsync();
        }
    }

    private async Task InitializeWebViewAsync()
    {
        try
        {
            await MapWebView.EnsureCoreWebView2Async();
            _webViewReady = true;
            InstallWebViewButton.Visibility = Visibility.Collapsed;
        }
        catch (Exception ex)
        {
            _webViewReady = false;
            InstallWebViewButton.Visibility = Visibility.Visible;
            RunMessage = $"嵌入浏览器初始化失败：{ex.Message}";
            WorkbenchStatus = "WebView2 unavailable";
        }
    }

    private async Task RunMainPipelineAsync()
    {
        if (_state.Process.IsRunning) return;
        IsBusy = true;
        RunProgress = 2;
        RunMessage = "Starting hidden bootstrap pipeline...";
        WorkbenchStatus = "Running main.py in background";
        var code = await _state.Process.StartAllAsync();
        if (code == 0)
        {
            RunProgress = 100;
            RunMessage = "Completed.";
            WorkbenchStatus = "Map generated";
            TryOpenMapPage();
        }
        else
        {
            RunMessage = $"Failed with exit code {code}";
            WorkbenchStatus = "Run failed";
        }
        IsBusy = false;
    }

    private void Process_ProgressChanged(object? sender, ProcessProgressEvent e)
    {
        Dispatcher.Invoke(() =>
        {
            if (e.Progress > 0) RunProgress = e.Progress;
            RunMessage = e.Message;
        });
    }

    private void Process_ProcessCompleted(object? sender, int exitCode)
    {
        Dispatcher.Invoke(() =>
        {
            if (exitCode == 0)
            {
                RunProgress = 100;
                WorkbenchStatus = "Pipeline finished";
            }
            else if (RunProgress < 100)
            {
                WorkbenchStatus = $"Pipeline failed ({exitCode})";
            }
        });
    }

    private void TryOpenMapPage()
    {
        if (!_webViewReady)
        {
            WorkbenchStatus = "WebView2 不可用（地图生成后可改用外部浏览器打开）";
            return;
        }

        var runtimeDir = new DirectoryInfo(_state.ProjectRoot);
        var installRoot = runtimeDir.Parent?.FullName ?? _state.ProjectRoot;
        var candidates = new[]
        {
            Path.Combine(_state.ProjectRoot, "visualizations", "interactive_air_quality_map.html"),
            Path.Combine(installRoot, "visualizations", "interactive_air_quality_map.html"),
        };
        var localMap = candidates.FirstOrDefault(File.Exists);
        if (!string.IsNullOrWhiteSpace(localMap))
        {
            MapWebView.Source = new Uri(localMap);
            WorkbenchStatus = "Map loaded in embedded WebView";
            return;
        }

        var html = $@"
<!doctype html>
<html><head><meta charset='utf-8'><title>Map Not Ready</title>
<style>body{{font-family:Segoe UI,Arial,sans-serif;background:#eef3f9;color:#19406b;padding:28px}}
.box{{max-width:780px;background:#fff;border:1px solid #d9e5f4;border-radius:12px;padding:20px}}
h2{{margin:0 0 10px}} code{{background:#f3f7fc;padding:2px 6px;border-radius:6px}}</style></head>
<body><div class='box'>
<h2>地图尚未生成</h2>
<p>主流程尚未成功完成，请点击上方 <b>Run Main (Hidden)</b> 重试。</p>
<p>常见原因：数据包未就位、Python 依赖未安装完成。</p>
<p>预期地图路径：</p>
<ul>
<li><code>{candidates[0]}</code></li>
<li><code>{candidates[1]}</code></li>
</ul>
</div></body></html>";
        MapWebView.CoreWebView2.NavigateToString(html);
        WorkbenchStatus = "Map file not found yet";
    }

    private async void StartAll_OnClick(object sender, RoutedEventArgs e)
    {
        await RunMainPipelineAsync();
    }

    private async void InstallWebView2_OnClick(object sender, RoutedEventArgs e)
    {
        InstallWebViewButton.IsEnabled = false;
        IsBusy = true;
        RunMessage = "正在安装 WebView2 Runtime...";
        WorkbenchStatus = "Installing WebView2 runtime";

        var ok = await Task.Run(InstallWebView2Runtime);

        IsBusy = false;
        InstallWebViewButton.IsEnabled = true;

        if (!ok)
        {
            RunMessage = "WebView2 安装失败，请检查网络后重试。";
            WorkbenchStatus = "WebView2 install failed";
            return;
        }

        RunMessage = "WebView2 安装完成，正在重新加载地图区域...";
        WorkbenchStatus = "Re-initializing WebView2";
        await InitializeWebViewAsync();
        TryOpenMapPage();
    }

    private static bool InstallWebView2Runtime()
    {
        var wingetOk = RunHiddenProcess(
            "powershell",
            "-NoProfile -ExecutionPolicy Bypass -Command \"winget install --id Microsoft.EdgeWebView2Runtime -e --silent --scope user --accept-package-agreements --accept-source-agreements\"",
            out _
        );
        if (wingetOk) return true;

        var tempExe = Path.Combine(Path.GetTempPath(), "MicrosoftEdgeWebView2Setup.exe");
        var downloadCmd =
            "$ErrorActionPreference='Stop';" +
            "$url='https://go.microsoft.com/fwlink/p/?LinkId=2124703';" +
            $"$out='{tempExe.Replace("\\", "\\\\")}';" +
            "Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $out";

        var downloaded = RunHiddenProcess(
            "powershell",
            $"-NoProfile -ExecutionPolicy Bypass -Command \"{downloadCmd}\"",
            out _
        );
        if (!downloaded || !File.Exists(tempExe)) return false;

        var installOk = RunHiddenProcess(tempExe, "/silent /install", out _);
        try { File.Delete(tempExe); } catch { }
        return installOk;
    }

    private static bool RunHiddenProcess(string fileName, string arguments, out int exitCode)
    {
        try
        {
            using var proc = Process.Start(new ProcessStartInfo(fileName, arguments)
            {
                UseShellExecute = false,
                CreateNoWindow = true,
                WindowStyle = ProcessWindowStyle.Hidden,
            });
            if (proc is null)
            {
                exitCode = -1;
                return false;
            }
            proc.WaitForExit();
            exitCode = proc.ExitCode;
            return exitCode == 0;
        }
        catch
        {
            exitCode = -1;
            return false;
        }
    }

    private void BackHome_OnClick(object sender, RoutedEventArgs e)
    {
        NavigationService?.Navigate(new HomePage(_state));
    }

    private void OnPropertyChanged([CallerMemberName] string? memberName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(memberName));
    }
}
