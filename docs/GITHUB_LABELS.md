# 🏷️ GitHub Labels Setup Guide

This document describes how to set up and maintain GitHub labels for the project. These labels help organize issues and make it easier for contributors to find work that matches their skills.

## 📋 Recommended Labels

### Priority Labels
| Label | Color | Description |
|-------|-------|-------------|
| `priority: critical` | `#b60205` | Critical issues that need immediate attention |
| `priority: high` | `#d93f0b` | High priority issues |
| `priority: medium` | `#fbca04` | Medium priority issues |
| `priority: low` | `#0e8a16` | Low priority issues |

### Type Labels
| Label | Color | Description |
|-------|-------|-------------|
| `bug` | `#d73a4a` | Something isn't working |
| `enhancement` | `#a2eeef` | New feature or request |
| `documentation` | `#0075ca` | Improvements or additions to documentation |
| `question` | `#d876e3` | Further information is requested |
| `dependencies` | `#0366d6` | Pull requests that update a dependency |

### Status Labels
| Label | Color | Description |
|-------|-------|-------------|
| `status: awaiting response` | `#fef2c0` | Waiting for response from issue author |
| `status: blocked` | `#b60205` | Blocked by another issue or external factor |
| `status: in progress` | `#fbca04` | Someone is actively working on this |
| `status: needs investigation` | `#ededed` | Needs more investigation |
| `status: ready` | `#0e8a16` | Ready to be worked on |
| `needs testing` | `#fbca04` | Released on dev, needs testing before production ⚡ *Auto-added* |
| `released on @dev` | `#ededed` | Released on dev branch |
| `released` | `#ededed` | Released on main branch |

### Difficulty Labels (For Contributors)
| Label | Color | Description |
|-------|-------|-------------|
| `good first issue` | `#7057ff` | Good for newcomers - well-defined, small scope |
| `help wanted` | `#008672` | Extra attention is needed from the community |
| `advanced` | `#5319e7` | Requires advanced knowledge of the codebase |

### Special Labels
| Label | Color | Description |
|-------|-------|-------------|
| `breaking change` | `#b60205` | Changes that break backward compatibility |
| `security` | `#ee0701` | Security-related issues |
| `wontfix` | `#ffffff` | This will not be worked on |
| `duplicate` | `#cfd3d7` | This issue or pull request already exists |
| `invalid` | `#e4e669` | This doesn't seem right |

### Area Labels (Optional)
| Label | Color | Description |
|-------|-------|-------------|
| `area: sensors` | `#1d76db` | Related to sensor entities |
| `area: coordinator` | `#1d76db` | Related to data coordinator |
| `area: config flow` | `#1d76db` | Related to configuration flow |
| `area: services` | `#1d76db` | Related to Home Assistant services |
| `area: translations` | `#1d76db` | Related to translations |

## 🚀 How to Apply Labels

### Automatically (via GitHub CLI)
```bash
# Create all recommended labels
gh label create "good first issue" --color "7057ff" --description "Good for newcomers"
gh label create "help wanted" --color "008672" --description "Extra attention is needed"
gh label create "priority: high" --color "d93f0b" --description "High priority"
gh label create "priority: critical" --color "b60205" --description "Critical issues"
gh label create "breaking change" --color "b60205" --description "Breaking changes"
gh label create "area: sensors" --color "1d76db" --description "Related to sensor entities"
gh label create "area: coordinator" --color "1d76db" --description "Related to data coordinator"
gh label create "area: config flow" --color "1d76db" --description "Related to configuration flow"
gh label create "area: services" --color "1d76db" --description "Related to services"
gh label create "advanced" --color "5319e7" --description "Requires advanced knowledge"
```

### Manually (via GitHub UI)
1. Go to your repository on GitHub
2. Click on "Issues" tab
3. Click "Labels" button
4. Click "New label"
5. Fill in the name, description, and color
6. Click "Create label"

## 🎯 How to Mark Issues as "Good First Issue"

When creating or triaging issues, consider marking them as "good first issue" if they:

