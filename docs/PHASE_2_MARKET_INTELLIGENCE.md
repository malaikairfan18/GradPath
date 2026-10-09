# GradPath Phase 2 — Job Market Intelligence

## Objective

Build an evidence-based job-market dataset for two target roles:
- Data Analyst
- Data Scientist

This phase collects job listings, labels their relevance, normalizes job titles, detects skills in available descriptions, compares observed skill patterns between roles, analyzes seniority and location, and performs basic salary-quality checks.

The outputs support GradPath's future skill-gap and career-readiness features. They are not a complete representation of all employer requirements.

## Data source and scope

- Job source: Adzuna API
- Market queried: United Kingdom
- Target role searches: Data Analyst and Data Scientist
- Collected listings after cross-query deduplication: 312
- Relevant listings: 251
- Uncertain listings: 37
- Irrelevant listings: 24
- Relevant Data Analyst listings: 124
- Relevant Data Scientist listings: 127

Two listings appeared in both role-search results. Cross-query duplicates were resolved by job ID, retaining the strongest relevance classification and preserving source-query provenance.

## Pipeline overview

1. **Job collection** — collect listings for the target roles.
2. **Relevance validation** — classify listings as relevant, uncertain, or irrelevant.
3. **Title normalization** — standardize job titles and assign title families.
4. **Text cleaning** — create cleaned description text for downstream analysis.
5. **Skill vocabulary construction** — build a 31-skill vocabulary informed by O*NET and ESCO data.
6. **Skill extraction** — match vocabulary terms and aliases against available job text.
7. **Relevant-match filtering** — retain skill matches from relevant listings only.
8. **Skill frequency analysis** — measure observed skill frequency overall and by role.
9. **Role comparison** — compare observed frequencies for Data Analyst and Data Scientist.
10. **Skill priority scoring** — rank role-specific skill evidence using the documented frequency-based method.
11. **Seniority analysis** — assign rule-based seniority labels from job titles.
12. **Location and salary analysis** — summarize locations and inspect salary data quality.
13. **Market intelligence assembly** — combine job-level features and aggregated skill evidence into final datasets.

## Main scripts

Scripts are located in `src/`.

- `collect_job_market.py` — collect job-market listings.
- `validate_job_relevance.py` — validate relevance and deduplicate across queries.
- `normalize_job_titles.py` — normalize titles.
- `add_title_family.py` — classify broad title families.
- `clean_job_descriptions.py` — clean description text.
- `build_skill_vocabulary.py` — construct the skill vocabulary.
- `extract_baseline_skills.py` — detect vocabulary matches in job text.
- `filter_relevant_skill_matches.py` — filter matches by relevance.
- `analyze_skill_frequency.py` — summarize observed skill frequencies.
- `compare_role_skills.py` — compare role-specific skill evidence.
- `score_skill_priority.py` — calculate role-specific skill priorities.
- `analyze_job_seniority.py` — classify seniority from titles.
- `analyze_location_salary.py` — analyze location and salary quality.
- `build_market_intelligence_dataset.py` — build final job-level datasets.

Run scripts from the repository root with the project virtual environment active. Use the dependency order above when regenerating outputs. Some scripts consume files created by earlier steps.

## Final datasets

### `data/processed/jobs_market_intelligence.csv`

The master dataset containing 312 unique job listings, including uncertain and irrelevant listings so the classification process remains auditable.

### `data/processed/jobs_market_intelligence_relevant.csv`

The 251 listings classified as relevant.

### `data/processed/job_skill_matches_baseline_relevant.csv`

A separate job-skill evidence table with 116 detected job-skill pairs across 80 unique relevant listings. One listing can contain multiple detected skills.

### Skill-analysis tables

- `skill_frequency_overall.csv`
- `skill_frequency_by_role.csv`
- `skill_role_comparison.csv`
- `skill_priority_scores.csv`

These tables summarize detected skills, observed role differences, and evidence-based priorities. They should not be interpreted as universal rankings of all employer requirements.

### Seniority, location, and salary tables

- `seniority_distribution.csv`
- `job_location_summary.csv`
- `job_region_summary.csv`
- `salary_quality_summary.csv`
- `salary_market_summary.csv`
- `location_salary_quality_detail.csv`

### Documentation and metadata

- `phase2_data_dictionary.csv` — descriptions of master-dataset columns.
- `phase2_market_intelligence_report.md` — final dataset summary and limitations.
- `skill_frequency_report.md` — skill-frequency findings.
- `skill_role_comparison_report.md` — role comparison findings.
- `skill_priority_report.md` — skill priority results.
- `seniority_analysis_report.md` — seniority findings.
- `location_salary_analysis_report.md` — location and salary findings.

## Current skill evidence

- Relevant listings: 251
- Listings with at least one detected skill: 80
- Listings with no detected skill: 171
- Relevant job-skill matches: 116
- Distinct skills observed in relevant matches: 18

A missing skill match does not mean a job does not require that skill. It means the skill was not detected in the available description text using the current vocabulary and matching rules.

## Seniority methodology

Seniority is inferred using title-based rules. Categories include management/principal, lead, senior, junior, entry-level/graduate, mid-level/experienced, and unspecified.

Titles can contain multiple seniority markers. Rule precedence determines the assigned category. These labels are approximations, not verified employer seniority levels.

## Salary methodology

The source-provided salary minimum, maximum, and predicted-salary indicator are retained. Basic plausibility rules flag suspicious values for review rather than silently deleting records.

Predicted and non-predicted salary records are summarized separately. Salary periods and comparability have not been independently verified, so results must not be described as confirmed annual salaries.

A record passing basic checks is not guaranteed to be accurate.

## Location methodology

Location regions are assigned using text-based heuristics. Unspecified UK-wide locations are kept separate, and unfamiliar locations may fall into an approximate or town-level category.

The broad-region labels are exploratory rather than authoritative geographic classifications.

## Limitations and responsible interpretation

1. **Description truncation:** many collected descriptions are approximately 500 characters. Skill frequencies are based on available text, not complete job specifications.
2. **Vocabulary coverage:** only skills included in the current vocabulary and recognized aliases can be detected.
3. **Rule-based relevance:** title-based labels do not guarantee that the full job description matches the target role.
4. **Sample coverage:** 312 collected listings are a limited sample, not a census of the UK job market.
5. **Search and source bias:** results depend on the queries, collection time, and listings exposed by the source.
6. **Seniority uncertainty:** title markers can be inconsistent or ambiguous.
7. **Salary uncertainty:** source values may use different pay periods or contain outliers.
8. **Regional uncertainty:** broad locations are assigned by heuristics and may be imperfect.
9. **Observed frequency is not universal importance:** a skill appearing frequently in this sample does not prove that it is more important for every employer or job.

These limitations should be considered when using the dataset to recommend learning priorities or assess a graduate's readiness.

## Validation criteria

The final build is expected to satisfy:

- 312 rows and 312 unique job IDs in the master dataset.
- 251 rows and 251 unique job IDs in the relevant-only dataset.
- No duplicate job-skill pairs in the relevant skill-match table.
- Skill evidence aggregated before joining to the master table.
- No skill evidence attached to uncertain or irrelevant jobs in the master dataset.
- Separate analytical tables retained for reproducibility and auditability.

## Next phase

Phase 3 should turn these validated market signals into a transparent analysis engine that compares a graduate's extracted skills with the requirements and evidence for a selected target role. It should preserve explanations for each gap and account for uncertainty in the underlying data.
