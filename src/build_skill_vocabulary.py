from pathlib import Path

import pandas as pd


# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------

ONET_PATH = Path(
    "data/processed/onet_technologies.csv"
)

ESCO_PATH = Path(
    "data/processed/esco_role_skills_clean.csv"
)

OUTPUT_PATH = Path(
    "data/processed/initial_skill_vocabulary.csv"
)


# -------------------------------------------------------------------
# Curated baseline vocabulary
# -------------------------------------------------------------------
#
# These are deliberately limited to high-value skills/concepts for
# the two GradPath target roles.
#
# O*NET and ESCO are used as provenance sources, but we do not dump
# every taxonomy entry into the extraction vocabulary.
# -------------------------------------------------------------------

BASELINE_SKILLS = [

    # ---------------------------------------------------------------
    # Programming
    # ---------------------------------------------------------------

    {
        "skill_name": "Python",
        "skill_category": "Programming",
        "role": "Both",
        "source": "O*NET",
        "aliases": "python;python 3",
    },

    {
        "skill_name": "R",
        "skill_category": "Programming",
        "role": "Both",
        "source": "O*NET",
        "aliases": "r programming;r language",
    },

    # ---------------------------------------------------------------
    # Databases
    # ---------------------------------------------------------------

    {
        "skill_name": "SQL",
        "skill_category": "Databases",
        "role": "Both",
        "source": "O*NET",
        "aliases": "sql;structured query language",
    },

    {
        "skill_name": "PostgreSQL",
        "skill_category": "Databases",
        "role": "Both",
        "source": "O*NET",
        "aliases": "postgres;postgresql",
    },

    {
        "skill_name": "MySQL",
        "skill_category": "Databases",
        "role": "Both",
        "source": "O*NET",
        "aliases": "mysql",
    },

    # ---------------------------------------------------------------
    # Data Analysis
    # ---------------------------------------------------------------

    {
        "skill_name": "Data Analysis",
        "skill_category": "Data Analysis",
        "role": "Both",
        "source": "ESCO",
        "aliases": "data analysis;data analytics;analytical analysis",
    },

    {
        "skill_name": "Data Cleaning",
        "skill_category": "Data Preparation",
        "role": "Both",
        "source": "ESCO",
        "aliases": "data cleaning;clean data;data cleansing",
    },

    {
        "skill_name": "Data Preprocessing",
        "skill_category": "Data Preparation",
        "role": "Both",
        "source": "ESCO",
        "aliases": "data preprocessing;data pre-processing;data preprocessing techniques",
    },

    # ---------------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------------

    {
        "skill_name": "Statistics",
        "skill_category": "Statistics",
        "role": "Both",
        "source": "ESCO",
        "aliases": "statistics;statistical analysis;statistical methods",
    },

    {
        "skill_name": "Statistical Modeling",
        "skill_category": "Statistics",
        "role": "Data Scientist",
        "source": "ESCO",
        "aliases": "statistical modeling;statistical modelling",
    },

    # ---------------------------------------------------------------
    # BI / Visualization
    # ---------------------------------------------------------------

    {
        "skill_name": "Power BI",
        "skill_category": "BI & Visualization",
        "role": "Data Analyst",
        "source": "O*NET/ESCO",
        "aliases": "power bi;microsoft power bi",
    },

    {
        "skill_name": "Tableau",
        "skill_category": "BI & Visualization",
        "role": "Data Analyst",
        "source": "O*NET/ESCO",
        "aliases": "tableau",
    },

    {
        "skill_name": "Data Visualization",
        "skill_category": "BI & Visualization",
        "role": "Both",
        "source": "ESCO",
        "aliases": "data visualization;data visualisation;information visualization;information visualisation",
    },

    # ---------------------------------------------------------------
    # Python data libraries
    # ---------------------------------------------------------------

    {
        "skill_name": "Pandas",
        "skill_category": "Data Analysis",
        "role": "Both",
        "source": "O*NET",
        "aliases": "pandas;python pandas",
    },

    {
        "skill_name": "NumPy",
        "skill_category": "Data Analysis",
        "role": "Data Scientist",
        "source": "O*NET",
        "aliases": "numpy",
    },

    # ---------------------------------------------------------------
    # Machine Learning
    # ---------------------------------------------------------------

    {
        "skill_name": "Machine Learning",
        "skill_category": "Machine Learning",
        "role": "Data Scientist",
        "source": "ESCO",
        "aliases": "machine learning;ml",
    },

    {
        "skill_name": "Deep Learning",
        "skill_category": "Machine Learning",
        "role": "Data Scientist",
        "source": "ESCO",
        "aliases": "deep learning;deep neural networks",
    },

    {
        "skill_name": "scikit-learn",
        "skill_category": "Machine Learning",
        "role": "Data Scientist",
        "source": "O*NET",
        "aliases": "scikit-learn;scikit learn;sklearn",
    },

    {
        "skill_name": "TensorFlow",
        "skill_category": "Machine Learning",
        "role": "Data Scientist",
        "source": "O*NET",
        "aliases": "tensorflow",
    },

    {
        "skill_name": "PyTorch",
        "skill_category": "Machine Learning",
        "role": "Data Scientist",
        "source": "O*NET",
        "aliases": "pytorch",
    },

    # ---------------------------------------------------------------
    # NLP
    # ---------------------------------------------------------------

    {
        "skill_name": "Natural Language Processing",
        "skill_category": "NLP",
        "role": "Data Scientist",
        "source": "ESCO",
        "aliases": "natural language processing;nlp",
    },

    # ---------------------------------------------------------------
    # Modeling
    # ---------------------------------------------------------------

    {
        "skill_name": "Data Modeling",
        "skill_category": "Data Modeling",
        "role": "Both",
        "source": "ESCO",
        "aliases": "data modeling;data modelling",
    },

    {
        "skill_name": "Feature Engineering",
        "skill_category": "Machine Learning",
        "role": "Data Scientist",
        "source": "O*NET/ESCO",
        "aliases": "feature engineering;feature extraction",
    },

    # ---------------------------------------------------------------
    # Data Engineering / ETL
    # ---------------------------------------------------------------

    {
        "skill_name": "ETL",
        "skill_category": "Data Engineering",
        "role": "Data Analyst",
        "source": "O*NET",
        "aliases": "etl;extract transform load;extract-transform-load",
    },

    {
        "skill_name": "Data Engineering",
        "skill_category": "Data Engineering",
        "role": "Data Scientist",
        "source": "ESCO",
        "aliases": "data engineering;data engineering methods",
    },

    # ---------------------------------------------------------------
    # Cloud
    # ---------------------------------------------------------------

    {
        "skill_name": "AWS",
        "skill_category": "Cloud",
        "role": "Data Scientist",
        "source": "O*NET",
        "aliases": "aws;amazon web services;amazon web services aws",
    },

    {
        "skill_name": "Microsoft Azure",
        "skill_category": "Cloud",
        "role": "Data Scientist",
        "source": "O*NET",
        "aliases": "azure;microsoft azure",
    },

    # ---------------------------------------------------------------
    # DevOps / Engineering
    # ---------------------------------------------------------------

    {
        "skill_name": "Git",
        "skill_category": "Version Control",
        "role": "Both",
        "source": "O*NET",
        "aliases": "git;git version control",
    },

    {
        "skill_name": "Docker",
        "skill_category": "DevOps",
        "role": "Data Scientist",
        "source": "O*NET",
        "aliases": "docker;docker containers;containerization",
    },

    # ---------------------------------------------------------------
    # Big Data
    # ---------------------------------------------------------------

    {
        "skill_name": "Apache Spark",
        "skill_category": "Big Data",
        "role": "Data Scientist",
        "source": "O*NET",
        "aliases": "spark;apache spark;pyspark",
    },

    {
        "skill_name": "Apache Hadoop",
        "skill_category": "Big Data",
        "role": "Data Scientist",
        "source": "O*NET",
        "aliases": "hadoop;apache hadoop",
    },
]


