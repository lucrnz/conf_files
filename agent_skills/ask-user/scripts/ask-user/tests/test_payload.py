from __future__ import annotations

import json
import sys

import pytest

from ask_user.payload import (
    Answer,
    Option,
    Payload,
    PayloadError,
    Question,
    encode_answers,
    first_incomplete,
    loads,
    parse_payload,
    page_complete,
)

SINGLE = {
    "questions": [
        {
            "question": "When does the agent use this?",
            "options": [
                {"label": "Fallback only", "description": "Native tool when present."},
                {"label": "Always this skill", "description": "Ignore the native tool."},
            ],
            "multi_select": False,
        }
    ]
}

MULTI = {
    "questions": [
        {
            "question": "Which extras?",
            "options": [
                {"label": "A", "description": "one"},
                {"label": "B", "description": "two"},
            ],
            "multi_select": True,
        }
    ]
}


def test_valid_single_select() -> None:
    payload = parse_payload(SINGLE)
    assert payload == Payload(
        questions=(
            Question(
                question="When does the agent use this?",
                options=(
                    Option(label="Fallback only", description="Native tool when present."),
                    Option(label="Always this skill", description="Ignore the native tool."),
                ),
                multi_select=False,
            ),
        )
    )


def test_valid_multi_select() -> None:
    payload = parse_payload(MULTI)
    assert payload.questions[0].multi_select is True
    assert [option.label for option in payload.questions[0].options] == ["A", "B"]


def test_loads_round_trip_text() -> None:
    payload = loads(json.dumps(SINGLE))
    assert payload.questions[0].question == "When does the agent use this?"


def test_preview_and_extra_keys_ignored() -> None:
    payload = parse_payload(
        {
            "extra": 1,
            "questions": [
                {
                    "question": " Pick? ",
                    "note": "ignored",
                    "options": [
                        {
                            "label": " Yes ",
                            "description": "ok",
                            "preview": {"any": True},
                            "hint": "nope",
                        }
                    ],
                }
            ],
        }
    )
    question = payload.questions[0]
    assert question.question == "Pick?"
    assert question.multi_select is False
    assert question.options == (Option(label="Yes", description="ok"),)


def test_missing_description_becomes_empty() -> None:
    payload = parse_payload(
        {"questions": [{"question": "Q", "options": [{"label": "A"}]}]}
    )
    assert payload.questions[0].options[0].description == ""


def test_invalid_json() -> None:
    with pytest.raises(PayloadError, match="invalid JSON"):
        loads("not-json")


def test_empty_text() -> None:
    with pytest.raises(PayloadError, match="invalid JSON"):
        loads("")


def test_non_object() -> None:
    with pytest.raises(PayloadError, match="JSON object"):
        parse_payload([])


def test_missing_questions() -> None:
    with pytest.raises(PayloadError, match="missing questions"):
        parse_payload({})


def test_empty_questions() -> None:
    with pytest.raises(PayloadError, match="non-empty"):
        parse_payload({"questions": []})


def test_whitespace_only_question() -> None:
    with pytest.raises(PayloadError, match="non-empty"):
        parse_payload({"questions": [{"question": "  ", "options": [{"label": "A"}]}]})


def test_empty_options() -> None:
    with pytest.raises(PayloadError, match="options must be non-empty"):
        parse_payload({"questions": [{"question": "Q", "options": []}]})


def test_empty_label() -> None:
    with pytest.raises(PayloadError, match="label must be non-empty"):
        parse_payload({"questions": [{"question": "Q", "options": [{"label": "  "}]}]})


def test_duplicate_labels() -> None:
    with pytest.raises(PayloadError, match="duplicate label"):
        parse_payload(
            {
                "questions": [
                    {
                        "question": "Q",
                        "options": [
                            {"label": "A"},
                            {"label": " A "},
                        ],
                    }
                ]
            }
        )


def test_reserved_other_label() -> None:
    with pytest.raises(PayloadError, match="Other"):
        parse_payload(
            {"questions": [{"question": "Q", "options": [{"label": "Other"}]}]}
        )


def test_non_bool_multi_select() -> None:
    with pytest.raises(PayloadError, match="multi_select"):
        parse_payload(
            {
                "questions": [
                    {"question": "Q", "options": [{"label": "A"}], "multi_select": "yes"}
                ]
            }
        )


def test_non_string_description() -> None:
    with pytest.raises(PayloadError, match="description"):
        parse_payload(
            {"questions": [{"question": "Q", "options": [{"label": "A", "description": 1}]}]}
        )


def test_page_complete() -> None:
    assert page_complete(("A",), None) is True
    assert page_complete((), " typed ") is True
    assert page_complete((), None) is False
    assert page_complete((), "   ") is False


def test_first_incomplete() -> None:
    pages = [(("A",), None), ((), None), ((), "x")]
    assert first_incomplete(pages) == 1
    assert first_incomplete([(("A",), None), ((), "x")]) is None


def test_encode_answers_compact() -> None:
    text = encode_answers(
        [
            Answer(question="When?", selected=("Fallback only",), other=None),
            Answer(question="Extras?", selected=("A", "B"), other="custom"),
        ]
    )
    assert text.endswith("\n")
    assert text.count("\n") == 1
    expected = json.dumps(json.loads(text), ensure_ascii=False, separators=(",", ":")) + "\n"
    assert text == expected
    assert json.loads(text) == {
        "answers": [
            {"question": "When?", "selected": ["Fallback only"], "other": None},
            {"question": "Extras?", "selected": ["A", "B"], "other": "custom"},
        ]
    }


def test_payload_import_does_not_load_pyside6() -> None:
    sys.modules.pop("ask_user.payload", None)
    before = {name for name in sys.modules if name == "PySide6" or name.startswith("PySide6.")}
    import ask_user.payload as payload_mod

    after = {name for name in sys.modules if name == "PySide6" or name.startswith("PySide6.")}
    assert payload_mod.RESERVED_OTHER == "Other"
    assert after == before
