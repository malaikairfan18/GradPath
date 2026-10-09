# GradPath Phase 2 Day 5 - Seniority Analysis

## Scope
- All collected listings: 312
- Relevant listings: 251
- Method: rule-based classification of job titles.

## Limitations
- Unspecified does not mean entry-level.
- Labels are inferred from title wording, not verified experience requirements.
- Rule order resolves titles containing multiple seniority markers.
- This collected sample is not necessarily representative of the entire UK market.

## Relevant jobs by role and seniority
```text
 role_category        seniority_level  job_count  role_total  percentage_within_role
  Data Analyst Entry-level / Graduate          4         124                    3.23
  Data Analyst                 Junior          7         124                    5.65
  Data Analyst                   Lead          3         124                    2.42
  Data Analyst                 Senior         20         124                   16.13
  Data Analyst            Unspecified         90         124                   72.58
Data Scientist Entry-level / Graduate         25         127                   19.69
Data Scientist                 Junior          5         127                    3.94
Data Scientist                   Lead          6         127                    4.72
Data Scientist Management / Principal          9         127                    7.09
Data Scientist                 Senior         26         127                   20.47
Data Scientist            Unspecified         56         127                   44.09
```

## Relevant job counts by role
```text
seniority_level  Entry-level / Graduate  Junior  Mid-level / Experienced  Unspecified  Senior  Lead  Management / Principal
role_category
Data Analyst                          4       7                        0           90      20     3                       0
Data Scientist                       25       5                        0           56      26     6                       9
```

## Counts across all collected listings
```text
role_relevance        seniority_level  job_count
    irrelevant Entry-level / Graduate          1
    irrelevant                   Lead          3
    irrelevant                 Senior          4
    irrelevant            Unspecified         16
      relevant Entry-level / Graduate         29
      relevant                 Junior         12
      relevant                   Lead          9
      relevant Management / Principal          9
      relevant                 Senior         46
      relevant            Unspecified        146
     uncertain Entry-level / Graduate          1
     uncertain                 Junior          2
     uncertain                   Lead          2
     uncertain Management / Principal          2
     uncertain                 Senior          7
     uncertain            Unspecified         23
```
