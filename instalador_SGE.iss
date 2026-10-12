
; ============================================================
; INSTALADOR SGE - Sistema de Gestión Educativa
; Distribución sin licencia preinstalada ni claves privadas
; ============================================================

#define MyAppName "SGE"
#define MyAppVersion "1.0.3"
#define MyAppPublisher "Manente Miguel Angel"
#define MyAppExeName "SGE.exe"
#define MyAppDescription "Sistema de Gestión Educativa"

[Setup]
AppId={{9BDDE23C-EE7E-4DC6-8065-24670A6AD351}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppComments={#MyAppDescription}
UninstallDisplayName=SGE - Sistema de Gestión Educativa

DefaultDirName={autopf}\SGE
DefaultGroupName=SGE
DisableProgramGroupPage=yes

SetupIconFile=SGE.ico
UninstallDisplayIcon={app}\SGE.exe
OutputDir=instalador
OutputBaseFilename=Instalador_SGE_1.0.3

Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
; Ejecutable y componentes de la versión probada
Source: "Distribucion_SGE\SGE\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Icono del programa
Source: "SGE.ico"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
; Carpetas compartidas para los datos de SGE
Name: "{commonappdata}\SGE"
Name: "{commonappdata}\SGE\Datos"
Name: "{commonappdata}\SGE\Seguridad"
Name: "{commonappdata}\SGE\Backups"
Name: "{commonappdata}\SGE\Logs"
Name: "{commonappdata}\SGE\Reportes"
Name: "{commonappdata}\SGE\Version"
Name: "{commonappdata}\SGE\Reportes\Profesores"
Name: "{commonappdata}\SGE\Reportes\Materias"
Name: "{commonappdata}\SGE\Reportes\Asignaciones"
Name: "{commonappdata}\SGE\Reportes\Inasistencias"
Name: "{commonappdata}\SGE\Reportes\Calendario"

[Icons]
Name: "{autodesktop}\SGE"; Filename: "{app}\SGE.exe"; WorkingDir: "{app}"; IconFilename: "{app}\SGE.ico"
Name: "{group}\SGE"; Filename: "{app}\SGE.exe"; WorkingDir: "{app}"; IconFilename: "{app}\SGE.ico"
Name: "{group}\Desinstalar SGE"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\SGE.exe"; Description: "Ejecutar SGE"; Flags: nowait postinstall skipifsilent
