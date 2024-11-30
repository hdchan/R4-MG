## Changelog

### 0.7.0
#### Feature updates
- Adds image rotation
- Adds redownload option for image resource
- Adds regenerate preview
- Adds placeholder logo
  
#### Engineering updates
- Adds additional sets for local mock

### 0.6.0
#### Feature updates
- Adds resource details setting
  
#### Engineering updates
- Fixes staging bug where previous source image was staged

### 0.5.0
#### Feature updates
- Adds contextual menu for images.
- Adds search base and leader shortcuts.

#### Engineering updates
- Fixes staging bug where prior staged resources were not removed.
- Creates asset provider.

### 0.4.1
#### Engineering updates
- Fixes configuration path.

### 0.4.0

#### Feature updates
- Removes contextual search and card context.
- Adds Settings pane.
- Adds additional image source configuration.

#### Engineering updates
- Abstracts and adds image source protocol.
- Removes CardSearchFlow.
  
### 0.3.0

#### Feature updates
- Adds search by type filter.
- Adds contextual search for row.
- Adds persistent settings.
- Add color to stage and unstage buttons.
- Add menu option to navigate to image location.

#### Engineering updates
- Modularized SWUDB client.
- Modularized image cacher and deployment objects.
- Refactors `TradingCard` to be primary object.
- Adds mock settings.
- Moves persistent settings to `AppData > Local`.
- Moves persistent image storage to `Pictures` directory.
- Changed build to be single file exe.

### 0.2.0

#### Feature updates
- Reprograms designation to: `R4-MG`.
- Adds performance mode 🚗💨.
- Adds keyboard shortcuts for:
  -  Focus search bar: `Ctrl+L`
  -  Submit search: `Enter`
  -  Navigate search list: `Key down`, `Key up`
  -  Flip selected card: `Ctrl+F`
  -  Stage selected card: `Ctrl+NUM`
  -  Push staged cards to production: `Ctrl+P`
- Updates UI layouts and improves responsiveness.
- Improves UX.

#### Engineering updates
- Refactors project to split core functionality from UI functionality.
- Implements async call for:
  - Search
  - Image download and processing
- Adds observer/subscriber.
- Adds configuration.

### 0.1.0
- MVP