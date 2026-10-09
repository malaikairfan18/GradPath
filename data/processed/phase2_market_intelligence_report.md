# GradPath Phase 2 — Market Intelligence

## Dataset overview
- Collected listings: 312
- Unique job IDs: 312
- Relevant listings: 251
- Relevant jobs with at least one detected skill: 80
- Relevant jobs with no detected skills: 171
- All jobs with detected skills: 80
- Relevant jobs flagged for salary review: 12

## Relevance labels
```text
role_relevance
irrelevant     24
relevant      251
uncertain      37
```

## Relevant jobs by role
```text
role_category
Data Analyst      124
Data Scientist    127
```

## Relevant jobs by seniority
```text
seniority_level
Entry-level / Graduate     29
Junior                     12
Lead                        9
Management / Principal      9
Senior                     46
Unspecified               146
```

## Skill analysis outputs
- Relevant job-skill match rows: 116
- Distinct skills in priority table: 31
- Overall skill frequency rows: 18
- Role comparison rows: 18

## Methodology and limitations
- The master dataset has one row per collected listing.
- Job-skill evidence is aggregated from relevant listings only.
- Skills are detected from the collected description text and are not guaranteed to capture all job requirements.
- Many source descriptions are short snippets, so absence of a detected skill is not proof that the job does not require it.
- Relevance and seniority labels are rule-based and should be interpreted as estimates.
- Location-region labels are heuristic.
- Salary values are source-provided; pay period and comparability have not been verified.
- The data represents this collected sample, not a census of the UK job market.

## Final outputs
- `jobs_market_intelligence.csv`: all 312 collected listings.
- `jobs_market_intelligence_relevant.csv`: the 251 relevant listings.
- `phase2_data_dictionary.csv`: column descriptions.
- `phase2_market_intelligence_report.md`: summary and limitations.

## Separate analytical tables retained
- `job_skill_matches_baseline_relevant.csv`
- `skill_frequency_overall.csv`
- `skill_frequency_by_role.csv`
- `skill_role_comparison.csv`
- `skill_priority_scores.csv`
- `seniority_distribution.csv`
- `job_region_summary.csv`
- `salary_market_summary.csv`
