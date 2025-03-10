# import datetime
# import os
import pandas as pd
from src import env_vars
# from src.repositories.s3_repository import S3Repository
from io import BytesIO

# s3_bucket = env_vars.S3_BUCKET
# s3_repository = S3Repository(s3_bucket)

# Creating buffer to append data in excel file for Upload
def create_excel_buffer(df_indices):
    # Create an in-memory Excel file using BytesIO
    excel_buffer = BytesIO()
    
    # Use pd.ExcelWriter to write the DataFrames into the in-memory buffer
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df_indices.to_excel(writer, sheet_name='Indices Disponibilidad', index=False)
        
    # Ensure the buffer pointer is at the start for upload
    excel_buffer.seek(0)
    return excel_buffer


def export_excel(body):
    # Extract indices_disponibilidad data
    indices_data = body.get('indices_disponibilidad', [])
    print("indices_data::",indices_data)

    # Convert indices_disponibilidad to DataFrame
    df_indices = pd.DataFrame(indices_data)[["ci","vocablo", "indice"]]
    print("Preview of df_indices DataFrame:")
    print(df_indices.head())

    df_indices.columns = ["CI", "Vocabulary", "Index"]
    excel_buffer = create_excel_buffer(df_indices)

    return excel_buffer
