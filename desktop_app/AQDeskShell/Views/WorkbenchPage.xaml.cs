using AQDeskShell.Services;
using AQDeskShell.ViewModels;
using System.ComponentModel;
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
        await MapWebView.EnsureCoreWebView2Async();
        TryOpenMapPage();
        if (!_autoStarted)
        {
            _autoStarted = true;
            await RunMainPipelineAsync();
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
        var candidates = new[]
        {
            Path.Combine(_state.ProjectRoot, "visualizations", "interactive_air_quality_map.html"),
            Path.Combine(@"C:\Users\xzh88\Desktop\cleaned\visualizations", "interactive_air_quality_map.html"),
        };
        var localMap = candidates.FirstOrDefault(File.Exists);
        if (!string.IsNullOrWhiteSpace(localMap))
        {
            MapWebView.Source = new Uri(localMap);
            WorkbenchStatus = "Map loaded in embedded WebView";
            return;
        }
        MapWebView.Source = new Uri("http://127.0.0.1:8790/health");
        WorkbenchStatus = "Map file not found yet, showing health endpoint";
    }

    private async void StartAll_OnClick(object sender, RoutedEventArgs e)
    {
        await RunMainPipelineAsync();
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
