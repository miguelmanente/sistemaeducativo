; ============================================================
;                    INSTALADOR SGE PROTEGIDO
;             Sistema de Gestión Educativa
; ============================================================

#define MyAppName "SGE"
#define MyAppVersion "1.0.3"
#define MyAppPublisher "SGE"
#define MyAppExeName "SGE.exe"
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
OutputBaseFilename=Instalador_SGE_1.0.3
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
UninstallDisplayName=SGE - Sistema de Gestión Educativa

[Files]
; Ejecutable SGE reconstruido desde inicio_protegido.py.
Source: "dist_protegido\SGE\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Activación sin clave privada: genera solicitudes e importa licencias.
Source: "dist_protegido\ActivacionSGE.exe"; DestDir: "{app}"; Flags: ignoreversion

Source: "SGE.ico"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
; La escuela necesita guardar la licencia en ProgramData sin escribir en Program Files.
Name: "{commonappdata}\SGE"; Permissions: users-modify
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
Name: "{group}\Activar SGE"; Filename: "{app}\ActivacionSGE.exe"; WorkingDir: "{app}"; IconFilename: "{app}\SGE.ico"
Name: "{group}\Desinstalar SGE"; Filename: "{uninstallexe}"

[Run]
; Después de instalar, abrir activación. La escuela genera la solicitud y recibe luego su licencia.
Filename: "{app}\ActivacionSGE.exe"; Description: "Activar SGE"; Flags: nowait postinstall skipifsilent
