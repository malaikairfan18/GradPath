# GradPath Job Market Data Collection

## Objective

Collect approximately 150 Data Analyst and 150 Data Scientist
job postings to build an evidence-based representation of
current job-market skill requirements.

## Collection Period

2026

## Target Roles

- Data Analyst
- Data Scientist

## Initial Test Sample

Before large-scale collection, a small test sample will be collected:

- 10 Data Analyst jobs
- 10 Data Scientist jobs

The test sample will be used to validate the API response,
data fields, role classification, duplicate handling, and
collection process.

## Primary Data Source

Adzuna Jobs API

## Supplementary Sources

Additional sources may be considered if needed to improve
coverage and diversity of the dataset.

## Data Fields

The exact raw schema will be finalized after inspecting
the actual API response.

Potential fields include:

- Job ID
- Job title
- Company
- Location
- Country
- Posting date
- Date collected
- Job description
- Source
- Source URL

## Role Classification

Each posting will be assigned a GradPath role category based
on the primary nature of the advertised position.

Initial categories:

- Data Analyst
- Data Scientist

## Duplicate Policy

Duplicate representations of the same underlying vacancy
should not be counted as independent jobs.

## Raw Data Policy

Original job descriptions and source information should be
preserved wherever possible.

Raw data should not be overwritten by processing steps.

## Data Quality

The collection process will check for:

- Missing values
- Duplicate jobs
- Invalid or missing URLs
- Inconsistent job titles
- Incomplete descriptions
- Incorrect role classification
- Repeated vacancies from different sources

## Methodological Principle

GradPath distinguishes between:

1. Observed data
2. Derived results
3. Assumptions and heuristics

Observed information comes directly from job postings.

Derived results are calculated from the collected data.

Assumptions and heuristics are human decisions made where
the available data cannot directly determine an answer.

This distinction will be maintained throughout the project.

## Limitations

The dataset may not represent the entire global job market.
Results may be affected by source coverage, geographic coverage,
job availability, search terms, and duplicate vacancies.

These limitations will be documented as the dataset develops.