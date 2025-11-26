# 🤝 Contribution Guidelines

Hey there! 👋 Thanks for considering contributing to this project! We're excited to have you here!

Whether you're fixing a typo, squashing a bug, or adding a cool new feature - every contribution matters! 🎉

There are just a few things to keep in mind to make sure everything runs smoothly:

## 🌿 Branching Strategy

Let's keep things organized! Here's how we handle branches:

- 🎯 **Merge your PR to the `dev` branch** - This is where all the magic happens! (PRs against `main` will be rejected)
- 🏠 The `main` branch is our "production" version - only stable releases here
- 🚀 The `dev` branch is where we test new stuff before it goes live

## 💬 Commit Messages

We use [conventional commits](https://www.conventionalcommits.org/) - sounds fancy, but it's actually pretty simple!

**Examples:**
- `feat: add temperature monitoring for spools` 🆕
- `fix: resolve issue with color visualization` 🐛
- `docs: update README with new sensor info` 📝
- `refactor: improve code structure` 🔧

This helps our CI/CD pipeline automatically create releases and changelogs. Pretty cool, right? 🎉

## 🛠️ Development Environment

### 🐳 Using the Dev Container (Highly Recommended!)

We've got you covered! This project includes a fully configured Dev Container that sets up everything for you automatically. No more "works on my machine" problems! 🎉

#### 📋 Prerequisites
- [Docker](https://www.docker.com/products/docker-desktop) installed and running 🐋
- [Visual Studio Code](https://code.visualstudio.com/) with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) 💻

#### 🚀 Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Disane87/spoolman-homeassistant.git
   cd spoolman-homeassistant
   ```

2. **Open in Dev Container:**
   - Open the project in VS Code
   - When prompted, click "Reopen in Container" (or press `F1` and select "Dev Containers: Reopen in Container")
   - Wait for the container to build and start (first time takes a few minutes)

3. **What's Included:**
   - ✅ **Home Assistant Core** - Full Home Assistant instance for testing
   - ✅ **Python 3.13** - Latest Python with all required dependencies
   - ✅ **Pre-configured tasks** - Start/stop Home Assistant with a single click
   - ✅ **Linting tools** - pylint, black, isort pre-configured
   - ✅ **Git** - Latest version for version control
   - ✅ **Node.js & npm** - For any frontend tooling needs

#### 🎮 Development Workflow

1. **🚀 Start Home Assistant:**
   - Press `Ctrl+Shift+B` (or `Cmd+Shift+B` on Mac)
   - Select "startHomeAssistant" task
   - Or run: `./scripts/develop` in the terminal
   - Home Assistant will start at `http://localhost:8123` 🏠

2. **🛑 Stop Home Assistant:**
   - Use the "stopHomeAssistant" task
   - Or press `Ctrl+C` in the terminal running Home Assistant

3. **📂 Configuration Location:**
   - Home Assistant config: `/config/` 🏠
   - Integration code: `/spoolman-homeassistant/custom_components/spoolman/` 📝
   - Logs: `/config/home-assistant.log` 📋

4. **🧪 Testing Your Changes:**
   - Make changes to the integration code ✏️
   - Restart Home Assistant (stop + start) 🔄
   - Check logs for any errors: `tail -f /config/home-assistant.log` 🔍
   - Configure the integration at `http://localhost:8123/config/integrations`

5. **🧪 Running Tests:**
   ```bash
   # Run all tests
   pytest tests/

   # Run specific test file
   pytest tests/test_sensor.py

   # Run with coverage
   pytest --cov=custom_components.spoolman tests/
   ```

6. **✨ Linting and Code Quality:**
   ```bash
   # Run pylint
   ./scripts/lint

   # Format code with black
   black custom_components/spoolman/

   # Sort imports
   isort custom_components/spoolman/
   ```

#### 🔗 Connecting to a Spoolman Instance

You'll need a running Spoolman instance to test the integration. Here are your options:

**Option 1: Use Docker (Recommended) 🐋**
```bash
docker run -d \
  --name spoolman \
  -p 7912:8000 \
  -v spoolman_data:/home/app/.local/share/spoolman \
  ghcr.io/donkie/spoolman:latest
```

**Option 2: Use existing Spoolman instance 🌐**
- Point the integration to your existing Spoolman URL during setup

#### 🐛 Debugging

1. **📝 Enable Debug Logging:**
   Add to `/config/configuration.yaml`:
   ```yaml
   logger:
     default: info
     logs:
       custom_components.spoolman: debug
   ```

2. **🔍 Use VS Code Debugger:**
   - Set breakpoints in your code 🎯
   - Use the included launch configuration "Python: Home Assistant"
   - Press `F5` to start debugging
   - Step through your code like a pro! 😎

3. **📋 Check Logs:**
   ```bash
   # Follow logs in real-time
   tail -f /config/home-assistant.log

   # Search for errors
   grep -i "error" /config/home-assistant.log

   # Filter integration logs
   grep "spoolman" /config/home-assistant.log
   ```

#### 📁 Folder Structure

Here's what goes where (so you don't get lost! 🗺️):

```
/spoolman-homeassistant/
├── custom_components/
│   └── spoolman/              # Main integration code
│       ├── __init__.py        # Integration setup
│       ├── sensor.py          # Sensor platform
│       ├── coordinator.py     # Data update coordinator
│       ├── config_flow.py     # Configuration flow
│       ├── select.py          # Location select entity
│       ├── services.yaml      # Service definitions
│       ├── manifest.json      # Integration manifest
│       └── sensors/           # Individual sensor classes (27 files)
├── config/                    # Home Assistant config directory
├── tests/                     # Unit tests
├── scripts/                   # Helper scripts
│   ├── develop               # Start Home Assistant
│   ├── lint                  # Run linting
│   └── setup                 # Setup development environment
├── .devcontainer/            # Dev Container configuration
└── docs/                     # Documentation

```

#### 🔄 Updating Home Assistant in Dev Container

Want to test with a newer Home Assistant version? No problem! Here's how:

**Option 1: Update Python Package (Quick) ⚡**
```bash
# Update to latest stable
pip install --upgrade homeassistant

# Or install specific version
pip install homeassistant==2024.11.0

# Restart Home Assistant after update
./scripts/develop
```

**Option 2: Rebuild Dev Container (Clean) 🧹**
```bash
# Exit and rebuild container
# In VS Code: Press F1 → "Dev Containers: Rebuild Container"
# Or rebuild from command line:
docker-compose -f .devcontainer/docker-compose.yml build --no-cache
```

**🔍 Check Home Assistant Version:**
```bash
# In terminal
hass --version

# Or in Home Assistant UI
# Settings → System → About
```

**📦 Update All Dependencies:**
```bash
# Update all Python packages
pip install --upgrade -r requirements.txt

# Verify integration dependencies
pip list | grep -E "homeassistant|aiohttp|pillow"
```

#### 💡 Tips & Tricks

Little things that'll save you time:

- **⚡ Reload Integration:** Instead of restarting HA completely, use Developer Tools → YAML → Reload "Custom Integrations" (much faster!)
- **🧹 Clear Cache:** Delete `/config/.storage/core.config_entries` if you need to reconfigure the integration from scratch
- **📊 Monitor Performance:** Use Home Assistant's built-in performance monitoring tools to see how your changes affect speed
- **📝 Entity Registry:** Check `/config/.storage/core.entity_registry` to see what entities are registered
- **🐍 Python Cache:** Clear `__pycache__` folders if you get weird import issues: `find . -type d -name __pycache__ -exec rm -rf {} +`
- **🗄️ Database Reset:** Delete `/config/home-assistant_v2.db` to start fresh (warning: loses all history!)

### 🏠 Alternative: Local Development (Without Container)

Prefer to keep things local? That's cool too! Here's how:

1. **📋 Requirements:**
   - Python 3.11 or higher
   - Home Assistant Core installed
   - Git

2. **Setup:**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Link integration to your HA config
   ln -s $(pwd)/custom_components/spoolman ~/.homeassistant/custom_components/spoolman
   ```

3. **Start Home Assistant:**
   ```bash
   hass -c ~/.homeassistant
   ```

**💡 Note:** We really recommend the Dev Container approach - it just works! But hey, you do you! 😊

## CI/CD Requirements

- Adhering to these guidelines is crucial because our CI/CD pipeline depends on this workflow. The `dev` branch is used for testing and validation, while `main` is reserved for stable releases.

## General Guidelines

1. **Code Quality:**
   - Ensure your code is clean, well-documented, and follows the project’s coding standards.
   - Write clear, concise, and descriptive comments where necessary.
   - Refactor code where needed to maintain readability and simplicity.

2. **Testing:**
   - Write unit tests for your code to ensure functionality.
   - Run all existing tests to make sure your changes do not break any existing functionality.
   - Ensure your code passes the CI tests before submitting a PR.

3. **Documentation:**
   - Update the documentation to reflect any changes in the code.
   - Ensure new features or changes are documented with examples and usage instructions.

4. **Issue Tracking:**
   - Reference any relevant issues in your commit messages and PR descriptions.
   - Use keywords like "fixes" or "closes" followed by the issue number to link PRs to issues.

5. **Code Reviews:**
   - Be responsive to feedback from code reviewers and make necessary changes promptly.
   - Review others' PRs if you have the expertise and provide constructive feedback.

6. **Style Guidelines:**
   - Follow the established coding style of the project. Consistency is key.
   - Use linting tools provided in the project to maintain code style.

7. **Communication:**
   - Be respectful and considerate in all communications.
   - Discuss any significant changes or new features with the project maintainers before starting work to ensure alignment with project goals.

## Thank You!

Thank you for contributing and helping to maintain the quality and consistency of the project!
