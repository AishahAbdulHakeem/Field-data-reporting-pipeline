# Field Data Cleaner

A Streamlit-based data cleaning app that turns one raw CSV or Excel file into a standardized, downloadable Excel output.

This project is a public, sanitized portfolio version of a larger operational data automation workflow I worked on during my internship. It focuses on a simple, recruiter-friendly user flow:

```text
Upload one CSV/XLSX file → standardize column names → remove empty rows → flag empty cells → download cleaned Excel file
```

## Internship Connection

During my internship, I worked on automating field-data reporting workflows that originally required manual spreadsheet cleaning, formatting, and report preparation. The larger internal workflow involved processing raw field files, standardizing inconsistent data, generating cleaned outputs, and making the results easier for non-technical users to review.

This public project reflects the core idea of that work: converting messy operational data into clean, structured, reviewable outputs through an easy-to-use interface.

## What This Public Version Includes

- Upload one `.csv`, `.xlsx`, or `.xls` file
- Standardize column names into clean Title Case
- Remove rows that are completely empty
- Flag rows that contain missing values
- Add an `Empty Cell Count` field
- Add an `Empty Columns` field listing which columns are missing values
- Preview cleaned records inside Streamlit
- Export the cleaned result as an Excel file

## How This Differs From the Internship Workflow

This version is intentionally simplified and sanitized for public portfolio use.

| Internship Workflow | Public GitHub Version |
|---|---|
| Processed specialized field-data workflows | Uses a general single-file cleaner |
| Included workflow-specific cleaning rules | Focuses on universal cleaning logic |
| Generated customized reporting outputs | Generates one standardized cleaned Excel file |
| Worked with internal/private operational data | Uses public-safe demo or user-uploaded files only |
| Included organization-specific context | Removes private names, credentials, logos, and internal details |
| Supported broader reporting automation | Demonstrates the core cleaning and quality-flagging logic |

## What This Project Demonstrates

- Python data cleaning with pandas
- Streamlit file-upload workflow
- Automated Excel file generation
- Column-name standardization for messy datasets
- Empty-row removal
- Empty-cell flagging for data quality review
- Cleaned data previews inside the app
- Downloadable reporting outputs for non-technical users

## Data Workflow

```text
Raw uploaded file
        ↓
Read CSV or Excel file
        ↓
Standardize column names
        ↓
Remove completely empty rows
        ↓
Flag rows with empty cells
        ↓
Preview cleaned data in Streamlit
        ↓
Download cleaned Excel file
```

## App Features

- Upload one `.csv`, `.xlsx`, or `.xls` file
- Standardize column names into clean Title Case
- Remove rows that are completely empty
- Add a `Has Empty Cells` flag
- Add an `Empty Cell Count` field
- Add an `Empty Columns` field listing which columns are missing values
- Preview cleaned records before download
- Export the cleaned result as an Excel file

## Demo File

A sample messy CSV file is included for testing:

```text
sample_data/test_messy_field_data.csv
```

The sample file includes messy column names, blank cells, and a completely empty row so users can test the cleaner quickly.

## Privacy Note

This repository is sanitized for public portfolio use. Real client data, credentials, upload archives, generated reports, private logos, organization-specific details, and internal configuration files were removed or replaced with sample placeholders.

## Project Structure

```text
├── main.py                 # Streamlit app entry point
├── utils.py                # Shared cleaning and Excel helpers
├── sample_data/            # Public sample data for testing
├── .gitignore              # Prevents secrets, outputs, and local files from being committed
└── requirements.txt        # Python dependencies
```

## Setup

```bash
git clone https://github.com/AishahAbdulHakeem/Field-data-reporting-pipeline.git
cd Field-data-reporting-pipeline
pip install -r requirements.txt
streamlit run main.py
```

## How to Use

1. Upload one CSV or Excel file.
2. Review the cleaning summary metrics.
3. Preview the cleaned data table.
4. Expand flagged rows to review missing cells.
5. Download the cleaned Excel file.

## Recruiter Summary

This project shows my ability to turn messy operational data into clean, reviewable outputs through a simple automation interface. It reflects experience with file ingestion, data standardization, data quality flagging, Excel output generation, and user-facing Streamlit tools.

The public version is intentionally smaller than the full internship workflow, but it demonstrates the same core automation pattern: reduce manual spreadsheet work, improve data consistency, and create outputs that non-technical users can act on.

## Future Improvements

- Add duplicate-row detection
- Add type validation for date and numeric columns
- Add downloadable data quality summary reports
- Add optional CSV export
- Deploy the app on Streamlit Cloud
- Add unit tests for core cleaning functions