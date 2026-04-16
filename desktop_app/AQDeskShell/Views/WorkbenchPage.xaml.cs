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
    private string _workbenchStatus = "未启动";

    public event PropertyChangedEventHandler? PropertyChanged;

    public string WorkbenchStatus
    {
        get => _workbenchStatus;
        set
        {
            if (_workbenchStatus == value) return;
            _workbenchStatus = value;
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(nameof(WorkbenchStatus)));
        }
    }

    public WorkbenchPage(ShellState state)
    {
        InitializeComponent();
        _state = state;
        DataContext = this;
        Loaded += WorkbenchPage_Loaded;
    }

    private async void WorkbenchPage_Loaded(object sender, RoutedEventArgs e)
    {
        await MapWebView.EnsureCoreWebView2Async();
        TryOpenMapPage();
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
            WorkbenchStatus = "地图已加载";
            return;
        }
        MapWebView.Source = new Uri("http://127.0.0.1:8790/health");
        WorkbenchStatus = "未找到地图文件，当前显示服务状态页";
    }

    private async void StartAll_OnClick(object sender, RoutedEventArgs e)
    {
        WorkbenchStatus = "正在启动服务...";
        var code = await _state.Process.StartAllAsync();
        WorkbenchStatus = code == 0 ? "服务启动完成" : $"服务启动失败，退出码 {code}";
        if (code == 0)
        {
            TryOpenMapPage();
        }
    }

    private void BackHome_OnClick(object sender, RoutedEventArgs e)
    {
        NavigationService?.Navigate(new HomePage(_state));
    }
}
