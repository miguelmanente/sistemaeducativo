```python
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['index.py'],

    pathex=[],

    binaries=[],

    datas=[
        ('manual', 'manual'),

        ('logo.png', '.'),

        ('logo2.png', '.'),

        ('logos.png', '.'),

        ('logotipo.png', '.'),

        # =================================================
        # CLAVE PÚBLICA UTILIZADA PARA VERIFICAR LICENCIAS
        # =================================================
        #
        # La clave privada NUNCA se incluye en el SGE.
        #
        ('Licenciamiento/claves/clave_publica.pem', 'claves'),
    ],

    # =====================================================
    #                MÓDULOS OCULTOS
    # =====================================================

    hiddenimports=[
        'cryptography',
        'cryptography.hazmat',
        'cryptography.hazmat.primitives',
        'cryptography.hazmat.primitives.serialization',
        'cryptography.hazmat.primitives.asymmetric',
        'cryptography.hazmat.primitives.asymmetric.ed25519',
    ],

    hookspath=[],

    hooksconfig={},

    runtime_hooks=[],

    excludes=[],

    noarchive=False,

    optimize=0,
)


# =========================================================
#                         PYZ
# =========================================================

pyz = PYZ(
    a.pure
)


# =========================================================
#                         EXE
# =========================================================

exe = EXE(
    pyz,

    a.scripts,

    [],

    exclude_binaries=True,

    name='SGE',

    debug=False,

    bootloader_ignore_signals=False,

    strip=False,

    upx=True,

    console=False,

    disable_windowed_traceback=False,

    argv_emulation=False,

    target_arch=None,

    codesign_identity=None,

    entitlements_file=None,
)


# =========================================================
#                       COLLECT
# =========================================================

coll = COLLECT(
    exe,

    a.binaries,

    a.datas,

    strip=False,

    upx=True,

    name='SGE',
)
```

### 🔐 ¿Qué queda ahora?

Tu compilación conserva:

```text
manual\
logo.png
logo2.png
logos.png
logotipo.png
```

y agrega correctamente:

```text
claves\
└── clave_publica.pem
```

La estructura esperada después de compilar será aproximadamente:

```text
dist\
└── SGE\
    ├── SGE.exe
    └── _internal\
        ├── claves\
        │   └── clave_publica.pem
        │
        ├── manual\
        ├── ...
        └── ...
```

Y **no se incluye**:

```text
clave_privada.pem
```

Eso es fundamental para la seguridad del sistema.

### Pero antes de compilar

Yo haría primero una prueba en desarrollo con la nueva `licencia.py`.

Desde:

```text
Sistema Académico\Licenciamiento
```

podés ejecutar:

```text
python licencia.py
```

Si todo está correcto, debería terminar mostrando:

```text
LICENCIA VÁLIDA ✅
```

y además:

```text
Huella del equipo : C6E54137649EFD300C27C7D8655208ECF99BEA6A97ED761881088848CD5D1429
```

**No compiles todavía.** Primero comprobemos que `licencia.py` valida correctamente la nueva licencia con la huella. Después hacemos la prueba más importante: **modificar artificialmente la huella para comprobar que la licencia es rechazada**, y recién después compilamos el SGE.


