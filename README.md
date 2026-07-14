# Browser Profile Manager

Browser Profile Manager is a premium Windows desktop productivity tool that
automatically discovers browser profiles from multiple Chromium-based
browsers and lets you instantly search, filter, and launch them from one
unified interface.

It is **not** a browser — it's a fast launcher that sits on top of the
browsers you already have installed.

## Features

- Automatic discovery of profiles from **Google Chrome**, **Microsoft
  Edge**, and **Brave Browser**
- Modular architecture — add support for Opera, Vivaldi, Arc, or plain
  Chromium by dropping in a small service class
- Instant, always-active search across profile name, account name, and
  browser
- Rounded browser filter pills with original browser logos
- Responsive profile grid (auto-adjusts, 5 cards per row on a full-size
  window)
- Single click to select, double click to launch, right click to open the
  profile's folder
- Full keyboard control (see below)
- One-time, explained permission prompt before any profile data is read
- All user data (permission choice, cache, logs) stored under
  `%LOCALAPPDATA%\BrowserProfileManager` — never inside `Program Files`
- Clean error handling with rotating log files, no crashes on missing
  browsers or unreadable profiles

## Tech stack

| Layer      | Technology                          |
|------------|--------------------------------------|
| Frontend   | HTML5, CSS3, vanilla JavaScript      |
| Backend    | Python 3.11+, Flask                  |
| Desktop    | PyWebView                            |
| Packaging  | PyInstaller (one-file `.exe`)        |
| Installer  | Inno Setup (`assets/installer.iss`)  |

## Folder structure

```
BrowserProfileManager/
├── app.py                    # Entry point: starts Flask + opens the PyWebView window
├── config.py                 # Paths, window size, browser registry, constants
├── requirements.txt
├── build.bat                 # One-command Windows build script
├── README.md
├── LICENSE
│
├── backend/
│   ├── app_factory.py        # Flask app factory
│   └── routes.py             # /api/* HTTP routes
│
├── services/
│   ├── base_service.py       # Shared Chromium profile discovery logic
│   ├── chrome_service.py
│   ├── edge_service.py
│   ├── brave_service.py
│   ├── profile_service.py    # Aggregates all browser services
│   ├── launcher_service.py   # Launches profiles / opens folders
│   └── permission_service.py # Persists the user's permission decision
│
├── utils/
│   ├── logger.py              # Rotating file + console logging
│   ├── json_store.py          # Safe JSON read/write helpers
│   └── paths.py                # Executable & avatar resolution helpers
│
├── templates/
│   └── index.html
│
├── static/
│   ├── css/styles.css
│   ├── js/app.js
│   └── images/                # Browser logos + default avatar (SVG)
│
├── icons/                     # app_icon(5).ico is generated at build time
├── scripts/
│   └── generate_icon.py       # Draws icons/app_icon(5).ico with Pillow
└── assets/
    └── installer.iss          # Inno Setup script
```

## Installation

Requires **Python 3.11+** on Windows.

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Running (development)

```bat
python app.py
```

This starts a local Flask server on `127.0.0.1` (an unused port is chosen
automatically) and opens it inside a native desktop window via PyWebView.
No browser tab, no visible console window in the packaged build.

## Building the executable

```bat
build.bat
```

This will:

1. Create/activate a virtual environment
2. Install dependencies from `requirements.txt`
3. Generate `icons/app_icon(5).ico`
4. Run PyInstaller to produce a single-file executable at
   `dist\BrowserProfileManager.exe`

## Creating an installer

Once `dist\BrowserProfileManager.exe` exists, install [Inno Setup](https://jrsoftware.org/isinfo.php)
and compile `assets\installer.iss`:

```bat
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" assets\installer.iss
```

The installer is written to `dist_installer\BrowserProfileManagerSetup.exe`.

## Keyboard shortcuts

| Key           | Action                          |
|---------------|----------------------------------|
| Arrow keys    | Move selection across the grid   |
| Enter         | Launch the selected profile (or focus search if nothing is selected) |
| Ctrl + F      | Focus the search bar             |
| Escape        | Clear the search / unfocus       |

Mouse: single click selects a card, double click launches it, right click
opens its profile folder.

## Permissions & privacy

On first launch, the app explains why it needs to read local browser
profile data (name, account label, avatar image) and asks for a one-time
confirmation. The decision is stored locally in
`%LOCALAPPDATA%\BrowserProfileManager\permission.json` and never sent
anywhere — everything in this app runs entirely on your machine.

## User data locations

All writable data lives under `%LOCALAPPDATA%\BrowserProfileManager\`:

- `permission.json` — the stored permission decision
- `settings.json` — reserved for future user settings
- `cache/avatars/` — reserved avatar cache directory
- `logs/app.log` — rotating application log (5 x 2MB)

Nothing is ever written inside `Program Files`.

## Extending to new browsers

Every currently supported browser is Chromium-based and shares identical
profile discovery logic (`services/base_service.py`). To add a new one
(Opera, Vivaldi, Arc, plain Chromium):

1. Add its `User Data` path and executable candidates to `config.py`
2. Create a new `services/<browser>_service.py` subclassing
   `ChromiumBrowserService` with just its id/name/path
3. Register it in `services/profile_service.py`
4. Add its logo to `static/images/browsers/` and a display name to
   `config.BROWSER_DISPLAY_NAMES`

No other code changes are required.

## Screenshots

_Add screenshots of the running application here once captured on a
Windows machine (`docs/screenshots/`)._

## License

MIT — see [LICENSE](LICENSE).
