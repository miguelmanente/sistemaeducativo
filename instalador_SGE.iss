
; ============================================================
;                    INSTALADOR SGE
;             Sistema de Gestión Educativa
; ============================================================

#define MyAppName "SGE"
#define MyAppVersion "1.0.2"
#define MyAppPublisher "SGE"
#define MyAppExeName "SGE.exe"
#define MyAppDescription "Sistema de Gestión Educativa"

[Setup]

; ------------------------------------------------------------
; Información de la aplicación
; ------------------------------------------------------------

AppId={{SGE-SISTEMA-GESTION-EDUCATIVA}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppComments={#MyAppDescription}

; ------------------------------------------------------------
; Icono del instalador
; ------------------------------------------------------------

SetupIconFile=SGE.ico
UninstallDisplayIcon={app}\SGE.ico

; ------------------------------------------------------------
; Ubicación de instalación
; ------------------------------------------------------------

DefaultDirName={autopf}\SGE
DefaultGroupName=SGE

; ------------------------------------------------------------
; Salida del instalador
; ------------------------------------------------------------

OutputDir=instalador
OutputBaseFilename=Instalador_SGE_1.0.2

; ------------------------------------------------------------
; Compresión
; ------------------------------------------------------------

Compression=lzma
SolidCompression=yes

; ------------------------------------------------------------
; Privilegios
; ------------------------------------------------------------

PrivilegesRequired=admin

; ------------------------------------------------------------
; Arquitectura
; ------------------------------------------------------------

ArchitecturesInstallIn64BitMode=x64compatible

; ------------------------------------------------------------
; Apariencia
; ------------------------------------------------------------

WizardStyle=modern

; ------------------------------------------------------------
; Desinstalación
; ------------------------------------------------------------

UninstallDisplayName=SGE - Sistema de Gestión Educativa

; ============================================================
; ARCHIVOS DEL PROGRAMA
; ============================================================

[Files]

Source: "dist\SGE\*"; \
    DestDir: "{app}"; \
    Flags: ignoreversion recursesubdirs createallsubdirs

; ------------------------------------------------------------
; Licencia de SGE
; ------------------------------------------------------------

Source: "Licenciamiento\Licencia_SGE.lic"; \
    DestDir: "{app}"; \
    Flags: ignoreversion

; ------------------------------------------------------------
; Icono de SGE
; ------------------------------------------------------------

Source: "SGE.ico"; \
    DestDir: "{app}"; \
    Flags: ignoreversion

; ============================================================
; CARPETAS DE DATOS
; ============================================================

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

; ============================================================
; ACCESOS DIRECTOS
; ============================================================

[Icons]

Name: "{autodesktop}\SGE"; \
    Filename: "{app}\SGE.exe"; \
    WorkingDir: "{app}"; \
    IconFilename: "{app}\SGE.ico"

Name: "{group}\SGE"; \
    Filename: "{app}\SGE.exe"; \
    WorkingDir: "{app}"; \
    IconFilename: "{app}\SGE.ico"

Name: "{group}\Desinstalar SGE"; \
    Filename: "{uninstallexe}"

; ============================================================
; EJECUCIÓN AL FINAL DE LA INSTALACIÓN
; ============================================================

[Run]

Filename: "{app}\SGE.exe"; \
    Description: "Ejecutar SGE"; \
    Flags: nowait postinstall skipifsilent

