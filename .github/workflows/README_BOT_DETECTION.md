# GitHub Actions: Bot Detection & Fork-PR Support

## Übersicht

Alle Workflows wurden angepasst für:
✅ **Fork-PR Support** - Workflows funktionieren jetzt auch bei PRs von Forks
✅ **Bot-Erkennung** - Automatisches Überspringen von Bot-PRs (Renovate, Dependabot, etc.)

## Wichtige Änderungen

### 1. Von `pull_request` zu `pull_request_target`

**Vorher:**
```yaml
on:
  pull_request:
    types: [opened]
```

**Nachher:**
```yaml
on:
  pull_request_target:
    types: [opened]
```

**Warum?**
- ✅ `pull_request_target` hat Write-Permissions auch bei Fork-PRs
- ✅ Läuft im Kontext des Base-Repos (sicher)
- ✅ Kann Labels/Kommentare auf Fork-PRs setzen

**Sicherheit:**
- ⚠️ **WICHTIG**: Kein Checkout von PR-Code bei `pull_request_target`!
- ✅ Nur API-Calls (github-script) sind sicher
- ✅ Wir nutzen `github.rest.pulls.listFiles()` statt Code-Checkout

### 2. Bot-Erkennung

**Implementierung:**
```yaml
if: |
  github.actor != 'renovate[bot]' &&
  github.actor != 'dependabot[bot]' &&
  !contains(github.actor, '[bot]')
```

**Erkannte Bots:**
- `renovate[bot]` - Renovate Bot
- `dependabot[bot]` - GitHub Dependabot
- `*[bot]` - Alle anderen Bots (z.B. `github-actions[bot]`)

**Warum Bots überspringen?**
1. 🤖 Bots brauchen keine Willkommensnachrichten
2. 📦 Dependency-Updates brauchen keine Issue-Links
3. 🔧 Automatische PRs brauchen keine Size-Labels
4. ⚡ Reduziert unnötigen Workflow-Lauf

## Angepasste Workflows

### ✅ auto-label.yml
- Event: `pull_request_target` (statt `pull_request`)
- Bot-Check: ✅
- Fork-Support: ✅
- Permissions: `issues: write`, `pull-requests: write`

### ✅ auto-link-issues.yml
- Event: `pull_request_target` (statt `pull_request`)
- Bot-Check: ✅
- Fork-Support: ✅
- Permissions: `pull-requests: write`, `issues: write`

### ✅ pr-size-labeler.yml
- Event: `pull_request_target` (statt `pull_request`)
- Bot-Check: ✅
- Fork-Support: ✅
- Permissions: `pull-requests: write`, `issues: write`
- **Fix**: Nutzt `github.rest.pulls.listFiles()` API statt Checkout

### ✅ auto-assign-area-labels.yml
- Event: `pull_request_target` (statt `pull_request`)
- Bot-Check: ✅
- Fork-Support: ✅
- **WICHTIG**: Checkout entfernt (Sicherheit bei `pull_request_target`)
- Nutzt nur GitHub API für Datei-Analyse

### ✅ check-pr-target-branch.yml
- Event: Bereits `pull_request_target` ✅
- Bot-Check: ✅ NEU
- Fork-Support: ✅
- Maintainer-Check: ✅

### ✅ welcome.yml
- Event: Bereits `pull_request_target` ✅
- Bot-Check: ✅ NEU
- Fork-Support: ✅

## Testfälle

### Test 1: Fork-PR von echtem User
```
Actor: external-contributor
Source: fork
Erwartung: ✅ Alle Workflows laufen normal
```

### Test 2: Fork-PR von Renovate Bot
```
Actor: renovate[bot]
Source: fork (oder eigenes Repo)
Erwartung: ✅ Workflows werden übersprungen
Log: "Skipping workflow for bot account"
```

### Test 3: Fork-PR von Dependabot
```
Actor: dependabot[bot]
Source: fork
Erwartung: ✅ Workflows werden übersprungen
```

### Test 4: Eigener PR von User
```
Actor: normal-user
Source: eigenes Repo
Erwartung: ✅ Alle Workflows laufen normal
```

## Sicherheits-Best Practices

### ✅ DO's:
- Nutze `pull_request_target` für Fork-PR Support
- Nutze nur GitHub API (`github-script`)
- Validiere Input von PR-Metadaten
- Dokumentiere Sicherheitsüberlegungen

### ❌ DON'Ts:
- **NIEMALS** PR-Code bei `pull_request_target` auschecken
- **NIEMALS** User-Input in Shell-Commands verwenden
- **NIEMALS** Secrets an PR-Context weitergeben
- **NIEMALS** `actions/checkout` ohne `ref` bei `pull_request_target`

## Betroffene Bot-Accounts (Beispiele)

Werden automatisch übersprungen:
- `renovate[bot]`
- `dependabot[bot]`
- `github-actions[bot]`
- `allcontributors[bot]`
- `semantic-release-bot`
- Jeder Account mit `[bot]` im Namen

## Migration Notes

### Für bestehende PRs:
- ✅ Keine Action nötig
- ✅ Workflows funktionieren ab sofort mit Forks
- ✅ Bot-PRs werden sauber übersprungen

### Für neue Workflows:
Verwende dieses Template:
```yaml
name: "My Workflow"

on:
  pull_request_target:  # Für Fork-Support!
    types: [opened]

jobs:
  my-job:
    runs-on: ubuntu-latest
    # Bot-Check hinzufügen
    if: |
      github.actor != 'renovate[bot]' &&
      github.actor != 'dependabot[bot]' &&
      !contains(github.actor, '[bot]')
    permissions:
      pull-requests: write
      issues: write

    steps:
      # NIEMALS checkout bei pull_request_target!
      # Nur github-script oder API-Calls
      - name: Do something
        uses: actions/github-script@v8
        with:
          script: |
            // Sicherer Code hier
```

## Monitoring

### Workflow läuft für Bots?
```yaml
# In jedem Job wird geloggt:
# "Skipping workflow for bot account: renovate[bot]"
```

### Workflow läuft nicht für echte User?
```yaml
# Prüfe ob User-Name "[bot]" enthält
# Prüfe ob explizite Bot-Namen korrekt sind
```

## Links

- [pull_request_target Event](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#pull_request_target)
- [Security Hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [GitHub API: pulls.listFiles](https://docs.github.com/en/rest/pulls/pulls#list-pull-requests-files)

## Changelog

**v2.0 - 2025-11-27**
- ✅ Alle Workflows unterstützen Fork-PRs
- ✅ Bot-Detection implementiert
- ✅ Sicherheits-Best-Practices angewendet
- ✅ Dokumentation erweitert

**v1.0 - Vorher**
- ❌ Fork-PRs funktionierten nicht (403 Fehler)
- ❌ Bots bekamen unnötige Kommentare/Labels
