
# R4-MG

**R4-MG** is an image asset loader and dashboard for streaming the Star Wars Unlimited TCG. It provides card search, preview, and production features for streamers, with integration for OBS and local asset management.

## Features

- Card search and preview
- Staging and production folders for stream assets
- OBS integration for live updates
- Locally managed sets and cache
- Keyboard shortcuts for fast workflow
- Custom directory search
- Configurable UI and behavior

See the [Changelog](./AppUI/Assets/Text/CHANGELOG.md) for recent updates.

## Installation

1. Download the [latest release build](https://github.com/hdchan/R4-MG/releases)
2. Extract the `R4-MG` folder.
3. Run `R4-MG.exe` or launch with Python:  
	`python app_ui.py`

## Usage

### Folders

- `cache/` — stores previewed cards from searches
- `production/` — stores cards for streaming; OBS should use files from here

### Dashboard

- Search for cards, stage them, and send to production
- The right panel lists `.png` files in `production/`
- Drag your own `.png` files into `production/` and refresh to use them

![Dashboard](./resources/dashboard.png)

### OBS Usage

- Source images from the `production/` folder in OBS
- Images update automatically when staged cards are sent to production

![OBS](./resources/obs.png)

### Keyboard Shortcuts

See [Keyboard Shortcuts](./AppUI/Assets/Text/shortcuts.md) for a full list.

## Contributing

Pull requests and issues are welcome! Please see the code style and contribution guidelines in the repo.

## License

This project is licensed under the MIT License.

## Attributions

- [SWU-DB.com](https://www.swu-db.com/api)
- [PySide6](https://doc.qt.io/qtforpython-6/)