# 🤖 GitHub Automations Overview

This document describes all automated workflows in this repository to help maintain code quality, streamline contributions, and reduce manual work.

## 📋 Active Automations

### 1. 🏷️ Auto Label (`auto-label.yml`)
**Triggers:** When labels are added to issues/PRs

**What it does:**
- ✅ Automatically adds `needs testing` when `released on @dev` is added
- ✅ Automatically removes `needs testing` when `released` is added

**Why:** Ensures proper testing workflow without manual label management.

---

### 2. 🎯 Auto Assign Area Labels (`auto-assign-area-labels.yml`)
**Triggers:** Issues opened/edited, PRs opened/edited/synchronized

**What it does:**
- Analyzes PR file changes or issue content
- Automatically adds relevant area labels:
  - `area: sensors` - Changes to sensor files
  - `area: coordinator` - Changes to coordinator
  - `area: config flow` - Changes to config/options flow
  - `area: services` - Changes to services
  - `documentation` - Documentation or translation changes

**Why:** Saves maintainers time organizing issues and makes filtering easier.

---

### 3. 🚫 Check PR Target Branch (`check-pr-target-branch.yml`)
**Triggers:** PRs targeting `main` branch

**What it does:**
- ✅ Detects PRs incorrectly targeting `main` instead of `dev`
- ✅ Posts helpful comment explaining the branching strategy
- ✅ Adds `needs information` label
- ✅ Fails the check to prevent accidental merges

**Why:** Enforces branching strategy (dev → main) and prevents production issues.

---

### 4. 📏 PR Size Labeler (`pr-size-labeler.yml`)
**Triggers:** PRs opened/synchronized

**What it does:**
- Calculates lines changed (additions + deletions)
- Adds size labels:
  - 🔹 `size:XS` - < 10 lines
  - 🔸 `size:S` - 10-29 lines
  - 🟠 `size:M` - 30-99 lines
  - 🟡 `size:L` - 100-499 lines
  - 🔴 `size:XL` - 500-999 lines
  - 🔴🔴 `size:XXL` - 1000+ lines
- Comments on large PRs (500+ lines) with tips

**Why:** Helps reviewers prioritize and provides feedback on PR size.

---

### 5. 🔗 Auto Link Issues in PR (`auto-link-issues.yml`)
**Triggers:** PRs opened/edited

**What it does:**
- Checks if PR description links to an issue using keywords:
  - `Fixes #123`, `Closes #123`, `Resolves #123`
- Posts reminder comment if no issue is linked
- Provides guidance on how to link issues

**Why:** Ensures traceability and automatically closes issues when PRs merge.

---

### 6. 📝 Conventional Commit Checker (`check-conventional-commits.yml`)
**Triggers:** PRs opened/edited

**What it does:**
- ✅ Validates PR title follows Conventional Commits format
- ✅ Posts helpful comment with examples if format is wrong
- ✅ Fails check if format doesn't match
- Accepts: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`, `build`

**Why:** Enables automatic versioning and changelog generation.

---

### 7. 👋 Welcome New Contributors (`welcome.yml`)
**Triggers:** First-time issue or PR from a user

**What it does:**
- Welcomes new contributors with friendly message
- Provides links to contributing guide
- Explains what happens next
- Offers help and encouragement

**Why:** Makes new contributors feel welcome and guides them through the process.

---

### 8. 🧹 Stale Good First Issues (`stale-good-first-issues.yml`)
**Triggers:** Daily at 00:00 UTC

**What it does:**
- Finds `good first issue` labels with no activity for 60 days
- Marks as `stale` and comments
- Closes after 7 more days of inactivity
- Exempts: `In Progress`, `priority: high`, `priority: critical`

**Why:** Keeps issue list fresh and relevant for new contributors.

---

### 9. 🧪 Validate (`validate.yml`)
**Triggers:** Manual, workflow call

**What it does:**
- Runs Home Assistant's `hassfest` validation
- Runs HACS validation
- Ensures integration meets HA standards

**Why:** Catches integration issues early before release.

---

### 10. 🔄 Update Contributors (`update-contributors.yml`)
**Triggers:** Push to main branch

**What it does:**
- Automatically updates contributor list in README
- Uses contrib.rocks for visual contributor display
- No manual maintenance needed

**Why:** Recognizes all contributors automatically.

---

### 11. 🚀 Semantic Release (`semantic_release.yml`)
**Triggers:** Push to main/master branch

**What it does:**
- Analyzes conventional commit messages
- Automatically determines version bump
- Generates changelog
- Creates GitHub release
- Publishes assets

**Why:** Fully automated release process based on commits.

---

### 12. 🧪 PR Tests (`pr_tests.yml`)
**Triggers:** Pull requests

**What it does:**
- Runs test suite
- Checks code coverage
- Validates code quality
- Reports results

**Why:** Ensures code quality before merge.

---

### 13. 🎨 Lint (`lint.yml`)
**Triggers:** Pull requests, pushes

**What it does:**
- Runs ruff/pylint checks
- Validates Python code style
- Checks formatting

**Why:** Maintains consistent code style.

---

### 14. 🎉 Celebrate First Contribution (`celebrate-first-contribution.yml`)
**Triggers:** When a PR is merged

**What it does:**
- ✅ Detects if this is the author's first merged PR
- ✅ Posts celebratory comment congratulating the contributor
- ✅ Adds `first contribution 🎉` label to the PR
- ✅ Encourages further contributions

**Why:** Makes contributors feel valued and celebrates their achievement.

---

### 15. ✨ Enhance Changelog with First Contributors (`enhance-changelog-contributors.yml`)
**Triggers:** When a release is published

**What it does:**
- ✅ Identifies first-time contributors in the release
- ✅ Adds "🎉✨ _First contribution!_" badge to their entries
- ✅ Creates a special "New Contributors" section in release notes
- ✅ Lists and thanks all first-time contributors

**Why:** Publicly recognizes new contributors and encourages community growth.

**Example output in changelog:**
```markdown
* **sensors:** add new temperature sensor (@newcontributor) 🎉✨ First contribution!

