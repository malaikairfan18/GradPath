# Phase 1 Day 2 — Occupation Mapping & O*NET/ESCO Analysis

## 1. Objective

The objective of Day 2 was to identify reliable occupation mappings for GradPath's initial target roles and understand how ESCO and O*NET represent occupation-related skills, knowledge, and technologies.

Initial GradPath target roles:

- Data Analyst
- Data Scientist

---

## 2. ESCO Occupation Mapping

### Data Analyst

- ESCO occupation: Data analyst
- Code: 2511.3
- Mapping type: Primary
- URI: http://data.europa.eu/esco/occupation/d3edb8f8-3a06-47a0-8fb9-9b212c006aa2

ESCO describes the occupation as involving importing, inspecting, cleaning, transforming and validating data, interpreting data in relation to business goals, and producing reports, visualizations and dashboards.

### Data Scientist

- ESCO occupation: Data scientist
- Code: 2511.4
- Mapping type: Primary
- URI: http://data.europa.eu/esco/occupation/258e46f9-0075-4a2e-adae-1ff0477e0f30

ESCO describes the occupation as finding and interpreting rich data sources, managing large amounts of data, merging data sources, ensuring consistency, visualization, and applying mathematical models.

---

## 3. O*NET Occupation Mapping

### Data Scientist

- O*NET occupation: Data Scientists
- O*NET-SOC Code: 15-2051.00
- Mapping type: Primary

This is an exact O*NET occupation match for the GradPath Data Scientist role.

### Data Analyst

O*NET 31.0 does not contain a generic occupation titled exactly "Data Analyst".

The selected proxy is:

- O*NET occupation: Business Intelligence Analysts
- O*NET-SOC Code: 15-2051.01
- Mapping type: Proxy

This is not treated as an exact equivalent. It is used because its responsibilities include querying data, identifying patterns and trends, and generating reports and business intelligence.

Other analyst occupations were considered but were less suitable for the initial GradPath Data Analyst profile.

---

## 4. O*NET Data Dimensions

O*NET separates occupation information into several useful dimensions.

### Essential Skills

File:

`data/external/onet/db_31_0_csv/essential_skills.csv`

Essential skills represent general/transferable skills rather than specific technologies.

Examples:

- Reading Comprehension
- Active Listening
- Writing
- Speaking
- Mathematics
- Critical Thinking
- Active Learning
- Learning Strategies
- Monitoring

Both Importance (`IM`) and Level (`LV`) values are available and should be preserved.

O*NET flags such as `Recommend Suppress` and `Not Relevant` must be respected during extraction.

---

## 5. Knowledge

File:

`data/external/onet/db_31_0_csv/knowledge.csv`

Knowledge is kept as a separate dimension from Essential Skills.

Relevant knowledge areas include:

- Computers and Electronics
- Engineering and Technology
- Mathematics
- Economics and Accounting
- Statistics-related areas represented within the O*NET knowledge structure

The complete O*NET taxonomy should be preserved in the raw data.

---

## 6. Software and Technology

File:

`data/external/onet/db_31_0_csv/software_skills.csv`

This dataset contains software/technology associations for occupations.

Important columns:

- O*NET-SOC Code
- Title
- Workplace Example
- Element ID
- Element Name
- Hot Technology
- In Demand

`Element Name` represents broader software categories.

`Workplace Example` contains specific technologies/software such as Python, SQL, Power BI, TensorFlow, Git, etc.

Therefore, GradPath should use `Workplace Example` when extracting concrete technology names.

---

## 7. Technology Analysis

### Data Scientist

- Total technologies: 87
- Shared with BI Analysts: 53
- Data Scientist only: 34

Data Scientist-specific examples include:

- Python ecosystem tools such as pandas, NumPy, SciPy and scikit-learn
- TensorFlow
- PyTorch
- Keras
- XGBoost
- spaCy
- MLflow
- Kubeflow
- PySpark
- Docker
- Kubernetes
- AWS SageMaker
- AWS S3
- BigQuery
- Apache Airflow
- Jupyter
- RESTful API

### Business Intelligence Analyst

- Total technologies: 203
- Shared with Data Scientists: 53
- BI Analyst only: 150

