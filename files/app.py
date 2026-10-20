"""GradPath UI. Run:  streamlit run app.py"""
import streamlit as st
import service as S
from theme import badge, card, empty, inject, metric

st.set_page_config(page_title="GradPath", page_icon="🎓", layout="wide")
inject()
ss = st.session_state
ss.setdefault("user", None)
ss.setdefault("page", "Overview")
NAV = ["Overview", "CV Analysis", "Skill Gaps", "Learning Plan", "Projects", "Progress", "Readiness Report", "Profile and Settings"]


def go(page): ss.page = page


def logout():
    ss.user = None
    ss.page = "Overview"


def auth():
    _, c, _ = st.columns([1, 2, 1])
    with c:
        st.title("GradPath")
        st.subheader("Build your skills. Prove your progress. Prepare for your next role.")
        st.write("GradPath helps you understand your career skill gaps, discover learning resources, "
                 "build practical projects, and track your progress toward your target role.")
        t_in, t_up = st.tabs(["Sign in", "Create account"])
        with t_in, st.form("signin"):
            ident = st.text_input("Username or email")
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("Sign in", type="primary"):
                try:
                    ss.user = S.login(ident, pw); st.rerun()
                except S.ServiceError as e:
                    st.error(str(e))
        with t_up, st.form("signup"):
            name = st.text_input("Username")
            email = st.text_input("Email address")
            pw = st.text_input("Password (at least 12 characters)", type="password")
            pw2 = st.text_input("Confirm password", type="password")
            if st.form_submit_button("Create account", type="primary"):
                try:
                    ss.user = S.register(name, email, pw, pw2); st.rerun()
                except S.ServiceError as e:
                    st.error(str(e))


def overview(uid, u):
    s = S.summary(uid)
    st.title(f"Welcome, {u['name']}")
    st.caption("Here is where you are and what to do next.")
    cols = st.columns(4)
    with cols[0]: metric("Target role", s["role"])
    with cols[1]: metric("Skills detected", s["detected"] if s["has_cv"] else "—", "From your latest CV")
    with cols[2]: metric("Potential gaps", s["gaps"] if s["has_cv"] else "—", "Based on your target role")
    with cols[3]: metric("Projects in progress", s["active"])
    title, text, page = S.next_action(uid)
    st.subheader("Next recommended action")
    card(title, text)
    st.button(f"Go to {page}", type="primary", on_click=go, args=(page,))
    st.subheader("Recent activity")
    if not s["activity"]:
        empty("No activity yet", "Your CV analyses, project updates and progress will appear here.")
    for when, what in s["activity"]:
        st.caption(f"{when} — {what}")


def cv_page(uid, u):
    st.title("CV Analysis")
    st.caption("Supported formats: PDF and DOCX, up to 5 MB.")
    f = st.file_uploader("Upload your CV", type=["pdf", "docx"])
    if f and st.button("Analyse CV", type="primary"):
        with st.spinner("Analysing your CV…"):
            try:
                S.analyze_cv(uid, f.name, f.size, f.getvalue()); st.success("Analysis complete.")
            except S.ServiceError as e:
                st.error(str(e))
    cv = S.get_cv(uid)
    if not cv:
        return empty("No CV analysed yet", "Upload a PDF or DOCX above to see your detected skills.")
    st.subheader("Detected skills")
    st.caption("Skills mentioned in a CV are not verified until you provide accepted evidence.")
    st.markdown(" ".join(badge(f"{k} · {S.STATUS['mentioned_unverified'][0]}", "info") for k in cv["skills"]), unsafe_allow_html=True)
    st.subheader("Extracted profile")
    for sec, items in cv["sections"].items():
        with st.expander(sec):
            for i in items: st.write("• " + i)
            if not items: st.caption("Nothing was extracted for this section.")


def gaps_page(uid, u):
    st.title("Skill Gaps")
    role = st.selectbox("Target role", list(S.ROLES), index=list(S.ROLES).index(S.get_role(uid)), format_func=S.ROLES.get)
    S.set_role(uid, role)
    g = S.get_gaps(uid)
    c = st.columns(3)
    with c[0]: metric("Skills considered", len(g))
    with c[1]: metric("Potential gaps", sum(x["status"] == "potential_gap" for x in g))
    with c[2]: metric("Need verification", sum(x["status"] == "mentioned_unverified" for x in g))
    st.dataframe([{"Skill": x["skill"], "Evidence status": S.STATUS[x["status"]][0], "Market priority": x["priority"],
                   "Explanation": x["why"], "Suggested action": x["action"]} for x in g], hide_index=True, use_container_width=True)
    st.info("Results depend on your CV's extracted content, the skill vocabulary and market data. "
            "A missing mention does not prove you lack a skill.")


