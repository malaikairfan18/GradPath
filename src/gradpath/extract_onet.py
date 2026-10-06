import pandas as pd
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]

ONET_DIR = PROJECT_ROOT / "data" / "external" / "onet" / "db_31_0_csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# GradPath target occupation mappings
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



def load_onet_file(filename: str) -> pd.DataFrame:
    """Load an O*NET CSV file from the raw data directory."""
    path = ONET_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"O*NET file not found: {path}")

    return pd.read_csv(path)

def filter_occupation(df: pd.DataFrame, onet_code: str) -> pd.DataFrame:
    """Return records belonging to one O*NET occupation."""
    return df[df["O*NET-SOC Code"] == onet_code].copy()

def extract_essential_skills(df: pd.DataFrame, onet_code: str) -> pd.DataFrame:
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

    filtered = filter_occupation(df, onet_code)

    return filtered[columns].copy()


def extract_knowledge(df: pd.DataFrame, onet_code: str) -> pd.DataFrame:
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

    filtered = filter_occupation(df, onet_code)

    return filtered[columns].copy()

def extract_technologies(df: pd.DataFrame, onet_code: str) -> pd.DataFrame:
    """Extract software and technology information for one O*NET occupation."""
    columns = [
        "O*NET-SOC Code",
        "Title",
        "Workplace Example",
        "Element ID",
        "Element Name",
        "Hot Technology",
        "In Demand",
    ]

    filtered = filter_occupation(df, onet_code)

    return filtered[columns].copy()

def add_gradpath_role(df: pd.DataFrame, role: str) -> pd.DataFrame:
    """Add the GradPath target role to extracted records."""
    result = df.copy()
    result.insert(0, "GradPath Role", role)
    return result



def main():
    # Load raw O*NET datasets
    essential_skills = load_onet_file("essential_skills.csv")
    knowledge = load_onet_file("knowledge.csv")
    software_skills = load_onet_file("software_skills.csv")

    print("O*NET files loaded successfully.")

    # Containers for processed records
    all_essential_skills = []
    all_knowledge = []
    all_technologies = []

    # Extract data for each GradPath occupation
    for role, mapping in OCCUPATIONS.items():
        code = mapping["onet_code"]

        print(f"\n{role}")
        print(f"O*NET occupation: {mapping['onet_title']}")
        print(f"O*NET code: {code}")

        skills = extract_essential_skills(essential_skills, code)
        knowledge_data = extract_knowledge(knowledge, code)
        technologies = extract_technologies(software_skills, code)

        skills = add_gradpath_role(skills, role)
        knowledge_data = add_gradpath_role(knowledge_data, role)
        technologies = add_gradpath_role(technologies, role)

        all_essential_skills.append(skills)
        all_knowledge.append(knowledge_data)
        all_technologies.append(technologies)

        print(f"Essential skill records: {len(skills)}")
        print(f"Knowledge records: {len(knowledge_data)}")
        print(f"Technology records: {len(technologies)}")

    # Combine both occupations
    essential_output = pd.concat(
        all_essential_skills,
        ignore_index=True,
    )

    knowledge_output = pd.concat(
        all_knowledge,
        ignore_index=True,
    )

    technology_output = pd.concat(
        all_technologies,
        ignore_index=True,
    )

    # Make sure the processed-data directory exists
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Save processed datasets
    essential_output.to_csv(
        PROCESSED_DIR / "onet_essential_skills.csv",
        index=False,
    )

    knowledge_output.to_csv(
        PROCESSED_DIR / "onet_knowledge.csv",
        index=False,
    )

    technology_output.to_csv(
        PROCESSED_DIR / "onet_technologies.csv",
        index=False,
    )

    print("\nProcessed O*NET data saved successfully.")
    print(f"Essential skills: {len(essential_output)}")
    print(f"Knowledge: {len(knowledge_output)}")
    print(f"Technologies: {len(technology_output)}")
    
if __name__ == "__main__":
    main()