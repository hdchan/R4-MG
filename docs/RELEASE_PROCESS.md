# Release Process Guide

This document outlines the steps for creating a new release of R4-MG.

## 1. Update Version Numbers

Update version number in the following files:
- `AppCore/Config/Configuration.py`:
```python
class Configuration:
    APP_VERSION = 'x.y.z'  # Increment using semantic versioning
```

## 2. Update Changelog

1. Open `AppUI/Assets/Text/CHANGELOG.md`
2. Add new version section at the top using format:
```markdown
## [x.y.z] - YYYY-MM-DD

### Added
- New features

### Changed  
- Updates to existing functionality

### Fixed
- Bug fixes

### Removed
- Removed features
```

## 3. Build & Test

1. Run tests:
```bat
python -m pytest Tests/
```

2. Build executable:
```bat
pyinstaller app_ui.spec
```

3. Test the built executable manually:
- Launch executable
- Verify core functionality
- Check changelog visibility in About screen
- Confirm version number displays correctly

## 4. Create Release

1. Commit changes with message "Release x.y.z"
2. Create Git tag: `git tag v{x.y.z}`
3. Push changes and tag: `git push && git push --tags`
4. Create GitHub release:
   - Title: "R4-MG v{x.y.z}" 
   - Description: Copy relevant changelog section
   - Attach built executable

## 5. Post-Release

1. Update version in `AppCore/Config/Configuration.py` to next development version (x.y.z-dev)
2. Create new "Unreleased" section in changelog
3. Commit changes with message "Begin development on x.y.z"

## Version Numbering

Follow semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes
- MINOR: New features, backwards compatible
- PATCH: Bug fixes, backwards compatible