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
        ('Licenciamiento/claves/clave_publica.pem', 'claves'),
    ],
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

pyz = PYZ(
    a.pure
)

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

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name='SGE',
)