# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app/main.py'],
    pathex=['.'],
    binaries=[],
    datas=[('app/drivers', 'app/drivers')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PoPo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
app = BUNDLE(
    exe,
    name='PoPo.app',
    icon='app/resources/icon.icns',
    bundle_identifier='com.its-newid.popo.mac.intel',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'NSDocumentsFolderUsageDescription': 'This app needs access to your Documents folder to save or read files.',
        'NSDownloadsFolderUsageDescription': 'This app needs access to your Downloads folder.',
        'NSDesktopFolderUsageDescription': 'This app needs access to your Desktop folder.'
    },
)
