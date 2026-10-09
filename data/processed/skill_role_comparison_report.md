# GradPath Phase 2 Day 3 — Role Skill Comparison

## Objective

Compare the observed frequency of baseline skills in relevant Data Analyst and Data Scientist job postings.

## Dataset coverage

- Relevant Data Analyst jobs: 124
- Relevant Data Scientist jobs: 127
- Skill-match rows: 116
- Distinct observed skills: 18
- Skills detected in both roles: 5
- Skills detected only in Data Analyst jobs: 5
- Skills detected only in Data Scientist jobs: 8

## Largest observed differences

Positive differences mean a higher observed frequency in Data Scientist jobs; negative differences mean a higher frequency in Data Analyst jobs.

| Skill | Data Analyst jobs | DA frequency (%) | Data Scientist jobs | DS frequency (%) | Difference (percentage points) |
|---|---:|---:|---:|---:|---:|
| Machine Learning | 0 | 0.00 | 42 | 33.07 | +33.07 |
| Power BI | 16 | 12.90 | 0 | 0.00 | -12.90 |
| Data Modeling | 5 | 4.03 | 0 | 0.00 | -4.03 |
| Data Analysis | 9 | 7.26 | 5 | 3.94 | -3.32 |
| SQL | 6 | 4.84 | 2 | 1.57 | -3.27 |
| Python | 1 | 0.81 | 5 | 3.94 | +3.13 |
| Data Visualization | 3 | 2.42 | 0 | 0.00 | -2.42 |
| Tableau | 3 | 2.42 | 0 | 0.00 | -2.42 |
| Natural Language Processing | 0 | 0.00 | 3 | 2.36 | +2.36 |
| Statistics | 0 | 0.00 | 3 | 2.36 | +2.36 |

## Interpretation and limitations

- Frequencies use distinct jobs, not raw match-row counts.
- Each role uses its own relevant-job denominator.
- Percentage-point difference is Data Scientist frequency minus Data Analyst frequency.
- A zero detected count means no match was found by the baseline extractor, not that the skill is absent from the role.
- Adzuna descriptions may be snippets, limiting skill detection.
- The analysis covers only the baseline vocabulary grounded in O*NET and ESCO; other skills cannot appear in this comparison.
- Results are descriptive observations from this sample, not proof of statistical significance or a complete UK market ranking.
- The higher-frequency label describes this sample only and should not be interpreted as causal evidence.

## Output

- `skill_role_comparison.csv`
- `skill_role_comparison_report.md`
