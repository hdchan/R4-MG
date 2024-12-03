## Changelog

### 0.10.0
#### Feature updates
- Add clear cache and unstage all resources options
- Async image processing
- Fix production button state bug when redownloading asset
- Fix crash when re-downloading multiple times
- Fix update preview when changing image source

#### Engineering updates
- Create App state model
- Abstracting os platform operations
- Add temp folder access
- Adjusting observation logic
- Consolidate downscale function
- Consolidate image processing
- Consolidating LocalResourceEvent
- Removing more dependencies
- Add old configuration to config updated event
- Move card aspect and type out of app core
- Arc refactors

### 0.9.3
#### Feature updates
- Fix production button state bug when redownloading asset

### 0.9.2
#### Feature updates
- Fix crash when re-downloading multiple times

### 0.9.1
#### Feature updates
- Fix update preview when changing image source

### 0.9.0
#### Feature updates
- Adding option to change display name length
- Add local search
- Tweaking dimensions
- Add emojis for card aspects
#### Engineering updates
- Update functions and paths for mac compatibility
- Move mock data to app UI folder

### 0.8.0
#### Feature updates
- Add search shortcut helper text
- Fix loading spinner visual bug
- Adjusting layout for search pane
- Prevent auto scroll when disable button
- Add default image when generating new file
- Update performance mode to hide image preview
- Adjust height policy for scroll view
- Add R4 CTA
- Add sound effect for cta image
- Remove performance setting from settings page
  
#### Engineering updates
- Handle empty production file edge case
  
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