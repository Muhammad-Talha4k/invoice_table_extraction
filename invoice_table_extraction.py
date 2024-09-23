import pandas as pd
import re
from tabulate import tabulate

file_path = 'C:/Users/TalhaPC/Downloads/Ningbo Sanata - OC636230138.xlsx - Invoice.csv'
df = pd.read_csv(file_path)

# Function to deduplicate column names
def deduplicate_columns(columns):
    seen = {}
    for i, col in enumerate(columns):
        if col not in seen:
            seen[col] = 0
        else:
            seen[col] += 1
            columns[i] = f"{col}_{seen[col]}"
    return columns

# Function to concatenate headers from two rows (generic concatenation)
def concatenate_headers(header_row_1, header_row_2):
    concatenated_headers = []
    for col1, col2 in zip(header_row_1, header_row_2):
        if pd.isna(col1) or col1 == '':
            if pd.notna(col2) and col2 != '':
                concatenated_headers.append(col2)
            else:
                concatenated_headers.append(None)
        else:
            if pd.notna(col2) and col2 != '':
                concatenated_headers.append(f"{col1} {col2}")
            else:
                concatenated_headers.append(col1)
    return concatenated_headers

# Function to check if a row is likely to be table data (not header)
def is_table_data(row):
    numeric_count = sum(pd.to_numeric(row, errors='coerce').notna())
    non_na_count = row.notna().sum()
    return numeric_count / non_na_count >= 0.5

# Function to extract table from CSV based on non-NaN percentage
def extract_table_from_csv(file_path, min_non_nan_pct=0.7):
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
                        # Concatenate headers and mark second row to skip
                        columns = concatenate_headers(row.tolist(), second_row)
                        skip_row = True  # Skip the second row (used for headers)
                else:
                    columns = row.tolist()
                
                # Rename NaN or None columns as Unnamed 1, 2, etc.
                for idx in range(len(columns)):
                    if columns[idx] is None or pd.isna(columns[idx]):
                        columns[idx] = f"Unnamed {unnamed_counter}"
                        unnamed_counter += 1
            else:
                # Skip the second row if already used for header concatenation
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

# Mapping keywords to package types
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

# Identify package type based on table columns
def find_package_type_in_table(table_df): 
    for col in map(str, table_df.columns):
        for keyword, package_type in package_type_mapping.items():
            if keyword.lower() in col.lower():
                return package_type
    return None

# Identify package type based on remaining DataFrame rows
def find_package_type_in_rows(remaining_data_df): 
    for index, row in remaining_data_df.iterrows():
        for value in row.values:
            if pd.notna(value):
                for keyword, package_type in package_type_mapping.items():
                    if keyword.lower() in str(value).lower():
                        return package_type
    return None

# Function to handle invoice extraction and package type detection
def process_dataframes(file_path):
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

# Example usage
csv_file =file_path  # Replace with the path to your CSV file
table_df, remaining_data_df = process_dataframes(csv_file)

# Display DataFrames using tabulate
print("Extracted Table DataFrame:")
print(tabulate(table_df, headers='keys', tablefmt='psql'))

print("\nRemaining DataFrame:")
print(tabulate(remaining_data_df, headers='keys', tablefmt='psql'))
