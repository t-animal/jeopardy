# Jeopardy (GTK)

A local Jeopardy-style quiz application built with Python + GTK. The app loads questions from YAML, manages players and scores, supports image/audio clues, and persists game progress to a YAML log.

## Installation

The project uses [uv](https://docs.astral.sh/uv/) for dependency and environment management.

Linux system prerequisites (required by `PyGObject`/`pycairo`) must be installed via your distro package manager before syncing Python dependencies.

Debian/Ubuntu example:

```bash
sudo apt install python3-dev libcairo2-dev libgirepository1.0-dev gir1.2-gtk-3.0
```

Create/sync the virtual environment with runtime + development dependencies:

```bash
uv sync --extra dev
```

If you only want runtime dependencies:

```bash
uv sync
```

## Running

```bash
uv run jeopardy --logFile log.yml --config config.yml
```

Equivalent module form:

```bash
uv run -m risiko_anwendung --logFile log.yml --config config.yml
```

If you get loads of GTK warnings it helps using a standard-conforming default template:

```bash
GTK_THEME=Adwaita:light uv run jeopardy --logFile log.yml --config config.yml
```

If you prefer a light theme for the application, append `--theme light`.

Example with the included sample config:

```bash
uv run jeopardy --logFile test.yml --config sample_config.yml
```

## Controls

Main screen keys:

- `Esc`: close current question / "Oops" action
- `F7`: toggle audio playback for current question
- `F8`: mark current question as "nobody knew it"
- `F9`: undo last action
- `F10`: redo last undone action
- `F11`: fullscreen (second monitor if available)
- `F12`: open RNG window
- `<Player key>`: player buzzes in

## Config file

The config should be a YAML file with a dictionary. The keys are category names, the entries are lists of clues. All categories must have an equal number of entries.

Supported answer forms:

- plain text
- `!double` (double jeopardy)
- `!image path/to/image.jpg`
- `!audio path/to/audio.mp3`
- combined tags: `!double*image`, `!double*audio`
- optional mapping form: `answer: ...` plus optional `question: ...`

Each list item can either be a legacy scalar/tagged value (backward compatible), or a mapping:

```yaml
- answer: !double "Some answer text"
  question: "What is the expected Jeopardy-style question?"
```

When a clue is opened, the optional `question` text is printed to the console (if present).

Sample files:

- `sample_config.yml`: new format using `answer` + optional `question`
- `sample_config_legacy.yml`: legacy scalar/tag format (still supported)

Example:

```yaml
Category A:
  - Some question.
  - |
    Some question with colons: or long text.

Category B:
  - !image path/to/image.jpg
  - !double*image path/to/imageDoubleJeopardy.jpg

Category C:
  - !double double jeopardy
  - another question

Category D:
  - answer: "This is the shown answer"
    question: "What is the hidden question?"
  - answer: !double*image path/to/image.jpg
    question: "What is shown in this image?"
```

## Repository overview

- `risiko_anwendung/`: main Python GTK app package
  - `model/`: player management, game table/results state, YAML config loading, and undo/redo history
  - `ui/`: game board window, player setup window, buzz handling, answer rendering (text/image/audio), and RNG window
  - `model/persistor/`: YAML snapshot persistence and restore logic for players/results
  - `__main__.py` + `custom*.css`: startup wiring, command-line options, and dark/light theme styling
- `hardware/`: optional buzzer integrations (Arduino and Launchpad scripts)
- `sample-assets/`: example media used by `sample_config.yml`

## Persistence and data

- The app appends snapshots to the log file passed via `--logFile`.
- Players and results are stored as YAML documents and restored on next start.
- `test.yml` is an example of persisted game history.

## Development

Type-checking is configured in `pyproject.toml` (Python 3.14 target):

```bash
uv run mypy
```
