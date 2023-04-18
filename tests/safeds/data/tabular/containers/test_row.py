from typing import Any

import pytest
from safeds.data.tabular.containers import Row, Table
from safeds.data.tabular.exceptions import UnknownColumnNameError
from safeds.data.tabular.typing import ColumnType, Integer, Schema, String


class TestFromDict:
    @pytest.mark.parametrize(
        ("data", "expected"),
        [
            (
                {},
                Row([]),
            ),
            (
                {
                    "a": 1,
                    "b": 2,
                },
                Row([1, 2], schema=Schema({"a": Integer(), "b": Integer()})),
            ),
        ],
    )
    def test_should_create_row_from_dict(self, data: dict[str, Any], expected: Row) -> None:
        assert Row.from_dict(data) == expected


class TestInit:
    @pytest.mark.parametrize(
        ("row", "expected"),
        [
            (Row([], Schema({})), Schema({})),
            (Row([0], Schema({"col1": Integer()})), Schema({"col1": Integer()})),
            (
                Row([0, "a"], Schema({"col1": Integer(), "col2": String()})),
                Schema({"col1": Integer(), "col2": String()}),
            ),
        ],
    )
    def test_should_use_the_schema_if_passed(self, row: Row, expected: Schema) -> None:
        assert row._schema == expected

    @pytest.mark.parametrize(
        ("row", "expected"),
        [
            (Row([]), Schema({})),
            (Row([0]), Schema({"column_0": Integer()})),
        ],
    )
    def test_should_infer_the_schema_if_not_passed(self, row: Row, expected: Schema) -> None:
        assert row._schema == expected


class TestEq:
    @pytest.mark.parametrize(
        ("row1", "row2", "expected"),
        [
            (Row.from_dict({}), Row.from_dict({}), True),
            (Row.from_dict({"col1": 0}), Row.from_dict({"col1": 0}), True),
            (Row.from_dict({"col1": 0}), Row.from_dict({"col1": 1}), False),
            (Row.from_dict({"col1": 0}), Row.from_dict({"col2": 0}), False),
            (Row.from_dict({"col1": 0}), Row.from_dict({"col1": "a"}), False),
        ],
    )
    def test_should_return_whether_two_rows_are_equal(self, row1: Row, row2: Row, expected: bool) -> None:
        assert (row1 == row2) == expected

    @pytest.mark.parametrize(
        ("row", "other"),
        [
            (Row.from_dict({"col1": 0}), None),
            (Row.from_dict({"col1": 0}), Table([])),
        ],
    )
    def test_should_return_not_implemented_if_other_is_not_row(self, row: Row, other: Any) -> None:
        assert (row.__eq__(other)) is NotImplemented


class TestGetitem:
    @pytest.mark.parametrize(
        ("row", "column_name", "expected"),
        [
            (Row.from_dict({"col1": 0}), "col1", 0),
            (Row.from_dict({"col1": 0, "col2": "a"}), "col2", "a"),
        ],
    )
    def test_should_return_the_value_in_the_column(self, row: Row, column_name: str, expected: Any) -> None:
        assert row[column_name] == expected

    @pytest.mark.parametrize(
        ("row", "column_name"),
        [
            (Row.from_dict({}), "col1"),
            (Row.from_dict({"col1": 0}), "col2"),
        ],
    )
    def test_should_raise_if_column_does_not_exist(self, row: Row, column_name: str) -> None:
        with pytest.raises(UnknownColumnNameError):
            # noinspection PyStatementEffect
            row[column_name]


class TestHash:
    @pytest.mark.parametrize(
        ("row1", "row2"),
        [
            (Row.from_dict({}), Row.from_dict({})),
            (Row.from_dict({"col1": 0}), Row.from_dict({"col1": 0})),
        ],
    )
    def test_should_return_same_hash_for_equal_rows(self, row1: Row, row2: Row) -> None:
        assert hash(row1) == hash(row2)

    @pytest.mark.parametrize(
        ("row1", "row2"),
        [
            (Row.from_dict({"col1": 0}), Row.from_dict({"col1": 1})),
            (Row.from_dict({"col1": 0}), Row.from_dict({"col2": 0})),
            (Row.from_dict({"col1": 0}), Row.from_dict({"col1": "a"})),
        ],
    )
    def test_should_return_different_hash_for_unequal_rows(self, row1: Row, row2: Row) -> None:
        assert hash(row1) != hash(row2)


