# AQDeskShell (Phase A)

Desktop shell prototype for this project:

- Home page: intro + report preview + environment bootstrap button
- Workbench page: embedded WebView2
- Global settings dialog (gear): environment, AI settings placeholder, health check, logs

## Build

```powershell
cd desktop_app\AQDeskShell
dotnet restore
dotnet build -c Debug
```

## Run

```powershell
dotnet run --project .\desktop_app\AQDeskShell\AQDeskShell.csproj
```

## Notes

- This is Phase A skeleton.
- Runtime bootstrap is delegated to existing `bootstrap_env.ps1`.
- Next phase will replace placeholder AI settings controls with real config persistence + provider check wiring.
- Data resolution now supports packaged bundle and external fallbacks:
  - main CSV: env/internal bundle/runtime sibling data/repo
  - heatmap daily CSV root: env/internal bundle/runtime sibling data/main-csv sibling/repo
  - optional emergency fallback can be provided via:
    - `APP_FALLBACK_MAIN_CSV`
    - `APP_FALLBACK_HEATMAP_ROOT`
