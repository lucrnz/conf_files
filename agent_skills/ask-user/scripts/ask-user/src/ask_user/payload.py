"""Parse, validate, and encode the ask-user JSON contract. Qt-free."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass

RESERVED_OTHER = "Other"


class PayloadError(Exception):
    """Invalid questions payload. Message is safe for stderr."""


@dataclass(frozen=True)
class Option:
    label: str
    description: str


@dataclass(frozen=True)
class Question:
    question: str
    options: tuple[Option, ...]
    multi_select: bool


@dataclass(frozen=True)
class Payload:
    questions: tuple[Question, ...]


@dataclass(frozen=True)
class Answer:
    question: str
    selected: tuple[str, ...]
    other: str | None


def loads(text: str) -> Payload:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise PayloadError("invalid JSON") from exc
    return parse_payload(data)


def parse_payload(data: object) -> Payload:
    if not isinstance(data, dict):
        raise PayloadError("payload must be a JSON object")
    if "questions" not in data:
        raise PayloadError("missing questions")
    raw_questions = data["questions"]
    if not isinstance(raw_questions, list):
        raise PayloadError("questions must be an array")
    if not raw_questions:
        raise PayloadError("questions must be non-empty")
    questions = tuple(_parse_question(item, index) for index, item in enumerate(raw_questions))
    return Payload(questions=questions)


def _parse_question(data: object, index: int) -> Question:
    where = f"question {index + 1}"
    if not isinstance(data, dict):
        raise PayloadError(f"{where} must be an object")
    if "question" not in data:
        raise PayloadError(f"{where} is missing question text")
    raw_text = data["question"]
    if not isinstance(raw_text, str):
        raise PayloadError(f"{where} text must be a string")
    text = raw_text.strip()
    if not text:
        raise PayloadError(f"{where} text must be non-empty")
    if "options" not in data:
        raise PayloadError(f"{where} is missing options")
    raw_options = data["options"]
    if not isinstance(raw_options, list):
        raise PayloadError(f"{where} options must be an array")
    if not raw_options:
        raise PayloadError(f"{where} options must be non-empty")
    options = tuple(_parse_option(item, where, opt_i) for opt_i, item in enumerate(raw_options))
    seen: set[str] = set()
    for option in options:
        if option.label in seen:
            raise PayloadError(f"{where} has duplicate label {option.label!r}")
        seen.add(option.label)
    if "multi_select" not in data:
        multi_select = False
    else:
        multi_select = data["multi_select"]
        if not isinstance(multi_select, bool):
            raise PayloadError(f"{where} multi_select must be a boolean")
    return Question(question=text, options=options, multi_select=multi_select)


def _parse_option(data: object, where: str, index: int) -> Option:
    opt_where = f"{where} option {index + 1}"
    if not isinstance(data, dict):
        raise PayloadError(f"{opt_where} must be an object")
    if "label" not in data:
        raise PayloadError(f"{opt_where} is missing label")
    raw_label = data["label"]
    if not isinstance(raw_label, str):
        raise PayloadError(f"{opt_where} label must be a string")
    label = raw_label.strip()
    if not label:
        raise PayloadError(f"{opt_where} label must be non-empty")
    if label == RESERVED_OTHER:
        raise PayloadError(f"{where} must not include a reserved {RESERVED_OTHER!r} option")
    if "description" not in data:
        description = ""
    else:
        raw_description = data["description"]
        if not isinstance(raw_description, str):
            raise PayloadError(f"{opt_where} description must be a string")
        description = raw_description
    return Option(label=label, description=description)


def page_complete(selected: Sequence[str], other: str | None) -> bool:
    if selected:
        return True
    return bool((other or "").strip())


def first_incomplete(pages: Sequence[tuple[Sequence[str], str | None]]) -> int | None:
    for index, (selected, other) in enumerate(pages):
        if not page_complete(selected, other):
            return index
    return None


def encode_answers(answers: Sequence[Answer]) -> str:
    payload = {
        "answers": [
            {
                "question": answer.question,
                "selected": list(answer.selected),
                "other": answer.other,
            }
            for answer in answers
        ]
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n"
