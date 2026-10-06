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

## 10. Day 2 Conclusion

The occupation mapping is now established:

| GradPath Role | ESCO | O*NET | Mapping |
|---|---|---|---|
| Data Analyst | Data analyst (2511.3) | Business Intelligence Analysts (15-2051.01) | ESCO primary, O*NET proxy |
| Data Scientist | Data scientist (2511.4) | Data Scientists (15-2051.00) | Primary |

The next phase of implementation is to build a reusable extraction pipeline rather than continuing with one-off exploratory commands.