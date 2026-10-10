# GradPath CV Extraction — Initial Evaluation

## Evaluation setup

- Evaluation type: controlled synthetic CV examples
- Number of CV cases: 3
- Skill matching: existing GradPath skill vocabulary and alias matching
- Section detection: existing GradPath section-heading detector

## Results

| Metric | Result |
|---|---:|
| Expected skill matches | 8 |
| Correct skill matches | 8 |
| Unexpected skill matches | 0 |
| Missed expected skills | 0 |
| Precision | 1.000 |
| Recall | 1.000 |
| F1 score | 1.000 |
| Section-heading detection recall | 1.000 |

## Additional checks

- Raw CV text excluded from the structured profile: passed.
- Extracted skills remain unverified: passed.
- Unknown technology was not added to the skill vocabulary: passed.

## Interpretation and limitations

All expected skills and section headings were detected in these three
synthetic examples. The benchmark is small and intentionally controlled.
It does not establish performance on real-world CVs, scanned PDFs, unusual
layouts, multi-column documents, misspellings, or previously unseen aliases.

The evaluation uses the canonical skill names and aliases in the existing
GradPath vocabulary. Expected labels must reflect that vocabulary.

The current profile generator creates schema-aligned entries but does not
reliably infer every degree, institution, employer, job title, date, or
project technology. Missing details should remain unknown rather than
being invented.

Extracted skills remain unverified. Mentioning a skill in a CV is not
proof of proficiency.

## Next evaluation improvements

1. Add more varied synthetic CVs and manually verified expected outputs.
2. Test heading variants and section headings with extra words.
3. Evaluate PDF and DOCX extraction separately.
4. Track errors by skill, section, and document format.
5. Measure performance on a carefully reviewed sample before making
   claims about real-world accuracy.
