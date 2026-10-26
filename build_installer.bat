@echo off
echo ========================================================
echo   Building Tethr Windows Executable and Setup Installer
echo ========================================================

cd /d "%~dp0"

echo [1/3] Generating multi-resolution application icon...
python -c "from PIL import Image; im = Image.open('assets/tethr_icon.png').convert('RGBA'); im.save('assets/tethr.ico', format='ICO', sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])"

echo [2/3] Compiling Tethr binary bundle with PyInstaller...
pyinstaller tethr.spec --noconfirm

echo [3/3] Building Setup Installer with Inno Setup...
if exist "C:\Users\omarv\AppData\Local\Programs\Inno Setup 6\ISCC.exe" (
    "C:\Users\omarv\AppData\Local\Programs\Inno Setup 6\ISCC.exe" installer.iss
) else (
    ISCC.exe installer.iss
)

echo ========================================================
echo   Build Complete!
echo   Installer created at: dist\installer\Tethr-Setup.exe
echo ========================================================
pause
