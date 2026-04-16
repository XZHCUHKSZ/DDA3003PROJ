using System.IO;
using System.IO.Compression;
using System.Net.Http;
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
    public const string DataBundleUrl = "https://github.com/XZHCUHKSZ/DDA3003PROJ/releases/download/data-v2026.04.16/data_bundle_2026.04.16.zip";
    public const string OnlineGuideUrl = "https://github.com/XZHCUHKSZ/DDA3003PROJ/blob/main/PRODUCT_PACKAGING_CHECKLIST.md";

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

        var mainCsv = FindCombinedCsv(dataDir);
        var mainOk = !string.IsNullOrWhiteSpace(mainCsv);
        var hourlyRoot = FindDailyRoot(dataDir) ?? dataDir;

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

    private static string? FindCombinedCsv(string root)
    {
        if (!Directory.Exists(root)) return null;
        var direct = Path.Combine(root, "combined_air_quality_data.csv");
        if (File.Exists(direct)) return direct;
        return Directory.GetFiles(root, "combined_air_quality_data.csv", SearchOption.AllDirectories)
            .OrderBy(p => p.Length)
            .FirstOrDefault();
    }

    private static string? FindDailyRoot(string root)
    {
        if (!Directory.Exists(root)) return null;
        var candidates = new[]
        {
            Path.Combine(root, "hourly"),
            Path.Combine(root, "data", "hourly"),
            Path.Combine(root, "hourly", "data"),
            Path.Combine(root, "data", "hourly", "data"),
        };
        foreach (var c in candidates)
        {
            if (CountDailyCsv(c) > 0) return c;
        }

        var dirs = Directory.GetDirectories(root, "*", SearchOption.AllDirectories).Prepend(root);
        string? best = null;
        var bestCount = 0;
        foreach (var d in dirs)
        {
            var c = CountDailyCsv(d);
            if (c > bestCount)
            {
                bestCount = c;
                best = d;
            }
        }
        return bestCount > 0 ? best : null;
    }

    private static int CountDailyCsv(string root)
    {
        if (!Directory.Exists(root)) return 0;
        return Directory.GetFiles(root, "*.csv", SearchOption.AllDirectories)
            .Count(fp => DailyToken.IsMatch(Path.GetFileNameWithoutExtension(fp)));
    }

    public async Task<string> DownloadAndExtractAsync(string projectRoot, IProgress<int>? progress = null, CancellationToken cancellationToken = default)
    {
        var status = Check(projectRoot);
        Directory.CreateDirectory(status.DataDir);

        var zipPath = Path.Combine(status.DataDir, "data_bundle.zip");
        using var http = new HttpClient { Timeout = TimeSpan.FromMinutes(30) };
        using var response = await http.GetAsync(DataBundleUrl, HttpCompletionOption.ResponseHeadersRead, cancellationToken);
        response.EnsureSuccessStatusCode();

        var total = response.Content.Headers.ContentLength ?? -1L;
        await using (var input = await response.Content.ReadAsStreamAsync(cancellationToken))
        await using (var output = File.Create(zipPath))
        {
            var buffer = new byte[1024 * 128];
            long readTotal = 0;
            int read;
            while ((read = await input.ReadAsync(buffer, 0, buffer.Length, cancellationToken)) > 0)
            {
                await output.WriteAsync(buffer.AsMemory(0, read), cancellationToken);
                readTotal += read;
                if (total > 0 && progress != null)
                {
                    var p = (int)Math.Clamp(readTotal * 85 / total, 0, 85);
                    progress.Report(p);
                }
            }
        }

        var extractDir = status.DataDir;
        ZipFile.ExtractToDirectory(zipPath, extractDir, overwriteFiles: true);
        progress?.Report(100);
        return extractDir;
    }
}
