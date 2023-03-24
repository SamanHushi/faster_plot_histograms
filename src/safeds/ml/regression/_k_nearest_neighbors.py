# noinspection PyProtectedMember
import safeds.ml._util_sklearn
from safeds.data.tabular.containers import Table, TaggedTable
from sklearn.neighbors import KNeighborsRegressor

from ._regressor import Regressor


# noinspection PyProtectedMember
class KNearestNeighbors(Regressor):
    """
    This class implements K-nearest-neighbors regressor. It can only be trained on a tagged table.

    Parameters
    ----------
    n_neighbors : int
        The number of neighbors to be interpolated with. Has to be less than or equal than the sample size.
    """

    def __init__(self, n_neighbors: int) -> None:
        self._regression = KNeighborsRegressor(n_neighbors)
        self.target_name = ""

    def fit(self, tagged_table: TaggedTable) -> None:
        """
        Fit this model given a tagged table.

        Parameters
        ----------
        tagged_table : TaggedTable
            The tagged table containing the feature and target vectors.

        Raises
        ------
        LearningError
            If the tagged table contains invalid values or if the training failed.
        """
        self.target_name = safeds.ml._util_sklearn.fit(self._regression, tagged_table)

    def predict(self, dataset: Table) -> Table:
        """
        Predict a target vector using a dataset containing feature vectors. The model has to be trained first.

        Parameters
        ----------
        dataset : Table
            The dataset containing the feature vectors.

        Returns
        -------
        table : Table
            A dataset containing the given feature vectors and the predicted target vector.

        Raises
        ------
        PredictionError
            If prediction with the given dataset failed.
        """
        return safeds.ml._util_sklearn.predict(
            self._regression,
            dataset,
            self.target_name,
        )
