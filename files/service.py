"""Service layer = the integration boundary.

Everything here is MOCK data for UI development. When integrating, keep these
function signatures and replace the bodies with calls into src/gradpath/
(auth, CV parser, gap analysis, recommenders, tracking, readiness).
Every candidate-specific function takes the authenticated user id (uid).
"""
from datetime import datetime

MOCK = True
ROLES = {"data_analyst": "Data Analyst", "data_scientist": "Data Scientist"}
# Presentation labels for backend status vocabulary: key -> (label, badge kind)
STATUS = {"mentioned_unverified": ("Mentioned – unverified", "info"), "verified": ("Verified", "ok"),
          "potential_gap": ("Potential gap", "warn"), "insufficient_evidence": ("Insufficient evidence", "muted"),
          "rejected_evidence": ("Evidence rejected", "err")}
PROGRESS = ["Not started", "In progress", "Completed"]
REQUIRED = {"data_analyst": [("SQL", "High"), ("Excel", "High"), ("Data Visualization", "High"),
                             ("Statistics", "Medium"), ("Python", "Medium")],
            "data_scientist": [("Python", "High"), ("SQL", "High"), ("Statistics", "High"),
                               ("Machine Learning", "High"), ("MLOps", "Medium"), ("Cloud", "Medium")]}
CATALOGUE = {"p1": dict(title="Sales Dashboard Analysis", level="Beginner", skills=["SQL", "Data Visualization", "Excel"],
                        desc="Clean a sales dataset and build an SQL-backed dashboard."),
             "p2": dict(title="Customer Churn Prediction", level="Intermediate", skills=["Python", "Statistics", "Machine Learning"],
                        desc="Build and evaluate a churn classifier."),
             "p3": dict(title="Deploy a Model API", level="Advanced", skills=["MLOps", "Cloud"],
                        desc="Serve a trained model behind a REST API.")}


class ServiceError(Exception):
    """Expected, user-presentable error."""


_USERS, _DATA = {}, {}


def _log(uid, text):
    _DATA[uid]["activity"].insert(0, (datetime.now().strftime("%d %b %Y, %H:%M"), text))


# ---- Authentication (replace with the existing auth module; never keep plaintext passwords) ----
def register(username, email, password, confirm):
    username, email = username.strip(), email.strip().lower()
    if not username or "@" not in email:
        raise ServiceError("Enter a username and a valid email address.")
    if len(password) < 12:
        raise ServiceError("Password must be at least 12 characters.")
    if password != confirm:
        raise ServiceError("Passwords do not match.")
    if any(username.lower() == r["name"].lower() or email == r["email"] for r in _USERS.values()):
        raise ServiceError("That username or email can't be used. Please try another.")
    uid = f"user_{len(_USERS) + 1}"
    _USERS[uid] = dict(id=uid, name=username, email=email, pw=password)
    _DATA[uid] = dict(role="data_scientist", cv=None, projects={}, progress={}, verified=set(), activity=[])
    return dict(id=uid, name=username, email=email)


def login(identifier, password):
    ident = identifier.strip().lower()
    r = next((r for r in _USERS.values() if ident in (r["name"].lower(), r["email"])), None)
    if not r or r["pw"] != password:
        raise ServiceError("Invalid username/email or password.")
    return dict(id=r["id"], name=r["name"], email=r["email"])


# ---- CV analysis ----
def get_role(uid): return _DATA[uid]["role"]
def set_role(uid, role): _DATA[uid]["role"] = role
def get_cv(uid): return _DATA[uid]["cv"]


def analyze_cv(uid, filename, size, data):
    if filename.lower().rsplit(".", 1)[-1] not in ("pdf", "docx"):
        raise ServiceError("Unsupported file type. Upload a PDF or DOCX.")
    if size > 5 * 1024 * 1024:
        raise ServiceError("The file is larger than 5 MB.")
    if not data:
        raise ServiceError("The file appears to be empty.")
    _DATA[uid]["cv"] = dict(file=filename, skills=["Python", "Pandas", "SQL"], sections={
        "Education": ["BSc Computer Science (sample)"], "Experience": [],
        "Projects": ["Sample project entry"], "Certifications": []})
    _log(uid, f"Analysed CV '{filename}'")
    return _DATA[uid]["cv"]


