# Build & Release Guide

## 1) Build desktop app exe

```powershell
dotnet publish .\desktop_app\AQDeskShell\AQDeskShell.csproj `
  -c Release `
  -r win-x64 `
  --self-contained true `
  -p:PublishSingleFile=true `
  -p:IncludeNativeLibrariesForSelfExtract=true `
  -o .\desktop_app\publish\win-x64
```

## 2) Build data bundle zip (separate download)

```powershell
python .\tools\build_data_bundle.py `
  --main-csv "C:\path\combined_air_quality_data.csv" `
  --hourly-root "D:\path\daily_csv_root" `
  --out-dir ".\release_data" `
  --version "2026.04.16"
```

Upload `release_data\data_bundle_<version>.zip` to your release page/cloud link.

## 3) Prepare installer payload

```powershell
python .\tools\prepare_setup_payload.py `
  --root . `
  --out .\dist\setup_payload `
  --publish-dir desktop_app/publish/win-x64
```

## 4) Build Setup.exe (Inno Setup)

Open `installer\DDA3003PROJ.iss` with Inno Setup Compiler and build.

Output:
- `dist\installer\DDA3003PROJ_Setup.exe`

## 5) End-user flow

1. Install `DDA3003PROJ_Setup.exe`
2. Download `data_bundle_<version>.zip`
3. Unzip so data lives under install folder `data\`
4. Start app, click `Check Data`, then `Open Map Workbench`

