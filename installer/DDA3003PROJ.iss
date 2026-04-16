; Inno Setup script for DDA3003PROJ desktop app
; Build payload first:
;   dotnet publish .\desktop_app\AQDeskShell\AQDeskShell.csproj -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -o .\desktop_app\publish\win-x64
;   python .\tools\prepare_setup_payload.py --root . --out .\dist\setup_payload --publish-dir desktop_app/publish/win-x64

#define MyAppName "DDA3003PROJ Air Quality Platform"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "DDA3003PROJ Team"
#define MyAppExeName "AQDeskShell.exe"
#define PayloadRoot "..\dist\setup_payload"

[Setup]
AppId={{5C9810D2-90DD-4B17-AF80-3EB20690BF6D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\DDA3003PROJ
DefaultGroupName=DDA3003PROJ
DisableProgramGroupPage=yes
OutputDir=..\dist\installer
OutputBaseFilename=DDA3003PROJ_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional tasks:"

[Files]
Source: "{#PayloadRoot}\app\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#PayloadRoot}\runtime\*"; DestDir: "{app}\runtime"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#PayloadRoot}\data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\DDA3003PROJ"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\DDA3003PROJ"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch DDA3003PROJ"; Flags: nowait postinstall skipifsilent


