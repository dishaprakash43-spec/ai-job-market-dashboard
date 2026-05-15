import streamlit as st
import pandas as pd
import plotly.express as px
import io
from docx import Document
import PyPDF2

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Job Market Dashboard",
    layout="wide"
)

# =========================================================
# DARK THEME
# =========================================================

st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: white;
}
.stApp {
    background-color: #020617;
}
h1,h2,h3,h4,h5,h6,p,label {
    color: white;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():
    df = pd.read_csv("job_market_india.csv")

    # Salary cleaning
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
# =========================================================
# LOGIN + SIGNUP SYSTEM
# =========================================================

# Session state setup
# =========================================================
# LOGIN + SIGNUP SYSTEM (FIXED FOR STREAMLIT CLOUD)
# =========================================================

import json
import os

USERS_FILE = "users.json"

# Create users file if not exists
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

# Load users
with open(USERS_FILE, "r") as f:
    users = json.load(f)

# Session states
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# =========================================================
# LOGIN PAGE
# =========================================================

if not st.session_state.logged_in:

    st.markdown("""
    <style>
    .title {
        text-align:center;
        font-size:48px;
        font-weight:bold;
        color:white;
    }

    .subtitle {
        text-align:center;
        color:lightgray;
        margin-bottom:30px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        "<div class='title'>🤖 AI Job Market Dashboard</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='subtitle'>Login or Create a New Account</div>",
        unsafe_allow_html=True
    )

    tab1, tab2 = st.tabs(["🔐 Login", "🆕 Sign Up"])

    # =====================================================
    # LOGIN
    # =====================================================

    with tab1:

        st.subheader("Login to Your Account")

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

                st.success("✅ Login Successful")

                st.rerun()

            else:
                st.error("❌ Invalid Username or Password")

    # =====================================================
    # SIGN UP
    # =====================================================

    with tab2:

        st.subheader("Create New Account")

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

            if new_user.strip() == "":
                st.warning("Please enter username")

            elif new_pass.strip() == "":
                st.warning("Please enter password")

            elif new_user in users:
                st.warning("Username already exists")

            elif new_pass != confirm_pass:
                st.warning("Passwords do not match")

            else:

                users[new_user] = new_pass

                with open(USERS_FILE, "w") as f:
                    json.dump(users, f)

                st.success("✅ Account Created Successfully")
                st.info("Now login using your new account")

    st.stop()
# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.image(
    "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
    width=150
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

states = []

possible_state_cols = [
    "State",
    "state",
    "Location"
]

state_col = None

for col in possible_state_cols:
    if col in df.columns:
        state_col = col
        break

if state_col:
    states = sorted(df[state_col].dropna().unique())

selected_states = st.sidebar.multiselect(
    "📍 Select States",
    states
)

# Salary range starts from 0
salary_min = 0

salary_max = int(df[salary_col].max()) if salary_col else 100000

salary_range = st.sidebar.slider(
    "💰 Salary Range",
    salary_min,
    salary_max,
    (salary_min, salary_max)
)

# Job Role filter
role_col = None

possible_role_cols = [
    "Job Title",
    "Role",
    "job_title",
    "Job Role"
]

for col in possible_role_cols:
    if col in df.columns:
        role_col = col
        break

roles = sorted(df[role_col].dropna().unique())

selected_roles = st.sidebar.multiselect(
    "💼 Select Job Roles",
    roles
)

search = st.sidebar.text_input("🔍 Search Job Role")

experience_level = st.sidebar.selectbox(
    "🧠 Experience Level",
    ["Fresher", "Mid-Level", "Experienced"]
)

# =========================================================
# FILTER DATA
# =========================================================

# =========================================================
# FILTER DATA
# =========================================================

filtered_df = df.copy()

# Apply State Filter
if selected_states:
    filtered_df = filtered_df[
        filtered_df[state_col].isin(selected_states)
    ]

# Apply Role Filter
if selected_roles:
    filtered_df = filtered_df[
        filtered_df[role_col].isin(selected_roles)
    ]

# Apply Salary Filter
if salary_col:
    filtered_df = filtered_df[
        (filtered_df[salary_col] >= salary_range[0]) &
        (filtered_df[salary_col] <= salary_range[1])
    ]

# Apply Search Filter
if search:
    filtered_df = filtered_df[
        filtered_df[role_col]
        .str.contains(search, case=False, na=False)
    ]

# =========================================================
# EMPTY FILTER FIX
# =========================================================

if filtered_df.empty:

    st.warning("""
    No exact match found for selected filters.
    Showing similar available jobs instead.
    """)

    # fallback data
    filtered_df = df.head(20)

# =========================================================
# AUTO SKILL GENERATOR
# =========================================================

def get_skills(role):

    role = str(role).lower()

    if "data scientist" in role:
        return ["Python", "Machine Learning", "SQL", "Deep Learning"]

    elif "data analyst" in role:
        return ["Excel", "SQL", "Power BI", "Statistics"]

    elif "frontend" in role:
        return ["HTML", "CSS", "JavaScript", "React"]

    elif "backend" in role:
        return ["Python", "Django", "APIs", "SQL"]

    elif "software engineer" in role:
        return ["Java", "DSA", "System Design", "Problem Solving"]

    elif "python" in role:
        return ["Python", "Flask", "Django", "APIs"]

    elif "machine learning" in role:
        return ["Python", "TensorFlow", "ML Algorithms", "Data Processing"]

    elif "ai engineer" in role:
        return ["Deep Learning", "TensorFlow", "Python", "Neural Networks"]

    elif "cloud" in role:
        return ["AWS", "Azure", "Linux", "Networking"]

    elif "business analyst" in role:
        return ["Excel", "Communication", "SQL", "Analytics"]

    elif "advisor" in role:
        return ["Communication", "Counselling", "Presentation Skills", "Guidance"]

    elif "artist" in role:
        return ["Creativity", "Animation", "Blender", "Design"]

    elif "teacher" in role:
        return ["Teaching", "Communication", "Subject Knowledge", "Presentation"]

    elif "manager" in role:
        return ["Leadership", "Management", "Communication", "Planning"]

    elif "developer" in role:
        return ["Programming", "Debugging", "APIs", "Problem Solving"]

    else:
        return [
            "Communication",
            "Teamwork",
            "Problem Solving",
            "Technical Knowledge"
        ]

# =========================================================
# DASHBOARD PAGE
# =========================================================

if page == "Dashboard":

    st.title("📊 Indian Job Market Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Jobs", len(filtered_df))

    avg_salary = int(filtered_df[salary_col].mean()) \
        if salary_col else 0

    col2.metric("Average Salary", f"₹ {avg_salary}")

    col3.metric(
        "States",
        filtered_df[state_col].nunique()
    )

    top_role = filtered_df[role_col].mode()[0] \
        if len(filtered_df) > 0 else "N/A"

    col4.metric("Top Role", top_role)

    st.subheader("📌 Top Job Roles")

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

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🏆 Top Hiring States")

    state_counts = (
        filtered_df[state_col]
        .value_counts()
        .reset_index()
    )

    state_counts.columns = ["State", "Jobs"]

    st.dataframe(state_counts)

# =========================================================
# SALARY ANALYSIS
# =========================================================

# =========================================================
# SALARY ANALYSIS
# =========================================================

elif page == "Salary Analysis":

    st.title("💰 Salary Analysis")

    # Handle empty filtered data
    if filtered_df.empty:

        st.warning("No data available for selected filters.")

    else:

        max_salary = filtered_df[salary_col].max()
        min_salary = filtered_df[salary_col].min()
        avg_salary = filtered_df[salary_col].mean()
        median_salary = filtered_df[salary_col].median()

        # Replace NaN values safely
        max_salary = 0 if pd.isna(max_salary) else int(max_salary)
        min_salary = 0 if pd.isna(min_salary) else int(min_salary)
        avg_salary = 0 if pd.isna(avg_salary) else int(avg_salary)
        median_salary = 0 if pd.isna(median_salary) else int(median_salary)

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Highest Salary",
            f"₹ {max_salary}"
        )

        col2.metric(
            "Lowest Salary",
            f"₹ {min_salary}"
        )

        col3.metric(
            "Average Salary",
            f"₹ {avg_salary}"
        )

        col4.metric(
            "Median Salary",
            f"₹ {median_salary}"
        )

        st.subheader("🏆 Highest Paying Jobs")

        top_jobs = (
            filtered_df
            .sort_values(by=salary_col, ascending=False)
            .head(10)
        )

        st.dataframe(
            top_jobs[[role_col, state_col, salary_col]]
        )

        # Download CSV
        csv = filtered_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇ Download CSV",
            csv,
            "filtered_jobs.csv",
            "text/csv"
        )

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

    st.plotly_chart(fig, use_container_width=True)

# =========================================================
# RESUME MATCH
# =========================================================

elif page == "Resume Match":

    st.title("📄 Resume Match Score")

    uploaded_file = st.file_uploader(
        "Upload Resume",
        type=["pdf", "docx"]
    )

    if uploaded_file:

        text = ""

        # PDF
        if uploaded_file.name.endswith(".pdf"):

            pdf_reader = PyPDF2.PdfReader(uploaded_file)

            for page in pdf_reader.pages:
                text += page.extract_text()

        # DOCX
        elif uploaded_file.name.endswith(".docx"):

            doc = Document(uploaded_file)

            for para in doc.paragraphs:
                text += para.text

        text = text.lower()

        resume_keywords = [
            "education",
            "skills",
            "experience",
            "project",
            "resume"
        ]

        is_resume = any(
            keyword in text
            for keyword in resume_keywords
        )

        if not is_resume:

            st.error("❌ This is not a valid resume.")

        else:

            st.success("✅ Resume Uploaded Successfully")

            all_skills = [
                "python",
                "sql",
                "excel",
                "machine learning",
                "deep learning",
                "react",
                "aws",
                "java",
                "communication",
                "power bi",
                "django",
                "tensorflow"
            ]

            found_skills = []

            for skill in all_skills:
                if skill in text:
                    found_skills.append(skill.title())

            st.subheader("🛠 Skills Found in Resume")

            if found_skills:
                st.write(", ".join(found_skills))
            else:
                st.warning("No known skills detected.")

            # Match role
            best_role = "Data Analyst"
            match_score = min(len(found_skills) * 15, 100)

            if "machine learning" in text:
                best_role = "Data Scientist"

            elif "react" in text:
                best_role = "Frontend Developer"

            elif "aws" in text:
                best_role = "Cloud Engineer"

            st.success(f"Best Matching Role: {best_role}")

            st.metric("Match Score", f"{match_score}%")

# =========================================================
# SKILL GAP ANALYSIS
# =========================================================

elif page == "Skill Gap Analysis":

    st.title("📚 Skill Gap Analysis")

    target_role = st.selectbox(
        "Select Target Role",
        roles
    )

    role_skills = get_skills(target_role)

    st.subheader("Required Skills")

    for skill in role_skills:
        st.write(f"✅ {skill}")

# =========================================================
# AI CAREER ADVISOR
# =========================================================
# =========================================================
# AI CAREER ADVISOR
# =========================================================

elif page == "AI Career Advisor":

    st.title("🤖 AI Career Advisor")

    user_skills = st.text_input(
        "Enter Your Skills (comma separated)"
    )

    if user_skills:

        skills = [
            skill.strip().lower()
            for skill in user_skills.split(",")
        ]

        # Recommendations
        recommendations = []

        if "python" in skills and "sql" in skills:
            recommendations.append("📊 Data Analyst")

        if "machine learning" in skills or "deep learning" in skills:
            recommendations.append("🤖 Data Scientist")

        if "react" in skills or "javascript" in skills:
            recommendations.append("💻 Frontend Developer")

        if "django" in skills or "flask" in skills:
            recommendations.append("⚙ Backend Developer")

        if "aws" in skills or "cloud" in skills:
            recommendations.append("☁ Cloud Engineer")

        if "excel" in skills and "communication" in skills:
            recommendations.append("📈 Business Analyst")

        if not recommendations:
            recommendations.append("🧠 Software Engineer")

        st.subheader("🎯 Recommended Career Paths")

        for rec in recommendations:
            st.success(rec)

        # Career advice
        st.subheader("📌 AI Suggestions")

        if "python" in skills:
            st.info("Improve Python projects to strengthen your profile.")

        if "machine learning" in skills:
            st.info("Build AI/ML projects and learn deployment.")

        if "react" in skills:
            st.info("Create frontend portfolio projects.")

        if "aws" in skills:
            st.info("Learn DevOps and cloud deployment.")

        if "communication" not in skills:
            st.warning("Improve communication skills for better placements.")

# =========================================================
# ROLE COMPARISON
# =========================================================

elif page == "Role Comparison":

    st.title("⚔ Role Comparison")

    role1 = st.selectbox(
        "Select Role 1",
        roles
    )

    role2 = st.selectbox(
        "Select Role 2",
        roles,
        index=1 if len(roles) > 1 else 0
    )

    role1_salary = filtered_df[
        filtered_df[role_col] == role1
    ][salary_col].mean()

    role2_salary = filtered_df[
        filtered_df[role_col] == role2
    ][salary_col].mean()

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
        color="Role"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Skills comparison
    st.subheader("🛠 Skills Comparison")

    skills1 = get_skills(role1)
    skills2 = get_skills(role2)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### 🔹 {role1}")

        for skill in skills1:
            st.write(f"✅ {skill}")

    with col2:
        st.markdown(f"### 🔹 {role2}")

        for skill in skills2:
            st.write(f"✅ {skill}")

# =========================================================
# ABOUT
# =========================================================

# =========================================================
# ABOUT
# =========================================================

elif page == "About":

    st.title("ℹ About This Project")

    st.markdown("""
    ## 🇮🇳 AI Powered Indian Job Market Dashboard

    ### 🚀 Key Features

    ✅ Salary Analysis  
    ✅ Resume Match Score  
    ✅ Resume Skill Extraction  
    ✅ AI Career Advisor  
    ✅ Skill Gap Analysis  
    ✅ Role Comparison  
    ✅ State-wise Job Analysis  
    ✅ CSV Download Feature  
    ✅ Login & Logout System  
    ✅ Interactive Filters  

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

    **Disha Prakash**
    """)
# =========================================================
# LOGOUT
# =========================================================

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
