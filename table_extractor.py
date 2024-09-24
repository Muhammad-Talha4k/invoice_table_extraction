import pandas as pd
import re

def deduplicate_columns(columns):
    
    """
    Deduplicates column names by appending a counter to any duplicate names.

    Args:
        columns (list): List of column names that may contain duplicates.

    Returns:
        list: A list of column names with duplicates resolved by appending a counter.
    """
    seen = {}
    for i, col in enumerate(columns):
        if col not in seen:
            seen[col] = 0
        else:
            seen[col] += 1
            columns[i] = f"{col}_{seen[col]}"
    return columns

def concatenate_headers(header_row_1, header_row_2):
    
    """
    Concatenates two rows of headers, ensuring that empty or NaN values in the first row 
    are replaced with values from the second row.

    Args:
        header_row_1 (list): The first row of headers.
        header_row_2 (list): The second row of headers.

    Returns:
        list: A list of concatenated headers.
    """
    concatenated_headers = []
    for col1, col2 in zip(header_row_1, header_row_2):
        if pd.isna(col1) or col1 == '':
            concatenated_headers.append(col2 if pd.notna(col2) and col2 != '' else None)
        else:
            concatenated_headers.append(f"{col1} {col2}" if pd.notna(col2) and col2 != '' else col1)
    return concatenated_headers

def is_table_data(row):
    
    """
    Determines whether a row contains mostly numeric data, indicating it is part of a table.

    Args:
        row (pd.Series): A pandas Series representing a row of data.

    Returns:
        bool: True if the row contains mostly numeric values, False otherwise.
    """
    numeric_count = sum(pd.to_numeric(row, errors='coerce').notna())
    non_na_count = row.notna().sum()
    return numeric_count / non_na_count >= 0.5

def extract_table_from_csv(file_path, min_non_nan_pct=0.7):
    
    """
    Extracts table data from a CSV file based on a minimum percentage of non-NaN values in rows. 
    It separates table data from the remaining data and deduplicates column names.

    Args:
        file_path (str): The path to the CSV file.
        min_non_nan_pct (float): The minimum percentage of non-NaN values required to classify 
                                 a row as part of the table. Default is 0.7.

    Returns:
        tuple: A tuple containing two DataFrames, one with the table data and one with the remaining data.
    """
    df = pd.read_csv(file_path)
    table_data = []
    remaining_data = []
    table_start_idx = None
    columns = df.columns.tolist()
    unnamed_counter = 1
    skip_row = False

    for i in range(len(df)):
        row = df.iloc[i]
        total_cols = len(row)
        non_nan_count = total_cols - row.isnull().sum()
        non_nan_pct = non_nan_count / total_cols
        
        if non_nan_pct >= min_non_nan_pct:
            if table_start_idx is None:
                table_start_idx = i
                if i + 1 < len(df):
                    second_row = df.iloc[i + 1].tolist()
                    if is_table_data(df.iloc[i + 1]):
                        columns = row.tolist()
                    else:
                        columns = concatenate_headers(row.tolist(), second_row)
                        skip_row = True
                else:
                    columns = row.tolist()
                
                for idx in range(len(columns)):
                    if columns[idx] is None or pd.isna(columns[idx]):
                        columns[idx] = f"Unnamed {unnamed_counter}"
                        unnamed_counter += 1
            else:
                if skip_row:
                    skip_row = False
                    continue
                table_data.append(row.tolist())
        else:
            remaining_data.append(row.tolist())

    if table_data:
        max_cols = max(len(row) for row in table_data)
        columns = columns[:max_cols]
        table_df = pd.DataFrame(table_data, columns=columns)
    else:
        table_df = pd.DataFrame(columns=columns)

    table_df.columns = deduplicate_columns(list(table_df.columns))
    remaining_data_df = pd.DataFrame(remaining_data, columns=df.columns)
    
    return table_df, remaining_data_df

