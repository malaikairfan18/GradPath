# GradPath Job Market Data Collection Log

## 1. Objective

GradPath Phase 2 collects real job postings to build an evidence-based representation of current employer requirements for **Data Analyst** and **Data Scientist** roles.

Phase 1 established occupational knowledge using structured sources such as **O*NET** and **ESCO**.

Phase 2 adds real-world job-market evidence.

The intended pipeline is:

```text
O*NET + ESCO
       ↓
Occupational Knowledge
       +
Real Job Postings
       ↓
Market Skill Requirements
       ↓
GradPath Skill Knowledge Base
```

The initial target is approximately:

* **150 Data Analyst postings**
* **150 Data Scientist postings**

for approximately **300 usable job postings**.

The target is approximate. Low-quality, duplicate, or irrelevant postings will not be retained simply to reach the target number.

---

## 2. Primary Data Source

### Adzuna Jobs API

The primary source for the initial GradPath job-market dataset is the **Adzuna Jobs API**.

Adzuna provides structured information about job postings, including:

* Job ID
* Job title
* Company
* Location
* Posting date
* Job description
* Source URL
* Salary information when available
* Contract information when available
* Job category information

The API was selected because it provides a programmatic and reproducible way to collect job-market data.

---

## 3. Geographic Scope

The initial dataset focuses on the:

**United Kingdom (UK)**

Adzuna country code:

```text
gb
```

The initial UK-only scope provides a controlled market for the first GradPath analysis.

The results should therefore be interpreted as evidence about the **sampled UK job market**, not the global job market.

Future versions may expand the geographic scope if sufficient data and a clear research purpose justify doing so.

---

## 4. Target Roles

GradPath initially focuses on two broad role categories.

### 4.1 Data Analyst

Potential search terminology includes:

* Data Analyst
* Junior Data Analyst
* Business Data Analyst
* BI Analyst
* Data Analytics

The search terminology may be expanded or refined during collection.

### 4.2 Data Scientist

Potential search terminology includes:

* Data Scientist
* Junior Data Scientist
* Applied Data Scientist
* Machine Learning Data Scientist
* Data Science

The search terminology may be expanded or refined during collection.

Any major changes to search terminology will be documented.

---

## 5. Collection Strategy

The collection process will use the following general workflow:

```text
Adzuna API
    ↓
Search by target role
    ↓
Collect multiple pages
    ↓
Store raw job records
    ↓
Validate records
    ↓
Remove duplicates
    ↓
Check role relevance
    ↓
Create processed dataset
    ↓
Extract skills
    ↓
Analyze market demand
```

The raw job data will be preserved separately from processed data.

---

## 6. Initial Validation Sample

Before beginning large-scale collection, a small test sample was collected to verify the API and data structure.

### Data Analyst

```text
10 postings
```

### Data Scientist

```text
10 postings
```

### Total

```text
20 postings
```

The initial sample was collected from the UK Adzuna endpoint.

---

## 7. Initial Validation Results

The initial 20-posting sample was inspected for basic data quality.

| Check                   | Result |
| ----------------------- | -----: |
| Total postings          |     20 |
| Data Analyst postings   |     10 |
| Data Scientist postings |     10 |
| Duplicate job IDs       |      0 |
| Duplicate source URLs   |      0 |
| Missing descriptions    |      0 |
| Empty descriptions      |      0 |
| Missing source URLs     |      0 |

The validation sample successfully confirmed that the current Adzuna collection method provides the minimum information required for the next stage of the pipeline.

However, the test sample is too small to make any market-level conclusions.

---

## 8. Current Raw Data Schema

The current Adzuna collector produces the following fields:

```text
job_id
role_category
job_title
company
location
country
latitude
longitude
contract_type
salary_min
salary_max
salary_is_predicted
posting_date
date_collected
description
category
source
source_url
```

### Field descriptions

