# 🚀 CareerPilot AI

### AI-Powered Career Guidance & Skill Assessment Platform

> **Turn resume evidence into career direction, skill-gap insights, learning paths, and interview preparation.**

<p align="center">

[![🚀 Live Demo](https://img.shields.io/badge/🚀_Live_Demo-CareerPilot_AI-2563EB?style=for-the-badge)](https://careerpilot-ai-e6yuswhz6s5dzfd5uh7hr4.streamlit.app/)
[![💻 GitHub](https://img.shields.io/badge/💻_Source_Code-GitHub-111827?style=for-the-badge)](https://github.com/krushnalp2007-cloud/CareerPilot-AI)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
</p>

---

## 🎯 What is CareerPilot AI?

CareerPilot AI is an AI-powered career development platform designed to help students understand their career readiness using:

- 🎯 Career goals
- 🧠 Self-reported skills
- 📄 Resume evidence
- 🤖 Gemini AI analysis

Instead of providing generic career advice, CareerPilot AI connects a student's **available evidence** with the requirements of their target career and identifies actionable skill gaps.

---

## ⚡ Why CareerPilot AI?

### From Resume → Evidence → Skill Gaps → Career Action
```text
        Student Profile
              │
              ▼
        Career Goal
              │
              ▼
    Dynamic Career Requirements
              │
              ▼
   Resume + Student Skill Evidence
              │
              ▼
        Gemini AI Analysis
              │
              ▼
    Evidence-Based Guardrails
              │
              ▼
         Skill Gaps
          │         │
          ▼         ▼
    Learning Path   Interview Prep
          │         │
          └────┬────┘
               ▼
        Career Development


✨ Core Features
Module	                                           What it does
📊 Dashboard	                                   Centralized view of career readiness and skill insights
📄 Resume Review	                           Reviews uploaded PDF/DOCX resumes using resume evidence
🔍 Skill Analysis	                           Compares career requirements against available student evidence
📚 Learning Path	                           Converts identified skill gaps into a structured career-building                                                      direction
🎤 Interview Preparation	                   Generates role-specific interview questions using Gemini AI
📥 Downloads	                                   Allows generated reports and interview questions to be downloaded
📱 Responsive UI	                           Tested on desktop and mobile devices
🧠 Evidence-Based AI —                             The Key Technical Feature


CareerPilot AI does not blindly display the raw score returned by the AI.


The application evaluates the evidence level associated with a skill and applies deterministic constraints before presenting the final score.


Evidence levels
Evidence	                     Score Treatment
❌ None - 0	                     Missing
🟡 Mentioned	                     Maximum 50
🟢 Demonstrated	                     Maximum 89
🔵 Strong Demonstrated	             80–100


Example
If a student only mentions a technology in their resume, the system should not treat that as strong technical proficiency.

Resume Evidence
      ↓
Gemini Evaluation
      ↓
Evidence Level
      ↓
Deterministic Guardrail
      ↓
Final Skill Score

This creates a controlled workflow where AI reasoning is combined with application-level rules.


🤖 How Gemini AI is Used

Gemini is used for dynamic AI tasks including:

Career Requirements

Determines practical skills relevant to the career entered by the student.

Resume Review

Analyzes the supplied resume content and identifies evidence, strengths, and areas for improvement.

Skill Analysis

Evaluates career-relevant skills against the student's available evidence.

Interview Preparation

Generates role-specific interview questions based on the selected career and available skill information.

CareerPilot AI is not simply a chatbot wrapper.

The application combines AI reasoning with resume processing, structured outputs, evidence rules, scoring guardrails, and a connected career-development workflow.


🏗️ System Architecture

High-Level Architecture
┌───────────────────────────────┐
│          Student              │
│ Career Goal + Skills + Resume │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│        Streamlit UI           │
└───────────────┬───────────────┘
                │
       ┌────────┴────────┐
       ▼                 ▼
┌─────────────┐   ┌──────────────┐
│ Resume      │   │ Student      │
│ Processing  │   │ Profile      │
└──────┬──────┘   └──────┬───────┘
       │                 │
       └────────┬────────┘
                ▼
┌───────────────────────────────┐
│         Gemini AI             │
│ Career + Resume + Skill       │
│ Analysis + Interview Prep     │
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│ Deterministic Guardrails      │
│ Evidence-Based Score Control  │
└───────────────┬───────────────┘
                ▼
       ┌────────┼────────┐
       ▼        ▼        ▼
   Skill Gaps  Learning  Interview
              Path       Preparation


🛠️ Technology Stack
Application
Python
Streamlit
AI
Google Gemini API
google-genai
Data & Visualization
Pandas
NumPy
Plotly
Resume Processing
PyPDF
python-docx
Configuration
python-dotenv
Streamlit Secrets
Deployment
Streamlit Community Cloud
Version Control
Git
GitHub


📄 Resume Processing

CareerPilot AI supports:

PDF Resume
    ↓
PyPDF
    ↓
Extracted Text
    ↓
AI Analysis

and:

DOCX Resume
    ↓
python-docx
    ↓
Extracted Text
    ↓
AI Analysis

The extracted content is then used as evidence for downstream career analysis.

🔍 Skill Analysis Workflow
1. User selects / enters a career
             ↓
2. Career requirements are generated dynamically
             ↓
3. Student skills + resume evidence are collected
             ↓
4. Gemini evaluates the available evidence
             ↓
5. Evidence-based score guardrails are applied
             ↓
6. Skill gaps are identified
             ↓
7. Career match and recommendations are displayed

The system is designed not to assume technical proficiency merely from:

Degree
College
Academic year
Career aspiration

The available evidence must support the skill evaluation.

📚 Learning Path

The identified skill gaps are converted into a structured career-building direction.

Typical progression:

Understand Fundamentals
          ↓
Strengthen Skill Gaps
          ↓
Build Practical Projects
          ↓
Document Projects
          ↓
Prepare for Interviews
          ↓
Build Career-Focused Resume
          ↓
Apply for Relevant Opportunities
🎤 Interview Preparation

CareerPilot AI can generate role-specific interview questions using Gemini AI.

Questions can consider:

Selected career
Student skills
Identified skill gaps

Generated questions include:

Category
Difficulty
Question

The question set can also be downloaded for later practice.

🔐 Security

API credentials are not committed to the public GitHub repository.

Local Development
GEMINI_API_KEY=your_api_key_here

The .env file is excluded through .gitignore.

Production Deployment

The Gemini API key is stored using Streamlit Cloud Secrets and accessed at runtime.

Local Development
       │
       └── .env
            │
            ▼
       Gemini API


Production
       │
       └── Streamlit Secrets
            │
            ▼
       Gemini API

⚠️ Never commit API keys or .env files to GitHub.

☁️ Deployment

CareerPilot AI is deployed using Streamlit Community Cloud.

GitHub Repository
        ↓
Streamlit Community Cloud
        ↓
Secure Secrets
        ↓
Public HTTPS Application
🚀 Live Application

Open CareerPilot AI →

🧪 Testing & Validation

The deployed application has been tested for:

✅ Navigation
✅ Gemini responses
✅ Error handling
✅ PDF resume upload
✅ DOCX resume processing
✅ Resume analysis
✅ Skill analysis
✅ Evidence-based scoring
✅ Learning Path flow
✅ Interview question generation
✅ Interview question download
✅ API-key security configuration
✅ Desktop UI
✅ Mobile UI
✅ Mobile button visibility
✅ Live deployment
📱 Responsive Design

CareerPilot AI has been tested on both desktop and mobile devices.

Mobile testing included:

Navigation
Resume upload
Skill Analysis
Learning Path
Interview Preparation
Button visibility
Overall usability

🎯 Project Impact

CareerPilot AI helps students:

Identify career-specific skill requirements
Understand their current evidence
Discover skill gaps
Improve their resumes
Create a focused learning direction
Prepare for relevant interviews

🚀 Future Scope

Potential future enhancements include:

💼 Internship Recommendation
🔎 Job Description Matching
🎓 Certification Tracking
🔗 LinkedIn Profile Analysis
🎤 AI Mock Interviews
📈 Career Progress Tracking
📷 OCR support for scanned resumes
📚 More detailed learning resources


👨‍💻 Developer
Krushnal Patil

B.Tech — Computer Science & Engineering

KIT

📜 License

This project is licensed under the MIT License.

<p align="center">
🚀 CareerPilot AI

From career goals to evidence-based career action.

🌐 Live Demo •
💻 GitHub Repository

</p> ```
