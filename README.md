# Requirements

- Python 3.12
- MacOS 12 Monteray or later
- Chrome Browser v137

# Usage

## environment setting

```bash
pip install -r requirements.txt
```

## Download Chrome Driver if need

If you use other Chrome Browser version or other OS, download the Chrome Driver from the link below:<br>

https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json

## Create executable file with PyInstaller

```bash
cd ${project_root_directory}
pyinstaller --clean popo.spec
```

## Distribute

1. Create `.zip` file

   ```bash
   cd dist
   zip -r PoPo.zip PoPo.app
   ```
2. Create `.dmg` file

   ```bash
   cd ${project_root_directory}
   create-dmg \
     --volname "PoPo" \
     --background "app/resources/dmg_background_right.png" \
     --window-pos 200 120 \
     --window-size 530 300 \
     --icon-size 100 \
     --icon "PoPo.app" 100 150 \
     --icon "Applications" 400 150 \
     --hide-extension "PoPo.app" \
     --app-drop-link 400 150 \
     "PoPo.dmg" \
     "dist/PoPo.app"
   ```
