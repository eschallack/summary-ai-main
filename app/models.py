import pandas as pd
from pydantic import BaseModel
from typing import List

# Define the schema model
class DataFrameSchema(BaseModel):
    column_name: str
    data_type: str
    optional: bool = False  # Defaults to False, making columns mandatory unless specified otherwise

# Validation function
def validate_dataframe(df: pd.DataFrame, expected_columns: List[DataFrameSchema]):
    for column in expected_columns:
        if column.column_name not in df.columns:
            if not column.optional:  # Raise an error for missing mandatory columns
                raise ValueError(f"Missing required column: {column.column_name}")
        else:
            # Validate the data type only if the column exists
            if not pd.api.types.is_dtype_equal(df[column.column_name].dtype, column.data_type):
                raise TypeError(
                    f"Column '{column.column_name}' has invalid type. "
                    f"Expected {column.data_type}, got {df[column.column_name].dtype}."
                )
    print("DataFrame validation passed.")
    return True
bulk_short_synopsis_schema = [
    DataFrameSchema(column_name='qd', data_type='object'),
    DataFrameSchema(column_name='title', data_type='object'),
    DataFrameSchema(column_name='synopsis', data_type='object'),
    DataFrameSchema(column_name='genre', data_type='object', optional=True),  # Optional
    DataFrameSchema(column_name='show_synopsis', data_type='object', optional=True),  # Optional
    DataFrameSchema(column_name='keywords', data_type='object', optional=True),  # Optional
]
if __name__ == "__main__":
    data = {
        'qd': ['Q1', 'Q2'],
        'title': ['Title 1', 'Title 2'],
        'synopsis': ['A brief summary.', 'Another summary.'],
        'show_synopsis': ['Yes', 'No'],
    }
    df = pd.DataFrame(data)
    try:
        validate_dataframe(df, bulk_short_synopsis_schema)
    except (ValueError, TypeError) as e:
        print(f"Validation failed: {e}")
