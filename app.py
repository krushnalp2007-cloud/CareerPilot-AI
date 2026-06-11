import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="CareerPilot AI",
    page_icon="🚀",
    layout="wide"
)
st.markdown("""
<div style="
background: linear-gradient(90deg,#162447,#1F4068);
padding:25px;
border-radius:15px;
text-align:center;
color:white;
">
<h1>🚀 CareerPilot AI</h1>
<h3>AI-Powered Multi-Agent Career Guidance Platform</h3>
<p>
Analyze Skills • Learning Paths • Resume Review • Interview Preparation
</p>
</div>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "career" not in st.session_state:
    st.session_state["career"] = "Data Analyst"

if "analyzed" not in st.session_state:
    st.session_state["analyzed"] = False

# ---------------- CSS ----------------
st.markdown("""
<style>
.stApp {
    background-color:#0f172a;
    color:white;
}

section[data-testid="stSidebar"] {
    background-color:#162447;
}

.card{
    background:#162447;
    padding:20px;
    border-radius:15px;
    text-align:center;
}

h1,h2,h3,h4,h5,h6{
    color:white !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.title("🚀 CareerPilot AI")

st.sidebar.markdown("### 👤 Krushnal Patil")
st.sidebar.markdown("Data Analyst Aspirant")

page = st.sidebar.radio(
    "Navigation",
    [
        "Skill Analysis",
        "Learning Path",
        "Resume Review",
        "Interview Prep"
        "Dashboard",
    ]
)

# ---------------- DASHBOARD ----------------
if page == "Dashboard":

    st.title("🚀 CareerPilot AI Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class='card'>
        <h3>Career Level</h3>
        <h2>Mid Level</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='card'>
        <h3>Resume Score</h3>
        <h2>85%</h2>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class='card'>
        <h3>Skill Match</h3>
        <h2>78%</h2>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("🎯 Career Progress Score")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=78,
        title={"text": "Career Match"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#4DA8FF"}
        }
    ))
    
    fig.update_layout(height=350)
    
    st.plotly_chart(fig, use_container_width=True)
    st.success("⭐ Current Position: Mid Level")

    st.markdown("### 🎯 Next Career Goal")

    st.info("""
    To reach Senior Level:

    ✅ Complete 2 Advanced Projects

    ✅ Earn Microsoft AI Certification

    ✅ Improve Resume Score to 90+

    ✅ Practice 50 Mock Interviews
    """)
# ---------------- SKILL ANALYSIS ----------------
elif page == "Skill Analysis":

    st.title("🚀 CareerPilot AI")

    name = st.text_input("Enter Your Name")

    career = st.selectbox(
        "Select Career Goal",
        [
            "Data Analyst",
            "AI Engineer",
            "Software Developer",
            "Data Scientist"
        ]
    )

    skills = st.text_area("Enter Your Skills")

    resume = st.file_uploader(
        "Upload Resume",
        type=["pdf", "docx"]
    )

    if st.button("Analyze Skills"):
        st.session_state.analyzed = True
        st.session_state["career"] = career

    if st.session_state.analyzed:

        if resume:
            st.success("Resume Uploaded Successfully")

        required = {
            "Data Analyst": ["Python", "SQL", "Power BI", "Statistics"],
            "AI Engineer": ["Python", "Machine Learning", "Deep Learning"],
            "Software Developer": ["Python", "Git", "Data Structures"],
            "Data Scientist": ["Python", "Machine Learning", "Statistics"]
        }

        missing = []

        for skill in required[career]:
            if skill.lower() not in skills.lower():
                missing.append(skill)

        match_percent = int(
            ((len(required[career]) - len(missing))
             / len(required[career])) * 100
        )

        st.markdown("---")

        st.subheader("📊 Skill Analytics")

        skills_df = pd.DataFrame({
            "Skill": ["Python", "SQL", "Power BI", "Statistics"],
            "Score": [85, 75, 65, 60]
        })

        st.bar_chart(skills_df.set_index("Skill"))

        st.subheader("Missing Skills")

        if missing:
            for skill in missing:
                st.write(f"• {skill}")
        else:
            st.success("No missing skills found!")

        st.subheader("Career Report")

        st.info(f"Career Goal: {career}")
        st.info(f"Skill Match: {match_percent}%")

        st.progress(match_percent)

        report_text = f"""
Career Goal: {career}
Missing Skills: {', '.join(missing)}
Skill Match: {match_percent}%
"""

        st.download_button(
            "📥 Download Career Report",
            report_text,
            file_name="career_report.txt"
        )

# ---------------- LEARNING PATH ----------------
elif page == "Learning Path":

    career = st.session_state["career"]

    st.header("📚 Learning Path")

    if career == "Data Analyst":
        roadmap = [
            "Learn Excel",
            "Learn SQL",
            "Learn Power BI",
            "Build Dashboard Projects",
            "Apply for Jobs"
        ]

    elif career == "AI Engineer":
        roadmap = [
            "Learn Python",
            "Learn ML",
            "Learn Deep Learning",
            "Build AI Projects",
            "Apply for Jobs"
        ]

    elif career == "Software Developer":
        roadmap = [
            "Learn Python",
            "Learn DSA",
            "Learn Git",
            "Build Projects",
            "Apply for Jobs"
        ]

    else:
        roadmap = [
            "Learn Python",
            "Learn Statistics",
            "Learn ML",
            "Build Projects",
            "Apply for Jobs"
        ]

    for step in roadmap:
        st.write("✅", step)

# ---------------- RESUME REVIEW ----------------
elif page == "Resume Review":

    st.header("📄 Resume Review")

    st.success("Resume Score: 85/100")

    st.write("Suggestions:")
    st.write("• Add measurable achievements")
    st.write("• Improve project descriptions")
    st.write("• Add certifications")
    st.write("• Include GitHub portfolio")

# ---------------- INTERVIEW PREP ----------------
elif page == "Interview Prep":

    st.header("🎤 Interview Preparation")

    questions = [
        "Explain one project you built.",
        "What challenges did you face?",
        "How would you improve your solution?",
        "Why should we hire you?",
        "Tell me about yourself."
    ]

    for q in questions:
        st.write("✅", q)

# ---------------- FOOTER ----------------
st.markdown("---")

st.markdown(
    """
    <center>
        <h3>CareerPilot AI</h3>
        <p>AI Powered Career Guidance Platform</p>
    </center>
    """,
    unsafe_allow_html=True 
)
