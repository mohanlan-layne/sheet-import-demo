import pytest

from services import parser


def _non_empty(value):
    if not str(value).strip():
        return "Value cannot be empty"
    return None


def _positive_integer(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return "Value must be an integer"
    if number <= 0:
        return "Value must be greater than zero"
    return None


def test_parse_csv_with_validation_errors():
    csv_content = """name,age\nAlice,30\nBob,\n,27\n"""

    result = parser.parse_data(
        csv_content,
        filename="people.csv",
        schema={"name": _non_empty, "age": _positive_integer},
    )

    assert result.rows == [{"name": "Alice", "age": "30"}]
    assert [e.row_number for e in result.errors] == [3, 4]
    assert {(e.field, e.reason) for e in result.errors} == {
        ("age", "Value must be an integer"),
        ("name", "Value cannot be empty"),
    }


def test_parse_json_collects_errors():
    json_content = """[
        {"name": "Alice", "age": 30},
        {"name": "", "age": -2}
    ]"""

    result = parser.parse_data(
        json_content,
        filename="people.json",
        schema={"name": _non_empty, "age": _positive_integer},
    )

    assert result.rows == [{"name": "Alice", "age": 30}]
    assert result.errors == [
        parser.ValidationIssue(
            row_number=2,
            field="name",
            reason="Value cannot be empty",
        ),
        parser.ValidationIssue(
            row_number=2,
            field="age",
            reason="Value must be greater than zero",
        ),
    ]


def test_register_parser_override():
    def fake_parser(text: str):
        return [{"name": "Override"}]

    parser.register_parser(".fake", fake_parser, starting_row=5)

    result = parser.parse_data("irrelevant", filename="data.fake")

    assert result.rows == [{"name": "Override"}]
    assert result.errors == []
