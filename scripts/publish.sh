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

# manifest.json mit der Release-Version stempeln. Muss VOR dem Zippen
# passieren, damit das ausgelieferte Zip die korrekte Version enthält
# (Home Assistant zeigt die 'version' aus der manifest.json an).
manifestFile="custom_components/spoolman/manifest.json"
if [ -f "$manifestFile" ]; then
  jq ".version = \"${nextReleaseVersion}\"" "$manifestFile" > manifest.tmp.json
  mv manifest.tmp.json "$manifestFile"
  echo "Die Eigenschaft 'version' in '$manifestFile' wurde auf '${nextReleaseVersion}' gesetzt."
else
  echo "Die Datei '$manifestFile' wurde nicht gefunden."
fi

# Befehl ausführen, um das ZIP-Archiv zu erstellen
zipCommand="zip ../../dist/spoolman-homeassistant_${nextReleaseVersion}.zip . -r"
echo "Führe folgenden Befehl aus: $zipCommand"

mkdir ./dist/

(cd ./custom_components/spoolman && ls -la && $zipCommand)

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
