using AQDeskShell.Services;
using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace AQDeskShell.ViewModels;

public class ShellState : INotifyPropertyChanged
{
    private string _headerStatus = "就绪";
    private readonly BootstrapService _bootstrapService;
    private readonly ProcessService _processService;
    private readonly HealthService _healthService;
    private readonly DataBundleService _dataBundleService;

    public event PropertyChangedEventHandler? PropertyChanged;

    public string ProjectRoot { get; }
    public string HeaderStatus
    {
        get => _headerStatus;
        set
        {
            if (_headerStatus == value) return;
            _headerStatus = value;
            OnPropertyChanged();
        }
    }

    public BootstrapService Bootstrap => _bootstrapService;
    public ProcessService Process => _processService;
    public HealthService Health => _healthService;
    public DataBundleService DataBundle => _dataBundleService;

    public ShellState(string projectRoot)
    {
        ProjectRoot = projectRoot;
        _bootstrapService = new BootstrapService(projectRoot);
        _processService = new ProcessService(projectRoot);
        _healthService = new HealthService();
        _dataBundleService = new DataBundleService();
        HookEvents();
    }

    private void HookEvents()
    {
        _bootstrapService.ProgressChanged += (_, e) =>
        {
            HeaderStatus = $"初始化中 {e.Progress}% · {e.Message}";
        };
        _bootstrapService.Completed += (_, ok) =>
        {
            HeaderStatus = ok ? "环境准备完成" : "环境准备失败";
        };
    }

    private void OnPropertyChanged([CallerMemberName] string? memberName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(memberName));
    }
}
