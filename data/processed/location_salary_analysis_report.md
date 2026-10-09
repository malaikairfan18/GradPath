# GradPath Phase 2 Day 6 - Location and Salary Analysis

## Scope
- Total collected listings: 312
- Relevant listings analysed: 251
- Country code in relevant sample: gb

## Location coverage
- Distinct location strings: 109
- Listings without coordinates: 56

### Listings by inferred broad region
Region labels are heuristic, based on text in the location field.

```text
 role_category             location_region  job_count  role_total  percentage_within_role
  Data Analyst             East of England          2         124                    1.61
  Data Analyst                      London         32         124                   25.81
  Data Analyst                    Midlands         13         124                   10.48
  Data Analyst          North West England          8         124                    6.45
  Data Analyst            Northern Ireland          9         124                    7.26
  Data Analyst Other / town-level location         23         124                   18.55
  Data Analyst                    Scotland         11         124                    8.87
  Data Analyst          South East England          4         124                    3.23
  Data Analyst          South West England          3         124                    2.42
  Data Analyst       UK-wide / unspecified         15         124                   12.10
  Data Analyst        Yorkshire and Humber          4         124                    3.23
Data Scientist             East of England          3         127                    2.36
Data Scientist                      London         44         127                   34.65
Data Scientist                    Midlands          9         127                    7.09
Data Scientist          North East England          1         127                    0.79
Data Scientist          North West England         12         127                    9.45
Data Scientist            Northern Ireland          3         127                    2.36
Data Scientist Other / town-level location         14         127                   11.02
Data Scientist                    Scotland          1         127                    0.79
Data Scientist          South East England         13         127                   10.24
Data Scientist          South West England         12         127                    9.45
Data Scientist       UK-wide / unspecified          9         127                    7.09
Data Scientist                       Wales          1         127                    0.79
Data Scientist        Yorkshire and Humber          5         127                    3.94
```

### Most frequent exact locations

```text
role_category             location_region                       location_text  job_count  role_total  percentage_within_role
 Data Analyst                      London                          London, UK         19         124                   15.32
 Data Analyst       UK-wide / unspecified                                  UK         15         124                   12.10
 Data Analyst                    Midlands           Birmingham, West Midlands          6         124                    4.84
 Data Analyst            Northern Ireland           Belfast, Northern Ireland          4         124                    3.23
 Data Analyst                      London          Farringdon, Central London          4         124                    3.23
 Data Analyst                    Scotland                   Glasgow, Scotland          4         124                    3.23
 Data Analyst        Yorkshire and Humber                    Hyde Park, Leeds          3         124                    2.42
 Data Analyst          North West England                Rusholme, Manchester          3         124                    2.42
 Data Analyst                      London           South West London, London          3         124                    2.42
 Data Analyst          South West England         Bristol, South West England          2         124                    1.61
 Data Analyst            Northern Ireland         Coleraine, Northern Ireland          2         124                    1.61
 Data Analyst                    Scotland Edinburgh Technopole, Milton Bridge          2         124                    1.61
 Data Analyst                    Scotland                 Edinburgh, Scotland          2         124                    1.61
 Data Analyst                    Scotland        Glasgow City Centre, Glasgow          2         124                    1.61
 Data Analyst          North West England               Liverpool, Merseyside          2         124                    1.61
 Data Analyst          North West England      Manchester, Greater Manchester          2         124                    1.61
 Data Analyst             East of England               Pampisford, Cambridge          2         124                    1.61
 Data Analyst Other / town-level location           Shendish, Hemel Hempstead          2         124                    1.61
 Data Analyst                      London            The City, Central London          2         124                    1.61
 Data Analyst                    Midlands        Wolverhampton, West Midlands          2         124                    1.61
 Data Analyst Other / town-level location          Abbotts Barton, Winchester          1         124                    0.81
 Data Analyst Other / town-level location             Alloa, Clackmannanshire          1         124                    0.81
 Data Analyst                    Midlands               Alum Rock, Birmingham          1         124                    0.81
 Data Analyst Other / town-level location               Antrim, County Antrim          1         124                    0.81
 Data Analyst                    Midlands           Balsall Heath, Birmingham          1         124                    0.81
 Data Analyst Other / town-level location                    Blackley, Elland          1         124                    0.81
 Data Analyst Other / town-level location                   Broadbottom, Hyde          1         124                    0.81
 Data Analyst                      London           Canary Wharf, East London          1         124                    0.81
 Data Analyst                      London              Central London, London          1         124                    0.81
 Data Analyst            Northern Ireland     County Antrim, Northern Ireland          1         124                    0.81
```

## Salary quality
- Listings passing basic salary checks: 239 of 251
- Listings flagged for review: 12
- Listings missing contract type: 159

### Salary quality by role

```text
 role_category salary_quality_status  job_count  role_total  percentage_within_role
  Data Analyst          Needs review          5         124                    4.03
  Data Analyst   Passed basic checks        119         124                   95.97
Data Scientist          Needs review          7         127                    5.51
Data Scientist   Passed basic checks        120         127                   94.49
```

### Predicted salary flag counts

```text
 salary_is_predicted  job_count  percentage_of_relevant_jobs
                   0        136                        54.18
                   1        115                        45.82
```

### Salary summaries after basic checks

```text
 role_category  salary_is_predicted  job_count  median_salary_min  median_salary_max  mean_salary_min  mean_salary_max  minimum_observed  maximum_observed
  Data Analyst                    0         66           47000.00           55000.00         51937.71         59057.70            350.00          156000.0
  Data Analyst                    1         53           49794.01           49794.01         49765.89         49765.89          29751.60           72691.6
Data Scientist                    0         58           39000.00           51500.00         47075.84         61206.07            100.00          169000.0
Data Scientist                    1         62           53537.27           53537.27         58702.45         58702.45          39228.73          126464.5
```

## Interpretation and limitations
- Salary fields are source-provided figures; the pay period and unit are not verified here.
- Values passing basic checks are not guaranteed to be accurate or comparable.
- Predicted and non-predicted salaries are summarized separately.
- Records flagged for review are retained in the detailed output and excluded from primary salary summaries.
- Location regions are heuristic; they should not be treated as verified administrative boundaries.
- The collected sample is not necessarily representative of the entire UK job market.

## Output files
- `job_location_summary.csv`: counts by exact location and role
- `job_region_summary.csv`: counts by inferred broad region and role
- `salary_quality_summary.csv`: basic salary quality by role
- `salary_market_summary.csv`: salary summaries by role and predicted flag
- `location_salary_quality_detail.csv`: relevant listings and quality flags
