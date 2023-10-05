#!/bin/bash

# Prüfe, ob die erforderlichen Parameter übergeben wurden
if [ $# -ne 4 ]; then
  echo "Verwendung: $0 <nextRelease.version> <branch.name> <commits.length> <Date.now()>"
  exit 1
fi

# Die Parameter in lesbare Variablen speichern
nextReleaseVersion="$1"
branchName="$2"
commitsLength="$3"
timestamp="$4"

# Befehl ausführen, um das ZIP-Archiv zu erstellen
zipCommand="zip dist/spoolman-homeassistant_${nextReleaseVersion}.zip custom_components/spoolman -j"
echo "Führe folgenden Befehl aus: $zipCommand"
$zipCommand

# JSON-Datei bearbeiten
jsonFile="hacs.json"

# Überprüfen, ob die JSON-Datei existiert
if [ -f "$jsonFile" ]; then
  # JSON-Datei parsen und 'filename' aktualisieren
  jq ".filename = \"spoolman-homeassistant_${nextReleaseVersion}.zip\"" "$jsonFile" > temp.json
  mv temp.json "$jsonFile"
  echo "Die Eigenschaft 'filename' in '$jsonFile' wurde auf 'spoolman-homeassistant_${nextReleaseVersion}.zip' aktualisiert."
else
  echo "Die Datei '$jsonFile' wurde nicht gefunden."
fi

# Optional: Ausgabe der Parameterwerte zur Bestätigung
echo "nextRelease.version: $nextReleaseVersion"
echo "branch.name: $branchName"
echo "commits.length: $commitsLength"
echo "Date.now(): $timestamp"
