#define MyAppName "Lithos"
#define MyAppVersion "1.0.2"
#define MyAppPublisher "Rıdvan Can PARMAK"
#define MyAppExeName "Lithos_v1_0_2.exe"

[Setup]
AppId={{24BBCEAD-4B72-4D0D-B58F-9C7F22EAA342}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} v{#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\Lithos
DefaultGroupName=Lithos
DisableProgramGroupPage=yes
OutputDir={#SourcePath}dist
OutputBaseFilename=Lithos_v1.0.2_Setup
SetupIconFile={#SourcePath}assets\lithos_v102.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\assets\lithos_v102.ico

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "{#SourcePath}assets\lithos_v102.ico"; DestDir: "{app}\assets"; Flags: ignoreversion
Source: "{#SourcePath}dist\Lithos_v1_0_2\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[InstallDelete]
; Remove ONLY old entry point; never delete user database files.
Type: files; Name: "{app}\Lithos.exe"

[Icons]
Name: "{group}\Lithos"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\lithos_v102.ico"
Name: "{autodesktop}\Lithos"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\lithos_v102.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Lithos"; Flags: nowait postinstall skipifsilent
