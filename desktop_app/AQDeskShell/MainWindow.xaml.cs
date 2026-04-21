using AQDeskShell.Services;
using AQDeskShell.ViewModels;
using AQDeskShell.Views;
using System.IO;
using System.Windows;

namespace AQDeskShell;

public partial class MainWindow : Window
{
    private readonly ShellState _state;
    private bool _immersiveMapMode;
    private WindowStyle _prevWindowStyle;
    private ResizeMode _prevResizeMode;
    private WindowState _prevWindowState;
    private bool _prevTopmost;

    public MainWindow()
    {
        InitializeComponent();
        var projectRoot = ResolveProjectRoot();
        _state = new ShellState(projectRoot);
        DataContext = _state;
        MainFrame.Navigate(new HomePage(_state));
    }

    private void OpenSettings_OnClick(object sender, RoutedEventArgs e)
    {
        var dialog = new SettingsDialog(_state)
        {
            Owner = this
        };
        dialog.ShowDialog();
    }

    public void SetMapImmersiveMode(bool enabled)
    {
        if (enabled == _immersiveMapMode) return;

        if (enabled)
        {
            _prevWindowStyle = WindowStyle;
            _prevResizeMode = ResizeMode;
            _prevWindowState = WindowState;
            _prevTopmost = Topmost;

            HeaderBar.Visibility = Visibility.Collapsed;
            HeaderRow.Height = new GridLength(0);
            WindowStyle = WindowStyle.None;
            ResizeMode = ResizeMode.NoResize;
            WindowState = WindowState.Maximized;
            Topmost = false;
            _immersiveMapMode = true;
            return;
        }

        HeaderBar.Visibility = Visibility.Visible;
        HeaderRow.Height = new GridLength(58);
        WindowStyle = _prevWindowStyle;
        ResizeMode = _prevResizeMode;
        WindowState = _prevWindowState;
        Topmost = _prevTopmost;
        _immersiveMapMode = false;
    }

    private static string ResolveProjectRoot()
    {
        var baseDir = AppDomain.CurrentDomain.BaseDirectory;
        var runtimeDir = Path.Combine(baseDir, "runtime");
        if (File.Exists(Path.Combine(runtimeDir, "main.py")))
        {
            return runtimeDir;
        }
        var dir = new DirectoryInfo(baseDir);
        while (dir != null && !File.Exists(Path.Combine(dir.FullName, "main.py")))
        {
            dir = dir.Parent;
        }
        return dir?.FullName ?? baseDir;
    }
}
