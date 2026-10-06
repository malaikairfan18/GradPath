import pandas as pd
from pathlib import Path


# ============================================================
# Project paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ONET_DIR = PROJECT_ROOT / "data" / "external" / "onet" / "db_31_0_csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


# ============================================================
# GradPath target occupation mappings
# ============================================================

OCCUPATIONS = {
    "Data Analyst": {
        "onet_code": "15-2051.01",
        "onet_title": "Business Intelligence Analysts",
        "mapping_type": "proxy",
    },
    "Data Scientist": {
        "onet_code": "15-2051.00",
        "onet_title": "Data Scientists",
        "mapping_type": "primary",
    },
}


# ============================================================
# Generic O*NET loader
# ============================================================

def load_onet_file(filename: str) -> pd.DataFrame:
    """Load an O*NET CSV file from the external O*NET dataset."""

    path = ONET_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"O*NET file not found: {path}")

    return pd.read_csv(path)


def filter_occupation(df: pd.DataFrame, onet_code: str) -> pd.DataFrame:
    """Return records belonging to one O*NET occupation."""

    return df[df["O*NET-SOC Code"] == onet_code].copy()


# ============================================================
# Skill / knowledge extraction
# ============================================================

def extract_essential_skills(
    df: pd.DataFrame,
    onet_code: str,
) -> pd.DataFrame:
    """Extract essential skills for one O*NET occupation."""

    columns = [
        "O*NET-SOC Code",
        "Title",
        "Element ID",
        "Element Name",
        "Scale ID",
        "Scale Name",
        "Data Value",
        "Recommend Suppress",
        "Not Relevant",
        "Date",
        "Domain Source",
    ]

    return filter_occupation(df, onet_code)[columns].copy()


def extract_transferable_skills(
    df: pd.DataFrame,
    onet_code: str,
) -> pd.DataFrame:
    """Extract transferable skills for one O*NET occupation."""

    columns = [
        "O*NET-SOC Code",
        "Title",
        "Element ID",
        "Element Name",
        "Scale ID",
        "Scale Name",
        "Data Value",
        "Recommend Suppress",
        "Not Relevant",
        "Date",
        "Domain Source",
    ]

    return filter_occupation(df, onet_code)[columns].copy()


def extract_knowledge(
    df: pd.DataFrame,
    onet_code: str,
) -> pd.DataFrame:
    """Extract knowledge areas for one O*NET occupation."""

    columns = [
        "O*NET-SOC Code",
        "Title",
        "Element ID",
        "Element Name",
        "Scale ID",
        "Scale Name",
        "Data Value",
        "Recommend Suppress",
        "Not Relevant",
        "Date",
        "Domain Source",
    ]

    return filter_occupation(df, onet_code)[columns].copy()


def extract_abilities(
    df: pd.DataFrame,
    onet_code: str,
) -> pd.DataFrame:
    """Extract abilities for one O*NET occupation."""

    columns = [
        "O*NET-SOC Code",
        "Title",
        "Element ID",
        "Element Name",
        "Scale ID",
        "Scale Name",
        "Data Value",
        "Recommend Suppress",
        "Not Relevant",
        "Date",
        "Domain Source",
    ]

    return filter_occupation(df, onet_code)[columns].copy()


# ============================================================
# Work evidence
# ============================================================

def extract_tasks(
    df: pd.DataFrame,
    onet_code: str,
) -> pd.DataFrame:
    """Extract task statements for one O*NET occupation."""

    columns = [
        "O*NET-SOC Code",
        "Title",
        "Task ID",
        "Task",
        "Task Type",
        "Incumbents Responding",
        "Date",
        "Domain Source",
    ]

    return filter_occupation(df, onet_code)[columns].copy()


def extract_work_activities(
    df: pd.DataFrame,
    onet_code: str,
) -> pd.DataFrame:
    """Extract work activities for one O*NET occupation."""

    columns = [
        "O*NET-SOC Code",
        "Title",
        "Element ID",
        "Element Name",
        "Scale ID",
        "Scale Name",
        "Data Value",
        "Recommend Suppress",
        "Not Relevant",
        "Date",
        "Domain Source",
    ]

    return filter_occupation(df, onet_code)[columns].copy()


# ============================================================
# Technology evidence
# ============================================================

def extract_technologies(
    df: pd.DataFrame,
    onet_code: str,
) -> pd.DataFrame:
    """Extract software and technology evidence."""

    columns = [
        "O*NET-SOC Code",
        "Title",
        "Workplace Example",
        "Element ID",
        "Element Name",
        "Hot Technology",
        "In Demand",
    ]

    return filter_occupation(df, onet_code)[columns].copy()


# ============================================================
# Preparation evidence
# ============================================================

