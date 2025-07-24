@echo off
setlocal enabledelayedexpansion

:: Setze das Basisverzeichnis
cd /d "%~dp0"

:: Definiere Quell- und Zielverzeichnis
set "source_dir=Z:\AI\projects\music\ace-data_tool\tools\convert_tools\inputs"
set "dest_dir=Z:\AI\projects\music\ace-data_tool\tools\convert_tools\outputs"

:: Zähle alle WAV-Dateien
echo Zähle WAV-Dateien...
set "total_files=0"
for /R "%source_dir%" %%i in (*.wav) do set /a total_files+=1

if %total_files% equ 0 (
    echo Keine WAV-Dateien gefunden in %source_dir%
    pause
    exit /b
)

echo Insgesamt zu konvertieren: %total_files% Dateien
echo.

:: Erstelle Ausgabeverzeichnis
mkdir "%dest_dir%" 2>nul

:: Initialisiere Zähler
set "processed_files=0"
set "success_count=0"
set "error_count=0"

echo Starte Konvertierung...
echo ========================================

:: Durchsuche rekursiv alle Unterordner nach WAV-Dateien
for /R "%source_dir%" %%i in (*.wav) do (
    :: Berechne relativen Pfad vom Quellverzeichnis
    set "fullpath=%%i"
    call set "relpath=%%fullpath:%source_dir%\=%%"
    
    :: Erstelle Zielordnerstruktur
    set "destfolder=%dest_dir%\!relpath!"
    :: Entferne Dateinamen vom Pfad
    for %%j in ("!destfolder!") do set "destfolder_dir=%%~dpj"
    mkdir "!destfolder_dir!" 2>nul
    
    :: Konvertiere Datei
    echo Konvertiere: !relpath!
    ffmpeg -i "%%i" -vn -ar 44100 -ac 2 -ab 320k -f mp3 "%dest_dir%\!relpath:~0,-4!.mp3" -y >nul 2>&1
    
    :: Prüfe ob Konvertierung erfolgreich war
    if !errorlevel! equ 0 (
        set /a success_count+=1
        echo [ERFOLG] !relpath!
    ) else (
        set /a error_count+=1
        echo [FEHLER] !relpath!
    )
    
    :: Aktualisiere Fortschritt
    set /a processed_files+=1
    set /a progress_percent=!processed_files! * 100 / %total_files%
    
    :: Zeige Fortschrittsbalken
    set "progress_bar="
    set /a progress_bars=!progress_percent! / 2
    for /l %%k in (1,1,!progress_bars!) do set "progress_bar=!progress_bar!█"
    for /l %%k in (!progress_bars!,1,50) do set "progress_bar=!progress_bar!░"
    
    echo [%progress_bar%] !progress_percent!%%
    echo.
)

echo ========================================
echo KONVERTIERUNG ABGESCHLOSSEN!
echo ========================================
echo Erfolgreich konvertiert: %success_count% Dateien
echo Fehlerhaft: %error_count% Dateien
echo Gesamt: %total_files% Dateien
echo.
echo Ausgabeverzeichnis: %dest_dir%
echo ========================================

pause