# CLAUDE.md

This file provides guidance to AI assistants working with this codebase.

## Project Overview

A Korean-language, browser-based daily time-tracking tool inspired by Notion. Users visually log activities across a 24-hour grid by dragging to select 10-minute blocks and applying color-coded activity labels. No build step, no backend, no dependencies.

## Repository Structure

```
Notion-template/
├── index.html    # App entry point and DOM structure
├── script.js     # All application logic
├── style.css     # Styling for the table and UI elements
└── README.md     # Minimal project readme
```

## Technology Stack

- **Vanilla HTML/CSS/JavaScript** — no frameworks, no bundlers, no package manager
- **localStorage** — only persistence mechanism (saves custom activities across sessions)
- **No external dependencies** — everything runs directly in the browser

## Application Architecture

### index.html
Defines the static structure:
- `<select id="activity">` — dropdown of available activities with `data-color` attributes
- `<button id="apply-btn">` — applies selected activity color to selected cells
- `<button id="add-activity-btn">` — toggles the activity creation modal
- `<div id="activity-modal">` — modal for adding custom activities (hidden by default)
- `<table id="time-table">` — populated dynamically by `script.js`

### script.js
All logic is in a single flat file:

| Function | Purpose |
|---|---|
| `loadActivities()` | Reads custom activities from localStorage on page load |
| `addActivityToSelect(name, color)` | Adds an `<option>` to the activity dropdown |
| `startSelection(event)` | `mousedown` handler — begins drag selection |
| `selectCell(event)` | `mouseover` handler — extends selection range during drag |
| `endSelection()` | `mouseup` handler — ends drag selection |
| `clearSelection()` | Removes `.selected` class from all cells |
| `getCellsInRange(start, end)` | Returns all non-hour cells between two cells (inclusive) |

**Event listeners (inline):**
- `applyBtn` click — applies the selected activity's color and name to `selectedCells`
- `addActivityBtn` click — toggles modal visibility
- `saveActivityBtn` click — validates, deduplicates, persists to localStorage, and adds to dropdown

### style.css
Minimal styles:
- Table uses `border-collapse: collapse`, centered with `margin: auto`
- Each `td` is `50px × 30px`
- `.selected` class applies `lightgray` background during drag preview

## Key Conventions

### Time Grid
- Rows cover hours **6:00 to 29:00** (`i` from 6 to 29), wrapping via `% 24` — so it shows 6 AM through 5 AM (next day)
- Columns represent 10-minute intervals (0, 10, 20, 30, 40, 50 minutes)
- Each data cell has `dataset.time` (e.g. `"14:30"`) and optionally `dataset.activity`
- Hour label cells have class `.hour-cell` and are excluded from selection logic

### Activity Colors
- Built-in activities and their colors are hardcoded in `index.html` via `data-color` attributes
- Custom activities are stored in localStorage as `[{ name: string, color: string }]`
- Color is stored as a hex string (e.g. `"#FF5733"`)

### Selection Mechanism
- Uses three mouse event listeners per cell (mousedown, mouseover, mouseup)
- `getCellsInRange` flattens all non-hour cells into an array and slices by index — selection is linear across the full grid, not confined to a single row

### UI Language
- All UI text is in **Korean**. Keep any new labels, alerts, or placeholder text in Korean to match the existing interface.

## Development Workflow

This project has no build process. To work on it:

1. Open `index.html` directly in a browser, or serve it with any static file server:
   ```bash
   python3 -m http.server 8000
   # or
   npx serve .
   ```
2. Edit HTML/CSS/JS files and reload the browser.
3. There are no tests, no linters, and no CI configuration.

## Git Conventions

- Default branch on the remote is `main`; local development has also used `master`
- Commit messages have been brief and informal (e.g. `"index.html"`, `"Add files via upload"`)
- No enforced commit message format

## What to Avoid

- Do not introduce a build system, bundler, or package manager unless explicitly requested — the project's simplicity is intentional
- Do not add frameworks (React, Vue, etc.) without explicit instruction
- Do not rename Korean UI strings to English without explicit instruction
- The `getCellsInRange` function selects cells linearly across the entire grid; be aware of this when modifying selection behavior
