import pandas as pd
import pytest
from safe_ds.data import Column
from safe_ds.exceptions import ColumnLengthMismatchError
from safe_ds.regression.metrics import _check_metrics_preconditions


@pytest.mark.parametrize(
    "actual, expected, error",
    [
        (["A", "B"], [1, 2], TypeError),
        ([1, 2], ["A", "B"], TypeError),
        ([1, 2, 3], [1, 2], ColumnLengthMismatchError),
    ],
)
def test_check_metrics_preconditions(
    actual: list[str | int], expected: list[str | int], error: type[Exception]
) -> None:
    actual_column = Column(
        pd.Series(actual),
        "actual",
    )
    expected_column = Column(
        pd.Series(expected),
        "expected",
    )
    with pytest.raises(error):
        _check_metrics_preconditions(actual_column, expected_column)