# Changelog

## 0.25.0
### Feature
- Deprecating Local Set option
- Prevent empty space string search for local managed set
- Ignore non-alphanumeric chars for local searches
- Fix crash where image from history does not exist
- Fix potential crash with tab widget slot
- Fix melee.gg import to check for subtitle

### Engineering
- Removing unused assets
- PySide fix for combobox
- Moving async logic to data source
- Remove PyQt5 dependencies
- Fix fontMetrics.width migration to .horizontalAdvance
- Refactor custom dir to use unified search table combo
- Unifying search table for custom dir search and card search


## 0.24.1
### Hotfix
- Fix search history dropdown

## 0.24.0
### Feature
- Migrate to PySide6

## 0.23.0
### Feature
- set current tab on settings window
- Add grid layout for image generator

### Engineering
- card search preview refactors
- unified search table component
- Refactoring folder structures
- further unification of search table
- abstracting cached history
- refactoring cache events

## 0.22.1
### Hotfix
- Fix exception thrown when "Main Deck" text is passed for Melee.gg importer

## 0.22.0
### UI/UX Changes
- Adjust sizing policy for source label
- Add stage & publish to contextual menu on draft list
- Add crash logging
- Saving importer
- Removing unnecessary padding
- Add debug option
- Fine tuning image preview scale factor
- Simplifying style refactors
- Working sideboard imported
- Working import image downloader
- Add regenerate button
- Add toggle to auto generate
- Fix bug where cannot restage after exception
- Handling broken flow when none-valid resource is published

### Engineering
- Separate internal app dependencies protocol
- Moving worker logic to image generator class
- Add API to create new pack from list
- Refactor external dependency name to SWUApp
- Fixing broken async call backs
- Decoupling config dependency
- Fully decouple SWU app models from App UI
- Adding visual debug for deck preview

## 0.21.2
### Feature
- Add stage & publish to contextual menu on draft list

## 0.21.1
### Hotfix
- Adjust sizing policy for source label

## 0.21.0
### Added
- Panel for updating draft list image generator styles

## 0.20.1
### Hotfix
- Fixed crash where configuration was saving incorrect value

## 0.20.0
### Added
- Unifying menu refactors
- Add layout rearrangements
- Separate window for draft list image preview
- Add sideboard to draft list image preview
- Exporter updates
- Add emoji to draft list line items

### Engineering
- Add debug log check
- Generalizing window dimensions to their own config object
- Move client folder out of AppUI
- Fix serialized variant bug

## 0.19.1
### Hotfix
- Fixed crash where unregistered card variants are not recognized

## 0.19.0

### Added
- Enhanced deck export functionality
  - New card selection dialog for export configuration
  - Support for leader and base card selection
  - Sideboard toggle for main deck cards
  - Multiple export format support
- Draft list improvements
  - Optional image preview panel
  - Header cell styling support for pack previews
  - Card deployment and publishing workflow
  - Configurable preview visibility
- New configuration options
  - `DRAFT_LIST_STYLES` for customizing pack preview appearance
  - `DRAFT_LIST_ADD_CARD_DEPLOYMENT_DESTINATION` for deployment targets
  - `IS_DRAFT_LIST_IMAGE_PREVIEW_ENABLED` for toggling preview panel

### Changed
- Reorganized configuration structure
  - Moved default values to `default_style` method
  - Added type hints for configuration properties

### Breaking Changes
- Modified set download path in manage set list
  - **Note**: All sets will need to be redownloaded when upgrading from 0.18.0
  - This affects locally managed sets and their storage location

### Removed
- Deprecated search/publish history caching
- Legacy build and deployment tasks

## 0.18.0

### Added
- Add LoF set 5
- Remove resize label below deployment list
- Implement locally managed sets

### Engineering
- Naming and import refactors
- Moves card search cache directory
- Moves history files directory
- Abstracting local asset resource and working asset downloader
- Dependency refactors
- Refactor router logic
- Decouple search table combo view
- Refactor recent search DS to be part of existing card search DS
- Fix calling dead object in observer

## 0.17.0

### Added
- Adds custom directory search with working previews
- Adds Death Star plans disc spinner