## 🎉 New Contributors
Welcome to our amazing new contributors! Thank you for making your first contribution!
@newcontributor, @anotheruser
```

---

## 🎯 Benefits

### For Maintainers
- ⏱️ **Saves Time**: Automatic labeling, size checking, and validation
- 🎯 **Better Organization**: Area labels applied automatically
- 🛡️ **Prevents Mistakes**: Branch checks, commit format validation
- 📊 **Better Insights**: Size labels, automatic linking

### For Contributors
- 👋 **Welcoming**: Friendly messages for first-timers
- 🎉 **Recognition**: First contributions are celebrated publicly
- 📖 **Guidance**: Helpful comments explain what's needed
- ✅ **Clear Expectations**: Automatic checks show what needs fixing
- 🚀 **Faster Reviews**: Well-organized PRs get reviewed faster
- 🌟 **Visibility**: Contributors featured in changelogs and README

### For the Project
- 📈 **Better Quality**: Automated testing and validation
- 📝 **Clean History**: Conventional commits enable automatic changelogs
- 🎯 **Issue Management**: Stale issues cleaned, good first issues fresh
- 🤝 **Community Growth**: Welcoming automation encourages contributions

---

## 🔧 Maintenance

### Updating Workflows
All workflows are in `.github/workflows/`. To modify:

1. Edit the YAML file
2. Test changes on a fork first
3. Submit PR with changes
4. Document changes in this file

### Adding New Automations
Consider these questions:
- Does it save manual work?
- Does it improve contributor experience?
- Does it maintain code quality?
- Is it well-documented?

### Monitoring
- Check Actions tab for failed workflows
- Review workflow logs for issues
- Update as GitHub Actions features evolve

---

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Release](https://github.com/semantic-release/semantic-release)
- [Home Assistant Developer Docs](https://developers.home-assistant.io/)

---

## 🎊 First Contribution Workflow

Here's how we celebrate new contributors:

1. **New contributor submits PR** → Welcomed by automation
2. **PR gets merged** → 🎉 Celebratory comment posted
3. **`first contribution 🎉` label added** → Easy to track
4. **Release is created** → Changelog enhanced with badges
5. **Release notes published** → First-timers get special section
6. **README updated** → Contributor appears in contributor list

**Example celebration comment:**
> 🎉🎊 **CONGRATULATIONS @username!** 🎊🎉
>
> This is your **FIRST MERGED CONTRIBUTION** to the Spoolman Home Assistant Integration!
>
> You're now officially part of our contributor community! 🌟

## 💡 Ideas for Future Automations

Want to add more? Consider:
- 🎖️ Auto-assign reviewers based on file changes
- 📊 Generate monthly contributor reports
- 🏆 Recognize top contributors with milestone badges
- 🔍 Auto-detect security vulnerabilities
- 📸 Auto-generate screenshots for UI changes
- 🌍 Auto-update translations via Crowdin
- 🎂 Birthday messages for repository anniversary

---

**Last Updated:** November 26, 2025
