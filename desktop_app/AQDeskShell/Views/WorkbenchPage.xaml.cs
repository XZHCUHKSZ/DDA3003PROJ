using AQDeskShell.Services;
using AQDeskShell.ViewModels;
using Microsoft.Web.WebView2.Core;
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
    private bool _isMapFullscreen;
    private DateTime _pipelineStartUtc = DateTime.MinValue;
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
        SetMapFullscreen(false);
    }

    private async void WorkbenchPage_Loaded(object sender, RoutedEventArgs e)
    {
        await InitializeWebViewAsync();

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
            MapWebView.NavigationCompleted -= MapWebView_NavigationCompleted;
            MapWebView.NavigationCompleted += MapWebView_NavigationCompleted;
        }
        catch (Exception ex)
        {
            _webViewReady = false;
            InstallWebViewButton.Visibility = Visibility.Visible;
            RunMessage = $"嵌入浏览器初始化失败：{ex.Message}";
            WorkbenchStatus = "WebView2 unavailable";
            IsBusy = false;
        }
    }

    private async Task RunMainPipelineAsync()
    {
        if (_state.Process.IsRunning) return;
        _pipelineStartUtc = DateTime.UtcNow;
        IsBusy = true;
        RunProgress = 2;
        RunMessage = "正在准备运行环境与数据...";
        WorkbenchStatus = "Running main.py in background";

        var code = await _state.Process.StartAllAsync();
        if (code == 0)
        {
            RunProgress = 96;
            RunMessage = "主流程完成，正在加载最新地图页面...";
            WorkbenchStatus = "Map generated";
            var opened = TryOpenMapPage(requireFresh: true);
            if (!opened)
            {
                IsBusy = false;
            }
        }
        else
        {
            RunMessage = $"主流程失败，退出码 {code}";
            WorkbenchStatus = "Run failed";
            IsBusy = false;
        }
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
                WorkbenchStatus = "Pipeline finished";
                if (RunProgress < 96) RunProgress = 96;
            }
            else if (RunProgress < 100)
            {
                WorkbenchStatus = $"Pipeline failed ({exitCode})";
            }
        });
    }

    private void MapWebView_NavigationCompleted(object? sender, CoreWebView2NavigationCompletedEventArgs e)
    {
        IsBusy = false;
        if (e.IsSuccess)
        {
            RunProgress = 100;
            RunMessage = "地图已加载完成。";
            WorkbenchStatus = "Map loaded in embedded WebView";
            return;
        }

        RunMessage = $"地图加载失败（0x{e.WebErrorStatus:X}）。";
        WorkbenchStatus = "Map navigation failed";
    }

    private bool TryOpenMapPage(bool requireFresh)
    {
        if (!_webViewReady)
        {
            WorkbenchStatus = "WebView2 不可用（地图生成后可改用外部浏览器打开）";
            return false;
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
            var lastWrite = File.GetLastWriteTimeUtc(localMap);
            if (requireFresh && _pipelineStartUtc != DateTime.MinValue && lastWrite < _pipelineStartUtc.AddSeconds(-1))
            {
                RunMessage = "检测到地图文件仍是旧缓存，请重试一次 Run Main。";
                WorkbenchStatus = "Stale map detected";
                return false;
            }

            var uri = new UriBuilder(new Uri(localMap))
            {
                Query = "v=" + lastWrite.Ticks
            }.Uri;
            MapWebView.Source = uri;
            WorkbenchStatus = "Loading fresh map";
            return true;
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
        return false;
    }

    private async void StartAll_OnClick(object sender, RoutedEventArgs e)
    {
        await RunMainPipelineAsync();
    }

    private void ToggleFullscreen_OnClick(object sender, RoutedEventArgs e)
    {
        SetMapFullscreen(!_isMapFullscreen);
    }

    private void SetMapFullscreen(bool enabled)
    {
        var wnd = Window.GetWindow(this) as MainWindow;
        wnd?.SetMapImmersiveMode(enabled);
        _isMapFullscreen = enabled;
        FullscreenButton.Content = enabled ? "退出全屏" : "全屏地图";
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
        TryOpenMapPage(requireFresh: false);
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
        SetMapFullscreen(false);
        NavigationService?.Navigate(new HomePage(_state));
    }

    private void OnPropertyChanged([CallerMemberName] string? memberName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(memberName));
    }
}