def extract_job_zone(
    df: pd.DataFrame,
    onet_code: str,
) -> pd.DataFrame:
    """Extract Job Zone information for one occupation."""

    columns = [
        "O*NET-SOC Code",
        "Title",
        "Job Zone",
        "Date",
        "Domain Source",
    ]

    return filter_occupation(df, onet_code)[columns].copy()


def extract_training_experience(
    df: pd.DataFrame,
    onet_code: str,
) -> pd.DataFrame:
    """Extract training and experience evidence."""

    columns = [
        "O*NET-SOC Code",
        "Title",
        "Element ID",
        "Element Name",
        "Scale ID",
        "Scale Name",
        "Data Value",
        "N",
        "Standard Error",
        "Lower CI Bound",
        "Upper CI Bound",
        "Recommend Suppress",
        "Date",
        "Domain Source",
    ]

    return filter_occupation(df, onet_code)[columns].copy()


# ============================================================
# GradPath metadata
# ============================================================

def add_gradpath_metadata(
    df: pd.DataFrame,
    role: str,
    mapping_type: str,
) -> pd.DataFrame:
    """Add GradPath role and mapping metadata."""

    result = df.copy()

    result.insert(0, "GradPath Role", role)
    result.insert(1, "Mapping Type", mapping_type)

    return result


# ============================================================
# Main extraction pipeline
# ============================================================

def main():

    # --------------------------------------------------------
    # Load O*NET datasets
    # --------------------------------------------------------

    datasets = {
        "essential_skills": load_onet_file("essential_skills.csv"),
        "transferable_skills": load_onet_file("transferable_skills.csv"),
        "knowledge": load_onet_file("knowledge.csv"),
        "abilities": load_onet_file("abilities.csv"),
        "tasks": load_onet_file("task_statements.csv"),
        "work_activities": load_onet_file("work_activities.csv"),
        "technologies": load_onet_file("software_skills.csv"),
        "job_zone": load_onet_file("job_zones.csv"),
        "training_experience": load_onet_file(
            "training_and_experience.csv"
        ),
    }

    print("O*NET files loaded successfully.")

    # --------------------------------------------------------
    # Containers
    # --------------------------------------------------------

    outputs = {
        "onet_essential_skills.csv": [],
        "onet_transferable_skills.csv": [],
        "onet_knowledge.csv": [],
        "onet_abilities.csv": [],
        "onet_tasks.csv": [],
        "onet_work_activities.csv": [],
        "onet_technologies.csv": [],
        "onet_job_zone.csv": [],
        "onet_training_experience.csv": [],
    }

    # --------------------------------------------------------
    # Extract each occupation
    # --------------------------------------------------------

    for role, mapping in OCCUPATIONS.items():

        code = mapping["onet_code"]
        mapping_type = mapping["mapping_type"]

        print(f"\n{'=' * 60}")
        print(f"GradPath Role: {role}")
        print(f"O*NET Occupation: {mapping['onet_title']}")
        print(f"O*NET Code: {code}")
        print(f"Mapping Type: {mapping_type}")
        print(f"{'=' * 60}")

        extracted = {
            "onet_essential_skills.csv": extract_essential_skills(
                datasets["essential_skills"], code
            ),
            "onet_transferable_skills.csv": extract_transferable_skills(
                datasets["transferable_skills"], code
            ),
            "onet_knowledge.csv": extract_knowledge(
                datasets["knowledge"], code
            ),
            "onet_abilities.csv": extract_abilities(
                datasets["abilities"], code
            ),
            "onet_tasks.csv": extract_tasks(
                datasets["tasks"], code
            ),
            "onet_work_activities.csv": extract_work_activities(
                datasets["work_activities"], code
            ),
            "onet_technologies.csv": extract_technologies(
                datasets["technologies"], code
            ),
            "onet_job_zone.csv": extract_job_zone(
                datasets["job_zone"], code
            ),
            "onet_training_experience.csv": extract_training_experience(
                datasets["training_experience"], code
            ),
        }

        for filename, dataframe in extracted.items():

            dataframe = add_gradpath_metadata(
                dataframe,
                role,
                mapping_type,
            )

            outputs[filename].append(dataframe)

            print(
                f"{filename}: {len(dataframe)} records"
            )

    # --------------------------------------------------------
    # Save processed outputs
    # --------------------------------------------------------

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("\nSaving processed O*NET datasets...")

    for filename, dataframes in outputs.items():

        combined = pd.concat(
            dataframes,
            ignore_index=True,
        )

        output_path = PROCESSED_DIR / filename

        combined.to_csv(
            output_path,
            index=False,
        )

        print(
            f"{filename}: {len(combined)} records"
        )

    print("\nO*NET extraction completed successfully.")


if __name__ == "__main__":
    main()