### Engineering
- Graceful handling of folder related exceptions
- Updates local api client to use update local async logic
- Implement async local file retrieval
- Removes CardResourceProvider and ImageSource

## 0.16.0

### Added
- Adds preview image scale option

## 0.15.0

### Added
- Adds reset search functionality and shortcut
- Adds new variant type emojis
- Adds configuration for horizontal layout

## 0.14.2

### Added
- Adds JTL local response
#### Hotfix
- Fix caching identifier conflict

## 0.14.1

#### Hotfix
- Fix edge case crash for no results

## 0.14.0

### Added
- Adds search source from FFG
- Removes swudb.com image source
- Updates "Quick Guide"
#### Engineering updates
- Adds pagination capabilities for `SearchTableViewController` and respective `DataSourceCardSearch`

## 0.13.1

#### Hotfix
- Update shortcut list

## 0.13.0

### Added
- Updating rounded corners
- Update refresh to maintain staging resource state when refreshing
- Add deployment list sort
- Add shortcuts list

## 0.12.0

### Added
- Adds configuration for max rescale size
### Engineering updates
- Adds new loading spinner prototype

## 0.11.0

### Added
- Adds window dimension configuration
- Add new card back
- Add creation date metadata
- Add recent search history
- Add recent publish history
- Add reset window size
- Close all windows when main window closed 
- Add markdown to about page
- Add duration string format

### Engineering updates
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

## 0.10.1

#### Hotfix
- Fix broken delegate to regenerate production image from link

## 0.10.0

### Added
- Add clear cache and unstage all resources options
- Async image processing
- Fix production button state bug when redownloading asset
- Fix crash when re-downloading multiple times
- Fix update preview when changing image source

### Engineering updates
- Create App state model
- Abstracting os platform operations
- Add temp folder access
- Adjusting observation logic
- Consolidate downscale function
- Consolidate image processing
- Consolidating LocalCardResourceFetchEvent
- Removing more dependencies
- Add old configuration to config updated event
- Move card aspect and type out of app core
- Arc refactors

## 0.9.3

#### Hotfix
- Fix production button state bug when redownloading asset

## 0.9.2

#### Hotfix
- Fix crash when re-downloading multiple times

## 0.9.1

#### Hotfix
- Fix update preview when changing image source

## 0.9.0

### Added
- Adding option to change display name length
- Add local search
- Tweaking dimensions
- Add emojis for card aspects
#### Engineering updates
- Update functions and paths for mac compatibility
- Move mock data to app UI folder

## 0.8.0

### Added
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
  
### Engineering updates
- Handle empty production file edge case
  
## 0.7.0

### Added
- Adds image rotation
- Adds redownload option for image resource
- Adds regenerate preview
- Adds placeholder logo
  
### Engineering updates
- Adds additional sets for local mock

## 0.6.0

### Added
- Adds resource details setting
  
### Engineering updates
- Fixes staging bug where previous source image was staged

## 0.5.0

### Added
- Adds contextual menu for images.
- Adds search base and leader shortcuts.

### Engineering updates
- Fixes staging bug where prior staged resources were not removed.
- Creates asset provider.

## 0.4.1

#### Hotfix
- Fixes configuration path.

## 0.4.0

### Added
- Removes contextual search and card context.
- Adds Settings pane.
- Adds additional image source configuration.

### Engineering updates
- Abstracts and adds image source protocol.
- Removes CardSearchFlow.
  
## 0.3.0

### Added
- Adds search by type filter.
- Adds contextual search for row.
- Adds persistent settings.
- Add color to stage and unstage buttons.
- Add menu option to navigate to image location.

### Engineering updates
- Modularized SWUDB client.
- Modularized image cacher and deployment objects.
- Refactors `TradingCard` to be primary object.
- Adds mock settings.
- Moves persistent settings to `AppData > Local`.
- Moves persistent image storage to `Pictures` directory.
- Changed build to be single file exe.

## 0.2.0

### Added
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

### Engineering updates
- Refactors project to split core functionality from UI functionality.
- Implements async call for:
  - Search
  - Image download and processing
- Adds observer/subscriber.
- Adds configuration.

## 0.1.0
- MVP