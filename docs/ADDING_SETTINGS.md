# How to Add New Settings to `Configuration.py`

This guide describes the process for adding new settings to the `Configuration.py` file in the R4-MG project.

## Steps

1. **Add a Key**
   - In the appropriate section (e.g., `Settings.Keys` or `Toggles.Keys`), add a new constant for your setting:
     ```python
     class Keys:
         NEW_SETTING = 'new_setting'
     ```

2. **Add a Default Value**
   - In the default configuration dictionary or initialization logic, add your new key and its default value:
     ```python
     DEFAULTS = {
         Keys.NEW_SETTING: <default_value>,
         # ...existing defaults...
     }
     ```

3. **Create a Getter**
   - Add a method to retrieve the value of your new setting:
     ```python
     def get_new_setting(self) -> <type>:
         return self._settings.get(Keys.NEW_SETTING, <default_value>)
     ```

4. **Create a Setter**
   - Add a method to update the value of your new setting:
     ```python
     def set_new_setting(self, value: <type>):
         self._settings[Keys.NEW_SETTING] = value
     ```

5. **Update Documentation**
   - Document the new setting in the code and in any user-facing documentation as needed.

## Example

Suppose you want to add a setting for enabling a dark mode feature:

1. Add the key:
   ```python
   class Keys:
       ENABLE_DARK_MODE = 'enable_dark_mode'
   ```
2. Add the default value:
   ```python
   DEFAULTS = {
       Keys.ENABLE_DARK_MODE: False,
   }
   ```
3. Create the getter:
   ```python
   def get_enable_dark_mode(self) -> bool:
       return self._settings.get(Keys.ENABLE_DARK_MODE, False)
   ```
4. Create the setter:
   ```python
   def set_enable_dark_mode(self, value: bool):
       self._settings[Keys.ENABLE_DARK_MODE] = value
   ```

## Tips
- Use clear, descriptive names for keys.
- Always provide a sensible default value.
- Update any relevant UI or logic to use the new setting.
- Test your changes to ensure the new setting works as expected.

---

For more details, see the comments and structure in `Configuration.py`.