| Field                 | Description                                   |
| --------------------- | --------------------------------------------- |
| `job_id`              | Unique identifier provided by the job source  |
| `role_category`       | GradPath role classification                  |
| `job_title`           | Original advertised job title                 |
| `company`             | Employer/company name                         |
| `location`            | Advertised job location                       |
| `country`             | Source country code                           |
| `latitude`            | Job location latitude when available          |
| `longitude`           | Job location longitude when available         |
| `contract_type`       | Contract type when available                  |
| `salary_min`          | Minimum salary when available                 |
| `salary_max`          | Maximum salary when available                 |
| `salary_is_predicted` | Whether the salary is estimated by the source |
| `posting_date`        | Original posting/creation date                |
| `date_collected`      | Date GradPath collected the posting           |
| `description`         | Original job description                      |
| `category`            | Job-board category                            |
| `source`              | Data source                                   |
| `source_url`          | Original job/source URL                       |

The schema may be extended if additional fields are required.

---

## 9. Raw Data Preservation

Raw job postings are treated as source data.

The following information should be preserved wherever possible:

* Original job title
* Original company
* Original location
* Original posting date
* Original description
* Original source URL
* Source-specific identifiers

Raw files should **not** be overwritten during cleaning or NLP processing.

Instead:

```text
Raw Data
   ↓
Processed Data
   ↓
Analysis Data
```

This allows the processing pipeline to be reproduced and audited.

---

## 10. Role Classification

The API search query will not automatically be treated as proof that a posting belongs to the requested role.

For example, searching for:

```text
data analyst
```

may return:

* Genuine Data Analyst positions
* Related analytics positions
* Broad data roles
* Training or placement programmes
* Other potentially irrelevant results

Therefore, GradPath will perform role validation before including postings in the final analysis.

The initial GradPath role categories are:

```text
Data Analyst
Data Scientist
```

The original job title will always be preserved.

---

## 11. Seniority Classification

Seniority is important because required skills may differ substantially between junior and senior positions.

Where possible, postings will be assigned a derived seniority category.

Initial categories:

```text
Intern
Entry / Junior
Mid
Senior
Lead
Principal
Manager
Unknown
```

The original job title will not be replaced.

For example:

```text
Original title:
Senior Data Analyst - Growth

Derived fields:

role_category = Data Analyst
seniority = Senior
```

Seniority classification is a derived field and may involve heuristic rules.

---

## 12. Duplicate Policy

The same vacancy should not be counted multiple times as independent evidence.

Duplicate detection will primarily use:

1. `job_id`
2. `source_url`

Additional fields may be considered when identifying possible duplicate representations of the same vacancy.

For example, the same job may appear through multiple search queries.

Therefore:

```text
Search Query A
      ↓
Job X

Search Query B
      ↓
Job X
```

must result in **one underlying job**, not two observations.

Duplicate removal will be performed during processing.

Raw collected data should remain preserved.

---

## 13. Data Quality Checks

The production collection pipeline will check for:

### Required fields

* Job ID
* Job title
* Description
* Source URL

### Missing values

* Missing job IDs
* Missing titles
* Missing descriptions
* Missing company information
* Missing locations
* Missing URLs

### Duplicate records

* Duplicate job IDs
* Duplicate source URLs
* Potential repeated vacancies

### Validity

* Invalid URLs
* Empty descriptions
* Malformed records
* Irrelevant postings
* Incorrect role classification

### Consistency

* Inconsistent role labels
* Unexpected job categories
* Suspicious repeated postings

---

## 14. Search and Collection Queries

The production pipeline will support multiple search queries for each role.

The purpose is to improve coverage while maintaining a clear role definition.

Example Data Analyst searches:

```text
data analyst
junior data analyst
business data analyst
BI analyst
data analytics
```

Example Data Scientist searches:

```text
data scientist
junior data scientist
applied data scientist
machine learning data scientist
data science
```

These queries are initial candidates and will be evaluated during collection.

Search-query changes will be documented.

---

## 15. Pagination

The production collection pipeline must support pagination.

A single API request should not be treated as the complete job market.

Conceptually:

```text
Search Query
     ↓
Page 1
     ↓
Page 2
     ↓
Page 3
     ↓
...
     ↓
Collected postings
```

Pagination will continue until the collection target is reached or the available relevant results are exhausted.

---

## 16. Collection Target

Initial target:

| Role           |   Target |
| -------------- | -------: |
| Data Analyst   |     ~150 |
| Data Scientist |     ~150 |
| **Total**      | **~300** |

The target represents the desired number of **usable postings**, not merely API responses.

For example:

```text
Collected: 180
Duplicates: 15
Irrelevant: 8
Invalid: 5

Usable: 152
```

The usable dataset should be reported as 152 rather than artificially reducing or increasing it to exactly 150.

---

## 17. Collection Date

Every collected job will contain:

```text
date_collected
```

This is separate from:

```text
posting_date
```

### `posting_date`

The date associated with the original job posting.

### `date_collected`

The date on which GradPath retrieved the job.

This distinction allows future analysis of data freshness and reproducibility.

---

## 18. Supplementary Sources

Adzuna will remain the primary source for the initial market dataset.

Additional sources may be introduced if necessary to improve:

* Job coverage
* Role diversity
* Employer diversity
* Geographic coverage

If supplementary sources are added, the dataset must retain a `source` field so that results can be analyzed by source.

Different sources should not be silently mixed together.

---

## 19. Methodological Principle

GradPath distinguishes between three types of information.

### 19.1 Observed Data

Information directly obtained from job postings.

Examples:

* Job title
* Company
* Description
* Location
* Posting date
* Salary

### 19.2 Derived Results

Information calculated or extracted from observed data.

Examples:

* Skill frequency
* Skill percentage
* Seniority
* Normalized skill names
* Role-specific skill demand

### 19.3 Assumptions and Heuristics

Human-defined rules used when the available data cannot directly determine an answer.

Examples:

* Role classification rules
* Seniority classification
* Skill normalization
* Duplicate heuristics

This distinction is important for making GradPath explainable and reproducible.

---

## 20. Limitations

The dataset will not represent the entire global employment market.

Potential limitations include:

* Adzuna coverage
* UK-only geographic scope
* Search-query selection
* Job-board ranking
* Duplicate vacancies
* Employer posting behavior
* Sample size
* Collection date
* API-specific limitations

Therefore, GradPath findings should be described as patterns observed in the **sampled UK job market**.

They should not automatically be presented as universal requirements for all Data Analyst or Data Scientist positions.

---

## 21. Current Project Status

### Completed

* Adzuna API credentials configured
* API connectivity tested
* Data Analyst API test completed
* Data Scientist API test completed
* 20 initial postings collected
* Raw CSV files created
* API response fields inspected
* Duplicate checks completed
* Missing description checks completed
* Missing URL checks completed
* Initial collection strategy defined

### Current files

```text
data/raw/data_analyst_test.csv
data/raw/data_scientist_test.csv
src/collect_jobs.py
src/test_adzuna.py
docs/job_collection_log.md
```

### Next step

Build the production job-collection pipeline with:

* Multiple search queries
* Pagination
* Configurable target counts
* Duplicate handling
* Role validation
* Collection logging
* Consistent raw output
* Error handling
* API request controls

---

## 22. Future Processing Pipeline

After collection, the data will move through the following stages:

```text
Raw Job Postings
       ↓
Validation
       ↓
Deduplication
       ↓
Role Classification
       ↓
Seniority Classification
       ↓
Description Cleaning
       ↓
Skill Extraction
       ↓
Skill Normalization
       ↓
Market Skill Frequency
       ↓
Role Comparison
       ↓
Skill Priority Signals
```

The resulting market data will later be combined with the Phase 1 O*NET and ESCO knowledge base.

---

## 23. Reproducibility and Security

All collection and processing scripts should remain version-controlled.

The collection process should be reproducible when API access is available.

API credentials must be stored in environment variables and must never be committed to Git.

Expected environment variables:

```text
ADZUNA_APP_ID
ADZUNA_APP_KEY
```

The `.env` file must remain excluded from version control.

---

## 24. Collection Log

This section will be updated as production collection runs are performed.

| Date       | Role           | Source | Query          | Jobs Collected | Valid | Duplicates | Invalid | Notes                  |
| ---------- | -------------- | ------ | -------------- | -------------: | ----: | ---------: | ------: | ---------------------- |
| 2026-10-06 | Data Analyst   | Adzuna | data analyst   |             10 |    10 |          0 |       0 | Initial API validation |
| 2026-10-06 | Data Scientist | Adzuna | data scientist |             10 |    10 |          0 |       0 | Initial API validation |

Future collection runs should be added to this table rather than replacing previous records.
