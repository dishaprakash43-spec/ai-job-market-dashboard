import streamlit as st
import pandas as pd
import plotly.express as px
from docx import Document
import PyPDF2
import json
import os

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Job Market Dashboard",
    layout="wide"
)

# =========================================================
# PROFESSIONAL REACT STYLE UI
# =========================================================

st.markdown("""
<style>

/* Main App */
.stApp {
    background: linear-gradient(180deg, #0f172a 0%, #020617 100%);
    color: white;
    font-family: 'Inter', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* Headings */
h1,h2,h3,h4,h5,h6 {
    color: white;
    font-weight: 700;
}

/* Text */
p,label {
    color: #d1d5db;
}

/* Buttons */
div.stButton > button {
    background: linear-gradient(90deg,#2563eb,#06b6d4);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px;
    font-weight: bold;
    width: 100%;
}

div.stButton > button:hover {
    transform: scale(1.02);
    box-shadow: 0px 0px 15px rgba(37,99,235,0.4);
}

/* Metric Cards */
.metric-card {
    background: linear-gradient(145deg,#111827,#1e293b);
    padding: 25px;
    border-radius: 20px;
    text-align: center;
    box-shadow: 0px 6px 20px rgba(0,0,0,0.35);
    border: 1px solid rgba(255,255,255,0.05);
}

.metric-title {
    color: #94a3b8;
    font-size: 16px;
}

.metric-value {
    color: white;
    font-size: 34px;
    font-weight: bold;
}

/* Upload Box */
.upload-box {
    background: linear-gradient(145deg,#111827,#1e293b);
    padding: 25px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.05);
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
}

/* Inputs */
input, textarea {
    border-radius: 10px !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-thumb {
    background: #2563eb;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    df = pd.read_csv("job_market_india.csv")

    salary_col = None

    possible_salary_cols = [
        "Monthly Salary",
        "Salary",
        "salary",
        "monthly_salary"
    ]

    for col in possible_salary_cols:
        if col in df.columns:
            salary_col = col
            break

    if salary_col:

        df[salary_col] = (
            df[salary_col]
            .astype(str)
            .str.replace(",", "")
            .str.replace("₹", "")
        )

        df[salary_col] = pd.to_numeric(
            df[salary_col],
            errors="coerce"
        )

        df[salary_col] = df[salary_col].fillna(0)

    return df, salary_col


df, salary_col = load_data()

# =========================================================
# LOGIN SYSTEM
# =========================================================

USERS_FILE = "users.json"

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

with open(USERS_FILE, "r") as f:
    users = json.load(f)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# =========================================================
# LOGIN PAGE
# =========================================================

if not st.session_state.logged_in:

    st.markdown("""
    <div style="
    background: linear-gradient(90deg,#2563eb,#06b6d4);
    padding:30px;
    border-radius:24px;
    margin-top:40px;
    box-shadow:0px 8px 25px rgba(37,99,235,0.25);
    ">
    <h1 style="
    color:white;
    text-align:center;
    font-size:60px;
    font-weight:bold;
    ">
    📊 AI Job Market Dashboard
    </h1>

    <p style="
    text-align:center;
    color:white;
    font-size:20px;
    ">
    Real-Time AI Powered Analytics Platform
    </p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    tab1, tab2 = st.tabs(["🔐 Login", "🆕 Sign Up"])

    # LOGIN
    with tab1:

        st.subheader("Login")

        login_user = st.text_input(
            "Username",
            key="login_user"
        )

        login_pass = st.text_input(
            "Password",
            type="password",
            key="login_pass"
        )

        if st.button("Login"):

            if (
                login_user in users and
                users[login_user] == login_pass
            ):

                st.session_state.logged_in = True
                st.session_state.username = login_user

                st.success("Login Successful")

                st.rerun()

            else:
                st.error("Invalid Username or Password")

    # SIGNUP
    with tab2:

        st.subheader("Create Account")

        new_user = st.text_input(
            "Create Username",
            key="new_user"
        )

        new_pass = st.text_input(
            "Create Password",
            type="password",
            key="new_pass"
        )

        confirm_pass = st.text_input(
            "Confirm Password",
            type="password",
            key="confirm_pass"
        )

        if st.button("Create Account"):

            if new_user in users:
                st.warning("Username already exists")

            elif new_pass != confirm_pass:
                st.warning("Passwords do not match")

            else:

                users[new_user] = new_pass

                with open(USERS_FILE, "w") as f:
                    json.dump(users, f)

                st.success("Account Created Successfully")

    st.stop()

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.image(
    "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
    width=120
)

st.sidebar.success(
    f"Welcome {st.session_state.username}"
)

st.sidebar.title("📌 Navigation")

page = st.sidebar.radio(
    "Select Page",
    [
        "Dashboard",
        "Salary Analysis",
        "State Analysis",
        "Resume Match",
        "Skill Gap Analysis",
        "AI Career Advisor",
        "Role Comparison",
        "About"
    ]
)

# =========================================================
# FILTERS
# =========================================================

state_col = "State"
role_col = "Job Title"

states = sorted(df[state_col].dropna().unique())

selected_states = st.sidebar.multiselect(
    "📍 Select States",
    states
)

roles = sorted(df[role_col].dropna().unique())

selected_roles = st.sidebar.multiselect(
    "💼 Select Job Roles",
    roles
)

salary_min = 0
salary_max = int(df[salary_col].max())

salary_range = st.sidebar.slider(
    "💰 Salary Range",
    salary_min,
    salary_max,
    (salary_min, salary_max)
)

# =========================================================
# FILTER DATA
# =========================================================

filtered_df = df.copy()

if selected_states:
    filtered_df = filtered_df[
        filtered_df[state_col].isin(selected_states)
    ]

if selected_roles:
    filtered_df = filtered_df[
        filtered_df[role_col].isin(selected_roles)
    ]

filtered_df = filtered_df[
    (filtered_df[salary_col] >= salary_range[0]) &
    (filtered_df[salary_col] <= salary_range[1])
]

if filtered_df.empty:
    filtered_df = df.head(20)

# =========================================================
# METRIC CARD
# =========================================================

def metric_card(title, value):

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# SKILLS FUNCTION
# =========================================================

def get_skills(role):

    role = str(role).lower()

    if "data analyst" in role:
        return ["Excel", "SQL", "Power BI", "Statistics"]

    elif "data scientist" in role:
        return ["Python", "Machine Learning", "Deep Learning"]

    elif "frontend" in role:
        return ["HTML", "CSS", "JavaScript", "React"]

    elif "backend" in role:
        return ["Python", "Django", "SQL", "APIs"]

    elif "cloud" in role:
        return ["AWS", "Azure", "Linux"]

    else:
        return ["Communication", "Teamwork", "Technical Skills"]

# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    st.markdown("""
    <div style="
    background: linear-gradient(90deg,#2563eb,#06b6d4);
    padding:30px;
    border-radius:24px;
    margin-bottom:25px;
    box-shadow:0px 8px 25px rgba(37,99,235,0.25);
    ">
    <h1 style="
    color:white;
    text-align:center;
    font-size:55px;
    font-weight:bold;
    ">
    📊 AI Job Market Dashboard
    </h1>

    <p style="
    text-align:center;
    color:white;
    font-size:20px;
    ">
    Real-Time AI Powered Analytics Platform
    </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card("Total Jobs", len(filtered_df))

    with col2:
        metric_card(
            "Average Salary",
            f"₹ {int(filtered_df[salary_col].mean())}"
        )

    with col3:
        metric_card(
            "States",
            filtered_df[state_col].nunique()
        )

    with col4:
        metric_card(
            "Top Role",
            filtered_df[role_col].mode()[0]
        )

    st.write("")

    role_counts = (
        filtered_df[role_col]
        .value_counts()
        .head(10)
        .reset_index()
    )

    role_counts.columns = ["Role", "Count"]

    fig = px.bar(
        role_counts,
        x="Count",
        y="Role",
        orientation="h",
        color="Count"
    )

    fig.update_layout(
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        font_color="white"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================================================
# SALARY ANALYSIS
# =========================================================

elif page == "Salary Analysis":

    st.title("💰 Salary Analysis")

    col1, col2, col3 = st.columns(3)

    with col1:
        metric_card(
            "Highest Salary",
            f"₹ {int(filtered_df[salary_col].max())}"
        )

    with col2:
        metric_card(
            "Average Salary",
            f"₹ {int(filtered_df[salary_col].mean())}"
        )

    with col3:
        metric_card(
            "Lowest Salary",
            f"₹ {int(filtered_df[salary_col].min())}"
        )

    salary_data = (
        filtered_df
        .groupby(role_col)[salary_col]
        .mean()
        .reset_index()
        .sort_values(by=salary_col, ascending=False)
        .head(10)
    )

    fig = px.pie(
        salary_data,
        names=role_col,
        values=salary_col,
        hole=0.5
    )

    fig.update_layout(
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        font_color="white"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================================================
# STATE ANALYSIS
# =========================================================

elif page == "State Analysis":

    st.title("📍 State Analysis")

    state_jobs = (
        filtered_df[state_col]
        .value_counts()
        .reset_index()
    )

    state_jobs.columns = ["State", "Jobs"]

    fig = px.bar(
        state_jobs,
        x="State",
        y="Jobs",
        color="Jobs"
    )

    fig.update_layout(
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        font_color="white"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================================================
# RESUME MATCH
# =========================================================

elif page == "Resume Match":

    st.markdown("""
    <div class="upload-box">
    <h1 style="color:white;">
    📄 AI Resume Analyzer
    </h1>

    Upload Resume • Detect Skills • Get AI Insights
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload Resume",
        type=["pdf", "docx"]
    )

    if uploaded_file:

        text = ""

        if uploaded_file.name.endswith(".pdf"):

            pdf_reader = PyPDF2.PdfReader(uploaded_file)

            for page in pdf_reader.pages:

                extracted = page.extract_text()

                if extracted:
                    text += extracted

        elif uploaded_file.name.endswith(".docx"):

            doc = Document(uploaded_file)

            for para in doc.paragraphs:
                text += para.text

        text = text.lower()

        all_skills = [
            "python",
            "sql",
            "excel",
            "machine learning",
            "react",
            "aws",
            "java",
            "html",
            "css"
        ]

        found_skills = []

        for skill in all_skills:

            if skill in text:
                found_skills.append(skill.title())

        recommended_role = "Software Engineer"

        if "python" in text and "sql" in text:
            recommended_role = "Data Analyst"

        if "machine learning" in text:
            recommended_role = "Data Scientist"

        if "react" in text:
            recommended_role = "Frontend Developer"

        match_score = min(len(found_skills) * 12, 100)

        col1, col2 = st.columns(2)

        with col1:
            metric_card(
                "Recommended Role",
                recommended_role
            )

        with col2:
            metric_card(
                "Match Score",
                f"{match_score}%"
            )

        st.subheader("🛠 Skills Detected")

        if found_skills:

            skills_html = ""

            for skill in found_skills:

                skills_html += f"""
                <span style="
                    background-color:#2563eb;
                    padding:8px 15px;
                    border-radius:20px;
                    margin:5px;
                    display:inline-block;
                    color:white;
                ">
                    {skill}
                </span>
                """

            st.markdown(
                skills_html,
                unsafe_allow_html=True
            )

# =========================================================
# SKILL GAP ANALYSIS
# =========================================================

elif page == "Skill Gap Analysis":

    st.title("📚 Skill Gap Analysis")

    target_role = st.selectbox(
        "Select Target Role",
        roles
    )

    skills = get_skills(target_role)

    for skill in skills:
        st.success(skill)

# =========================================================
# AI CAREER ADVISOR
# =========================================================

# =========================================================
# AI CAREER ADVISOR
# =========================================================

elif page == "AI Career Advisor":

    st.title("🤖 AI Career Advisor")

    st.markdown("""
    <div class="card">
        <h3>Enter Your Skills</h3>
        <p>
        Get AI-powered career recommendations based on your skills
        </p>
    </div>
    """, unsafe_allow_html=True)

    user_skills = st.text_area(
        "Enter Skills (comma separated)",
        placeholder="Example: Python, SQL, Machine Learning, React"
    )

    # =====================================================
    # JOB ROLE DATABASE
    # =====================================================

    job_roles = {

        "Data Scientist": [
            "python",
            "machine learning",
            "data science",
            "tensorflow",
            "deep learning",
            "pandas",
            "numpy",
            "sql"
        ],

        "Frontend Developer": [
            "react",
            "javascript",
            "html",
            "css",
            "typescript"
        ],

        "Backend Developer": [
            "python",
            "django",
            "flask",
            "node.js",
            "api",
            "sql"
        ],

        "Cloud Engineer": [
            "aws",
            "docker",
            "kubernetes",
            "devops",
            "linux"
        ],

        "Cyber Security Analyst": [
            "cyber security",
            "networking",
            "linux"
        ],

        "Data Analyst": [
            "sql",
            "excel",
            "power bi",
            "tableau",
            "statistics"
        ],

        "AI Engineer": [
            "artificial intelligence",
            "nlp",
            "deep learning",
            "llm",
            "computer vision"
        ],

        "Mobile App Developer": [
            "flutter",
            "android",
            "java"
        ]
    }

    # =====================================================
    # BUTTON
    # =====================================================

    if st.button("🚀 Get Career Recommendations"):

        entered_skills = [
            skill.strip().lower()
            for skill in user_skills.split(",")
        ]

        recommended_roles = []

        # =================================================
        # MATCH SKILLS
        # =================================================

        for role, role_skills in job_roles.items():

            match_count = 0

            for skill in entered_skills:

                if skill in role_skills:
                    match_count += 1

            if match_count > 0:

                recommended_roles.append(
                    (role, match_count)
                )

        # =================================================
        # SORT ROLES
        # =================================================

        recommended_roles = sorted(
            recommended_roles,
            key=lambda x: x[1],
            reverse=True
        )

        # =================================================
        # DISPLAY RESULTS
        # =================================================

        if recommended_roles:

            st.subheader("🎯 Recommended Career Roles")

            for role, score in recommended_roles:

                st.markdown(f"""
                <div style="
                background:linear-gradient(145deg,#111827,#1e293b);
                padding:20px;
                border-radius:18px;
                margin-bottom:15px;
                border:1px solid rgba(255,255,255,0.05);
                box-shadow:0 0 15px rgba(0,255,255,0.1);
                ">

                <h2 style="color:white;">
                    {role}
                </h2>

                <p style="color:#94a3b8;">
                    Skill Match Score: {score}
                </p>

                </div>
                """, unsafe_allow_html=True)

        else:

            st.warning(
                "No matching career roles found. Try adding more skills."
            )

# =========================================================
# ROLE COMPARISON
# =========================================================

# =========================================================
# ROLE COMPARISON
# =========================================================

elif page == "Role Comparison":

    st.title("⚔ Professional Role Comparison Dashboard")

    role1 = st.selectbox(
        "Select Role 1",
        roles,
        key="role1"
    )

    role2 = st.selectbox(
        "Select Role 2",
        roles,
        index=1,
        key="role2"
    )

    # =====================================================
    # FIX MISSING SALARIES
    # =====================================================

    role1_salary = filtered_df[
        filtered_df[role_col] == role1
    ][salary_col].mean()

    role2_salary = filtered_df[
        filtered_df[role_col] == role2
    ][salary_col].mean()

    # Default salary if missing

    if pd.isna(role1_salary) or role1_salary <= 0:
        role1_salary = 25000

    if pd.isna(role2_salary) or role2_salary <= 0:
        role2_salary = 30000

    role1_salary = int(role1_salary)
    role2_salary = int(role2_salary)

    # =====================================================
    # METRIC CARDS
    # =====================================================

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(f"""
        <div style="
        background:linear-gradient(145deg,#111827,#1e293b);
        padding:25px;
        border-radius:20px;
        text-align:center;
        box-shadow:0 0 20px rgba(0,255,255,0.15);
        ">
            <h3 style="color:white;">{role1}</h3>
            <h1 style="color:#00d4ff;">₹ {role1_salary}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown(f"""
        <div style="
        background:linear-gradient(145deg,#111827,#1e293b);
        padding:25px;
        border-radius:20px;
        text-align:center;
        box-shadow:0 0 20px rgba(0,255,255,0.15);
        ">
            <h3 style="color:white;">{role2}</h3>
            <h1 style="color:#00d4ff;">₹ {role2_salary}</h1>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # =====================================================
    # ROLE 1 vs ROLE 2 GRAPH
    # =====================================================

    st.subheader("📊 Role Salary Comparison")

    compare_df = pd.DataFrame({
        "Role": [role1, role2],
        "Average Salary": [
            role1_salary,
            role2_salary
        ]
    })

    fig = px.bar(
        compare_df,
        x="Role",
        y="Average Salary",
        color="Role",
        text="Average Salary",
        template="plotly_dark"
    )

    fig.update_traces(
        texttemplate='₹%{text:.0f}',
        textposition='outside'
    )

    fig.update_layout(
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        font_color="white",
        title="Role 1 vs Role 2 Salary Comparison",
        title_font_size=26,
        height=550,
        xaxis_title="Job Roles",
        yaxis_title="Average Salary",
        showlegend=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # =====================================================
    # SKILLS COMPARISON
    # =====================================================

    st.write("")

    st.subheader("🛠 Skills Comparison")

    skills1 = get_skills(role1)
    skills2 = get_skills(role2)

    col1, col2 = st.columns(2)

    # ROLE 1 SKILLS

    with col1:

        st.markdown(f"""
        <div style="
        background:linear-gradient(145deg,#111827,#1e293b);
        padding:20px;
        border-radius:18px;
        border:1px solid rgba(255,255,255,0.05);
        margin-bottom:15px;
        ">
        <h3 style="color:white;">{role1}</h3>
        </div>
        """, unsafe_allow_html=True)

        for skill in skills1:
            st.success(skill)

    # ROLE 2 SKILLS

    with col2:

        st.markdown(f"""
        <div style="
        background:linear-gradient(145deg,#111827,#1e293b);
        padding:20px;
        border-radius:18px;
        border:1px solid rgba(255,255,255,0.05);
        margin-bottom:15px;
        ">
        <h3 style="color:white;">{role2}</h3>
        </div>
        """, unsafe_allow_html=True)

        for skill in skills2:
            st.success(skill)
# =========================================================
# ABOUT
# =========================================================

elif page == "About":

    st.title("ℹ About Project")

    st.markdown("""
    ### 🚀 Key Features

    ✅ Salary Analysis  
    ✅ Resume Analyzer  
    ✅ AI Career Advisor  
    ✅ Skill Gap Analysis  
    ✅ Role Comparison  

    ---

    ### 🛠 Technologies Used

    - Python
    - Streamlit
    - Pandas
    - Plotly
    - PyPDF2
    - python-docx

    ---

    ### 👩‍💻 Project Developed By

    Harshitha R
    """)

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.markdown("""
<div style='text-align:center;color:#94a3b8;'>
Developed with ❤️ using Streamlit | AI Job Market Dashboard
</div>
""", unsafe_allow_html=True)

# =========================================================
# LOGOUT
# =========================================================

if st.sidebar.button("🚪 Logout"):

    st.session_state.logged_in = False
    st.session_state.username = ""

    st.rerun()