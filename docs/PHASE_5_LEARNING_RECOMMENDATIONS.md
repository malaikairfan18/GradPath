\# Phase 5 — Learning Recommendation Engine



\## 1. Overview



Phase 5 implements the GradPath Learning Recommendation Engine. It converts skill-gap analysis results from Phase 4 into structured, explainable learning recommendations for the target roles Data Analyst and Data Scientist.



The engine uses a curated learning-resource catalogue and the candidate's skill-evidence status. It is designed to avoid inventing learning resources and to handle uncertain or incomplete evidence cautiously.



\## 2. Main Components



\- `src/gradpath/learning\_recommendations.py` — recommendation logic, input validation, resource matching, explanations, and output ordering.

\- `data/resources/learning\_resources.csv` — curated catalogue of learning resources.

\- `src/test\_learning\_recommendations.py` — unit tests for recommendation behavior.

\- `src/test\_phase5\_integration.py` — integration tests using Phase 4 skill-gap outputs.

\- `src/test\_learning\_recommendation\_edge\_cases.py` — tests for missing values and invalid inputs.



\## 3. Recommendation Behavior



The engine supports the Data Analyst and Data Scientist target roles.



It uses the candidate's skill status and available resources to determine an appropriate action. Potential skill gaps can receive learning recommendations when a compatible resource exists. Missing resources must not result in fabricated learning actions.



Uncertain evidence and incomplete CV extraction are handled cautiously. Verified skills are excluded from recommendations by default unless maintenance recommendations are explicitly enabled.



Recommendations include explanations that distinguish market evidence, ESCO evidence, and candidate readiness. The engine validates incoming skill-gap records and resource catalogues rather than silently accepting malformed inputs.



\## 4. Learning Resource Catalogue



The catalogue currently contains 31 resources covering 31 skill IDs, from `SK001` to `SK031`.



| Attribute | Observed result |

|---|---|

| Total resources | 31 |

| Missing values | 0 |

| Duplicate resource IDs | 0 |

| Duplicate skill-role pairs | 0 |

| Duplicate URLs | 4 |

| Resource types | Tutorials, courses, documentation, exercises |

| Access | 30 free resources and 1 freemium resource |

| Difficulty | 24 beginner and 7 intermediate resources |



Resources are assigned to Data Analyst, Data Scientist, or shared (`Both`) roles.



\### Catalogue Quality Considerations



The catalogue has initial breadth but only one entry per skill ID. Some URLs are reused across skills, including pandas tutorials and Power BI training. Reused URLs should be retained when the same material genuinely supports multiple skills; otherwise, more specific destinations should be added.



General Microsoft Learn links should be reviewed to ensure that they lead learners toward the topic described by the resource title. Resource URLs and descriptions should be periodically verified for accuracy, accessibility, and relevance.



\## 5. Validation and Error Handling



The implementation includes validation for required skill-gap fields, supported target roles, candidate statuses, priority scores, and resource metadata.



Edge-case handling includes:



\- Missing priority scores represented by `NaN`.

\- Missing market ranks.

\- Rejection of invalid priority text.

\- Safe handling of string boolean values.

\- Rejection of unsupported resource difficulty labels.

\- Rejection of unsupported resource types.

\- Exclusion of potential gaps when no compatible learning resource exists.



A missing numeric priority is normalized to a low-priority value rather than being treated as strong evidence. Invalid numeric text and non-finite priority values are rejected.



\## 6. Testing Results



The following tests passed during Phase 5 development:



| Test suite | Result |

|---|---:|

| Learning recommendation unit tests | 13 passed |

| Phase 4-to-Phase 5 integration tests | 5 passed |

| Learning recommendation edge-case tests | 6 passed |

| Total | 24 passed |



These results reflect the test runs performed during development. Regression testing across earlier phases remains a separate completion check.



\## 7. Current Limitations



\- The learning-resource catalogue is curated and has limited redundancy per skill.

\- Some resources use broad landing pages or URLs shared by multiple skills.

\- The catalogue has more Data Scientist-specific resources than Data Analyst-specific resources.

\- Resource quality, availability, and link accuracy require periodic review.

\- Passing tests establishes expected software behavior for the covered cases; it does not independently establish the educational quality of every resource or the real-world predictive validity of recommendations.



\## 8. Completion Checklist



\- \[x] Implement learning recommendation engine.

\- \[x] Add unit tests.

\- \[x] Verify Phase 4-to-Phase 5 integration.

\- \[x] Add edge-case tests.

\- \[x] Validate initial resource-catalogue structure.

\- \[ ] Review resource URLs and skill mappings.

\- \[ ] Run regression tests for earlier phases.

\- \[ ] Review the final Git diff.

\- \[ ] Commit Phase 5 implementation and documentation.
