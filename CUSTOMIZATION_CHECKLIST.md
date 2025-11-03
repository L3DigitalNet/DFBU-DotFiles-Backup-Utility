# Customization Checklist

Use this checklist when adapting this template for your own project.

## 🎯 Before You Start

- [ ] Read `QUICKSTART.md` (5 minutes)
- [ ] Read `README.md` (10 minutes)
- [ ] Run the example application (`python src/main.py`)
- [ ] Run the tests (`pytest tests/`)
- [ ] Understand the MVVM structure

## 📝 Initial Setup

### 1. Project Information

- [ ] Update `README.md` with your project name
- [ ] Update `README.md` with your project description
- [ ] Update `src/utils/constants.py` with your app name
- [ ] Update `pyproject.toml` with your project metadata
- [ ] Update `LICENSE` with your name/organization
- [ ] Update repository URL in clone commands

### 2. GitHub Configuration

- [ ] Update `.github/workflows/ci.yml` if needed
- [ ] Configure branch protection rules
- [ ] Set up Codecov (optional)
- [ ] Add repository secrets if needed

### 3. Git Configuration

- [ ] Initialize as template: `git init` (if starting fresh)
- [ ] Update `.gitignore` for your specific needs
- [ ] Create initial commit

## 🗑️ Remove Example Code

Once you understand the structure, remove the examples:

### Models

- [ ] Delete `src/models/example_model.py` (or keep as reference)
- [ ] Delete `tests/unit/test_example_model.py`
- [ ] Create your first model in `src/models/`
- [ ] Create tests for your model

### Services

- [ ] Delete `src/services/example_service.py` (or keep as reference)
- [ ] Create your first service in `src/services/`
- [ ] Inject your service into ViewModels

### ViewModels

- [ ] Keep or modify `src/viewmodels/main_viewmodel.py`
- [ ] Delete `tests/unit/test_main_viewmodel.py` or update for your VM
- [ ] Create ViewModels for your features
- [ ] Write tests for your ViewModels

### Views

- [ ] Modify `src/views/main_window.py` for your UI
- [ ] Create additional views as needed
- [ ] Connect views to your ViewModels

### Integration Tests

- [ ] Update `tests/integration/test_application.py` for your app
- [ ] Add integration tests for your workflows

## 🎨 Customize UI

### Main Window

- [ ] Update window title in `src/views/main_window.py`
- [ ] Update window size
- [ ] Design your layout
- [ ] Add your widgets
- [ ] Style your application (QSS/stylesheets)

### Additional Windows

- [ ] Create dialog classes if needed
- [ ] Create custom widgets if needed
- [ ] Add icons and resources

### Resources

- [ ] Add your application icon
- [ ] Add other resources (images, fonts, etc.)
- [ ] Set up Qt Resource System if needed

## ⚙️ Configuration

### Application Config

- [ ] Add configuration file support (JSON, YAML, etc.)
- [ ] Create config service if needed
- [ ] Add settings/preferences dialog
- [ ] Store user preferences

### Dependencies

- [ ] Add your specific dependencies to `requirements.txt`
- [ ] Pin versions for production
- [ ] Test with different Python versions
- [ ] Update `pyproject.toml` dependencies

## 🧪 Testing Strategy

### Unit Tests

- [ ] Achieve 90%+ coverage for Models
- [ ] Achieve 90%+ coverage for ViewModels
- [ ] Mock all external dependencies
- [ ] Test edge cases and error handling

### Integration Tests

- [ ] Test complete user workflows
- [ ] Test with real services (or test doubles)
- [ ] Test cross-component communication

### Manual Testing

- [ ] Create test plan document
- [ ] Test on all target platforms
- [ ] Test with different screen sizes
- [ ] Test accessibility features

## 📦 Packaging & Distribution

### PyInstaller (Recommended)

- [ ] Install PyInstaller: `pip install pyinstaller`
- [ ] Create spec file: `pyi-makespec src/main.py`
- [ ] Customize spec file
- [ ] Test build: `pyinstaller your_app.spec`
- [ ] Test executable on clean system

### Alternative Packaging

- [ ] Consider Briefcase (modern option)
- [ ] Consider Nuitka (compiled Python)

### Distribution

- [ ] Create Linux package (.deb, .rpm, AppImage, Flatpak, Snap)
- [ ] Set up auto-updates mechanism
- [ ] Create download page
- [ ] Prepare release notes

## 🚀 CI/CD Enhancement

### GitHub Actions

- [ ] Add build workflow
- [ ] Add packaging workflow
- [ ] Add release workflow
- [ ] Add deployment workflow

