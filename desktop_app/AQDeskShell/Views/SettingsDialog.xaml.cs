using AQDeskShell.Services;
using AQDeskShell.ViewModels;
using System.ComponentModel;
using System.IO;
using System.Runtime.CompilerServices;
using System.Windows;

namespace AQDeskShell.Views;

public partial class SettingsDialog : Window, INotifyPropertyChanged
{
    private readonly ShellState _state;
    private string _environmentStatus = "未执行";
    private int _environmentProgress;
    private string _healthStatus = "未检查";
    private string _logsText = "";

    public event PropertyChangedEventHandler? PropertyChanged;

    public string EnvironmentStatus
    {
        get => _environmentStatus;
        set
        {
            if (_environmentStatus == value) return;
            _environmentStatus = value;
            OnPropertyChanged();
        }
    }

    public int EnvironmentProgress
    {
        get => _environmentProgress;
        set
        {
            if (_environmentProgress == value) return;
            _environmentProgress = value;
            OnPropertyChanged();
        }
    }

    public string HealthStatus
    {
        get => _healthStatus;
        set
        {
            if (_healthStatus == value) return;
            _healthStatus = value;
            OnPropertyChanged();
        }
    }

    public string LogsText
    {
        get => _logsText;
        set
        {
            if (_logsText == value) return;
            _logsText = value;
            OnPropertyChanged();
        }
    }

    public SettingsDialog(ShellState state)
    {
        InitializeComponent();
        _state = state;
        DataContext = this;
        _state.Bootstrap.ProgressChanged += Bootstrap_ProgressChanged;
        _state.Bootstrap.Completed += Bootstrap_Completed;
        LoadLogs();
    }

    private void Bootstrap_ProgressChanged(object? sender, BootstrapProgressEvent e)
    {
        Dispatcher.Invoke(() =>
        {
            if (e.Progress > 0) EnvironmentProgress = e.Progress;
            EnvironmentStatus = e.Message;
        });
    }

    private void Bootstrap_Completed(object? sender, bool ok)
    {
        Dispatcher.Invoke(() =>
        {
            EnvironmentStatus = ok ? "初始化成功" : "初始化失败";
            if (ok) EnvironmentProgress = 100;
            LoadLogs();
        });
    }

    private async void BootstrapPrepare_OnClick(object sender, RoutedEventArgs e)
    {
        EnvironmentStatus = "正在初始化...";
        EnvironmentProgress = 0;
        var ok = await _state.Bootstrap.RunPrepareAsync();
        if (!ok)
        {
            MessageBox.Show("初始化失败，请查看日志页。", "错误", MessageBoxButton.OK, MessageBoxImage.Error);
        }
    }

    private async void RefreshHealth_OnClick(object sender, RoutedEventArgs e)
    {
        var (map, ai, heatmap) = await _state.Health.CheckAllAsync();
        HealthStatus = $"主控:{(map ? "OK" : "FAIL")}  AI:{(ai ? "OK" : "FAIL")}  热力:{(heatmap ? "OK" : "FAIL")}";
    }

    private void LoadLogs()
    {
        try
        {
            var logDir = Path.Combine(_state.ProjectRoot, "logs");
            if (!Directory.Exists(logDir))
            {
                LogsText = "暂无日志。";
                return;
            }
            var files = Directory.GetFiles(logDir, "*.log");
            if (files.Length == 0)
            {
                LogsText = "暂无日志文件。";
                return;
            }
            var latest = files.OrderByDescending(File.GetLastWriteTimeUtc).First();
            LogsText = File.ReadAllText(latest);
        }
        catch (Exception ex)
        {
            LogsText = $"读取日志失败: {ex.Message}";
        }
    }

    private void OnPropertyChanged([CallerMemberName] string? memberName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(memberName));
    }
}
