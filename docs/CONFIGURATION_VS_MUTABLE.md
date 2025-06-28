# Configuration vs MutableConfiguration

This document explains the differences between the `Configuration` and `MutableConfiguration` classes in the R4-MG project.

## Configuration
- **Purpose:**
  - Represents a read-only, stable snapshot of application settings.
  - Used for accessing configuration values that should not be changed during runtime.
- **Usage:**
  - Provides getters for settings and toggles.
  - Used throughout the application for consistent, safe access to configuration data.
- **Characteristics:**
  - Immutable after creation.
  - Typically instantiated from saved settings or defaults.
  - Ensures that configuration state is not accidentally modified.

## MutableConfiguration
- **Purpose:**
  - Represents a writable version of the configuration.
  - Used for updating, saving, or modifying settings during runtime.
- **Usage:**
  - Allows setters and direct modification of configuration values.
  - Used when the application needs to change settings, e.g., in response to user actions or during setup.
- **Characteristics:**
  - Mutable: values can be changed after instantiation.
  - Can be converted to a `Configuration` for safe, read-only access.
  - Used by configuration managers and UI components that allow settings changes.

## Typical Workflow
1. **Startup:**
   - Load settings from disk into a `MutableConfiguration`.
   - Convert to a `Configuration` for use throughout the app.
2. **During Runtime:**
   - If settings need to be changed, use `MutableConfiguration`.
   - Save changes back to disk.
   - Update the read-only `Configuration` as needed.

## Example
```python
# Load configuration
mutable_config = MutableConfiguration.load_from_file('settings.yaml')
config = Configuration(mutable_config.to_data())

# Access read-only values
print(config.window_width)

# Update a setting
mutable_config.set_window_width(1024)
mutable_config.save_to_file('settings.yaml')
```

## Summary
- Use `Configuration` for safe, read-only access to settings.
- Use `MutableConfiguration` when you need to change or save settings.
- This separation helps prevent accidental changes and supports robust configuration management.

---

For more details, see the implementation and comments in `Configuration.py` and related files.
