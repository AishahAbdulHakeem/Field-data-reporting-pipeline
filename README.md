# Field Data Reporting Pipeline

A public, sanitized version of a data cleaning and reporting workflow inspired by internship work. This project demonstrates how raw field data can be uploaded, cleaned, standardized, validated, and converted into dashboard-ready outputs and Excel summaries.

## What This Project Demonstrates

- Python data cleaning with pandas and NumPy
- Streamlit-based workflow interface
- Automated Excel report generation
- Modular cleaning scripts for multiple field-data workflows
- Safe configuration patterns using environment variables
- Optional Airtable integration using placeholder credentials

## Data Workflow

```text
Raw uploaded files
        ↓
File type detection
        ↓
Cleaning and standardization
        ↓
Validation and summary metrics
        ↓
Cleaned Excel/CSV outputs
        ↓
Dashboard-ready reporting data
```

## Privacy Note

This repository is sanitized for public portfolio use. Real client data, farm names, credentials, upload archives, generated reports, private logos, and internal configuration files were removed or replaced with sample placeholders.

## Project Structure

```text
├── main.py                 # Streamlit app entry point
├── pipeline.py             # Core pipeline orchestration
├── file_reader.py          # File reading and upload helpers
├── udder_hygiene.py        # Udder hygiene cleaning workflow
├── teat_hygiene.py         # Teat hygiene cleaning workflow
├── teat.py                 # Teat scoring transformation logic
├── stall_eval.py           # Stall evaluation cleaning workflow
├── stripyields.py          # Strip yield workflow
├── airtable_push.py        # Optional Airtable integration with placeholders
├── sample_data/            # Synthetic sample input data
├── .env.example            # Safe example config
└── requirements.txt
```

## Setup

```bash
git clone https://github.com/AishahAbdulHakeem/Field-data-reporting-pipeline.git
cd Field-data-reporting-pipeline
pip install -r requirements.txt
streamlit run main.py
```

## Configuration

Copy `.env.example` to `.env` and add your own credentials only if you plan to test external integrations. Never commit `.env` or `secrets.toml`.

## Recruiter Summary

This project shows my ability to turn messy operational data workflows into repeatable automation systems. It reflects experience with file ingestion, data cleaning, report generation, dashboard-ready outputs, and integration patterns for operational reporting.