### Testing

- [ ] Add performance tests
- [ ] Add UI tests (if applicable)
- [ ] Add security scanning
- [ ] Add dependency checking

## 📚 Documentation

### User Documentation

- [ ] Write user guide
- [ ] Create screenshots/GIFs
- [ ] Document features
- [ ] Create FAQ

### Developer Documentation

- [ ] Document architecture decisions
- [ ] Create API documentation
- [ ] Document build process
- [ ] Document deployment process

### Code Documentation

- [ ] Update all docstrings
- [ ] Add inline comments for complex logic
- [ ] Document non-obvious decisions
- [ ] Keep AGENTS.md updated with patterns

## 🔧 Advanced Features

### Optional Enhancements

- [ ] Add logging to file
- [ ] Add crash reporting
- [ ] Add analytics (if appropriate)
- [ ] Add auto-update mechanism
- [ ] Add plugin system
- [ ] Add themes/skins support
- [ ] Add internationalization (i18n)
- [ ] Add keyboard shortcuts
- [ ] Add system tray integration
- [ ] Add command-line interface

### Database Integration

- [ ] Choose database (SQLite, PostgreSQL, etc.)
- [ ] Add database service
- [ ] Add migration system
- [ ] Add database tests

### Network Features

- [ ] Add HTTP client service
- [ ] Add WebSocket support
- [ ] Add authentication
- [ ] Handle network errors gracefully

## 🐛 Error Handling

### User-Facing Errors

- [ ] Create error dialog class
- [ ] Add user-friendly error messages
- [ ] Add error reporting mechanism
- [ ] Log errors appropriately

### Developer Errors

- [ ] Add debug mode
- [ ] Add verbose logging option
- [ ] Add development tools/utilities
- [ ] Document common issues

## 🎯 Final Checklist

### Before First Release

- [ ] All tests passing
- [ ] Code coverage > 90%
- [ ] No linting errors
- [ ] Type checking passes
- [ ] Documentation complete
- [ ] README accurate
- [ ] License chosen and applied
- [ ] Version number set

### Quality Checks

- [ ] No hardcoded secrets
- [ ] No sensitive data in repository
- [ ] Error handling comprehensive
- [ ] User experience smooth
- [ ] Performance acceptable
- [ ] Memory leaks checked

### Legal & Compliance

- [ ] License file updated
- [ ] Third-party licenses documented
- [ ] Copyright notices added
- [ ] Privacy policy (if applicable)
- [ ] Terms of service (if applicable)

## 📋 Ongoing Maintenance

### Regular Tasks

- [ ] Update dependencies regularly
- [ ] Monitor for security issues
- [ ] Review and respond to issues
- [ ] Review and merge PRs
- [ ] Update documentation
- [ ] Write release notes

### Community

- [ ] Set up issue templates
- [ ] Set up PR templates
- [ ] Create CODE_OF_CONDUCT.md
- [ ] Create SECURITY.md
- [ ] Respond to community feedback

## 💡 Tips

1. **Don't delete examples immediately** - Keep them as reference until you understand the patterns
2. **Start small** - Add one feature at a time
3. **Test as you go** - Don't accumulate untested code
4. **Follow the patterns** - The template structure is designed for scalability
5. **Ask for help** - Use the GitHub Copilot instructions and AGENTS.md
6. **Keep MVVM strict** - Don't mix concerns between layers
7. **Document decisions** - Future you will thank present you
8. **Automate everything** - Use CI/CD, pre-commit hooks, etc.

## 🎓 Learning Resources

If you need to learn more:

- [ ] Review example code in this template
- [ ] Read PySide6 documentation
- [ ] Study MVVM pattern in depth
- [ ] Learn SOLID principles
- [ ] Practice TDD (Test-Driven Development)
- [ ] Study Qt Designer for UI design

## ✅ You're Ready When

- [x] You understand MVVM architecture
- [x] You can create a feature end-to-end
- [x] You can write tests for your code
- [x] You understand dependency injection
- [x] You can use signals/slots correctly
- [x] You maintain SOLID principles
- [x] Your tests are passing
- [x] Your code is documented

**Now go build something amazing! 🚀**

---

## 📝 Notes

Use this space to track your project-specific customizations:

```
Project Name: ___________________________
Start Date: ___________________________
Target Release: ___________________________

Key Features:
-
-
-

Custom Dependencies:
-
-
-

Platform Targets:
☑ Linux only (Python 3.14, PySide6 6.8.0+)

Notes:




```
