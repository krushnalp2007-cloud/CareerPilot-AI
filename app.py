import streamlit as st

st.set_page_config(
    page_title="CareerPilot AI",
    page_icon="🚀",
    layout="wide"
)
st.markdown("""
<style>

.main{
    background-color:#0E1B3D;
}

section[data-testid="stSidebar"] {
    background-color: #162447;
}    

.card{
    background:#162447;
    padding:20px;
    border-radius:15px;
    text-align:center;
}

.metric{
    font-size:30px;
    font-weight:bold;
    color:#4DA8FF;
} 

</style>
""",unsafe_allow_html=True)
    
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
st.sidebar.image(
    "https://via.placeholder.com/120",
    width=120
)    

st.sidebar.markdown("### 👤 Krushnal Patil")
st.sidebar.markdown("Data Analyst Aspirant")
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
if page == "Dashboard":

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

    st.subheader("Career Roadmap")

    st.progress(25)
    st.write("Intern")

    st.progress(50)
    st.write("Junior")

    st.progress(75)
    st.write("Mid Level")

    st.progress(100)
    st.write("Senior")

    st.markdown("---")

    st.subheader("Skill Gap Analysis")

    st.progress(80, text="Python")
    st.progress(60, text="SQL")
    st.progress(40, text="Machine Learning")

    if page == "Skill Analysis":

        st.title("🚀 CareerPilot AI")
        st.markdown("""
        ## Welcome to CareerPilot AI

        AI-Powered Career Guidence Platform
        """)
        st.subheader("Multi-Agent Career & Skill Development Assistant")
    
    if "analyzed" not in st.session_state:
        st.session_state.analyzed = False
    
    if not st.session_state.analyzed:

        name = st.text_input("Enter Your Name")

        career = st.selectbox(
            "Select Career Goal",
            ["Data Analyst","AI Engineer","Software Developer","Data Scientist"]
        )

        skills = st.text_area("Enter Your Skills")

        resume = st.file_uploader(
            "Upload Resume",
            type=["pdf","docx"]
        )

    if st.button("Analyze Skills"):
        st.session_state.analyzed = True

    if resume:
        st.success("Resume Uploaded Successfull")
    st.title("🚀 CareerPilot AI Dashboard")

    st.markdown(f"""
    # Welcome, {name} 👋

    ### Career Goal: {career}
    """)
    st.markdown("---")
    col1,col2,col3,col4 = st.columns(4)

    with col1:
        st.metric("Resume Score", "85%", "+5%")

    with col2:
        st.metric("Skill Match", "78%", "+8%")

    with col3:
        st.metric("Missing Skills", "2")

    with col4:
        st.metric("Career Level", "Mid")
    
    st.markdown("---")    
        import pandas as pd

        skills_df = pd.DataFrame({
            "Skill": ["Python", "SQL", "Power BI", "Statistics"],
            "Score": [85, 75, 65, 60]
        })

        st.subheader("📊 Skill Analytics")

        st.bar_chart(
            skills_df.set_index("Skill")
        )
        
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

        st.subheader("Missing Skills")

        for skill in missing:
            st.write(f"• {skill}")
        st.header("📊 Career Report")

        st.info(f"Career Goal: {career}")
        st.info(f"Missing Skills: {', '.join(missing)}")
        st.info(f"Total Missing Skills: {len(missing)}")
        match_percent = int(
            ((len(required[career])-len(missing))
            / len(required[career])) * 100
        )   

        st.progress(match_percent)
        st.success(f"Skill Match: {match_percent}%")
        report_text = f"""
        Career Goal: {career}
        Missing Skills: {", ".join(missing)}
        Skill Match: {match_percent}%
        """

        st.download_button(
            "📥 Download Career Report",
            report_text,
            file_name="career_report.txt"
        )
        left,right = st.columns(2)
        st.header("🛣 Career Roadmap")
        
        if career == "Data Analyst":
            st.write("1️⃣ Learn Excel")
            st.write("2️⃣ Learn SQL")
            st.write("3️⃣ Learn Power BI")
            st.write("4️⃣ Build Dashboard Projects")
            st.write("5️⃣ Apply for Data Analyst Jobs")

        elif career == "AI Engineer":
            st.write("1️⃣ Learn Python")
            st.write("2️⃣ Learn Machine Learning")
            st.write("3️⃣ Learn Deep Learning")
            st.write("4️⃣ Build AI Projects")
            st.write("5️⃣ Apply for AI Engineer Jobs")

        elif career == "Software Developer":
            st.write("1️⃣ Learn Python")
            st.write("2️⃣ Learn Data Structures")
            st.write("3️⃣ Learn Git & GitHub")
            st.write("4️⃣ Build Full Stack Projects")
            st.write("5️⃣ Apply for Developer Jobs")

        elif career == "Data Scientist":
            st.write("1️⃣ Learn Python")
            st.write("2️⃣ Learn Statistics")
            st.write("3️⃣ Learn Machine Learning")
            st.write("4️⃣ Build Data Science Projects")
            st.write("5️⃣ Apply for Data Scientist Jobs")
            
            st.header("📚 Learning Path Agent")
        
        for item in missing:
            st.write(f"Learn {item}")
        resources = {
            "Power BI":"https://learn.microsoft.com/power-bi/",
            "Statistics":"https://www.khanacademy.org/math/statistics-probability",
            "Machine Learning":"https://www.coursera.org/learn/machine-learning"
        }  

        for skill in missing:
            if skill in resources:
                st.markdown(f"📚 [{skill} Course]({resources[skill]})")
        st.header("🏆 Recommended Certifications")

        if career == "Data Analyst":
            st.write("📜 Google Data Analytics Certificate")
            st.write("📜 Microsoft Power BI Certificate")

        elif career == "AI Engineer":
            st.write("📜 Machine Learning Specialization")
            st.write("📜 Deep Learning Specialization")

        elif career == "Software Developer":
            st.write("📜 Meta Backend Developer")
            st.write("📜 Python Programming Certificate")

        elif career == "Data Scientist":
            st.write("📜 IBM Data Science Professional Certificate")
            st.write("📜 Machine Learning Specialization")

        st.header("🌐 Learning Platforms")

        st.write("📚 Coursera")
        st.write("📚 Udemy")
        st.write("📚 Microsoft Learn")
        st.write("📚 Kaggle Learn")
        
        st.header("🤖 AI Career Tips")

        if career == "Data Analyst":
           st.info("Focus on Excel, SQL, Power BI, and Dashboard Projects.")

        elif career == "AI Engineer":
           st.info("Build Machine Learning and Deep Learning projects using Python.")

        elif career == "Software Developer":
           st.info("Master DSA, GitHub, Full Stack Development, and System Design.")

        elif career == "Data Scientist":
           st.info("Learn Statistics, Machine Learning, and Data Visualization.")
        
        st.header("📁 Portfolio Builder Agent")

        if career == "Data Analyst":
            st.write("• Sales Dashboard")
            st.write("• HR Analytics Dashboard")
            st.write("• Customer Churn Analysis")

        elif career == "AI Engineer":
            st.write("• Resume Analyzer")
            st.write("• Chatbot")
            st.write("• AI Career Coach")

        elif career == "Software Developer":
            st.write("• Task Manager App")
            st.write("• Portfolio Website")
            st.write("• E-Commerce Website")

            st.header("🎯 Recommended Jobs")

        if career == "Data Analyst":
            st.write("• Junior Data Analyst")
            st.write("• Business Analyst")
            st.write("• Reporting Analyst")

        elif career == "AI Engineer":
            st.write("• AI Engineer")
            st.write("• Machine Learning Engineer")

        elif career == "Software Developer":
            st.write("• Python Developer")
            st.write("• Full Stack Developer")
        
        elif career == "Data Scientist":
            st.write("• Data Scientist")
            st.write("• Machine Learning Engineer")
        st.header("💰 Salary Insights")

        if career == "Data Analyst":
            st.info("Average Salary: ₹4-10 LPA")

        elif career == "AI Engineer":
            st.info("Average Salary: ₹8-20 LPA")

        elif career == "Software Developer":
            st.info("Average Salary: ₹5-18 LPA")

        elif career == "Data Scientist":
            st.info("Average Salary: ₹7-20 LPA")    

        st.header("📄 Resume Review Agent")

        st.success("Resume Score: 85/100")

        st.write("Suggestions:")
        st.write("• Add measurable achievements")
        st.write("• Improve project descriptions")

        st.header("🎤 Interview Preparation Agent")

        st.write("Interview Questions:")

        st.write("1. Explain one project you built.")
        st.write("2. What challenges did you face?")
        st.write("3. How would you improve your solution?")
        st.header("🚀 Success Tips")

        tips = [
            "Build projects regularly",
            "Practice interview questions",
            "Learn from real-world datasets",
            "Contribute on GitHub",
            "Keep updating your portfolio"
        ]

        for tip in tips:
            st.write("✅", tip)
   
        st.success("🎉 Career Analysis Completed Successfully!")

        st.markdown("---")

        st.markdown(
            """
            <center>
                <h3>CareerPilot AI</h3>
                <p>AI-Powered Career Guidance Platform</p>
            </center>
            """,
            unsafe_allow_html=True
        )    
