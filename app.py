import streamlit as st

st.set_page_config(
    page_title="CareerPilot AI",
    page_icon="🚀",
    layout="wide"
)
st.markdown("""
<style>
.stApp {
    background-color: #0f172a;
    color: white;
}

h1,h2,h3,h4,h5,h6 {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🚀 CareerPilot AI")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Skill Analysis",
        "Learning Path",
        "Resume Review",
        "Interview Prep"
    ]
)

st.title("🚀 CareerPilot AI")
st.subheader("Multi-Agent Career & Skill Development Assistant")

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

skills = st.text_area(
    "Enter Your Skills (comma separated)",
    placeholder="Python, SQL, Excel"
)

if st.button("Analyze Skills"):

    st.header("📊 Skill Analysis Agent")

    missing = []

    required = {
        "Data Analyst": ["Python", "SQL", "Power BI", "Statistics"],
        "AI Engineer": ["Python", "Machine Learning", "Deep Learning"],
        "Software Developer": ["Python", "Git", "Data Structures"],
        "Data Scientist": ["Python", "Machine Learning", "Statistics"]
    }

    for skill in required[career]:
        if skill.lower() not in skills.lower():
            missing.append(skill)

    st.write("Missing Skills:")
    st.write(missing)

    st.header("📚 Learning Path Agent")

    for item in missing:
        st.write(f"Learn {item}")

    st.header("🗂 Portfolio Builder Agent")

    if career == "Data Analyst":
        st.write("- Sales Dashboard")
        st.write("- HR Analytics Dashboard")
        st.write("- Customer Churn Analysis")

    elif career == "AI Engineer":
        st.write("- Resume Analyzer")
        st.write("- Chatbot")
        st.write("- AI Career Coach")

    elif career == "Software Developer":
        st.write("- Task Manager App")
        st.write("- Portfolio Website")
        st.write("- E-Commerce Website")

    st.header("📄 Resume Review Agent")

    st.success("Resume Score: 85/100")

    st.write("Suggestions:")
    st.write("- Add measurable achievements")
    st.write("- Improve project descriptions")

    st.header("🎤 Interview Preparation Agent")

    st.write("Interview Questions:")

    st.write("1. Explain one project you built.")
    st.write("2. What challenges did you face?")
    st.write("3. How would you improve your solution?")
