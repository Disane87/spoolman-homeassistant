# GitHub Actions: PR Target Branch Check

## Was macht dieser Workflow?

Der Workflow `check-pr-target-branch.yml` prüft automatisch bei jedem Pull Request, ob dieser gegen den richtigen Branch gerichtet ist.

## Regeln

### Für **Community Contributors** (Nicht-Maintainer):
- ✅ PRs **MÜSSEN** gegen `dev` Branch gehen
- ❌ PRs gegen `main` werden **automatisch abgelehnt**
- 📢 Automatischer Kommentar mit Anleitung zur Korrektur
- 🏷️ Labels werden automatisch hinzugefügt: `needs information`, `wrong target branch`

### Für **Maintainer** (Admin/Write/Maintain Permissions):
- ✅ Dürfen PRs gegen `main` erstellen
- ✅ Workflow wird automatisch übersprungen
- ℹ️ Keine Kommentare oder Labels

## Warum diese Regel?

**Branching Strategy:**
- `main` = Production (nur stabile Releases)
- `dev` = Development (alle neuen Changes, Testing)

**Vorteile:**
1. 🔒 **Qualitätskontrolle**: Alle Community-Changes durchlaufen Review in `dev`
2. 🧪 **Testing**: Ausreichend Zeit zum Testen vor Production
3. 📦 **Saubere Releases**: `main` bleibt stabil und releasefähig
4. 🤝 **Community Workflow**: Klare Prozesse für alle Contributors

## Wie funktioniert's?

### 1. Permission Check
```javascript
const { data: permission } = await github.rest.repos.getCollaboratorPermissionLevel({
  owner: context.repo.owner,
  repo: context.repo.repo,
  username: pr.user.login
});

isMaintainer = ['admin', 'maintain', 'write'].includes(permission.permission);
```

### 2. Conditional Logic
- **Maintainer?** → Workflow wird übersprungen
- **Community?** → Target Branch wird geprüft

### 3. Aktion bei falscher Branch
- Kommentar mit Erklärung und Anleitung
- Labels hinzufügen
- Workflow schlägt fehl (roter Status)

## Fehlerbehebung für Contributors

### Option 1: Base Branch ändern (Empfohlen)
1. Gehe zu deinem PR
2. Klicke "Edit" neben dem Titel
3. Ändere "base: main" zu "base: dev"
4. Klicke "Change base"

### Option 2: Neuer PR
1. PR schließen
2. Neuen PR gegen `dev` erstellen

## Trigger

Der Workflow läuft bei:
- `pull_request_target` (wichtig für Fork-PRs!)
  - `opened` - Neuer PR
  - `synchronize` - Neue Commits
  - `reopened` - PR wieder geöffnet
  - `edited` - PR bearbeitet

**Warum `pull_request_target`?**
- Funktioniert auch bei Fork-PRs
- Hat Write-Permissions für Kommentare/Labels
- Sicherheit: Läuft im Kontext des Base-Repos

## Permissions

```yaml
permissions:
  pull-requests: write  # Für Labels
  issues: write         # Für Kommentare
```

## Testing

### Testfall 1: Community PR gegen main
```bash
# Erwartetes Verhalten:
1. Kommentar wird erstellt
2. Labels werden hinzugefügt
3. Workflow schlägt fehl (❌)
```

### Testfall 2: Community PR gegen dev
```bash
# Erwartetes Verhalten:
1. Workflow wird nicht getriggert
2. Keine Kommentare/Labels
3. Normal weiter mit anderen Checks
```

### Testfall 3: Maintainer PR gegen main
```bash
# Erwartetes Verhalten:
1. Permission Check erkennt Maintainer
2. Workflow wird übersprungen
3. Keine Kommentare/Labels
4. Workflow läuft durch (✅)
```

## Labels

Stelle sicher, dass folgende Labels existieren:
- `needs information`
- `wrong target branch` (neu erstellt durch diesen Workflow)

## Links

- [Contributing Guide](../CONTRIBUTING.md#-branching-strategy)
- [GitHub Permissions](https://docs.github.com/en/organizations/managing-user-access-to-your-organizations-repositories/repository-roles-for-an-organization)
- [pull_request_target Event](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#pull_request_target)

## Maintainer Notizen

### Label erstellen (falls nicht vorhanden):
1. Gehe zu: https://github.com/Disane87/spoolman-homeassistant/labels
2. Klicke "New label"
3. Name: `wrong target branch`
4. Description: `PR targets wrong branch (should be dev, not main)`
5. Color: `#d73a4a` (rot)