class TestIter:
    @pytest.mark.parametrize(
        ("row", "expected"),
        [
            (Row.from_dict({}), []),
            (Row.from_dict({"col1": 0}), ["col1"]),
        ],
    )
    def test_should_return_an_iterator_for_the_column_names(self, row: Row, expected: list[str]) -> None:
        assert list(row) == expected


class TestLen:
    @pytest.mark.parametrize(
        ("row", "expected"),
        [
            (Row.from_dict({}), 0),
            (Row.from_dict({"col1": 0, "col2": "a"}), 2),
        ],
    )
    def test_should_return_the_number_of_columns(self, row: Row, expected: int) -> None:
        assert len(row) == expected


class TestGetValue:
    @pytest.mark.parametrize(
        ("row", "column_name", "expected"),
        [
            (Row.from_dict({"col1": 0}), "col1", 0),
            (Row.from_dict({"col1": 0, "col2": "a"}), "col2", "a"),
        ],
    )
    def test_should_return_the_value_in_the_column(self, row: Row, column_name: str, expected: Any) -> None:
        assert row.get_value(column_name) == expected

    @pytest.mark.parametrize(
        ("row", "column_name"),
        [
            (Row.from_dict({}), "col1"),
            (Row.from_dict({"col1": 0}), "col2"),
        ],
    )
    def test_should_raise_if_column_does_not_exist(self, row: Row, column_name: str) -> None:
        with pytest.raises(UnknownColumnNameError):
            row.get_value(column_name)


class TestHasColumn:
    @pytest.mark.parametrize(
        ("row", "column_name", "expected"),
        [
            (Row.from_dict({}), "col1", False),
            (Row.from_dict({"col1": 0}), "col1", True),
            (Row.from_dict({"col1": 0}), "col2", False),
        ],
    )
    def test_should_return_whether_the_row_has_the_column(self, row: Row, column_name: str, expected: bool) -> None:
        assert row.has_column(column_name) == expected


class TestGetColumnNames:
    @pytest.mark.parametrize(
        ("row", "expected"),
        [
            (Row.from_dict({}), []),
            (Row.from_dict({"col1": 0}), ["col1"]),
        ],
    )
    def test_should_return_the_column_names(self, row: Row, expected: list[str]) -> None:
        assert row.get_column_names() == expected


class TestGetTypeOfColumn:
    @pytest.mark.parametrize(
        ("row", "column_name", "expected"),
        [
            (Row.from_dict({"col1": 0}), "col1", Integer()),
            (Row.from_dict({"col1": 0, "col2": "a"}), "col2", String()),
        ],
    )
    def test_should_return_the_type_of_the_column(self, row: Row, column_name: str, expected: ColumnType) -> None:
        assert row.get_type_of_column(column_name) == expected

    @pytest.mark.parametrize(
        ("row", "column_name"),
        [
            (Row.from_dict({}), "col1"),
            (Row.from_dict({"col1": 0}), "col2"),
        ],
    )
    def test_should_raise_if_column_does_not_exist(self, row: Row, column_name: str) -> None:
        with pytest.raises(UnknownColumnNameError):
            row.get_type_of_column(column_name)


class TestCount:
    @pytest.mark.parametrize(
        ("row", "expected"),
        [
            (Row.from_dict({}), 0),
            (Row.from_dict({"col1": 0, "col2": "a"}), 2),
        ],
    )
    def test_should_return_the_number_of_columns(self, row: Row, expected: int) -> None:
        assert row.count() == expected


class TestToDict:
    @pytest.mark.parametrize(
        ("row", "expected"),
        [
            (
                Row([]),
                {},
            ),
            (
                Row([1, 2], schema=Schema({"a": Integer(), "b": Integer()})),
                {
                    "a": 1,
                    "b": 2,
                },
            ),
        ],
    )
    def test_should_return_dict_for_table(self, row: Row, expected: dict[str, Any]) -> None:
        assert row.to_dict() == expected
