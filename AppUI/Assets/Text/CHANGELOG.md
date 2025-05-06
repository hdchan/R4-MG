## Changelog

### 0.15.0
#### Feature updates
- Adds reset search functionality and shortcut
- Adds new variant type emojis

### 0.14.2
#### Feature updates
- Adds JTL local response
#### Hotfix
- Fix caching identifier conflict

### 0.14.1
#### Hotfix
- Fix edge case crash for no results

### 0.14.0
#### Feature updates
- Adds search source from FFG
- Removes swudb.com image source
- Updates "Quick Guide"
#### Engineering updates
- Adds pagination capabilities for `SearchTableViewController` and respective `CardSearchDataSource`

### 0.13.1
#### Hotfix
- Update shortcut list

### 0.13.0
#### Feature updates
- Updating rounded corners
- Update refresh to maintain staging resource state when refreshing
- Add deployment list sort
- Add shortcuts list

### 0.12.0
#### Feature updates
- Adds configuration for max rescale size
#### Engineering updates
- Adds new loading spinner prototype

### 0.11.0
#### Feature updates
- Adds window dimension configuration
- Add new card back
- Add creation date metadata
- Add recent search history
- Add recent publish history
- Add reset window size
- Close all windows when main window closed 
- Add markdown to about page
- Add duration string format

#### Engineering updates
- Adds abstract image processor
- Fix broken delegate to regenerate production image from link
- Refactor search datasource out of application core
- Refactoring assembly
- Renaming "ProviderProtocol" to "Providing"
- Create DependencyProviding
- Adding async timer to configuration manager
- Move platform service out of app core
- Removing app core
- Add time stamps to transmissions
- Moving data source into tableview and removing delegates
- Modularize table views
- Inverted shortcut binding
- Refactor MenuActionCoordinator
- Refactor ImageDeploymentViewController and encapsulating logic
- Fix proper datasource from preview
- Limit post processing from production file
- Add LocalResourceDataSourceProviding protocol to image preview
- Temp move async save to window
- Refactoring configuration manager
- Adding hook for application termination and saving
- Refactor configuration to recursively create key values if not exist
- Add configuration to hide deployment controls
- Add custom encoder
- Refactor configuration implementation

### 0.10.1
#### Hotfix
- Fix broken delegate to regenerate production image from link

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
- Consolidating LocalResourceFetchEvent
- Removing more dependencies
- Add old configuration to config updated event
- Move card aspect and type out of app core
- Arc refactors

### 0.9.3
#### Hotfix
- Fix production button state bug when redownloading asset

### 0.9.2
#### Hotfix
- Fix crash when re-downloading multiple times

### 0.9.1
#### Hotfix
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
#### Hotfix
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