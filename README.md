## Invoice Table Extraction and Table to JSON Converter

## Overview

This repository provides a Streamlit application for extracting tabular data from CSV files, processing it, and converting it into a structured JSON format. The application handles various CSV structures, deduplicates column names, identifies package types, and extracts invoice reference numbers.

## Project Structure

- **`streamlit_app.py`**: Main Streamlit application file.
- **`invoice_table_extraction.py`**: Table Processing code 
- **`README.md`**: Documentation for the project.

## Application Workflow

1. **File Upload**:
   - The user uploads a CSV file containing invoice data.

2. **Table Extraction**:
   - The application automatically detects and extracts table-like data from the CSV.

3. **Header Handling**:
   - If necessary, it concatenates headers from multiple rows and manages duplicate column names.

4. **Package Type Detection**:
   - The application identifies package types based on predefined keywords found in the data.

5. **Invoice Number Extraction**:
   - Regular expressions are used to extract invoice reference numbers from the remaining data.

6. **JSON Conversion**:
   - The extracted DataFrame is converted into JSON format for easy integration with other applications.

7. **Display Results**:
   - The application displays the extracted table and its JSON representation.

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

Example
Upload a CSV file containing invoice data.
The application will process the file, extract relevant table data, and display it along with the JSON representation.

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
