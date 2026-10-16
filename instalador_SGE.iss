; ============================================================
; INSTALADOR SGE - ACTIVACIÓN OFFLINE POR EL TÉCNICO
; No distribuye la clave privada ni una licencia fija de otra PC.
; ============================================================

#define MyAppName "SGE"
#define MyAppVersion "1.0.4"
#define MyAppPublisher "SGE"
#define MyAppDescription "Sistema de Gestión Educativa"

[Setup]
AppId={{SGE-SISTEMA-GESTION-EDUCATIVA}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppComments={#MyAppDescription}
SetupIconFile=SGE.ico
UninstallDisplayIcon={app}\SGE.ico
DefaultDirName={autopf}\SGE
DefaultGroupName=SGE
OutputDir=instalador
OutputBaseFilename=Instalador_SGE_1.0.4
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
UninstallDisplayName=SGE - Sistema de Gestión Educativa

[Files]
; Distribución del SGE que ya fue compilada y probada.
Source: "Distribucion_SGE\SGE\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Activación offline: crea solicitud e importa licencia firmada.
; Esta aplicación NO contiene la clave privada.
Source: "dist_activacion\ActivacionSGE.exe"; DestDir: "{app}"; Flags: ignoreversion

Source: "SGE.ico"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
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
Name: "{group}\Activación SGE"; Filename: "{app}\ActivacionSGE.exe"; WorkingDir: "{app}"; IconFilename: "{app}\SGE.ico"
Name: "{group}\Desinstalar SGE"; Filename: "{uninstallexe}"

[Run]
; No abrir SGE hasta que haya una licencia válida.
; El técnico prepara la solicitud y luego importa la licencia emitida.
Filename: "{app}\ActivacionSGE.exe"; Description: "Preparar activación de SGE"; Flags: nowait postinstall skipifsilent


