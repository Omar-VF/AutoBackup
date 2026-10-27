; Inno Setup Script for Tethr
; Generates a professional Windows Setup Installer for Tethr Automated Billing Data Vault

#define MyAppName "Tethr"
#ifndef MyAppVersion
#define MyAppVersion "1.0.0"
#endif
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

[Registry]
; Clean up Windows startup registry entries upon uninstall
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueName: "{#MyAppName}"; Flags: uninsdeletevalue
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueName: "{#MyAppName}"; Flags: uninsdeletevalue; Check: IsAdminInstallMode

[UninstallDelete]
; Delete all files and subdirectories created during app execution in {app}
Type: filesandordirs; Name: "{app}"
; Delete application configuration, backup history, and logs in %APPDATA%\Tethr
Type: filesandordirs; Name: "{userappdata}\{#MyAppName}"
; Delete any temporary updater or cache files in %LOCALAPPDATA%\Tethr
Type: filesandordirs; Name: "{localappdata}\{#MyAppName}"
Type: files; Name: "{localappdata}\Temp\Tethr-Setup*.exe"
Type: files; Name: "{autodesktop}\{#MyAppName}.lnk"
Type: files; Name: "{userstartup}\{#MyAppName}.lnk"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall

[Code]
// Helper procedure to terminate running instances of Tethr
procedure KillRunningApp();
var
  ResultCode: Integer;
begin
  // Terminate Tethr.exe if currently running to release file locks
  Exec('taskkill.exe', '/F /IM {#MyAppExeName}', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Sleep(500);
end;

function InitializeSetup(): Boolean;
begin
  KillRunningApp();
  Result := True;
end;

function InitializeUninstall(): Boolean;
begin
  KillRunningApp();
  Result := True;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // Guarantee complete removal of app installation folder
    if DirExists(ExpandConstant('{app}')) then
      DelTree(ExpandConstant('{app}'), True, True, True);

    // Guarantee complete removal of user data folder in %APPDATA%\Tethr
    if DirExists(ExpandConstant('{userappdata}\{#MyAppName}')) then
      DelTree(ExpandConstant('{userappdata}\{#MyAppName}'), True, True, True);
  end;
end;
