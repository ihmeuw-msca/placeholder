"""
===================
Data Specifications
===================

Gives data specifications that are used in
:class:`~placeholder.data.data.Data`.

A :class:`~placeholder.data.data.Data` class can be subclassed
for use in applications that have other standard columns outside
of the three default
"""

from dataclasses import dataclass
from typing import List

from placeholder.exceptions import PlaceholderError


class DataSpecCompatibilityError(PlaceholderError):
    """Error raised when the data specs are not compatible with the data frame to be used."""
    pass


@dataclass
class DataSpecs:

    col_obs: str
    col_obs_se: str
    col_groups: List[str] = None

    def __post_init__(self):
        pass

    @property
    def _col_attributes(self):
        return [x for x in dir(self) if isinstance(x, str)
                if x.startswith('col_')]

    @property
    def _data_attributes(self):
        return [getattr(self, x) for x in self._col_attributes]

    @staticmethod
    def _col_to_name(x: str) -> str:
        return ''.join(x.split('col_')[1:])

    def _validate_df(self, df):
        """Validates the existing

        Parameters
        ----------
        df
            A pandas.DataFrame to be validated with these specifications.

        """
        for column in self._data_attributes:
            if isinstance(column, str):
                column = [column]
            for col in column:
                if col not in df.columns:
                    raise DataSpecCompatibilityError(f"{col} is not in data columns: {df.columns}")


def _check_compatible_specs(specs: List[DataSpecs]):
    first_spec = specs[0]
    for i, spec in enumerate(specs[1:]):
        if sorted(spec._col_attributes) != sorted(first_spec._col_attributes):
            raise DataSpecCompatibilityError(
                "At least one data spec is different."
                f"Columns in spec 1 are {spec._col_attributes}."
                f"Columns in spec {i+2} are {spec._col_attributes}."
            )
