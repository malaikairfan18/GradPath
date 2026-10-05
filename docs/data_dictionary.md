# GradPath Data Dictionary

## Purpose

This document defines the fields used in the raw GradPath job
posting dataset.

The raw dataset preserves information collected from the source
as closely as possible. GradPath-specific fields are clearly
identified.

---

## Job Posting Fields

| Field | Type | Source | Description |
|---|---|---|---|
| `job_id` | string | Adzuna | Unique identifier assigned to the job by Adzuna. |
| `role_category` | string | GradPath | GradPath classification of the job: Data Analyst or Data Scientist. |
| `job_title` | string | Adzuna | Original job title returned by the source. |
| `company` | string | Adzuna | Company or employer name. |
| `location` | string | Adzuna | Human-readable job location. |
| `country` | string | GradPath/API context | Country associated with the job search or source result. |
| `latitude` | float | Adzuna | Latitude associated with the job location, when available. |
| `longitude` | float | Adzuna | Longitude associated with the job location, when available. |
| `contract_type` | string | Adzuna | Contract type returned by the source, when available. |
| `salary_min` | float | Adzuna | Minimum salary returned by the source, when available. |
| `salary_max` | float | Adzuna | Maximum salary returned by the source, when available. |
| `salary_is_predicted` | string | Adzuna | Indicates whether the salary value was predicted by Adzuna. |
| `posting_date` | datetime | Adzuna | Original job creation/posting timestamp. |
| `date_collected` | date | GradPath | Date on which GradPath collected the job posting. |
| `description` | text | Adzuna | Job description returned by the source. |
| `category` | string | Adzuna | Job category assigned by Adzuna. |
| `source` | string | GradPath | Name of the source from which the posting was collected. |
| `source_url` | string | Adzuna | URL used to access the job posting. |

---

## Data Handling Principles

### Raw Data

Raw job descriptions and source information should be preserved
as closely as possible.

Raw data should not be overwritten by cleaning or analysis.

### Missing Values

Missing values will be represented consistently and documented.
They will not be silently replaced with invented values.

### Derived Fields

Fields created by GradPath rather than directly provided by the
source will be identified as derived or GradPath metadata.

Examples:

- `role_category`
- `country`
- `date_collected`
- `source`

### Excluded Source Fields

Some fields returned by the API may not be stored in the raw
dataset if they are unnecessary for analysis or contain
source-specific metadata that does not contribute to GradPath.

For example, Adzuna's `adref` field is not currently included.

### Future Processed Data

Skill extraction, normalized skill names, skill categories,
skill levels, and other analytical fields will be stored
separately from the raw job dataset.

The raw dataset should remain reproducible and traceable to
the original source response.