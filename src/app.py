import csv
import tempfile
from pathlib import Path

import streamlit as st

from gradpath.cv_profile import build_candidate_profile
from gradpath.skill_gap import analyze_skill_gaps
from gradpath.learning_recommendations import recommend_learning_actions
from gradpath.project_recommendations import recommend_projects

from gradpath.project_tracking import (
    assign_project,
    get_candidate_project_assignments,
    update_project_status,
    submit_project_skill_evidence,
)
from gradpath.auth import (
    authenticate_user,
    initialize_auth_database,
    register_user,
)

st.set_page_config(
    page_title="GradPath | Career Readiness",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Visual design ----------
st.markdown(
    """
    <style>
    :root {
        color-scheme: light;
    }

    .stApp {
        background: linear-gradient(
            135deg, #f7f5ff 0%, #f2f9ff 52%, #f2fbf7 100%
        );
        color: #26324b;
    }

    [data-testid="stHeader"] {
        background: rgba(255, 255, 255, 0.75);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #eee9ff 0%, #eaf6ff 100%);
        border-right: 1px solid #e2e5f2;
    }

    [data-testid="stSidebar"] * {
        color: #303858;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2.2rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 2rem 2.2rem;
        border-radius: 24px;
        background: linear-gradient(115deg, #e8e1ff, #e1f3ff 65%, #dcf7ed);
        border: 1px solid rgba(255, 255, 255, 0.9);
        margin-bottom: 1.5rem;
    }

    .eyebrow {
        color: #6956b8;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 0.75rem;
        font-weight: 800;
        margin-bottom: 0.6rem;
    }

    .hero h1 {
        color: #283252;
        font-size: clamp(2rem, 4vw, 3rem);
        line-height: 1.15;
        margin: 0 0 0.7rem 0;
        font-weight: 800;
    }

    .hero p {
        color: #52617d;
        font-size: 1.05rem;
        max-width: 690px;
        line-height: 1.7;
        margin-bottom: 0;
    }

    .section-heading {
        color: #293653;
        font-size: 1.35rem;
        font-weight: 750;
        margin: 1.1rem 0 0.3rem 0;
    }


    .brand-mark {
        font-size: 1.65rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        color: #40366f;
        padding-top: 0.35rem;
    }

    .brand-caption {
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        color: #77718f;
        margin: 0.25rem 0 1.5rem 0;
    }

    .sidebar-navigation {
        display: flex;
        flex-direction: column;
        gap: 0.45rem;
        margin-top: 0.8rem;
    }

    .nav-link {
        display: block;
        padding: 0.7rem 0.8rem;
        border: 1px solid #e7e2f2;
        border-radius: 0.7rem;
        background: rgba(255, 255, 255, 0.72);
        color: #40366f !important;
        text-decoration: none !important;
        font-weight: 600;
        transition: background 0.2s ease, border-color 0.2s ease;
    }

    .nav-link:hover {
        background: #eee9fb;
        border-color: #c8bce9;
    }


    .section-description {
        color: #6b7690;
        margin-bottom: 1rem;
        font-size: 0.94rem;
    }

    [data-testid="stMetric"] {
        background: #ffffff;
        padding: 1.1rem 1.2rem;
        border-radius: 16px;
        border: 1px solid #e7e9f4;
        box-shadow: 0 4px 16px rgba(58, 67, 110, 0.045);
    }

    [data-testid="stMetricLabel"] {
        color: #68748e;
    }

    [data-testid="stMetricValue"] {
        color: #34416a;
    }

    [data-testid="stFileUploader"] {
        background: #ffffff;
        border: 1.5px dashed #b9b0ed;
        border-radius: 18px;
        padding: 1rem;
    }

    .stButton > button {
        border-radius: 12px;
        font-weight: 650;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #e7e9f4;
        border-radius: 14px;
        overflow: hidden;
    }

    [data-testid="stExpander"] {
        background: #ffffff;
        border: 1px solid #e7e9f4;
        border-radius: 14px;
    }

    .status-note {
        background: #fff7e9;
        color: #795721;
        border: 1px solid #f6e1b8;
        border-radius: 12px;
        padding: 0.85rem 1rem;
        line-height: 1.55;
        margin: 0.7rem 0 1rem 0;
    }

    .footer {
        color: #818ba0;
        text-align: center;
        padding-top: 2.5rem;
        font-size: 0.82rem;
    }

    /* Cleaner dashboard typography and spacing */
    h2, h3, h4 {
        color: #293653;
        letter-spacing: -0.025em;
    }

    h3 {
        margin-top: 1.5rem;
        margin-bottom: 0.6rem;
    }

    p {
        line-height: 1.65;
    }

    hr {
        border-color: #e4e7f2;
        margin: 1.5rem 0;
    }

    /* More polished buttons */
    .stButton > button {
        min-height: 2.65rem;
        padding: 0.55rem 1.1rem;
        border: 1px solid #d9d3ef;
        background: #ffffff;
        color: #453b78;
        transition: all 0.18s ease;
    }

    .stButton > button:hover {
        border-color: #8e7bd0;
        background: #f0ecff;
        color: #34275f;
    }


    /* Authentication tabs: readable labels and clear selection */
    [data-testid="stTabs"] button[data-baseweb="tab"] {
        color: #40366f !important;
        background-color: #f0ecff !important;
        border-radius: 10px 10px 0 0;
    }

    [data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
        color: #ffffff !important;
        background-color: #6250a4 !important;
        border-bottom: 3px solid #6250a4 !important;
    }

    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        background-color: #f0ecff !important;
        border-bottom: 1px solid #d9d3ef;
        gap: 8px;
    }

    /* Form fields: white background with dark, readable text */
    [data-testid="stTextInput"] input {
        background-color: #ffffff !important;
        color: #26324b !important;
        border: 1px solid #c9c4dc !important;
    }

    [data-testid="stTextInput"] input::placeholder {
        color: #73718a !important;
        opacity: 1;
    }

    /* Keep authentication buttons readable */
    [data-testid="stFormSubmitButton"] button {
        background-color: #6250a4 !important;
        color: #ffffff !important;
        border: 1px solid #6250a4 !important;
        border-radius: 10px !important;
        font-weight: 650 !important;
    }

    [data-testid="stFormSubmitButton"] button:hover {
        background-color: #4f407f !important;
        color: #ffffff !important;
    }


    /* Consistent card-like surfaces */
    [data-testid="stMetric"],
    [data-testid="stExpander"],
    [data-testid="stFileUploader"] {
        box-shadow: 0 5px 18px rgba(53, 61, 100, 0.045);
    }

    /* More readable tables */
    [data-testid="stDataFrame"] {
        background: #ffffff;
        border: 1px solid #e3e6f1;
        border-radius: 14px;
    }

    /* Keep the content comfortable on smaller screens */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .hero {
            padding: 1.4rem;
            border-radius: 18px;
        }
    }


    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- Authentication ----------
initialize_auth_database()

if "user_id" not in st.session_state:
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.email = None

if not st.session_state.user_id:
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">Your next chapter starts here</div>
            <h1>Welcome to GradPath.</h1>
            <p>
                Sign in or create an account to build your career profile,
                explore learning recommendations, and track your projects.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    login_tab, register_tab = st.tabs(["Sign in", "Create account"])

    with login_tab:
        with st.form("login_form"):
            login_identifier = st.text_input(
                "Username or email",
                key="login_identifier",
            )
            login_password = st.text_input(
                "Password",
                type="password",
                key="login_password",
            )
            login_submitted = st.form_submit_button(
                "Sign in",
                use_container_width=True,
            )

        if login_submitted:
            user = authenticate_user(
                login_identifier,
                login_password,
            )

            if user:
                st.session_state.user_id = user["user_id"]
                st.session_state.username = user["username"]
                st.session_state.email = user["email"]
                st.rerun()
            else:
                st.error("Invalid username/email or password.")

    with register_tab:
        with st.form("register_form"):
            new_username = st.text_input(
                "Username",
                help="Use 3–32 letters, numbers, periods, underscores, or hyphens.",
            )
            new_email = st.text_input("Email address")
            new_password = st.text_input(
                "Password",
                type="password",
                help="Use at least 12 characters.",
            )
            confirm_password = st.text_input(
                "Confirm password",
                type="password",
            )
            register_submitted = st.form_submit_button(
                "Create account",
                use_container_width=True,
            )

        if register_submitted:
            if new_password != confirm_password:
                st.error("The passwords do not match.")
            else:
                try:
                    user = register_user(
                        username=new_username,
                        email=new_email,
                        password=new_password,
                    )
                    st.session_state.user_id = user["user_id"]
                    st.session_state.username = user["username"]
                    st.session_state.email = user["email"]
                    st.success("Account created successfully.")
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))

    st.markdown(
        '<div class="footer">GradPath · Your progress, your pathway</div>',
        unsafe_allow_html=True,
    )
    st.stop()

# Use the authenticated identity throughout this session.
candidate_id = st.session_state.user_id


# ---------- Navigation ----------
with st.sidebar:
    st.markdown(
        """
        <div class="brand-mark">🎯 GradPath</div>
        <div class="brand-caption">YOUR CAREER, WITH A CLEARER PATH</div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(f"Signed in as @{st.session_state.username}")

    if st.button("Log out", use_container_width=True):
        for key in (
            "user_id",
            "username",
            "email",
        ):
            st.session_state.pop(key, None)

        st.rerun()

    st.markdown("### Your workspace")

    target_role = st.selectbox(
        "Your target role",
        ["Data Analyst", "Data Scientist"],
        key="target_role",
    )

    st.markdown(
        """
        <div class="sidebar-navigation">
            <a class="nav-link" href="#cv-analysis">📄 CV Analysis</a>
            <a class="nav-link" href="#skill-development">🧩 Skill Development</a>
            <a class="nav-link" href="#learning-plan">📚 Learning Plan</a>
            <a class="nav-link" href="#project-workspace">🚀 Project Workspace</a>
            <a class="nav-link" href="#project-tracking">📌 Project Tracking</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption("Phase 10 · Career readiness workspace")


# ---------- Welcome ----------
st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Your next chapter starts here</div>
        <h1>Make your skills<br>work for your future.</h1>
        <p>
            Understand your current strengths, discover what to learn next,
            and build evidence of your abilities — one step at a time.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f'<div class="section-heading">Your {target_role} pathway</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-description">'
    'Start with your CV. GradPath will organise the information '
    'and help you understand your current profile.'
    '</div>',
    unsafe_allow_html=True,
)

# ---------- CV analysis ----------
st.markdown('<div id="cv-analysis"></div>', unsafe_allow_html=True)
st.markdown("### 📄 CV analysis")

uploaded_file = st.file_uploader(
    "Upload your CV to get started",
    type=["pdf", "docx"],
    help="PDF and DOCX files are supported.",
)

if uploaded_file is None:
    st.info(
        "✨ Your first step: upload a CV to create your structured profile."
    )
else:
    temporary_path = None

    try:
        suffix = Path(uploaded_file.name).suffix.lower()

        with tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False,
        ) as temporary_file:
            temporary_file.write(uploaded_file.getvalue())
            temporary_path = Path(temporary_file.name)

        with st.spinner("Reading your CV and organising your profile..."):
            profile = build_candidate_profile(
                temporary_path,
                candidate_id=candidate_id,
            )

        skills = profile.get("skills", [])
        education = profile.get("education", [])
        experience = profile.get("experience", [])
        projects = profile.get("projects", [])
        certifications = profile.get("certifications", [])
        warnings = profile.get("extraction_warnings", [])

        st.success("Your CV has been processed.")

        st.markdown("#### Your profile at a glance")

        metric_columns = st.columns(4)
        metrics = [
            ("Detected skills", len(skills)),
            ("Education entries", len(education)),
            ("Experience entries", len(experience)),
            ("Project entries", len(projects)),
        ]

        for column, (label, value) in zip(metric_columns, metrics):
            with column:
                st.metric(label, value)

        st.markdown("#### 🧩 Your detected skills")
        st.markdown(
            '<div class="section-description">'
            'These skills were mentioned in your CV. A mention alone '
            'does not establish proficiency.'
            '</div>',
            unsafe_allow_html=True,
        )

        if skills:
            skill_rows = [
                {
                    "Skill": skill.get("skill_name", "Unknown"),
                    "Category": skill.get("skill_category", "Uncategorised"),
                    "Role relevance": skill.get("role", "Not specified"),
                    "Evidence status": skill.get(
                        "verification_status", "unverified"
                    ).replace("_", " ").title(),
                }
                for skill in skills
            ]

            st.dataframe(
                skill_rows,
                use_container_width=True,
                hide_index=True,
                height=min(420, 38 * (len(skill_rows) + 1)),
            )
        else:
            st.info(
                "No recognised skills were detected. "
                "This does not necessarily mean you lack those skills."
            )


        # ---------- Skill-gap analysis ----------
        st.markdown('<div id="skill-development"></div>', unsafe_allow_html=True)
        st.markdown("#### 🎯 Your skill-gap analysis")
        st.caption(
            f"Comparing your CV evidence with the {target_role} "
            "skill requirements and available job-market evidence."
        )

        try:
            gap_results = analyze_skill_gaps(profile, target_role)

            if gap_results:
                gap_rows = [
                    {
                        "Skill": item["skill_name"],
                        "Candidate status": (
                            item["candidate_status"]
                            .replace("_", " ")
                            .title()
                        ),
                        "Market frequency (%)": round(
                            item["market_observed_frequency_pct"], 2
                        ),
                        "Priority score": item["priority_score"],
                        "ESCO relationship": item["esco_relationship"].title(),
                        "Explanation": item["explanation"],
                    }
                    for item in gap_results
                ]

                st.dataframe(
                    gap_rows,
                    use_container_width=True,
                    hide_index=True,
                )

                st.info(
                    "A potential gap means a skill was not detected in your "
                    "CV; it does not prove you lack that skill. CV mentions "
                    "remain unverified unless supported by appropriate evidence."
                )
            else:
                st.info(
                    "No skill-gap records were returned for this profile "
                    "and target role."
                )

        except Exception as exc:
            st.error("Skill-gap analysis could not be completed.")
            st.caption(f"Technical details: {type(exc).__name__}")


        # ---------- Learning recommendations ----------
        st.markdown('<div id="learning-plan"></div>', unsafe_allow_html=True)
        st.markdown("#### 📚 Your learning recommendations")
        st.caption(
            "Explore learning actions based on your skill-gap analysis "
            "and the available learning resources."
        )

        if "gap_results" not in locals():
            st.info(
                "Learning recommendations are unavailable because "
                "skill-gap analysis did not complete."
            )
        elif not gap_results:
            st.info(
                "No skill-gap records are available to generate "
                "learning recommendations for this role."
            )
        else:
            try:
                learning_results = recommend_learning_actions(
                    skill_gaps=gap_results,
                    target_role=target_role,
                )

                if learning_results:
                    learning_rows = []

                    for item in learning_results:
                        resource_url = item.get("resource_url")
                        resource_title = item.get("resource_title")

                        learning_rows.append(
                            {
                                "Skill": item["skill_name"],
                                "Recommended action": (
                                    item["recommended_action"]
                                    .replace("_", " ")
                                    .replace("-", " ")
                                    .title()
                                ),
                                "Priority score": item["priority_score"],
                                "Market rank": (
                                    item["market_priority_rank"]
                                    if item["market_priority_rank"] is not None
                                    else "Not ranked"
                                ),
                                "Learning resource": (
                                    resource_title
                                    if resource_title
                                    else "No suitable resource available"
                                ),
                                "Provider": (
                                    item.get("provider") or "Not specified"
                                ),
                                "Resource type": (
                                    item.get("resource_type") or "Not specified"
                                ),
                                "Difficulty": (
                                    item.get("difficulty") or "Not specified"
                                ),
                                "Access": (
                                    item.get("access_type") or "Not specified"
                                ),
                                "Explanation": item["explanation"],
                            }
                        )

                    st.dataframe(
                        learning_rows,
                        use_container_width=True,
                        hide_index=True,
                    )

                    linked_resources = [
                        item
                        for item in learning_results
                        if item.get("resource_url")
                    ]

                    if linked_resources:
                        st.markdown("##### Open learning resources")

                        for item in linked_resources:
                            st.markdown(
                                f"- [{item['skill_name']}: "
                                f"{item['resource_title']}]"
                                f"({item['resource_url']})"
                            )

                    st.caption(
                        "Priority scores are heuristic ordering signals, "
                        "not predictions of readiness or employment. "
                        "Recommendations identify useful next actions; "
                        "they do not prove that a skill is missing."
                    )
                else:
                    st.info(
                        "No learning actions were generated for the "
                        "current skill-gap results."
                    )

            except Exception as exc:
                st.error("Learning recommendations could not be generated.")
                st.caption(f"Technical details: {type(exc).__name__}")



        # ---------- Project recommendations ----------
        st.markdown(
            '<div id="project-workspace"></div>',
            unsafe_allow_html=True,
        )
        st.markdown("#### 🛠️ Your project recommendations")
        st.caption(
            "Explore practical projects that help you practise skills "
            "relevant to your selected role."
        )

        if "gap_results" not in locals():
            st.info(
                "Project recommendations are unavailable because "
                "skill-gap analysis did not complete."
            )
        elif not gap_results:
            st.info(
                "No skill-gap records are available to recommend projects."
            )
        else:
            try:
                project_results = recommend_projects(
                    skill_gaps=gap_results,
                    target_role=target_role,
                )

                if project_results:
                    project_rows = [
                        {
                            "Project": item["project_title"],
                            "Difficulty": item["difficulty"],
                            "Estimated hours": item["estimated_hours"],
                            "Skills practised": ", ".join(
                                item["covered_skills"]
                            ),
                            "Actionable gaps covered": (
                                f"{item['covered_gap_count']} of "
                                f"{item['total_actionable_gaps']}"
                            ),
                            "Coverage (%)": item["coverage_score"],
                        }
                        for item in project_results
                    ]

                    st.dataframe(
                        project_rows,
                        use_container_width=True,
                        hide_index=True,
                    )

                    st.markdown("##### Explore project details")

                    for item in project_results:
                        with st.expander(
                            f"{item['project_title']} — "
                            f"{item['estimated_hours']} hours "
                            f"· {item['difficulty']}"
                        ):
                            st.write(item["description"])

                            st.markdown("**Skills to practise**")
                            if item["covered_skills"]:
                                st.write(", ".join(item["covered_skills"]))
                            else:
                                st.caption("No covered skills listed.")

                            st.markdown("**Expected deliverables**")
                            st.write(item["deliverables"])

                            st.markdown("**Evidence criteria**")
                            st.write(item["evidence_criteria"])

                            prerequisites = item["prerequisites"]
                            st.markdown("**Prerequisites**")
                            if prerequisites:
                                st.write(", ".join(prerequisites))
                            else:
                                st.write("No prerequisites listed.")

                            st.markdown("**Why this project was recommended**")
                            st.write(item["explanation"])

                    st.caption(
                        "Project rankings are heuristic, not predictions "
                        "of employability or skill mastery. Skills covered "
                        "by a project are not automatically verified; "
                        "evidence must be assessed separately."
                    )
                else:
                    st.info(
                        "No suitable projects were found for the current "
                        "skill gaps and selected role."
                    )

            except Exception as exc:
                st.error("Project recommendations could not be generated.")
                st.caption(f"Technical details: {type(exc).__name__}")


        # ---------- Project tracking ----------
        st.markdown(
            '<div id="project-tracking"></div>',
            unsafe_allow_html=True,
        )
        st.markdown("#### 📌 Project tracking")
        st.caption(
            "Assign a recommended project, track your progress, and submit "
            "evidence of skills practised. Submitted evidence remains "
            "unverified until reviewed separately."
        )


        try:
            assignments = get_candidate_project_assignments(
                candidate_id=candidate_id,
                target_role=target_role,
            )

            st.markdown("##### Assign a recommended project")

            if "project_results" in locals() and project_results:
                project_options = {
                    f"{item['project_title']} "
                    f"({item['estimated_hours']} hours)": item["project_id"]
                    for item in project_results
                }

                selected_project_label = st.selectbox(
                    "Choose a recommended project",
                    options=list(project_options.keys()),
                    key="tracking_project_choice",
                )

                if st.button("Assign project", key="assign_project_button"):
                    try:
                        assignment_id = assign_project(
                            candidate_id=candidate_id,
                            project_id=project_options[
                                selected_project_label
                            ],
                            target_role=target_role,
                        )
                        st.success(
                            f"Project assigned successfully "
                            f"(assignment #{assignment_id})."
                        )
                        st.rerun()
                    except ValueError as exc:
                        st.warning(str(exc))
            else:
                st.info(
                    "Generate project recommendations before assigning "
                    "a project."
                )

            st.markdown("##### Your assigned projects")

            if not assignments:
                st.info(
                    "You have no assigned projects for this role yet."
                )
            else:
                for assignment in assignments:
                    assignment_id = int(assignment["assignment_id"])
                    current_status = assignment["status"]
                    project_title = assignment["project_title"]

                    with st.expander(
                        f"{project_title} — "
                        f"{current_status.replace('_', ' ').title()}"
                    ):
                        st.write(f"**Assignment ID:** {assignment_id}")
                        st.write(f"**Status:** {current_status.title()}")

                        status_options = {
                            "not_started": ["in_progress", "abandoned"],
                            "in_progress": ["completed", "abandoned"],
                            "completed": [],
                            "abandoned": [],
                        }
                        allowed_statuses = status_options.get(
                            current_status, []
                        )

                        if allowed_statuses:
                            new_status = st.selectbox(
                                "Update status",
                                options=allowed_statuses,
                                format_func=lambda value: value.replace(
                                    "_", " "
                                ).title(),
                                key=f"status_{assignment_id}",
                            )

                            if st.button(
                                "Save status",
                                key=f"save_status_{assignment_id}",
                            ):
                                try:
                                    update_project_status(
                                        assignment_id=assignment_id,
                                        new_status=new_status,
                                        candidate_id=candidate_id,
                                    )
                                    st.success("Project status updated.")
                                    st.rerun()
                                except ValueError as exc:
                                    st.warning(str(exc))

                        skill_ids = [
                            item.strip()
                            for item in str(
                                assignment.get("skill_ids") or ""
                            ).split(";")
                            if item.strip()
                        ]

                        if skill_ids:
                            st.markdown("**Submit skill evidence**")

                            vocabulary_path = (
                                Path(__file__).resolve().parents[1]
                                / "data"
                                / "processed"
                                / "initial_skill_vocabulary.csv"
                            )
                            with vocabulary_path.open(
                                "r", encoding="utf-8-sig", newline=""
                            ) as vocabulary_file:
                                skill_names = {
                                    row["skill_id"]: row["skill_name"]
                                    for row in csv.DictReader(vocabulary_file)
                                }

                            available_skill_ids = [
                                skill_id
                                for skill_id in skill_ids
                                if skill_id in skill_names
                            ]

                            if available_skill_ids:
                                selected_skill_id = st.selectbox(
                                    "Skill practised",
                                    options=available_skill_ids,
                                    format_func=lambda skill_id: (
                                        f"{skill_names[skill_id]} "
                                        f"({skill_id})"
                                    ),
                                    key=f"evidence_skill_{assignment_id}",
                                )

                                explanation = st.text_area(
                                    "Explain what you did and what evidence "
                                    "you can provide",
                                    placeholder=(
                                        "Describe your contribution, methods, "
                                        "and the relevant deliverable."
                                    ),
                                    key=f"evidence_text_{assignment_id}",
                                )

                                if st.button(
                                    "Submit skill evidence",
                                    key=f"submit_evidence_{assignment_id}",
                                ):
                                    try:
                                        result = submit_project_skill_evidence(
                                            assignment_id=assignment_id,
                                            candidate_id=candidate_id,
                                            skill_id=selected_skill_id,
                                            explanation=explanation,
                                        )
                                        st.success(
                                            "Evidence submitted and recorded "
                                            "as unverified."
                                        )
                                        st.caption(
                                            "Verification status: "
                                            f"{result.get('verification_status', 'unverified')}"
                                        )
                                    except ValueError as exc:
                                        st.warning(str(exc))
                            else:
                                st.warning(
                                    "No matching canonical skills were found "
                                    "for this project's evidence form."
                                )
                        else:
                            st.caption(
                                "No canonical skill IDs are listed for this "
                                "project."
                            )

        except Exception as exc:
            st.error("Project tracking could not be loaded.")
            st.caption(f"Technical details: {type(exc).__name__}")


        profile_tab, warnings_tab, technical_tab = st.tabs(
            ["Profile details", "Extraction notes", "Technical details"]
        )

        with profile_tab:
            detail_columns = st.columns(2)

            with detail_columns[0]:
                st.markdown("**Education**")
                if education:
                    for entry in education:
                        st.write(
                            "• " + str(
                                entry.get("details")
                                or entry.get("degree")
                                or "Education entry"
                            )
                        )
                else:
                    st.caption("No education entries extracted.")

                st.markdown("**Experience**")
                if experience:
                    for entry in experience:
                        st.write(
                            "• " + str(
                                entry.get("description")
                                or entry.get("job_title")
                                or "Experience entry"
                            )
                        )
                else:
                    st.caption("No experience entries extracted.")

            with detail_columns[1]:
                st.markdown("**Projects**")
                if projects:
                    for entry in projects:
                        st.write(
                            "• " + str(
                                entry.get("name")
                                or entry.get("description")
                                or "Project entry"
                            )
                        )
                else:
                    st.caption("No project entries extracted.")

                st.markdown("**Certifications**")
                if certifications:
                    for entry in certifications:
                        st.write(
                            "• " + str(entry.get("name") or "Certification")
                        )
                else:
                    st.caption("No certification entries extracted.")

        with warnings_tab:
            if warnings:
                for warning in warnings:
                    st.warning(warning)
            else:
                st.success("No extraction warnings were reported.")

            st.markdown(
                '<div class="status-note">'
                '<strong>Important:</strong> CV extraction can miss or '
                'misclassify information. Review your profile for accuracy. '
                'Detected skills remain unverified until supported by '
                'appropriate evidence.'
                '</div>',
                unsafe_allow_html=True,
            )

        with technical_tab:
            st.caption(
                "Structured output from the existing GradPath CV engine."
            )
            st.json(profile)

    except Exception:
        st.error(
            "GradPath could not process this CV. Check that the file is "
            "a valid PDF or DOCX and try again."
        )

    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

st.markdown(
    '<div class="footer">'
    'GradPath · Evidence-based career development · '
    'Your progress, your pathway'
    '</div>',
    unsafe_allow_html=True,
)
