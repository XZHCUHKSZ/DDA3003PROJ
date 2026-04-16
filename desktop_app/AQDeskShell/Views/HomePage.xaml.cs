using AQDeskShell.ViewModels;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Runtime.CompilerServices;
using System.Windows;
using System.Windows.Controls;

namespace AQDeskShell.Views;

public partial class HomePage : Page, INotifyPropertyChanged
{
    private readonly ShellState _state;
    private int _initProgress;
    private string _initMessage = "Waiting for runtime setup.";
    private string _dataStatusMessage = "Checking data bundle...";
    private string _dataPathHint = "";

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

    public string DataStatusMessage
    {
        get => _dataStatusMessage;
        set
        {
            if (_dataStatusMessage == value) return;
            _dataStatusMessage = value;
            OnPropertyChanged();
        }
    }

    public string DataPathHint
    {
        get => _dataPathHint;
        set
        {
            if (_dataPathHint == value) return;
            _dataPathHint = value;
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
        RefreshDataStatus();
    }

    private void RefreshDataStatus()
    {
        var status = _state.DataBundle.Check(_state.ProjectRoot);
        DataStatusMessage = status.Message;
        DataPathHint = $"Expected folder: {status.DataDir}";
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
        InitMessage = "Preparing runtime...";
        InitProgress = 0;
        var ok = await _state.Bootstrap.RunPrepareAsync();
        if (!ok)
        {
            MessageBox.Show("Runtime setup failed. Open settings > logs for details.", "Setup Failed", MessageBoxButton.OK, MessageBoxImage.Error);
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
            InitMessage = ok ? "Runtime ready." : "Runtime setup failed.";
        });
    }

    private void OpenWorkbench_OnClick(object sender, RoutedEventArgs e)
    {
        NavigationService?.Navigate(new WorkbenchPage(_state));
    }

    private void CheckData_OnClick(object sender, RoutedEventArgs e)
    {
        RefreshDataStatus();
    }

    private void OpenDataFolder_OnClick(object sender, RoutedEventArgs e)
    {
        var status = _state.DataBundle.Check(_state.ProjectRoot);
        Directory.CreateDirectory(status.DataDir);
        Process.Start(new ProcessStartInfo("explorer.exe", status.DataDir) { UseShellExecute = true });
    }

    private void OpenGuide_OnClick(object sender, RoutedEventArgs e)
    {
        var guide = Path.Combine(_state.ProjectRoot, "PRODUCT_PACKAGING_CHECKLIST.md");
        if (File.Exists(guide))
        {
            Process.Start(new ProcessStartInfo(guide) { UseShellExecute = true });
            return;
        }
        MessageBox.Show("Guide not found.");
    }

    private void OnPropertyChanged([CallerMemberName] string? memberName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(memberName));
    }
}

