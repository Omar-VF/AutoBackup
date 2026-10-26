; Inno Setup Script for Tethr
; Generates a professional Windows Setup Installer for Tethr Automated Billing Data Vault

#define MyAppName "Tethr"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Tethr"
#define MyAppExeName "Tethr.exe"
#define MyAppAssocName "Tethr Backup Archive"
#define MyAppAssocExt ".tethr"

[Setup]
; Unique AppId for upgrade detection
AppId={{8B490E7A-F70C-44E2-9E86-8E3A9C8D4B12}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
; Support per-user or administrative install seamlessly
PrivilegesRequiredOverridesAllowed=commandline dialog
PrivilegesRequired=lowest
CloseApplications=yes
RestartApplications=yes
OutputDir=dist\installer
OutputBaseFilename=Tethr-Setup
SetupIconFile=assets\tethr.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "autostart"; Description: "Launch Tethr automatically when Windows starts (System Tray)"; GroupDescription: "Startup Options:"

[Files]
Source: "dist\Tethr\*"; DestDir: "{app}"; Excludes: "*.json,*.log,*.tmp"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--minimized"; Tasks: autostart

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
