import pytest
from safeds.data.labeled.containers import TabularDataset
from safeds.data.tabular.containers import Table
from safeds.exceptions import OutOfBoundsError
from safeds.ml.classical.classification import GradientBoostingClassifier


@pytest.fixture()
def training_set() -> TabularDataset:
    table = Table({"col1": [1, 2, 3, 4], "col2": [1, 2, 3, 4]})
    return table.to_tabular_dataset(target_name="col1")


class TestNumberOfTrees:
    def test_should_be_passed_to_fitted_model(self, training_set: TabularDataset) -> None:
        fitted_model = GradientBoostingClassifier(number_of_trees=2).fit(training_set)
        assert fitted_model.number_of_trees == 2

    def test_should_be_passed_to_sklearn(self, training_set: TabularDataset) -> None:
        fitted_model = GradientBoostingClassifier(number_of_trees=2).fit(training_set)
        assert fitted_model._wrapped_model is not None
        assert fitted_model._wrapped_model.n_estimators == 2

    @pytest.mark.parametrize("number_of_trees", [-1, 0], ids=["minus_one", "zero"])
    def test_should_raise_if_less_than_1(self, number_of_trees: int) -> None:
        with pytest.raises(OutOfBoundsError):
            GradientBoostingClassifier(number_of_trees=number_of_trees)


class TestLearningRate:
    def test_should_be_passed_to_fitted_model(self, training_set: TabularDataset) -> None:
        fitted_model = GradientBoostingClassifier(learning_rate=2).fit(training_set)
        assert fitted_model.learning_rate == 2

    def test_should_be_passed_to_sklearn(self, training_set: TabularDataset) -> None:
        fitted_model = GradientBoostingClassifier(learning_rate=2).fit(training_set)
        assert fitted_model._wrapped_model is not None
        assert fitted_model._wrapped_model.learning_rate == 2

    @pytest.mark.parametrize("learning_rate", [-1.0, 0.0], ids=["minus_one", "zero"])
    def test_should_raise_if_less_than_or_equal_to_0(self, learning_rate: float) -> None:
        with pytest.raises(OutOfBoundsError):
            GradientBoostingClassifier(learning_rate=learning_rate)
