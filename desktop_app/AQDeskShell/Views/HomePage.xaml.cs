using AQDeskShell.ViewModels;
using System.ComponentModel;
using System.IO;
using System.Runtime.CompilerServices;
using System.Windows;
using System.Windows.Controls;

namespace AQDeskShell.Views;

public partial class HomePage : Page, INotifyPropertyChanged
{
    private readonly ShellState _state;
    private int _initProgress;
    private string _initMessage = "等待初始化";

    public event PropertyChangedEventHandler? PropertyChanged;

    public int InitProgress
    {
        get => _initProgress;
        set
        {
            if (_initProgress == value) return;
            _initProgress = value;
            OnPropertyChanged();
        }
    }

    public string InitMessage
    {
        get => _initMessage;
        set
        {
            if (_initMessage == value) return;
            _initMessage = value;
            OnPropertyChanged();
        }
    }

    public HomePage(ShellState state)
    {
        InitializeComponent();
        _state = state;
        DataContext = this;
        _state.Bootstrap.ProgressChanged += Bootstrap_ProgressChanged;
        _state.Bootstrap.Completed += Bootstrap_Completed;
        LoadReportPreview();
    }

    private void LoadReportPreview()
    {
        var readmePath = Path.Combine(_state.ProjectRoot, "README.md");
        if (File.Exists(readmePath))
        {
            ReportBrowser.Navigate(readmePath);
        }
    }

    private async void InitEnv_OnClick(object sender, RoutedEventArgs e)
    {
        InitMessage = "正在初始化环境...";
        InitProgress = 0;
        var ok = await _state.Bootstrap.RunPrepareAsync();
        if (!ok)
        {
            MessageBox.Show("环境初始化失败，请到设置-日志查看详情。", "初始化失败", MessageBoxButton.OK, MessageBoxImage.Error);
        }
    }

    private void Bootstrap_ProgressChanged(object? sender, Services.BootstrapProgressEvent e)
    {
        Dispatcher.Invoke(() =>
        {
            if (e.Progress > 0) InitProgress = e.Progress;
            InitMessage = e.Message;
        });
    }

    private void Bootstrap_Completed(object? sender, bool ok)
    {
        Dispatcher.Invoke(() =>
        {
            InitProgress = ok ? 100 : InitProgress;
            InitMessage = ok ? "初始化完成" : "初始化失败";
        });
    }

    private void OpenWorkbench_OnClick(object sender, RoutedEventArgs e)
    {
        NavigationService?.Navigate(new WorkbenchPage(_state));
    }

    private void OnPropertyChanged([CallerMemberName] string? memberName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(memberName));
    }
}
