using System.IO;
using System.Text.RegularExpressions;

namespace AQDeskShell.Services;

public record DataBundleStatus(
    bool MainCsvOk,
    bool HourlyOk,
    string DataDir,
    int HourlyCsvCount,
    string Message
);

public class DataBundleService
{
    private static readonly Regex DailyToken = new(@"\d{8}", RegexOptions.Compiled);

    public DataBundleStatus Check(string projectRoot)
    {
        var root = new DirectoryInfo(projectRoot);
        var dataDir = Path.Combine(root.FullName, "data");
        if (!Directory.Exists(dataDir))
        {
            var sibling = Path.Combine(root.Parent?.FullName ?? root.FullName, "data");
            if (Directory.Exists(sibling)) dataDir = sibling;
        }

        var mainCsv = Path.Combine(dataDir, "combined_air_quality_data.csv");
        var mainOk = File.Exists(mainCsv);
        var hourlyRoot = Path.Combine(dataDir, "hourly");
        if (!Directory.Exists(hourlyRoot)) hourlyRoot = dataDir;

        var count = 0;
        if (Directory.Exists(hourlyRoot))
        {
            count = Directory.GetFiles(hourlyRoot, "*.csv", SearchOption.AllDirectories)
                .Count(fp => DailyToken.IsMatch(Path.GetFileNameWithoutExtension(fp)));
        }
        var hourlyOk = count > 0;
        var msg = mainOk && hourlyOk
            ? $"Data ready: main csv + {count} daily csv files"
            : $"Data missing. Need data/combined_air_quality_data.csv and daily csv under data/hourly";
        return new DataBundleStatus(mainOk, hourlyOk, dataDir, count, msg);
    }
}