BI Analyst-specific technologies include many enterprise, reporting, business intelligence, database, ERP, CRM and Microsoft/Oracle/SAP ecosystem technologies.

### Shared technologies

Important shared examples include:

- Python
- SQL
- Power BI
- Tableau
- Excel
- R
- Git
- GitHub
- PostgreSQL
- Microsoft SQL Server
- Azure
- AWS
- Spark
- Snowflake
- SAS
- MATLAB

This demonstrates that technology overlap alone cannot completely distinguish Data Analyst and Data Scientist roles.

---

## 8. Technology Prioritization

GradPath should not treat every technology in O*NET as equally important.

O*NET provides:

- Hot Technology
- In Demand

These signals can later help prioritize technologies.

For example, common technologies such as Python and SQL should not automatically receive the same treatment as low-priority general software such as word processors or presentation software.

Future GradPath scoring should consider technology relevance and priority rather than simply counting whether a technology appears in O*NET.

---

## 9. Source Separation

ESCO and O*NET should remain separate source systems during the initial knowledge-base construction.

The raw information should be preserved without prematurely merging or renaming skills.

A later normalization layer will map equivalent concepts across:

- ESCO
- O*NET
- Job-market data
- CV/profile skills

This will allow GradPath to maintain source provenance while eventually creating a unified skill ontology.

---

## 10. Additional O*NET Evidence Dimensions

To avoid treating every occupation requirement as a single type of "skill", GradPath extracts several additional O*NET dimensions.

### Transferable Skills

File:

`data/external/onet/db_31_0_csv/transferable_skills.csv`

Transferable skills describe capabilities that can apply across different activities and occupations.

Examples include:

- Complex Problem Solving
- Programming
- Judgment and Decision Making
- Systems Analysis
- Systems Evaluation
- Time Management
- Coordination
- Social Perceptiveness

Not every transferable skill is relevant to every occupation. O*NET's `Not Relevant` flag must therefore be preserved.

### Abilities

File:

`data/external/onet/db_31_0_csv/abilities.csv`

Abilities represent underlying capabilities associated with occupational performance.

Abilities are kept separate from skills because an ability is not necessarily something that should be treated as a learned CV skill.

### Tasks

File:

`data/external/onet/db_31_0_csv/task_statements.csv`

Tasks describe activities actually performed within an occupation.

Examples for Data Scientists include:

- Analyzing and processing large datasets
- Creating graphs and visualizations
- Testing and validating predictive models
- Cleaning and manipulating raw data
- Applying feature-selection algorithms
- Presenting analytical results
- Recommending data-driven solutions

Examples for Business Intelligence Analysts include:

- Generating business reports
- Maintaining BI tools and dashboards
- Collecting business intelligence data
- Analyzing industry and geographic trends
- Synthesizing information to support recommendations

Tasks provide behavioral/work evidence and should not automatically be converted into skills.

### Work Activities

File:

`data/external/onet/db_31_0_csv/work_activities.csv`

Work Activities provide a higher-level representation of activities involved in performing an occupation.

They are maintained separately from individual task statements.

---

## 11. Occupation Preparation Evidence

GradPath also extracts preparation-related information separately from skill evidence.

### Job Zone

File:

`data/external/onet/db_31_0_csv/job_zones.csv`

Both initial GradPath occupations are classified as:

- Job Zone 4
- Considerable Preparation Needed

O*NET describes Job Zone 4 as generally requiring considerable work-related skill, knowledge, or experience. Most occupations in this zone require a four-year bachelor's degree, while additional work-related experience, training, or vocational preparation may also be involved.

Job Zone is treated as occupation preparation context rather than as a skill-gap score.

### Training and Experience

File:

`data/external/onet/db_31_0_csv/training_and_experience.csv`

GradPath preserves O*NET evidence related to:

- Related Work Experience
- On-Site/In-Plant Training
- On-the-Job Training
- Job-related Apprenticeship

These records should not be interpreted as direct skill requirements.

They represent preparation and experience characteristics of the occupation.

---

## 12. O*NET Scale Interpretation

File:

`data/external/onet/db_31_0_csv/scales_reference.csv`

Important scales used by GradPath include:

- `IM` — Importance, range 1–5
- `LV` — Level, range 0–7
- `RW` — Related Work Experience categories
- `OJ` — On-the-Job Training categories
- `PT` — On-Site/In-Plant Training categories
- `RL/RQ` — Required education categories