# -------------------------------------------------------------------
# Helper
# -------------------------------------------------------------------

def validate_source_files():
    """
    Confirm that the Phase-1 source files exist and contain the
    expected columns.
    """

    if not ONET_PATH.exists():
        raise FileNotFoundError(
            f"O*NET file not found: {ONET_PATH}"
        )

    if not ESCO_PATH.exists():
        raise FileNotFoundError(
            f"ESCO file not found: {ESCO_PATH}"
        )

    onet_df = pd.read_csv(ONET_PATH)
    esco_df = pd.read_csv(ESCO_PATH)

    required_onet_columns = [
        "GradPath Role",
        "Title",
        "Element Name",
    ]

    required_esco_columns = [
        "GradPath Role",
        "skillLabel",
        "skillType",
        "altLabels",
    ]

    for column in required_onet_columns:
        if column not in onet_df.columns:
            raise ValueError(
                f"Missing O*NET column: {column}"
            )

    for column in required_esco_columns:
        if column not in esco_df.columns:
            raise ValueError(
                f"Missing ESCO column: {column}"
            )

    return onet_df, esco_df


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def main():

    print("\nGradPath Initial Skill Vocabulary")
    print("=" * 60)

    # ---------------------------------------------------------------
    # Validate Phase-1 sources
    # ---------------------------------------------------------------

    onet_df, esco_df = validate_source_files()

    print(
        f"\nO*NET technology records available: "
        f"{len(onet_df)}"
    )

    print(
        f"ESCO role-skill records available: "
        f"{len(esco_df)}"
    )

    # ---------------------------------------------------------------
    # Create vocabulary
    # ---------------------------------------------------------------

    vocabulary = pd.DataFrame(
        BASELINE_SKILLS
    )

    # ---------------------------------------------------------------
    # Add stable IDs
    # ---------------------------------------------------------------

    vocabulary.insert(
        0,
        "skill_id",
        [
            f"SK{i:03d}"
            for i in range(
                1,
                len(vocabulary) + 1,
            )
        ],
    )

    # ---------------------------------------------------------------
    # Basic validation
    # ---------------------------------------------------------------

    if vocabulary["skill_name"].duplicated().any():

        duplicates = (
            vocabulary.loc[
                vocabulary["skill_name"].duplicated(),
                "skill_name",
            ]
            .tolist()
        )

        raise ValueError(
            f"Duplicate skill names found: {duplicates}"
        )

    # ---------------------------------------------------------------
    # Save
    # ---------------------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    vocabulary.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8",
    )

    # ---------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------

    print("\n" + "=" * 60)
    print("VOCABULARY SUMMARY")
    print("=" * 60)

    print(
        f"\nTotal baseline skills: "
        f"{len(vocabulary)}"
    )

    print("\nBy role:")

    print(
        vocabulary["role"]
        .value_counts()
    )

    print("\nBy category:")

    print(
        vocabulary["skill_category"]
        .value_counts()
    )

    print("\nVocabulary:")

    print(
        vocabulary[
            [
                "skill_id",
                "skill_name",
                "skill_category",
                "role",
                "source",
            ]
        ].to_string(index=False)
    )

    print("\nOutput:")
    print(OUTPUT_PATH)

    print("\nInitial skill vocabulary complete.")


if __name__ == "__main__":
    main()