def learning_page(uid, u):
    st.title("Learning Plan")
    recs = S.get_learning(uid)
    if not recs:
        return empty("No recommendations yet", "Analyse your CV and choose a target role to get recommendations.")
    for r in recs:
        with st.container(border=True):
            st.markdown(f"**{r['title']}**")
            st.caption(f"{r['skill']} · {r['type']} · {r['provider']}")
            st.write(r["reason"])
            if r["url"]: st.link_button("Open resource", r["url"])
            else: st.caption("No link available yet.")


def progress_page(uid, u):
    st.title("Progress")
    recs = S.get_learning(uid)
    if not recs:
        empty("No learning activities", "Activities appear here once you have recommendations.")
    for r in recs:
        cur = S.get_progress(uid, r["id"])
        new = st.selectbox(r["title"], S.PROGRESS, index=S.PROGRESS.index(cur), key=f"lp_{r['id']}")
        if new != cur: S.set_progress(uid, r["id"], new)
    st.subheader("Assessments")
    empty("No assessment history", "Results will appear here once the assessment workflow is connected.")


def projects_page(uid, u):
    st.title("Projects")
    t1, t2 = st.tabs(["Recommended", "My workspace"])
    with t1:
        for p in S.get_projects(uid):
            with st.container(border=True):
                st.markdown(f"**{p['title']}** · {p['level']}")
                st.write(p["desc"]); st.caption(f"Skills: {', '.join(p['skills'])}"); st.caption(p["reason"])
                if p["assigned"]: st.markdown(badge("In your workspace", "ok"), unsafe_allow_html=True)
                elif st.button("Assign to my workspace", key=f"a_{p['id']}"):
                    try: S.assign_project(uid, p["id"]); st.rerun()
                    except S.ServiceError as e: st.error(str(e))
    with t2:
        ws = S.get_workspace(uid)
        if not ws: empty("No projects assigned", "Assign a recommended project to start tracking it.")
        for p in ws:
            with st.expander(f"{p['title']} — {p['status']}"):
                st.write(p["desc"]); st.caption(f"Skills: {', '.join(p['skills'])}")
                new = st.selectbox("Status", S.PROGRESS, index=S.PROGRESS.index(p["status"]), key=f"s_{p['id']}")
                if st.button("Update status", key=f"u_{p['id']}"):
                    try: S.set_project_status(uid, p["id"], new); st.success("Status updated."); st.rerun()
                    except S.ServiceError as e: st.error(str(e))
                st.markdown("**Skill evidence**")
                if p["evidence"]:
                    st.markdown(badge(p["evidence"]["status"], "warn"), unsafe_allow_html=True)
                    st.caption("Submitted evidence is not verified until it is accepted.")
                url = st.text_input("Link to your work (e.g. GitHub)", key=f"e_{p['id']}")
                note = st.text_area("What does this evidence show?", key=f"n_{p['id']}")
                if st.button("Submit evidence", key=f"x_{p['id']}"):
                    try: S.submit_evidence(uid, p["id"], url, note); st.success("Evidence submitted for review."); st.rerun()
                    except S.ServiceError as e: st.error(str(e))


def readiness_page(uid, u):
    st.title("Readiness Report")
    r = S.readiness(uid)
    if not r: return empty("No readiness result yet", "Analyse your CV first.")
    c = st.columns(3)
    with c[0]: metric("Readiness score", f"{r['score']}%" if r["score"] is not None else "Not enough evidence")
    with c[1]: metric("Verified skills", f"{r['verified']} of {r['total']}")
    with c[2]: metric("Mentioned, unverified", r["mentioned"])
    st.subheader("What contributed")
    st.write("Only verified evidence counts toward the score. CV mentions, learning progress and submitted "
             "(not yet accepted) evidence are shown separately and do not raise it.")
    st.subheader("Limitations")
    st.info("This is an evidence summary, not a guarantee of employability.")


def profile_page(uid, u):
    st.title("Profile and Settings")
    st.write(f"**Username:** {u['name']}"); st.write(f"**Email:** {u['email']}")
    st.write(f"**Target role:** {S.ROLES[S.get_role(uid)]}")
    st.button("Log out", type="primary", on_click=logout)


PAGES = {"Overview": overview, "CV Analysis": cv_page, "Skill Gaps": gaps_page, "Learning Plan": learning_page,
         "Projects": projects_page, "Progress": progress_page, "Readiness Report": readiness_page,
         "Profile and Settings": profile_page}

if not ss.user:
    auth()
else:
    with st.sidebar:
        st.markdown("### 🎓 GradPath")
        st.radio("Navigation", NAV, key="page", label_visibility="collapsed")
        if S.MOCK: st.caption("Demo data: not connected to the GradPath backend.")
        st.button("Log out", on_click=logout)
    PAGES[ss.page](ss.user["id"], ss.user)
