# GradPath Skill Priority Report

## Method

Skills are ranked separately for Data Analyst and Data Scientist.
Ranking is based on observed frequency in relevant job listings:
distinct jobs with a detected skill match divided by relevant jobs.
Role denominators are calculated from jobs_role_validated.csv.
All vocabulary skills applicable to each role are retained,
including skills with zero detected matches.

Evidence labels describe the number of detected job matches only.
They do not measure statistical certainty or prove that a skill is
required by the market. Zero matches do not mean a skill is unnecessary.
The baseline matcher uses a fixed vocabulary and limited job-description
text, so skills can be missed.

Priority rank is a descriptive frequency ranking, not a complete
measure of educational value, skill difficulty, or employer importance.

## Results by role

### Data Analyst

- Relevant jobs: 124
- Skills ranked: 16
- Skills with detected matches: 7
- Skills with zero detected matches: 9

| Rank | Skill | Matched jobs | Observed frequency | Evidence |
|---:|---|---:|---:|---|
| 1 | Power BI | 16 / 124 | 12.90% | Stronger (11+ jobs) |
| 2 | Data Analysis | 9 / 124 | 7.26% | Moderate (6-10 jobs) |
| 3 | SQL | 6 / 124 | 4.84% | Moderate (6-10 jobs) |
| 4 | Data Modeling | 5 / 124 | 4.03% | Limited (3-5 jobs) |
| 5 | Data Visualization | 3 / 124 | 2.42% | Limited (3-5 jobs) |
| 6 | Tableau | 3 / 124 | 2.42% | Limited (3-5 jobs) |
| 7 | Python | 1 / 124 | 0.81% | Very limited (1-2 jobs) |
| 8 | Data Cleaning | 0 / 124 | 0.00% | No detected evidence |
| 9 | Data Preprocessing | 0 / 124 | 0.00% | No detected evidence |
| 10 | ETL | 0 / 124 | 0.00% | No detected evidence |

### Data Scientist

- Relevant jobs: 127
- Skills ranked: 28
- Skills with detected matches: 12
- Skills with zero detected matches: 16

| Rank | Skill | Matched jobs | Observed frequency | Evidence |
|---:|---|---:|---:|---|
| 1 | Machine Learning | 42 / 127 | 33.07% | Stronger (11+ jobs) |
| 2 | Data Analysis | 5 / 127 | 3.94% | Limited (3-5 jobs) |
| 3 | Python | 5 / 127 | 3.94% | Limited (3-5 jobs) |
| 4 | Natural Language Processing | 3 / 127 | 2.36% | Limited (3-5 jobs) |
| 5 | Statistics | 3 / 127 | 2.36% | Limited (3-5 jobs) |
| 6 | Feature Engineering | 2 / 127 | 1.57% | Very limited (1-2 jobs) |
| 7 | SQL | 2 / 127 | 1.57% | Very limited (1-2 jobs) |
| 8 | Statistical Modeling | 2 / 127 | 1.57% | Very limited (1-2 jobs) |
| 9 | AWS | 1 / 127 | 0.79% | Very limited (1-2 jobs) |
| 10 | Data Cleaning | 1 / 127 | 0.79% | Very limited (1-2 jobs) |
