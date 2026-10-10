# GradPath Candidate Profile Schema

## 1. Purpose

This document defines the structured output of the Phase 3 CV
parsing and skill extraction pipeline.

The profile contains career-relevant information for skill-gap
analysis. The original CV remains separate from this profile.

## 2. Design principles

- Use the existing GradPath skill vocabulary and stable skill IDs.
- Preserve short evidence snippets so skill matches can be inspected.
- Record the CV section where each skill was found.
- Distinguish a skill mention from supporting evidence.
- Never mark a skill as verified solely because it appears in a CV.
- Represent missing information as null or an empty list.
- Record extraction warnings rather than silently hiding failures.
- Do not store full CV text, contact details, or original file paths
  in the structured profile by default.

## 3. Top-level profile structure

A candidate profile contains:

- schema_version: version of this profile structure.
- candidate_id: generated identifier for the profile.
- source_document: document type and extraction metadata.
- education: extracted education entries.
- experience: extracted work experience entries.
- projects: extracted project entries.
- certifications: extracted certification entries.
- skills: normalized skills with supporting evidence.
- extraction_warnings: limitations or issues encountered.

## 4. Example profile

{
  "schema_version": "1.0",
  "candidate_id": "candidate_001",
  "source_document": {
    "file_type": "pdf",
    "extraction_status": "success",
    "text_char_count": 2450
  },
  "education": [
    {
      "degree": "BS Data Science",
      "institution": "Example University",
      "start_date": null,
      "end_date": "2026",
      "details": null
    }
  ],
  "experience": [
    {
      "job_title": "Data Analyst Intern",
      "organization": "Example Company",
      "start_date": null,
      "end_date": null,
      "description": "Analyzed datasets using Python and SQL."
    }
  ],
  "projects": [
    {
      "name": "Sales Analysis",
      "description": "Analyzed sales data and created a dashboard.",
      "technologies": ["Python", "SQL", "Power BI"]
    }
  ],
  "certifications": [
    {
      "name": "Example Data Analytics Certificate",
      "issuer": null,
      "date": null
    }
  ],
  "skills": [
    {
      "skill_id": "SK001",
      "skill_name": "Python Programming",
      "skill_category": "Programming",
      "role": "Both",
      "evidence": [
        {
          "section": "Projects",
          "text": "Analyzed datasets using Python.",
          "evidence_type": "project_mention"
        }
      ],
      "matched_alias": "python",
      "match_type": "alias",
      "normalization_status": "matched",
      "verification_status": "unverified"
    }
  ],
  "extraction_warnings": []
}

This example is illustrative. Actual skill IDs, names, categories,
roles, and aliases must come from the existing GradPath vocabulary.

## 5. Field definitions

### Source document

- file_type: supported input type, such as pdf or docx.
- extraction_status: success, partial, or failed.
- text_char_count: number of characters extracted from the document.

Do not include the original file path or the full extracted text.

### Education

- degree: degree or qualification stated in the CV.
- institution: educational institution, if identified.
- start_date: start date or year, when available.
- end_date: end date, graduation year, or expected graduation year.
- details: relevant additional education information.

### Experience

- job_title: role or position.
- organization: employer or organization, if identified.
- start_date and end_date: dates as stated or normalized when reliable.
- description: relevant extracted responsibilities and achievements.

### Projects

- name: project name, if identified.
- description: relevant project summary.
- technologies: technologies explicitly associated with the project.

### Certifications

- name: certification title.
- issuer: issuing organization, when identified.
- date: certification date, when available.

### Skills

- skill_id: stable ID from the GradPath skill vocabulary.
- skill_name: canonical vocabulary name.
- skill_category: category from the vocabulary.
- role: role applicability from the vocabulary.
- evidence: short supporting snippets and their CV sections.
- matched_alias: vocabulary alias that triggered the match.
- match_type: canonical or alias match.
- normalization_status: matched or another documented status.
- verification_status: unverified unless independently assessed.

### Evidence types

- skill_mention: the skill is explicitly mentioned in the CV.
- project_mention: the skill appears in project-related evidence.
- experience_mention: the skill appears in work-related evidence.
- education_mention: the skill appears in education-related evidence.
- certification_mention: the skill appears in certification-related evidence.

These categories describe where the text was found. They do not
prove actual proficiency.

## 6. Extraction rules

1. Do not invent missing dates, organizations, qualifications, or skills.
2. Use null for unknown single values and empty lists for absent collections.
3. Preserve short evidence snippets from the source text.
4. Normalize recognized skills using the existing GradPath vocabulary.
5. Keep unmatched skill phrases available for later review rather than
   assigning them an invented skill ID.
6. Record parsing failures, ambiguous matches, and other important
   limitations in extraction_warnings.
7. Keep profile output consistent across PDF and DOCX inputs.

## 7. Privacy and storage

The structured profile must not contain the complete original CV,
personal contact details, or the original file path by default.

Original documents and extracted text should be handled separately,
with appropriate access controls and temporary processing where possible.

## 8. Validation requirements

Before a profile is accepted, validate that:

- all required top-level keys exist;
- collection fields are lists;
- skill IDs exist in the GradPath vocabulary;
- canonical skill names and categories agree with that vocabulary;
- evidence snippets are non-empty when a skill match is recorded;
- verification_status is not automatically set to verified;
- missing values use the documented null or empty-list conventions;
- parsing problems are recorded rather than silently ignored.
