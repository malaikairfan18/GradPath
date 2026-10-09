# GradPath Phase 2 Day 2 — Skill Frequency Analysis

## Purpose

Measure how frequently baseline skills were detected in relevant Data Analyst and Data Scientist job postings collected from Adzuna.

## Dataset coverage

- Collected jobs: 312
- Relevant jobs: 251
- Baseline skill-match rows: 116
- Distinct skills observed in matches: 18
- Relevant jobs with at least one detected baseline skill: 80

### Relevant jobs by role

| Role | Relevant jobs | Match rows | Jobs with at least one match |
|---|---:|---:|---:|
| Data Analyst | 124 | 47 | 34 |
| Data Scientist | 127 | 69 | 46 |

## Top 10 skills overall

| Rank | Skill | Jobs with skill | Relevant jobs | Observed frequency (%) | Match rows |
|---:|---|---:|---:|---:|---:|
| 1 | Machine Learning | 42 | 251 | 16.73 | 42 |
| 2 | Power BI | 16 | 251 | 6.37 | 16 |
| 3 | Data Analysis | 14 | 251 | 5.58 | 14 |
| 4 | SQL | 8 | 251 | 3.19 | 8 |
| 5 | Python | 6 | 251 | 2.39 | 6 |
| 6 | Data Modeling | 5 | 251 | 1.99 | 5 |
| 7 | Data Visualization | 3 | 251 | 1.20 | 3 |
| 8 | Feature Engineering | 3 | 251 | 1.20 | 3 |
| 9 | Natural Language Processing | 3 | 251 | 1.20 | 3 |
| 10 | Statistics | 3 | 251 | 1.20 | 3 |

## Methodology and interpretation

- A skill's `match_count` is the number of rows in the extracted match file.
- `jobs_with_skill` counts distinct job IDs for that skill.
- Overall frequency divides distinct jobs with the detected skill by all relevant jobs.
- Role-specific frequency divides by all relevant jobs in that role.
- Rankings prioritize distinct jobs with the detected skill; match count and skill name break ties.
- These are observed frequencies in the collected sample, not estimates of the entire UK job market.
- Adzuna descriptions may be snippets. A skill not detected is not proof that the job does not require it.
- The baseline vocabulary is limited to 31 skills derived from O*NET and ESCO. Unlisted skills cannot be measured here.
- Frequency measures observed mentions/detections, not skill importance, proficiency, or causation.
- The dataset can contain multiple skills per job, so match-row counts should not be summed as unique jobs.

## Validation

- Relevant job IDs are unique.
- Every match maps to a relevant job.
- Role labels agree between the job and match datasets.
- Missing job IDs, skill IDs, and skill names are rejected.
- The relevant-job count is checked against the Day 1 checkpoint (251 jobs); match-row counts are derived from the current filtered dataset.

## Output files

- `skill_frequency_overall.csv`
- `skill_frequency_by_role.csv`
- `skill_frequency_report.md`
