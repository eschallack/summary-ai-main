# Data model validation

import pandas as pd
from pydantic import BaseModel
from typing import List

class DataFrameSchema(BaseModel):
    column_name: str
    data_type: str
    optional: bool = False  # Defaults to False, making columns mandatory unless specified otherwise

def validate_dataframe(df: pd.DataFrame, expected_columns: List[DataFrameSchema]):
    for column in expected_columns:
        if column.column_name not in df.columns:
            if not column.optional:
                raise ValueError(f"Missing required column: {column.column_name}")
        else:
            if not pd.api.types.is_dtype_equal(df[column.column_name].dtype, column.data_type):
                raise TypeError(
                    f"Column '{column.column_name}' has invalid type. "
                    f"Expected {column.data_type}, got {df[column.column_name].dtype}."
                )
    print("DataFrame validation passed.")
    return True

bulk_short_synopsis_schema = [
    DataFrameSchema(column_name='id', data_type='object'),
    DataFrameSchema(column_name='title', data_type='object'),
    DataFrameSchema(column_name='synopsis', data_type='object'),
    DataFrameSchema(column_name='genre', data_type='object', optional=True),  # Optional
    DataFrameSchema(column_name='show_synopsis', data_type='object', optional=True),  # Optional
    DataFrameSchema(column_name='keywords', data_type='object', optional=True),  # Optional
]
