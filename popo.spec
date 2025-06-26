# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from app.config import APP_NAME, APP_VERSION

datas = [
    ('app/drivers', 'app/drivers'),
] + collect_data_files('fake_useragent')

a = Analysis(
    ['app/main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=2,
    version=APP_VERSION,
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
    version=APP_VERSION,
)
app = BUNDLE(
    exe,
    name=f'{APP_NAME}.app',
    icon='app/resources/icon.icns',
    bundle_identifier='com.its-newid.popo.mac.intel',
    info_plist={
        'CFBundleName': APP_NAME,
        'CFBundleShortVersionString': APP_VERSION,
        'CFBundleVersion': APP_VERSION, 
        'NSHighResolutionCapable': 'True',
        'NSDocumentsFolderUsageDescription': 'This app needs access to your Documents folder to save or read files.',
        'NSDownloadsFolderUsageDescription': 'This app needs access to your Downloads folder.',
        'NSDesktopFolderUsageDescription': 'This app needs access to your Desktop folder.'
    },
)