# ---- Gaps, learning, projects ----
def get_gaps(uid):
    d = _DATA[uid]; cv = d["cv"]; have = set(cv["skills"]) if cv else set(); rows = []
    for skill, prio in REQUIRED[d["role"]]:
        if skill in d["verified"]: s, why, act = "verified", "Accepted evidence on file.", "Keep practising."
        elif not cv: s, why, act = "insufficient_evidence", "No CV analysed yet.", "Upload a CV."
        elif skill in have: s, why, act = "mentioned_unverified", "Found in your CV but not backed by evidence.", "Complete a project to provide evidence."
        else: s, why, act = "potential_gap", "Not found in your CV. It may still be a skill you have.", "Follow the learning plan."
        rows.append(dict(skill=skill, status=s, priority=prio, why=why, action=act))
    return rows


def get_learning(uid):
    role = ROLES[_DATA[uid]["role"]]
    return [dict(id=f"L-{g['skill']}", skill=g["skill"], title=f"{g['skill']}: placeholder resource", type="Course",
                 provider="Not connected", url=None, reason=f"Targets a potential {role} gap.")
            for g in get_gaps(uid) if g["status"] == "potential_gap"]


def get_progress(uid, lid): return _DATA[uid]["progress"].get(lid, PROGRESS[0])


def set_progress(uid, lid, status):
    _DATA[uid]["progress"][lid] = status
    _log(uid, f"Learning progress: {lid} → {status}")


def get_projects(uid):
    d = _DATA[uid]; req = {s for s, _ in REQUIRED[d["role"]]}
    gaps = {g["skill"] for g in get_gaps(uid) if g["status"] == "potential_gap"}
    out = []
    for pid, p in CATALOGUE.items():
        if req & set(p["skills"]):
            hit = sorted(gaps & set(p["skills"]))
            out.append({**p, "id": pid, "assigned": pid in d["projects"],
                        "reason": f"Targets gap: {', '.join(hit)}." if hit else "Develops skills relevant to your target role."})
    return out


def get_workspace(uid):
    return [{**CATALOGUE[pid], "id": pid, **rec} for pid, rec in _DATA[uid]["projects"].items()]


def assign_project(uid, pid):
    if pid in _DATA[uid]["projects"]:
        raise ServiceError("This project is already in your workspace.")
    _DATA[uid]["projects"][pid] = dict(status=PROGRESS[0], evidence=None)
    _log(uid, f"Assigned project '{CATALOGUE[pid]['title']}'")


def _owned(uid, pid):
    if pid not in _DATA[uid]["projects"]:
        raise ServiceError("Project not found in your workspace.")
    return _DATA[uid]["projects"][pid]


def set_project_status(uid, pid, status):
    _owned(uid, pid)["status"] = status
    _log(uid, f"Project '{CATALOGUE[pid]['title']}' → {status}")


def submit_evidence(uid, pid, url, note):
    rec = _owned(uid, pid)
    if not url.startswith(("http://", "https://")):
        raise ServiceError("Enter a valid link starting with http:// or https://.")
    if not note.strip():
        raise ServiceError("Describe what the evidence shows.")
    rec["evidence"] = dict(url=url, note=note.strip(), status="Submitted – pending review")
    _log(uid, f"Submitted evidence for '{CATALOGUE[pid]['title']}'")


# ---- Overview / readiness ----
def summary(uid):
    d = _DATA[uid]; g = get_gaps(uid)
    return dict(role=ROLES[d["role"]], has_cv=bool(d["cv"]), detected=len(d["cv"]["skills"]) if d["cv"] else 0,
                gaps=sum(x["status"] == "potential_gap" for x in g),
                active=sum(p["status"] == "In progress" for p in d["projects"].values()), activity=d["activity"][:5])


def next_action(uid):
    d = _DATA[uid]
    if not d["cv"]: return "Upload your CV", "Start by analysing your CV so GradPath can detect your skills.", "CV Analysis"
    if not d["projects"]: return "Pick a project", "Assign a recommended project to start building evidence.", "Projects"
    if any(p["status"] == "In progress" for p in d["projects"].values()):
        return "Continue your project", "Update your status or submit evidence for work in progress.", "Projects"
    return "Review your readiness", "See what your evidence currently supports.", "Readiness Report"


def readiness(uid):
    d = _DATA[uid]
    if not d["cv"]: return None
    total = len(REQUIRED[d["role"]]); ver = len(d["verified"])
    return dict(score=round(100 * ver / total) if ver else None, verified=ver, total=total,
                mentioned=sum(g["status"] == "mentioned_unverified" for g in get_gaps(uid)))