package_type_mapping = {
    "CTNS": "CTN",
    "QTY/CTN": "CTN",
    "Cartons": "CTN",
    "palate": "Palate",
    "px": "Palate",
    "boxes": "Boxes",
    "euro palate": "Euro Palate",
    "bags": "Bags",
    "cases": "Cases"
}

def find_package_type_in_table(table_df):
    """
    Searches for package type keywords in the table columns and returns the corresponding package type.

    Args:
        table_df (pd.DataFrame): The DataFrame representing the extracted table.

    Returns:
        str or None: The detected package type or None if no package type is found.
    """
    for col in map(str, table_df.columns):
        for keyword, package_type in package_type_mapping.items():
            if keyword.lower() in col.lower():
                return package_type
    return None

def find_package_type_in_rows(remaining_data_df):
    
    """
    Searches for package type keywords in the remaining rows and returns the corresponding package type.

    Args:
        remaining_data_df (pd.DataFrame): The DataFrame representing the remaining non-table data.

    Returns:
        str or None: The detected package type or None if no package type is found.
    """
    for _, row in remaining_data_df.iterrows():
        for value in row.values:
            if pd.notna(value):
                for keyword, package_type in package_type_mapping.items():
                    if keyword.lower() in str(value).lower():
                        return package_type
    return None

def process_dataframes(file_path):
    
    """
    Processes the CSV file to extract table data and remaining data, detects package type and reference number.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        tuple: A tuple containing two DataFrames:
               - table_df: The DataFrame with the extracted table and detected package type.
               - remaining_data_df: The DataFrame with the remaining non-table data.
    """
    table_df, remaining_data_df = extract_table_from_csv(file_path)
    
    package_type = find_package_type_in_table(table_df)
    if not package_type:
        package_type = find_package_type_in_rows(remaining_data_df)
    if package_type:
        table_df['Package Type'] = package_type

    
    invoice_pattern = re.compile(
        r'\b(?:'
        r'(?<![A-Z]{4})\d{7,8}'
        r'|\d{8}-\d{2}'
        r'|[A-Z]{2}(?!CU)\d{9}'
        r'|[A-Z]{3}\d{6}[A-Z]'
        r'|[A-Z]{4}\d{6}[A-Z]\d{4}[A-Z]'
        r'|\d{2}[A-Z]{2}\d{4}-\d{3}'
        r'|[A-Z]{2,}\d{4,}-?\d{0,3}'
        r'|[A-Z]{1,3}/\d{1,4}/\d{2}-\d{2}'
        r'|\d{4}-\d{4}-\d{4}-\d{4}'
        r'|23-24/\d{5,}'
        r'|[A-Z]{3}-\d{3}/\d{2}-\d{2}'
        r'|\b\d{5}\b.*\b\d{5}\b|\b\d{5}\b.*\b\d{5}\b'
        r'|\b\d{5}\b.*?\b\d{5}\b.*?\b\d{5}\b'
        r'|\b\d{5}\b'
        r'|[A-Z]\d{2}-\d{5}'  
        r')\b(?![\d-])',
        re.IGNORECASE
)
    reference_number = None

    for row in remaining_data_df.values:
        row_text = ' '.join([str(item) for item in row if pd.notna(item)])
        match = invoice_pattern.search(row_text)
        if match:
            reference_number = match.group(0)
            break

    if reference_number:
        table_df['Reference Number'] = reference_number

    return table_df, remaining_data_df

def convert_df_to_json(df):
    
    """
    Converts a pandas DataFrame into a JSON-like list of dictionaries for each row and column.

    Args:
        df (pd.DataFrame): The DataFrame to convert to JSON.

    Returns:
        list: A list of dictionaries where each dictionary represents a column or cell in the DataFrame.
    """
    json_list = []
    for col_index, col_name in enumerate(df.columns):
        json_list.append({
            "column": col_index,
            "column name": col_name
        })
    
    for row_index, row in df.iterrows():
        for col_index, value in enumerate(row):
            json_list.append({
                "row": row_index,
                "column": col_index,
                "text": str(value)
            })
    
    return json_list