Importance and Level must remain separate.

For example, a high Importance value indicates that an element is important to the occupation, while Level represents the required level of the element.

GradPath should not combine these values into a single score during the initial knowledge-base construction.

---

## 13. Processed O*NET Knowledge Base

The reusable extraction pipeline is implemented in:

`src/gradpath/extract_onet.py`

The pipeline currently extracts the following processed datasets:

- `onet_essential_skills.csv`
- `onet_transferable_skills.csv`
- `onet_knowledge.csv`
- `onet_abilities.csv`
- `onet_tasks.csv`
- `onet_work_activities.csv`
- `onet_technologies.csv`
- `onet_job_zone.csv`
- `onet_training_experience.csv`

All processed files are stored in:

`data/processed/`

Each occupation record retains GradPath-specific metadata including:

- GradPath Role
- Mapping Type

Original O*NET occupation identifiers and source metadata are also preserved.

---

## 14. Current Extraction Results

The current processed O*NET datasets contain:

| Dataset | Records |
|---|---:|
| Essential Skills | 40 |
| Transferable Skills | 100 |
| Knowledge | 132 |
| Abilities | 208 |
| Tasks | 33 |
| Work Activities | 164 |
| Technologies | 290 |
| Job Zone | 2 |
| Training & Experience | 60 |

These counts represent extracted O*NET records, not unique GradPath skills or technologies.

Further normalization and deduplication will be performed in a later knowledge-base layer.

---

## 15. Knowledge Representation Principle

GradPath will preserve the distinction between different types of occupational evidence:

`Essential Skill ≠ Transferable Skill ≠ Knowledge ≠ Ability`

`Task ≠ Work Activity`

`Technology ≠ Skill`

`Preparation Evidence ≠ Skill`

This separation is important because GradPath will eventually combine structured occupational knowledge with real job-market data and CV/profile information.

The later normalization layer can establish relationships between these concepts without destroying their original source meaning or provenance.

---

## 16. Day 2 Conclusion

The initial occupation knowledge foundation is now established.

GradPath has:

1. Mapped Data Analyst and Data Scientist to ESCO.
2. Mapped both roles to appropriate O*NET occupations.
3. Identified the O*NET Data Analyst mapping as a proxy rather than an exact equivalent.
4. Inspected the major O*NET evidence dimensions.
5. Verified the meaning of important O*NET scales and preparation categories.
6. Built a reusable O*NET extraction pipeline.
7. Generated processed occupation evidence for both target roles.

The next step is no longer exploratory O*NET inspection. The extracted evidence should now be evaluated and integrated with the other GradPath knowledge sources, particularly ESCO and job-market data, while maintaining source provenance.

## ESCO Skill Knowledge Base

### ESCO occupation-skill relationships

The ESCO `occupationSkillRelations_en.csv` dataset was inspected to understand how ESCO connects occupations with required skills and knowledge.

For the two GradPath target occupations, the mapped ESCO occupation relationships produced:

| GradPath Role  | Relationship | Skill Type       | Count |
| -------------- | ------------ | ---------------- | ----: |
| Data Analyst   | Essential    | Knowledge        |    19 |
| Data Analyst   | Essential    | Skill/Competence |    16 |
| Data Analyst   | Optional     | Knowledge        |    21 |
| Data Analyst   | Optional     | Skill/Competence |    10 |
| Data Scientist | Essential    | Knowledge        |    18 |
| Data Scientist | Essential    | Skill/Competence |    45 |
| Data Scientist | Optional     | Knowledge        |    22 |
| Data Scientist | Optional     | Skill/Competence |    12 |

There were **164 occupation-skill/knowledge relationships** across the two mapped occupations.

The ESCO model distinguishes between:

* `skill/competence` — an ability or capability that can be demonstrated.
* `knowledge` — a body of information or understanding required for an occupation.

GradPath therefore preserves these as separate evidence types rather than combining them into one generic "skill" category.

### ESCO skill metadata

The `skills_en.csv` dataset was inspected to understand the metadata available for individual ESCO concepts.

Important fields include:

* `conceptUri` — unique ESCO concept identifier.
* `preferredLabel` — canonical concept name.
* `altLabels` — alternative terminology useful for future NLP and job-post matching.
* `skillType` — distinguishes skill/competence from knowledge.
* `reuseLevel` — indicates the reuse level of the concept across occupations/sectors.
* `definition` and `description` — semantic information about the concept.
* `status` and `modifiedDate` — concept lifecycle and version information.

This metadata will support later skill normalization and NLP-based matching.

### ESCO hierarchy

The `skillsHierarchy_en.csv` file was inspected as a taxonomy/category layer.

The hierarchy contains Level 0 through Level 3 categories, but the 113 unique ESCO concepts linked to the GradPath occupations did not directly match these hierarchy URI columns.

Therefore, GradPath does not force the occupation-linked leaf concepts into this hierarchy. The hierarchy is retained as a separate taxonomy layer that may be useful for future categorization.

### ESCO skill-to-skill relationships

The `skillSkillRelations_en.csv` dataset contains relationships between individual ESCO skill/knowledge concepts.

The complete dataset contains 5,818 relationships:

* 5,629 optional
* 189 essential

Most relationships originate from `skill/competence` concepts and point to `knowledge` concepts.

After filtering to concepts associated with the two GradPath target occupations, **124 relevant relationships** were identified:

* 104 optional
* 20 essential
* 122 originating from skill/competence
* 2 originating from knowledge
* 109 related knowledge concepts
* 15 related skill/competence concepts

This relationship layer is treated as an **enrichment and supporting-knowledge layer**, not as the primary skill-gap scoring mechanism. The core requirement signal remains the occupation-to-skill/knowledge relationship from `occupationSkillRelations_en.csv`.

### Processed ESCO datasets

The following processed datasets were created:

| File                                          | Purpose                                                   | Rows |
| --------------------------------------------- | --------------------------------------------------------- | ---: |
| `data/processed/esco_role_skills.csv`         | Initial merged role-skill dataset with full ESCO metadata |  164 |
| `data/processed/esco_role_skills_clean.csv`   | Clean role-skill/knowledge dataset                        |  164 |
| `data/processed/esco_skill_relationships.csv` | Role-relevant ESCO skill relationships                    |  124 |

Both final processed datasets contain **zero duplicate rows**.

### ESCO knowledge representation principle

GradPath will preserve the distinction between:

```text
Occupation
    ↓
Occupation Requirement
    ↓
Skill/Competence OR Knowledge
    ↓
Supporting Skill/Knowledge Relationships
```

The project will not flatten these concepts into a single undifferentiated skill list.

This distinction is important because later stages of GradPath may use different evidence types for different purposes:

* `skill/competence` → direct capability matching.
* `knowledge` → knowledge-area matching and supporting context.
* `essential` → higher-priority occupation requirement.
* `optional` → supplementary occupation requirement.
* `altLabels` → terminology expansion for NLP matching.
* skill relationships → supporting knowledge and recommendation context.

### ESCO conclusion

ESCO provides GradPath with a structured occupation-to-skill knowledge base that complements the O*NET evidence layer.

The ESCO data is particularly valuable for:

1. Structured skill and knowledge concepts.
2. Essential versus optional occupation requirements.
3. Alternative terminology for NLP matching.
4. Explicit semantic definitions.
5. Relationships between skills/competences and supporting knowledge.

ESCO and O*NET will remain separate source systems during Phase 1. They will be compared and potentially integrated at a later modeling stage rather than being prematurely merged.

### ESCO role comparison

A role-level comparison was created using the unique ESCO concepts associated with the two GradPath target occupations.

The comparison identified:

| Comparison          | Concepts |
| ------------------- | -------: |
| Shared              |       51 |
| Data Analyst only   |       16 |
| Data Scientist only |       46 |

The comparison contains **113 unique ESCO concepts** across the two occupations.

This comparison is used as an analytical reference rather than a direct skill-gap score. A concept being present only in one occupation does not automatically mean that it is mandatory; the original ESCO `essential`/`optional` relationship and `skill/competence`/`knowledge` type are retained.

The comparison is stored in:

`data/processed/esco_role_comparison.csv`

This provides an initial evidence-based view of how ESCO differentiates the Data Analyst and Data Scientist roles.
