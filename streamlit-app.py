import streamlit as st
import pandas as pd
from table_extractor import process_dataframes, convert_df_to_json

def main():
    
    """
    The main function for the Streamlit app. It provides the interface for users to upload a CSV file, 
    processes the file using `process_dataframes`, and displays the extracted table and its JSON conversion.
    
    If a CSV file is uploaded:
    - Extracts the table and remaining data from the CSV file.
    - Converts the extracted table DataFrame to JSON format.
    - Displays the converted JSON data.
    - Reconstructs the table from the JSON format and displays it as a DataFrame.

    Streamlit UI Elements:
    - A title header for the app.
    - A file uploader to allow users to upload a CSV file.
    - Displays JSON format and the table reconstructed from JSON data.
    """
    st.title("CSV Table Extractor and JSON Converter")

    uploaded_file = st.file_uploader("Upload a CSV File", type="csv")

    if uploaded_file is not None:
        table_df, remaining_data_df = process_dataframes(uploaded_file)

        json_data = convert_df_to_json(table_df)

        st.subheader("Converted Table to JSON:")
        st.json(json_data)

        if json_data:
            st.subheader("JSON to Table Conversion:")

            json_columns = [item for item in json_data if "column name" in item]
            json_rows = [item for item in json_data if "row" in item]

            json_to_table = pd.DataFrame([{
                "row": item["row"],
                "column": item["column"],
                "text": item["text"]
            } for item in json_rows])

            table_from_json = json_to_table.pivot(index='row', columns='column', values='text')

            table_from_json = table_from_json.reset_index(drop=True)

            column_headers = [item["column name"] for item in json_columns]
            table_from_json.columns = column_headers[:len(table_from_json.columns)]

            st.dataframe(table_from_json)

if __name__ == "__main__":
    main()