### ✅ Criteria for "Good First Issue"
- **Clear Scope**: Well-defined and focused on a single task
- **Documentation**: Has clear description and acceptance criteria
- **Self-Contained**: Doesn't require deep knowledge of entire codebase
- **Low Risk**: Changes won't affect critical functionality
- **Guided**: Includes hints, examples, or links to relevant code
- **Testable**: Easy to verify the fix works correctly

### 📝 Good First Issue Template

When creating a good first issue, include:

```markdown
## 🎯 Description
[Clear description of what needs to be done]

## 💡 Hints
- File to edit: `custom_components/spoolman/sensor.py`
- Look at line 123 for similar implementation
- Related documentation: [link]

## ✅ Acceptance Criteria
- [ ] Criteria 1
- [ ] Criteria 2
- [ ] Tests added/updated
- [ ] Documentation updated if needed

## 🚀 Getting Started
1. Fork the repository
2. Set up development environment (see CONTRIBUTING.md)
3. Make your changes
4. Run tests: `pytest tests/`
5. Submit a pull request

## 📚 Resources
- [Relevant documentation](link)
- [Similar implementation](link)
```

### 🔍 Examples of Good First Issues

**Example 1: Documentation**
```
Title: Add example automation for low filament alert
Labels: good first issue, documentation
Description: Add a practical example to README.md showing how to create
an automation that sends a notification when filament is low.
```

**Example 2: Simple Enhancement**
```
Title: Add unit test for weight conversion helper
Labels: good first issue, enhancement, area: tests
Description: Add missing unit test for the weight_to_grams() helper
function in helpers/units.py
```

**Example 3: Small Bug Fix**
```
Title: Fix typo in German translation
Labels: good first issue, bug, area: translations
Description: Correct spelling error in de.json translation file
```

## 🔄 Label Workflow

### For Maintainers

**When a new issue is created:**
1. Add type label (bug/enhancement/documentation/question)
2. Add priority label if urgent
3. Add area label to categorize
4. Consider if it's a "good first issue"
5. Add "help wanted" if community help is welcome

**When work begins:**
1. Add "status: in progress"
2. Assign to the person working on it

**When PR is submitted:**
1. Link PR to issue
2. Review and provide feedback
3. Merge when approved

**When issue is closed:**
1. Remove "status: in progress"
2. Ensure issue is properly labeled for future reference

## 📊 Using Labels to Track Progress

**Find issues to work on:**
- Good first issues: `is:open is:issue label:"good first issue"`
- Help wanted: `is:open is:issue label:"help wanted"`
- High priority bugs: `is:open is:issue label:bug label:"priority: high"`

**Track project health:**
- Open bugs: `is:open is:issue label:bug`
- Feature requests: `is:open is:issue label:enhancement`
- Documentation needs: `is:open is:issue label:documentation`

## 🎓 Best Practices

1. **Be Consistent**: Use the same labels for similar issues
2. **Be Specific**: Don't over-label; 3-5 labels per issue is usually enough
3. **Keep Updated**: Remove labels that no longer apply
4. **Communicate**: Use labels to signal status to contributors
5. **Review Regularly**: Audit labels monthly to ensure they're still relevant

## 🤖 Automated Label Workflows

This repository uses GitHub Actions to automatically manage labels:

### Auto-Label Workflow (`.github/workflows/auto-label.yml`)

**Automatic "needs testing" Label:**
- ✅ When `released on @dev` is added → `needs testing` is automatically added
- ✅ When `released` is added → `needs testing` is automatically removed

This ensures that:
1. Features/fixes released on `dev` branch are flagged for testing
2. Once promoted to `main` (production), the testing flag is cleared
3. No manual label management needed for the testing workflow

**How it works:**
```
Issue/PR → Add "released on @dev" → GitHub Action → Auto-add "needs testing"
Issue/PR → Add "released" → GitHub Action → Auto-remove "needs testing"
```

## 🔗 Resources

- [GitHub Labels Documentation](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels)
- [GitHub CLI Labels Reference](https://cli.github.com/manual/gh_label)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
