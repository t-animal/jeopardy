from collections.abc import Sequence
import shutil
import sys
import textwrap


ESC = "\033"
CSI = f"{ESC}["
BOLD = f"{CSI}1m"
RESET = f"{CSI}0m"
CLEAR_LINE = f"{CSI}2K"
CARRIAGE_RETURN = "\r"
NEWLINE = "\n"
CURSOR_UP_SUFFIX = "A"
CURSOR_DOWN_SUFFIX = "B"

_last_question_box_height = 0



def print_controls() -> None:
    key_width = 14
    action_width = 12

    groups: Sequence[tuple[str, Sequence[tuple[str, str, str]]]] = [
        (
            "Clue controls",
            [
                ("Esc", "Close", 'Close current clue / "Oops" action'),
                ("F7", "Audio", "Toggle audio playback for current clue"),
                ("F8", "Nobody", 'Set current clue to "nobody knew it"'),
            ],
        ),
        (
            "History",
            [
                ("F9", "Undo", "Undo last action"),
                ("F10", "Redo", "Redo last undone action"),
            ],
        ),
        (
            "Grid controls",
            [
                ("F11", "Fullscreen", "Fullscreen (only on second monitor if available)"),
                ("F12", "RNG", 'Display the "RNG"'),
                ("<Player key>", "Buzz", "A player wants to answer"),
            ],
        ),
    ]

    print()
    print("-" * (key_width + action_width + 52))

    for index, (group_name, rows) in enumerate(groups):
        if index > 0:
            print()

        print(group_name)
        for key, action, description in rows:
            print(f"{BOLD}{action:<{action_width}}{RESET}{key:<{key_width}}{description}")

    print()


def print_current_question(category: str, row: int, question: str) -> None:
    global _last_question_box_height

    points = (row + 1) * 100
    category_prefix = "Category: "
    question_prefix = "Question: "

    category_line_plain = f"{category} ({points})"

    max_inner_width = _get_terminal_max_inner_width()
    category_lines = _wrap_line_with_indentation(category_line_plain, len(category_prefix), max_inner_width)
    question_lines = _wrap_line_with_indentation(question, len(question_prefix), max_inner_width)
    lines = _build_question_box_lines(category_lines, question_lines, category_prefix, question_prefix)

    clear_current_question_box()
    sys.stdout.write(CARRIAGE_RETURN)
    sys.stdout.write(NEWLINE.join(lines))
    sys.stdout.flush()

    _last_question_box_height = len(lines)

def clear_current_question_box() -> None:
    global _last_question_box_height

    if _last_question_box_height <= 0:
        return

    sys.stdout.write(CARRIAGE_RETURN)
    sys.stdout.write(_cursor_up(_last_question_box_height - 1))

    for index in range(_last_question_box_height):
        sys.stdout.write(CLEAR_LINE)
        if index < _last_question_box_height - 1:
            sys.stdout.write(_cursor_down(1))
            sys.stdout.write(CARRIAGE_RETURN)

    sys.stdout.write(_cursor_up(_last_question_box_height - 1))
    sys.stdout.write(CARRIAGE_RETURN)
    sys.stdout.flush()

    _last_question_box_height = 0

def _cursor_up(lines: int) -> str:
    if lines <= 0:
        return ""
    return f"{CSI}{lines}{CURSOR_UP_SUFFIX}"


def _cursor_down(lines: int) -> str:
    if lines <= 0:
        return ""
    return f"{CSI}{lines}{CURSOR_DOWN_SUFFIX}"


def _get_terminal_max_inner_width() -> int:
    terminal_width = shutil.get_terminal_size(fallback=(120, 24)).columns
    return max(20, terminal_width - 4)

def _wrap_line_with_indentation(text: str, indentation: int, max_inner_width: int) -> list[str]:
    text_width = max(1, max_inner_width - indentation)
    text_chunks = textwrap.wrap(
        text,
        width=text_width,
        break_long_words=True,
        break_on_hyphens=False,
    )

    if len(text_chunks) > 1:
        return [text_chunks[0]] + [(" " * indentation) + chunk for chunk in text_chunks[1:]]

    return text_chunks or [""]


def _build_question_box_lines(
    category_chunks: list[str],
    question_chunks: list[str],
    category_prefix: str,
    question_prefix: str,
) -> list[str]:
    category_lines = ([f"{category_prefix}{category_chunks[0]}"] + category_chunks[1:]) if category_chunks else []
    question_lines = ([f"{question_prefix}{question_chunks[0]}"] + question_chunks[1:]) if question_chunks else []
    plain_lines = category_lines + question_lines

    width = max(len(line) for line in plain_lines)

    top = f"┌{'─' * (width + 2)}┐"
    bottom = f"└{'─' * (width + 2)}┘"
    lines: list[str] = [top]

    _append_plain_box_lines(lines, category_lines, width)
    _append_question_box_lines(lines, question_chunks, question_prefix, width)

    lines.append(bottom)
    return lines


def _append_plain_box_lines(lines: list[str], content_lines: list[str], width: int) -> None:
    for content in content_lines:
        lines.append(f"│ {content.ljust(width)} │")


def _append_question_box_lines(lines: list[str], question_chunks: list[str], question_prefix: str, width: int) -> None:
    first_question_text = question_chunks[0]
    first_question_plain = question_prefix + first_question_text
    first_question_padding = width - len(first_question_plain)
    lines.append(
        f"│ {question_prefix}{BOLD}{first_question_text}{RESET}{' ' * first_question_padding} │"
    )

    for question_chunk in question_chunks[1:]:
        continuation_plain = question_chunk
        continuation_padding = width - len(continuation_plain)
        lines.append(
            f"│ {BOLD}{question_chunk}{RESET}{' ' * continuation_padding} │"
        )