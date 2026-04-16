using AQDeskShell.Services;
using AQDeskShell.ViewModels;
using AQDeskShell.Views;
using System.IO;
using System.Windows;

namespace AQDeskShell;

public partial class MainWindow : Window
{
    private readonly ShellState _state;

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
