# Phase 9: Readiness Scoring Engine

## 1. Purpose

Phase 9 provides a deterministic, explainable report of a candidate's
Verified Skill Coverage for a selected GradPath target role.

The metric is deliberately not called a probability of getting hired.
It describes verified evidence against the current canonical skill
vocabulary, not complete professional readiness.

## 2. Metric definition

Verified Skill Coverage is:

`(verified eligible skills / total eligible canonical skills) * 100`

A skill contributes to the numerator only when:
- Its skill ID exists in the canonical vocabulary for the selected role.
- At least one evidence record has status `verified`.
- No evidence record for that skill has status `rejected`.

Duplicate verified records count the skill only once.

If verified and rejected evidence both exist for a skill, that skill is
marked `conflicting_evidence` and excluded until the conflict is resolved.

If there are no eligible canonical skills, `coverage_percent` is `None`
and `coverage_calculation_status` is `no_eligible_skills`.

## 3. Role-specific denominator

A role's eligible vocabulary includes skills labeled `Both` and skills
labeled for the selected target role.

The current baseline vocabulary contains:
- Data Analyst: 16 eligible canonical skills.
- Data Scientist: 28 eligible canonical skills.

These counts describe the current vocabulary only. They do not establish
that the vocabulary contains every skill required by the job market.

## 4. Evidence rules

The following evidence statuses are recognized:
- `unverified`
- `assessed`
- `verified`
- `rejected`

Only `verified` evidence without a rejected-evidence conflict contributes
to Verified Skill Coverage.

The following do not automatically verify a skill:
- A skill mentioned in a CV.
- Completion of a course or learning activity.
- Completion of a project.
- An assessment attempt by itself.

Missing evidence does not prove that a candidate lacks a skill.

## 5. Assessment summaries

Assessment attempts are summarized separately by assessment type:
- `quiz`
- `coding_exercise`
- `project_evaluation`
- `other`

For valid numeric scores, the normalized percentage is:

`score / max_score * 100`

Only valid finite scores where `max_score > 0` and
`0 <= score <= max_score` are included in the average.

Scoreless attempts and invalid score records are counted separately.
Different assessment types are never combined into one average.

An assessment is attributed to a role only when it is linked to a learning
activity whose candidate and skill match the assessment and whose target
role is supported. Other attempts are reported as unattributed.

Assessment averages are descriptive evidence, not the Verified Skill
Coverage numerator.

## 6. Data safety and compatibility

The scoring engine:
- Opens the existing SQLite database in read-only mode.
- Does not initialize, migrate, or modify database tables.
- Supports the Phase 6 schema version 1 and Phase 8 schema version 2.
- Rejects missing required tables and unsupported schema versions.
- Uses the canonical vocabulary file to determine eligible skills.
- Produces deterministic reports for unchanged inputs and database state.

Phase 9 does not modify Phase 1-8 source files or database schemas.

## 7. Python usage

From the repository root, with the project's virtual environment active:

```python
from gradpath.readiness_scoring import score_readiness

report = score_readiness(
    candidate_id="candidate-1",
    target_role="Data Analyst",
)

print(report["coverage_percent"])
print(report["coverage_calculation_status"])
print(report["skills"])
print(report["assessments"])
```

The database and vocabulary paths can be supplied explicitly when testing
or evaluating a separate dataset.

## 8. Command-line usage

From the repository root:

```powershell
python -m gradpath.readiness_scoring `
  --candidate-id "candidate-1" `
  --target-role "Data Analyst"
```

Optional arguments:
- `--database`: path to the existing progress database.
- `--vocabulary`: path to the canonical skill vocabulary CSV.

## 9. Report fields

- `coverage_percent`: verified skill coverage percentage, or `None` when
  no eligible skills exist.
- `coverage_calculation_status`: `calculated` or `no_eligible_skills`.
- `verified_skill_count`: number of unique eligible skills counted.
- `eligible_skill_count`: denominator for the selected role.
- `evidence_conflict_count`: number of skills with both verified and
  rejected evidence.
- `coverage_status_counts`: counts for verified, conflicting,
  evidence-not-verified, and no-recorded-evidence skills.
- `skills`: per-skill evidence status and inclusion decision.
- `assessments`: assessment summaries for the selected role, unattributed
  attempts, and attempts linked to the other supported role.
- `limitations`: interpretation warnings.
- `database_schema_version`: schema version read from the database.

## 10. Limitations and future evaluation

Verified Skill Coverage depends on the quality and completeness of the
canonical vocabulary and evidence verification process. It does not
measure every aspect of job performance, communication, experience,
portfolio quality, or hiring decisions.

Market-priority scores may help prioritize skill gaps elsewhere in
GradPath, but they do not change the coverage formula.

Before using this metric for consequential decisions, the vocabulary,
verification criteria, assessment quality, and scoring behavior should
be evaluated against appropriate real-world evidence.

## 11. Tests

Phase 9 tests are in `src/test_readiness_scoring.py`.

Run them from the repository root:

```powershell
python -m py_compile .\src\gradpath\readiness_scoring.py .\src\test_readiness_scoring.py
python .\src\test_readiness_scoring.py
```

The test suite covers role-specific denominators, verified and conflicting
evidence, duplicate records, candidate isolation, assessment summaries,
unattributed assessments, schema-version handling, read-only behavior,
invalid inputs, empty vocabularies, and deterministic output.
