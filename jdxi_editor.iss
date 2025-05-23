; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!
#define MyAppName "JDXI Editor"
#define MyAppVersion "0.0.5"
#define MyAppPublisher "Mark Brooks"
#define MyAppURL "https://www.github.com/"
#define MyAppExeName "jdxi_editor.exe"
#define MyAppAssocName MyAppName + " File"
#define MyAppAssocExt ".syx"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{BCD0DE8E-EA62-4A25-B7A1-46F861D7C4F4}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
;DefaultDirName={localappdata}\Programs\\-{#MyAppVersion}
; DefaultDirName=C:\Evotec\
DefaultDirName={localappdata}\Programs\jdxi_editor
ChangesAssociations=yes
DisableProgramGroupPage=yes
; Remove the following line to run in administrative install mode (install for all users.)
PrivilegesRequired=lowest
;OutputDir=C:\Users\MBrooks\
; OutputDir=C:\Users\MBrooks\
OutputBaseFilename=jdxi_editor-0.0.5_setup_win_x86-64
OutputDir=C:\Users\MBrooks\jdxi
;SetupIconFile=C:\Users\MBrooks\projects\\designer\icons\.ico
SetupIconFile=resources\jdxi_icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
WizardImageFile=resources\jdxi_cartoon_600.bmp
;WizardSmallImageFile=jdxi_editor_Setup_55x55.bmp,jdxi_editor_Setup_64x68.bmp,jdxi_editor_Setup_92x97.bmp,jdxi_editor_Setup_92x97.bmp,jdxi_editor_Setup_92x97.bmp,jdxi_editor_Setup_110x106.bmp,jdxi_editor_Setup_119x123.bmp,jdxi_editor_Setup_138x140.bmp

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
;Source: "C:\Users\MBrooks\projects\jdxi_editor\dist\\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\\jdxi_editor\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
;Source: "C:\Users\MBrooks\projects\\dist\\jdxi_editor\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\\jdxi_editor\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files


[Registry]
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocKey}"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".myp"; ValueData: ""

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent


