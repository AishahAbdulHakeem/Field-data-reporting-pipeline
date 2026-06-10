# Field Data Reporting Pipeline

A Streamlit-based data cleaning and reporting app that turns raw field data files into standardized, downloadable Excel outputs.

This project is a public, sanitized portfolio version of an operational data automation workflow. It focuses on one clean user flow:

```text
Upload ZIP/files → clean and standardize data → preview cleaned tables → download Excel workbook
```

## What This Project Demonstrates

- Python data cleaning with pandas
- Streamlit file-upload workflow
- Automated Excel workbook generation
- File type detection for CSV and Excel files
- Column standardization and metadata enrichment
- Cleaned data previews inside the app
- Downloadable reporting outputs for non-technical users

## Data Workflow

```text
Raw uploaded ZIP
        ↓
Extract CSV / Excel files
        ↓
Detect workflow from file names
        ↓
Read and standardize each file
        ↓
Add farm and visit metadata
        ↓
Preview cleaned data in Streamlit
        ↓
Generate downloadable Excel workbook
```

## App Features

- Upload a ZIP containing raw CSV or Excel files
- Automatically extract and process supported files
- Standardize column names into readable labels
- Add farm name and visit date metadata
- Categorize files into reporting workflows based on file names
- Preview cleaned records before download
- Export all cleaned sheets into one Excel workbook

## Privacy Note

This repository is sanitized for public portfolio use. Real client data, farm names, credentials, upload archives, generated reports, private logos, and internal configuration files were removed or replaced with sample placeholders.

## Project Structure

```text
├── main.py                 # Streamlit app entry point
├── utils.py                # Shared cleaning and Excel helpers
├── file_reader.py          # General file reading helper
├── sample_data/            # Synthetic sample files for testing
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

1. Create a ZIP file containing CSV or Excel files.
2. Name the ZIP using this pattern if you want farm/date metadata parsed automatically:

```text
Demo_Farm_20250601.zip
```

3. Upload the ZIP in the Streamlit app.
4. Review cleaned data previews.
5. Download the cleaned Excel workbook.

## Recruiter Summary

This project shows my ability to turn messy operational data workflows into repeatable automation systems. It reflects experience with file ingestion, data cleaning, metadata enrichment, report generation, and user-facing Streamlit tools for non-technical users.

## Future Improvements

- Add stronger validation rules for each workflow type
- Add a generated data quality summary sheet
- Add downloadable error logs for skipped files
- Add sample ZIP files for demo testing
- Deploy the app on Streamlit Cloud
- Add unit tests for core cleaning functions