# CLAUDE.md

This file provides guidance to AI assistants working with this codebase.

## Project Overview

A Windows desktop widget for daily time-tracking and reflection. Users drag to create activity blocks on a vertical timeline, log reflections (잘한 점 / 아쉬운 점 / 나아갈 점) per activity, and search past activities by tag.

## Repository Structure

```
├── main.py        # Entry point — initialises DB, creates QApplication, system tray
├── widget.py      # MainWidget — frameless always-on-top window (header + scroll area)
├── timeline.py    # TimelineWidget — custom QWidget, all drag/paint logic
├── dialogs.py     # AddActivityDialog, ActivityDetailDialog (reflection inputs)
├── search.py      # SearchWindow — tag-based full-history search
├── database.py    # SQLite CRUD via sqlite3 standard library
├── models.py      # Activity and Reflection dataclasses
├── timelog.db     # Auto-created SQLite database (not committed)
└── README.md      # Korean-language setup and usage guide
```

## Technology Stack

- **Python 3.10+** with **PyQt6** — only external dependency
- **SQLite** via the standard library `sqlite3` module
- No build system, no bundler, no other dependencies
- Run directly: `python main.py`

## Application Architecture

### Data layer (`models.py` → `database.py`)

| Model | Fields |
|---|---|
| `Activity` | `id`, `date`, `start_time`, `end_time`, `name`, `tags: list[str]`, `color` |
| `Reflection` | `activity_id`, `good`, `bad`, `next_steps` (each a `list[str]` of 3 items) |

`database.py` functions: `init_db`, `save_activity`, `get_activities_by_date`, `delete_activity`, `save_reflection`, `get_reflection`, `search_by_tag`.

### Timeline widget (`timeline.py`)

The most complex module. Key design points:

- **Time representation**: times stored as `"HH:MM"` strings where `HH` can exceed 23 (e.g. `"25:30"` = 1:30 AM next day). `time_to_min` converts to raw minutes from midnight.
- **Layout constants**: `START_HOUR = 6`, `END_HOUR = 26`, `HOUR_HEIGHT = 64` px, `LABEL_WIDTH = 44` px, `SNAP_MIN = 10` minutes.
- **Drag state machine**: `drag_mode` ∈ `{'create', 'move', 'resize_top', 'resize_bottom', None}`. `drag_moved: bool` distinguishes a click (show detail dialog) from an actual drag. The threshold is 4 px.
- **Mouse events**: `mousePressEvent` sets mode; `mouseMoveEvent` updates positions; `mouseReleaseEvent` commits changes to DB or opens dialogs.
- **`paintEvent`**: draws hour grid, activity blocks (with tag labels for tall blocks), and a semi-transparent drag-preview rectangle during 'create' drags.

### Widget window (`widget.py`)

- `MainWidget` is a `FramelessWindowHint + WindowStaysOnTopHint + Tool` window.
- Header is draggable to move the widget around the screen.
- Contains a `QScrollArea` (640 px tall) holding the `TimelineWidget` (1280 px = 20 h × 64 px).
- Default scroll position: 08:00 (2 hours from start).

### Dialogs (`dialogs.py`)

- `AddActivityDialog`: captures name + comma-separated tags. First tag drives the block color via `_tag_color()` (MD5 hash → palette index).
- `ActivityDetailDialog`: shows activity header and three `_ReflectionSection` widgets (3 `QLineEdit` inputs each). Saves on "저장" button.

### Search (`search.py`)

- `SearchWindow` is a separate `Qt.WindowType.Window`.
- Calls `db.search_by_tag(tag)` which does a SQL `LIKE '%"tag"%'` match against the JSON tags column.
- Results rendered as `_ResultCard` widgets inside a `QScrollArea`.

## Key Conventions

### Time system
- Timeline covers **06:00–26:00** (6 AM to 2 AM next day).
- Times stored as `"HH:MM"` with hours potentially > 23 to avoid date rollover ambiguity.
- All pixel ↔ time conversions go through `min_to_y` / `y_to_min` / `time_to_min` in `timeline.py`.
- Always snap to `SNAP_MIN = 10` minute intervals.

### Colors
- Each activity's color is derived from its first tag using `tag_color()` (MD5 → index into `TAG_COLORS` list).
- Tagless activities use `TAG_COLORS[0]` (#4A90D9).

### UI language
- All UI text is in **Korean**. Keep any new labels, alerts, and placeholder text in Korean.

### Dark theme
- Background: `#13131F` (timeline), `#1A1A2A` / `#1E1E2E` (panels), `#232336` (header).
- Accent: `#4A90D9` (blue), `#6478DC` (drag preview border).
- Text: `#FFFFFF` (primary), `#CCCCDD` (secondary), `#666888` (muted).

## Development Workflow

No build step required:

```bash
pip install PyQt6
python main.py
```

`timelog.db` is created automatically on first run next to `main.py`.

## What to Avoid

- Do not introduce additional dependencies beyond PyQt6.
- Do not change the time representation to `datetime` objects in the DB — keep times as `"HH:MM"` strings with 24+ hour support.
- Do not break the `drag_moved` flag logic in `TimelineWidget` — it is the only thing distinguishing a click from a drag.
- Do not rename Korean UI strings to English.
- The `SNAP_MIN` constant is used throughout; adjust only via the constant, never hardcode `10`.
