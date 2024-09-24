## Invoice  Table Extractor and JSON Converter

## Overview

This project provides a Streamlit web application that allows users to upload CSV files, extract tabular data, and convert the extracted tables into JSON format. It handles deduplication of column names, identifies package types, and searches for invoice reference numbers within the data. The application aims to facilitate the extraction and manipulation of tabular data from CSV files efficiently.

## Project Structure

- **`streamlit-app.py`**: Main Streamlit application file.
- **`table_extractor.py`**: Table Processing code 
- **`README.md`**: Documentation for the project.

## Application Workflow

1. Upload CSV Files: Users can upload CSV files directly through the web interface.
2. Table Extraction: The application detects table-like structures in the CSV and extracts relevant data.
3. JSON Conversion: Converts the extracted table data into a JSON-like format for easy handling and manipulation.
4. Reconstruction from JSON: The application can reconstruct the DataFrame from its JSON representation.
5. Package Type Identification: Automatically identifies package types based on predefined keywords.
6. Reference Number Extraction: Searches for invoice reference numbers based on defined regex patterns.

## JSON Format Structure 

The data is structured in a JSON format consisting of an array of objects representing the columns and rows of the data table. Each object contains relevant information about the data structure.

### Table Columns JSON Structure
- column: Index of the column (0-based)
- column name: Name of the column as it appears in the data table

```json
[
    {
        "column": <column_index>,
        "column name": "<column_name>"
    },
    {
        "row": <row_index>,
        "column": <column_index>,
        "text": "<cell_value>"
    }
]
```
### Table Data JSON Structure
- row: Index of the row (0-based)
- column: Index of the column that this cell belongs to
- text: The value contained in that cell

```json
[
{
"row":0,
"column":0,
"text":"cell value"
}
{
"row":0,
"column":1,
"text":"cell value"
}
{
"row":0,
"column":2,
"text":"cell value"
}
]
```
## Installation

### Requirements

- Python 3.x
- Streamlit
- Pandas
- NumPy

### Cloning the Repository

``` bash 
git clone https://github.com/Muhammad-Talha4k/invoice_table_extraction_.git
cd invoice_table_extraction_
```
## Usage

Upload a CSV File: Use the provided interface to upload a CSV file.

Results:
The app will display the extracted table in JSON format.
It will also reconstruct and display the table from the JSON data.

## Contributing
Contributions are welcome! If you would like to contribute to this project, please follow these steps:

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## Contact
For any questions or inquiries, feel free to reach out:

- Email: muhammadtalhasheikh50@gmail.com
- GitHub: Muhammad-Talha4k
