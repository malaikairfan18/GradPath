# Phase 7: Project Recommendations Engine

## 1. Purpose

Phase 7 recommends practical portfolio projects that address actionable skill gaps for a candidate's selected target role.

The engine is designed to be deterministic and explainable. It uses the existing GradPath skill vocabulary, Phase 4 skill-gap results, and a curated project catalogue. It does not use a generative AI API to decide which projects to recommend.

Supported target roles:
- Data Analyst
- Data Scientist

## 2. Implementation

Main module: `src/gradpath/project_recommendations.py`

Automated tests: `src/test_project_recommendations.py`

Project catalogue: `data/resources/project_catalogue.csv`

Skill vocabulary: `data/processed/initial_skill_vocabulary.csv`

Public function:

```python
recommend_projects(
    skill_gaps,
    target_role,
    projects=None,
    vocabulary=None,
    project_path=PROJECT_CATALOGUE_PATH,
    max_hours=None,
    max_difficulty=None,
    include_maintenance=False,
)
```

The function returns a list of project recommendation dictionaries. It can use the default catalogue and vocabulary or accept DataFrames for testing and controlled evaluation.

## 3. Project catalogue

The catalogue contains eight curated projects:

| ID | Project | Role | Difficulty | Estimated hours |
|---|---|---|---|---:|
| PRJ001 | Exploratory Data Analysis Portfolio | Both | Beginner | 12 |
| PRJ002 | SQL Business Analysis | Both | Beginner | 14 |
| PRJ003 | Interactive Business Intelligence Dashboard | Data Analyst | Intermediate | 18 |
| PRJ004 | End-to-End Data Cleaning and ETL Pipeline | Data Analyst | Intermediate | 20 |
| PRJ005 | Statistical Analysis and Hypothesis Testing | Data Scientist | Intermediate | 16 |
| PRJ006 | Explainable Machine Learning Benchmark | Data Scientist | Intermediate | 24 |
| PRJ007 | Text Classification and NLP Evaluation | Data Scientist | Advanced | 28 |
| PRJ008 | Containerized Machine Learning API | Data Scientist | Advanced | 26 |

The catalogue records the skills addressed, project description, role compatibility, difficulty, estimated effort, prerequisites, deliverables, and evidence criteria.

Skill references use canonical IDs from the existing vocabulary, such as `SK001` for Python and `SK003` for SQL. Skill names are not used as substitutes for IDs when matching gaps to projects.

The catalogue is a curated initial set, not an exhaustive representation of every possible portfolio project.

## 4. Input validation

The engine validates the project catalogue and gap records before making recommendations.

Validation includes:
- Required catalogue fields and unique project IDs.
- Supported project roles and difficulty values.
- Positive estimated project hours.
- Known, non-duplicated skill IDs and prerequisites.
- Compatibility between project roles and role-specific skills.
- Supported target roles and valid gap records.
- Duplicate gap IDs and unknown skill IDs.
- Valid hour and difficulty filters.

Invalid inputs should raise validation errors rather than silently produce misleading recommendations.

## 5. Actionable skill gaps

By default, the engine considers gaps with these candidate statuses:
- `potential_gap`
- `insufficient_evidence`
- `mentioned_unverified`
- `rejected_evidence`

Skills marked `verified_skill_present` are excluded by default. Set `include_maintenance=True` to allow verified skills to be included for maintenance-oriented recommendations.

An actionable gap is not necessarily a confirmed skill deficiency. In particular, insufficient CV extraction or unverified mentions can make a gap uncertain. Recommendations identify uncertain skills and advise reviewing CV evidence.

Prerequisites are advisory: the engine does not assume the candidate has completed them.

## 6. Filtering and ranking

Optional filters:
- `max_hours`: exclude projects requiring more than the supplied number of hours.
- `max_difficulty`: limit results to the selected supported difficulty level.

Eligible projects are ranked using this deterministic ordering:

1. Number of actionable skill gaps covered, descending.
2. Mean market priority, descending, but only when every eligible recommendation has comparable observed market evidence.
3. Covered actionable gaps per estimated project hour, descending.
4. Estimated hours, ascending.
5. Project ID, ascending, for deterministic tie-breaking.

Market priority comes from the existing Phase 4 gap records. It describes observed evidence in the current dataset; it is not a probability of employment or a direct measure of a skill's universal importance.

If comparable market evidence is incomplete across eligible recommendations, market priority is reported when available but is not used for ranking.

`coverage_score` and `ranking_score` currently report the same coverage percentage:

`covered actionable skill gaps / total actionable skill gaps * 100`

This is a coverage measure, not the composite sorting formula or a job-readiness score.

## 7. Explainability

Recommendations report the project identity, role fit, covered skill IDs and names, coverage, difficulty, estimated hours, prerequisites, deliverables, evidence criteria, market evidence, ranking method, and an explanation.

Explanations distinguish observed market evidence from missing observations. No observed matches in the current job dataset do not establish that a skill has zero real-world demand.

The engine does not claim that completing a recommended project guarantees employability.

## 8. Relationship with Phase 6

Recommendations identify `project` as the evidence type for tracking and use `unverified` as the initial verification status.

These output fields do not automatically create a progress-tracker database record. A later application workflow must explicitly record submitted project evidence using the Phase 6 tracking functions.

Project completion alone must never mark a skill as verified. Verification requires a separate evidence or assessment process.

This phase does not change the Phase 6 SQLite schema.

## 9. Testing

Run the Phase 7 tests from the repository root:

```powershell
python -m py_compile src\gradpath\project_recommendations.py src\test_project_recommendations.py
python src\test_project_recommendations.py
```

The current Phase 7 test suite contains 22 tests covering:
- Real catalogue loading and role filtering.
- Deterministic output and multi-skill coverage.
- Unknown or incomplete market evidence.
- Verified-skill maintenance behavior.
- Hour and difficulty filters.
- Duplicate and unknown skill/project identifiers.
- Role compatibility of project skills and prerequisites.
- Required-field validation.
- The rule that project completion does not automatically verify a skill.

Passing these tests establishes the tested behavior only. It does not, by itself, establish recommendation quality with real candidates.

## 10. Limitations and next steps

Current limitations:
- The catalogue has eight curated projects.
- Estimated effort and evidence criteria are manually defined.
- Market evidence depends on the existing job dataset and its known coverage limitations.
- Prerequisite completion is not automatically assessed.
- Project recommendations are not yet automatically persisted as learning activities or project-evidence records.
- End-to-end UI integration and real-user evaluation remain future work.

Next steps:
1. Run the existing regression tests for Phases 4–6.
2. Review the final Phase 7 diff and test edge cases.
3. Obtain approval before committing Phase 7.
4. Design an explicit project-evidence submission and verification workflow.
5. Integrate project recommendations and progress into the complete GradPath user journey.
