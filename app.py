import os
import re
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document
except ImportError:
    Document = None


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CareerPilot AI",
    page_icon="🚀",
    layout="wide",
)


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error(
        "Gemini API key not found. Please add GEMINI_API_KEY to your .env file."
    )
    st.stop()

try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"Unable to initialize Gemini: {e}")
    st.stop()


# ============================================================
# STRUCTURED OUTPUT MODELS
# ============================================================

class CareerRequirementsResult(BaseModel):
    required_skills: list[str] = Field(
        description="Core technical skills required for the target career."
    )


class SkillEvaluation(BaseModel):
    skill: str = Field(description="Name of the evaluated skill")
    score: int = Field(
        description="Evidence-based proficiency score from 0 to 100",
        ge=0,
        le=100,
    )
    status: str = Field(
        description="One of: Strong, Developing, Weak, Missing"
    )
    evidence_level: str = Field(
        description="One of: None, Mentioned, Demonstrated, Strong Demonstrated"
    )
    evidence: str = Field(
        description="Exact or closely paraphrased evidence from supplied student information. If no evidence exists, say None."
    )
    reason: str = Field(
        description="Short explanation based only on supplied student information."
    )


class SkillAnalysisResult(BaseModel):
    evaluations: list[SkillEvaluation]
    overall_match: int = Field(
        description="Overall match from 0 to 100",
        ge=0,
        le=100,
    )
    missing_skills: list[str]
    summary: str


class ResumeReviewResult(BaseModel):
    overall_score: int = Field(
        description="Resume quality/readiness score from 0 to 100",
        ge=0,
        le=100,
    )
    summary: str = Field(
        description="Factual summary based only on the supplied resume text."
    )
    strengths: list[str] = Field(
        description="Resume strengths that are explicitly supported by the supplied resume."
    )
    issues: list[str] = Field(
        description="Specific issues or limitations detected in the supplied resume text."
    )
    detected_skills: list[str] = Field(
        description="Technical/professional skills explicitly present in the supplied resume."
    )
    missing_or_unclear_sections: list[str] = Field(
        description="Sections or information not detected or unclear in the supplied resume text."
    )
    recommendations: list[str] = Field(
        description="Actionable resume improvements. Do not claim that the student already has anything recommended."
    )


class CareerAnalysisResult(BaseModel):
    strengths: list[str]
    skill_gaps: list[str]
    priority_skills: list[str]
    recommended_steps: list[str]
    career_readiness_advice: list[str]


class InterviewQuestion(BaseModel):
    question: str
    category: str
    difficulty: str


class InterviewPrepResult(BaseModel):
    questions: list[InterviewQuestion]


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_STATE = {
    "career": "",
    "student_name": "",
    "student_skills": "",
    "resume_text": None,
    "resume_name": None,
    "resume_signature": None,
    "resume_analysis": None,
    "analyzed": False,
    "skill_analysis": None,
    "career_analysis": None,
    "required_skills": [],
    "interview_questions": None,
    "interview_source": None,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# RESUME TEXT EXTRACTION
# ============================================================

def extract_resume_text(uploaded_file):
    """Extract text from PDF or DOCX."""
    if uploaded_file is None:
        return None

    try:
        file_name = uploaded_file.name.lower()

        if file_name.endswith(".pdf"):
            if PdfReader is None:
                st.error("PDF support is not installed. Run: pip install pypdf")
                return None

            reader = PdfReader(uploaded_file)
            pages = []

            for page in reader.pages:
                pages.append(page.extract_text() or "")

            text = "\n".join(pages).strip()

        elif file_name.endswith(".docx"):
            if Document is None:
                st.error(
                    "DOCX support is not installed. Run: pip install python-docx"
                )
                return None

            document = Document(uploaded_file)
            paragraphs = [
                paragraph.text
                for paragraph in document.paragraphs
                if paragraph.text.strip()
            ]
            text = "\n".join(paragraphs).strip()

        else:
            st.warning("Only PDF and DOCX resumes are supported.")
            return None

        if not text:
            st.warning(
                "The resume was uploaded, but no readable text was found. "
                "If it is a scanned PDF, OCR will be required."
            )
            return None

        return text

    except Exception as e:
        st.error(f"Could not read the resume: {e}")
        return None


# ============================================================
# DYNAMIC CAREER REQUIREMENTS
# ============================================================

def generate_required_skills_with_gemini(career):
    """
    Generate core skills for ANY career goal entered by the user.
    No hardcoded career dropdown is used.
    """

    prompt = f"""
You are the Career Requirements Agent for CareerPilot AI.

TARGET CAREER:
{career}

Generate the most important CORE technical/professional skills needed
for this exact career.

Rules:
1. The career may be specific, such as Backend Developer, Java Developer,
   Cloud Engineer, Cybersecurity Analyst, DevOps Engineer, etc.
2. Return 5 to 10 practical skills.
3. Prefer skills that can realistically be evaluated from a student's
   skills, resume, projects, internships, certifications, or courses.
4. Do not include generic personality traits.
5. Do not assume the student possesses any of these skills.
6. Do not use the student's profile as evidence.
7. Avoid duplicates.
8. Keep skill names concise and recognizable.

Return only the requested structured JSON.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=CareerRequirementsResult,
                temperature=0.1,
            ),
        )

        if not response.text:
            raise ValueError("Gemini returned an empty career-requirements response.")

        result = CareerRequirementsResult.model_validate_json(response.text)

        cleaned = []
        seen = set()

        for skill in result.required_skills:
            skill = skill.strip()
            normalized = skill.lower()

            if skill and normalized not in seen:
                cleaned.append(skill)
                seen.add(normalized)

        return cleaned[:10]

    except Exception as e:
        if is_quota_error(e):
            st.warning(
                "Gemini API quota is exhausted for this project/model. "
                "This is an API usage limit, not a problem with your uploaded resume or code. "
                "Wait for the quota reset or use a project/model with available quota."
            )
        else:
            st.error(f"Could not generate career requirements: {e}")
        return []


# ============================================================
# RESUME REVIEW ANALYSIS
# ============================================================

def analyze_resume_with_gemini(resume_text, career=""):
    """Review only the content actually extracted from the uploaded resume."""

    if not resume_text or not resume_text.strip():
        return None

    resume_context = resume_text[:30000]
    target_career = career.strip() if career and career.strip() else "Not specified"

    prompt = f"""
You are the Resume Review Agent for CareerPilot AI.

TARGET CAREER:
{target_career}

RESUME CONTENT:
{resume_context}

============================================================
STRICT RESUME EVIDENCE POLICY
============================================================

Review ONLY the text supplied above.

Do NOT:
- invent skills, projects, internships, jobs, certifications, achievements, or education
- assume a skill from the student's degree or branch
- assume proficiency from a keyword alone
- treat recommendations as completed work
- claim that a section exists unless it is actually present in the supplied text
- treat an academic year as current unless the resume explicitly establishes that it is current

You MAY:
- identify information explicitly present in the resume
- identify information that is not detected in the extracted text
- point out unclear wording, missing detail, weak evidence, or incomplete descriptions
- recommend what the student could add or improve

IMPORTANT:
A missing item means "not detected in the supplied extracted text", not necessarily that the original visual resume does not contain it.

If a technical skill is listed but there is no project/task/experience showing its use, treat it as listed rather than demonstrated.

============================================================
SCORING
============================================================

Give an overall resume quality/readiness score from 0 to 100 based only on:
- clarity
- completeness of detectable information
- specificity of experience/project descriptions
- evidence of skills
- organization visible in the extracted text
- relevance to the target career when a target career is provided

Do not increase the score because the student is a CSE student.

============================================================
RETURN
============================================================

1. overall_score
2. summary
3. strengths
4. issues
5. detected_skills
6. missing_or_unclear_sections
7. recommendations

Return ONLY the requested structured JSON.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ResumeReviewResult,
                temperature=0.1,
            ),
        )

        if not response.text:
            raise ValueError("Gemini returned an empty resume-review response.")

        result = ResumeReviewResult.model_validate_json(response.text)
        result.overall_score = max(0, min(result.overall_score, 100))
        return result

    except Exception as e:
        if is_quota_error(e):
            st.warning(
                "Gemini API quota is exhausted. Resume extraction still works, but "
                "AI review cannot run until Gemini quota is available again."
            )
        else:
            st.error(f"Gemini resume review failed: {e}")
        return None


# ============================================================
# DETERMINISTIC EVIDENCE GUARDRAIL
# ============================================================

def normalize_evaluation(evaluation):
    """
    Prevent unsupported high scores after Gemini responds.

    None -> 0
    Mentioned -> max 50
    Demonstrated -> max 89
    Strong Demonstrated -> 80-100
    """

    level = evaluation.evidence_level.strip().lower()

    if level == "none":
        evaluation.score = 0
        evaluation.status = "Missing"
        evaluation.evidence = "None"

    elif level == "mentioned":
        evaluation.score = min(evaluation.score, 50)

        if evaluation.score < 30:
            evaluation.status = "Weak"
        else:
            evaluation.status = "Developing"

    elif level == "demonstrated":
        evaluation.score = min(evaluation.score, 89)

        if evaluation.score >= 70:
            evaluation.status = "Strong"
        elif evaluation.score >= 50:
            evaluation.status = "Developing"
        else:
            evaluation.status = "Weak"

    elif level == "strong demonstrated":
        evaluation.score = min(max(evaluation.score, 80), 100)
        evaluation.status = "Strong"

    else:
        evaluation.score = 0
        evaluation.status = "Missing"
        evaluation.evidence_level = "None"
        evaluation.evidence = "None"
        evaluation.reason = (
            "No reliable evidence level was returned, so the skill was "
            "treated conservatively as unsupported."
        )

    return evaluation


# ============================================================
# EVIDENCE-BASED SKILL ANALYSIS
# ============================================================

def analyze_skills_with_gemini(
    name,
    career,
    skills,
    required_skills,
    resume_text=None,
):
    """Evaluate the student's profile using evidence-only rules."""

    required_text = ", ".join(required_skills)

    manual_skills = (
        skills.strip()
        if skills and skills.strip()
        else "Not provided"
    )

    resume_context = (
        resume_text[:25000]
        if resume_text
        else "No resume was uploaded or no readable resume text was extracted."
    )

    prompt = f"""
You are CareerPilot AI, an evidence-based career skill assessment system.

TARGET CAREER:
{career}

STUDENT NAME:
{name.strip() if name and name.strip() else "Student"}

STUDENT-ENTERED SKILLS:
{manual_skills}

RESUME CONTENT:
{resume_context}

REQUIRED SKILLS:
{required_text}

============================================================
STRICT EVIDENCE POLICY
============================================================

Evaluate ONLY information explicitly supplied in:
1. Student-entered skills
2. Resume content

Valid evidence includes:
- A skill explicitly listed
- A project that clearly uses the skill
- Internship/work experience that clearly uses the skill
- A certification/course explicitly connected to the skill
- A clearly described technical task using the skill

DO NOT infer a skill from:
- The student's degree
- Being a CSE/CS student
- The student's academic year
- The student's college
- A related skill
- A common university subject
- A career aspiration
- A vague statement
- General assumptions about students

VERY IMPORTANT:
The resume may contain outdated academic information.
Do NOT use academic year as evidence for technical proficiency.
Do NOT say that a student knows DSA, APIs, Linux, testing, frameworks,
or any other technical skill merely because they study Computer Science.

============================================================
EVIDENCE LEVELS
============================================================

Use exactly one:

None:
No explicit evidence exists.

Mentioned:
The skill is explicitly listed or briefly mentioned, but there is
little/no evidence of actual usage.

Demonstrated:
The supplied information shows actual use through a project,
internship, work experience, course work with concrete usage,
or another clear technical activity.

Strong Demonstrated:
The supplied information shows substantial or repeated use with
strong supporting evidence.

============================================================
SCORING RULES
============================================================

None:
Score MUST be 0 and status MUST be Missing.

Mentioned:
Score should normally be 30-50.
NEVER score above 50 based only on a keyword/listing.

Demonstrated:
Score may be 50-89 depending on evidence.

Strong Demonstrated:
Score may be 80-100.

A keyword alone is NOT proof of proficiency.

Do not invent projects, internships, certifications, work experience,
technical tasks, proficiency levels, or achievements.

For every skill provide:
- skill
- score
- status
- evidence_level
- evidence
- reason

If no evidence exists:
evidence_level MUST be None
evidence MUST be None
score MUST be 0

============================================================
OVERALL MATCH
============================================================

overall_match must reflect the evaluated skill scores.
Do not increase it because the student is a CSE student.
Do not increase it because the student is interested in the career.

missing_skills MUST contain every skill that is Missing, Weak,
or below 50.

The summary must be factual and evidence-based.

Return ONLY the requested structured JSON.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SkillAnalysisResult,
                temperature=0.1,
            ),
        )

        if not response.text:
            raise ValueError("Gemini returned an empty skill-analysis response.")

        result = SkillAnalysisResult.model_validate_json(response.text)

        # Apply deterministic evidence guardrails.
        result.evaluations = [
            normalize_evaluation(item)
            for item in result.evaluations
        ]

        # Make sure every required skill is represented.
        evaluation_map = {
            item.skill.strip().lower(): item
            for item in result.evaluations
            if item.skill.strip()
        }

        final_evaluations = []

        for required_skill in required_skills:
            item = evaluation_map.get(required_skill.lower())

            if item is None:
                item = SkillEvaluation(
                    skill=required_skill,
                    score=0,
                    status="Missing",
                    evidence_level="None",
                    evidence="None",
                    reason="No explicit evidence was found in the supplied information.",
                )

            final_evaluations.append(item)

        result.evaluations = final_evaluations

        # Calculate the overall score ourselves.
        if result.evaluations:
            result.overall_match = round(
                sum(item.score for item in result.evaluations)
                / len(result.evaluations)
            )
        else:
            result.overall_match = 0

        # Calculate missing/weak skills ourselves.
        result.missing_skills = [
            item.skill
            for item in result.evaluations
            if item.status == "Missing"
            or item.status == "Weak"
            or item.score < 50
        ]

        return result

    except Exception as e:
        if is_quota_error(e):
            st.warning(
                "Gemini API quota is exhausted. Skill Analysis cannot generate a new "
                "AI result until quota is available again."
            )
        else:
            st.error(f"Gemini skill analysis failed: {e}")
        return None


# ============================================================
# DETAILED AI CAREER ANALYSIS
# ============================================================

def generate_ai_career_analysis(
    name,
    career,
    skills,
    evaluations,
    missing_skills,
    resume_text=None,
):
    """Generate an evidence-based detailed career report."""

    evaluation_text = "\n".join(
        [
            (
                f"- {item.skill}: {item.score}/100, "
                f"status={item.status}, "
                f"evidence_level={item.evidence_level}, "
                f"evidence={item.evidence}, "
                f"reason={item.reason}"
            )
            for item in evaluations
        ]
    )

    missing_text = (
        ", ".join(missing_skills)
        if missing_skills
        else "None"
    )

    resume_context = (
        resume_text[:25000]
        if resume_text
        else "No readable resume content was provided."
    )

    prompt = f"""
You are CareerPilot AI, a professional evidence-based career guidance assistant.

STUDENT NAME:
{name.strip() if name and name.strip() else "Student"}

TARGET CAREER:
{career}

CURRENTLY ENTERED SKILLS:
{skills if skills and skills.strip() else "Not manually provided"}

RESUME CONTENT:
{resume_context}

SKILL EVALUATION:
{evaluation_text}

MISSING / WEAK SKILLS:
{missing_text}

STRICT RULES:
1. Use ONLY supplied information and the skill evaluation.
2. Do not invent projects, internships, certifications, jobs,
   achievements, or technical experience.
3. Do not infer technical knowledge from degree, branch, college,
   or academic year.
4. Do not treat an outdated academic year in the resume as current fact.
5. Do not call a skill a strength unless the evaluation contains evidence.
6. If evidence is missing, say evidence is missing.
7. Recommendations may describe what the student SHOULD learn next,
   but must not describe those recommendations as completed work.
8. Keep the analysis specific to the selected career.
9. Give realistic advice for a college student.

Return:
1. Strengths
2. Skill Gaps
3. Priority Skills to Learn
4. Recommended Next Steps
5. Career Readiness Advice

Keep every statement factual and evidence-based.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=CareerAnalysisResult,
                temperature=0.2,
            ),
        )

        if not response.text:
            raise ValueError("Gemini returned an empty career-analysis response.")

        return CareerAnalysisResult.model_validate_json(response.text)

    except Exception as e:
        if is_quota_error(e):
            st.warning(
                "Gemini API quota is exhausted. Detailed career analysis will be "
                "available after the quota resets."
            )
        else:
            st.error(f"Gemini career analysis failed: {e}")
        return None


# ============================================================
# INTERVIEW PREPARATION
# ============================================================

def is_quota_error(error):
    text = str(error).upper()
    return "429" in text or "RESOURCE_EXHAUSTED" in text or "QUOTA" in text


def get_builtin_interview_questions(career):
    """
    Clearly labelled built-in practice questions.
    These are NOT presented as Gemini-generated content.
    They are used only when Gemini is unavailable.
    """
    career_lower = career.lower()

    if "ui/ux" in career_lower or "ux" in career_lower or "ui" in career_lower:
        questions = [
            ("What is the difference between UI design and UX design?", "Fundamentals", "Easy"),
            ("Explain your typical UI/UX design process from user research to final design.", "Process", "Medium"),
            ("What is user research and why is it important?", "User Research", "Medium"),
            ("What is a wireframe, and when would you use one?", "Wireframing", "Easy"),
            ("What is the difference between a wireframe, mockup, and prototype?", "Prototyping", "Medium"),
            ("How would you conduct usability testing for a new interface?", "Usability", "Medium"),
            ("How would you design a responsive interface for mobile, tablet, and desktop?", "Responsive Design", "Medium"),
            ("What accessibility principles should a UI/UX developer consider?", "Accessibility", "Medium"),
            ("How do you handle conflicting feedback from users and stakeholders?", "Problem Solving", "Hard"),
            ("Which UI/UX design tools have you used, and how did you use them in a project?", "Tools & Projects", "Medium"),
        ]
    elif "cloud" in career_lower:
        questions = [
            ("What is cloud computing?", "Fundamentals", "Easy"),
            ("Explain the difference between IaaS, PaaS, and SaaS.", "Cloud Fundamentals", "Medium"),
            ("What is virtualization and why is it useful in cloud computing?", "Infrastructure", "Medium"),
            ("What is the difference between a public, private, and hybrid cloud?", "Cloud Architecture", "Medium"),
            ("What is a VPC and why is it used?", "Networking", "Medium"),
            ("What is load balancing?", "Scalability", "Medium"),
            ("What is auto-scaling and when would you use it?", "Scalability", "Medium"),
            ("What is the difference between a container and a virtual machine?", "Containers", "Medium"),
            ("How would you secure a cloud-hosted application?", "Security", "Hard"),
            ("Describe a cloud architecture you would design for a scalable web application.", "Architecture", "Hard"),
        ]
    elif "data analyst" in career_lower or "data analytics" in career_lower:
        questions = [
            ("What is the difference between data cleaning and data transformation?", "Data Fundamentals", "Easy"),
            ("How would you handle missing values in a dataset?", "Data Cleaning", "Medium"),
            ("What is the difference between INNER JOIN and LEFT JOIN in SQL?", "SQL", "Medium"),
            ("How would you find duplicate records in SQL?", "SQL", "Easy"),
            ("What is the difference between correlation and causation?", "Statistics", "Medium"),
            ("How would you choose an appropriate chart for a business problem?", "Visualization", "Medium"),
            ("How would you explain a data insight to a non-technical stakeholder?", "Communication", "Medium"),
            ("What steps would you follow when starting a new analytics project?", "Problem Solving", "Medium"),
            ("Tell me about a data project you have worked on and the result you achieved.", "Projects", "Medium"),
            ("How would you validate that your analysis is producing reliable results?", "Data Quality", "Hard"),
        ]
    elif "software" in career_lower or "developer" in career_lower or "engineer" in career_lower:
        questions = [
            ("Explain the difference between a class and an object.", "OOP", "Easy"),
            ("What is the purpose of encapsulation in object-oriented programming?", "OOP", "Medium"),
            ("What is the difference between an array and a linked list?", "Data Structures", "Medium"),
            ("Explain the difference between a stack and a queue.", "Data Structures", "Easy"),
            ("What is an API and why is it useful in software development?", "Backend", "Medium"),
            ("What is the difference between GET and POST in HTTP?", "Web Development", "Easy"),
            ("How would you debug a feature that works locally but fails in production?", "Debugging", "Hard"),
            ("What is version control and why is Git useful?", "Development Tools", "Easy"),
            ("Describe a software project you built and the main technical challenge you faced.", "Projects", "Medium"),
            ("How would you design a backend service that needs to handle many concurrent users?", "System Design", "Hard"),
        ]
    else:
        questions = [
            (f"What does a professional working as a {career} typically do?", "Career Fundamentals", "Easy"),
            (f"What are the most important technical skills for a {career}?", "Technical Skills", "Easy"),
            (f"How would you approach learning a new technology required for {career}?", "Learning", "Medium"),
            ("Describe a technical project you have worked on and your contribution to it.", "Projects", "Medium"),
            ("How do you debug a problem when your first approach does not work?", "Problem Solving", "Medium"),
            ("How do you keep your technical knowledge up to date?", "Professional Development", "Easy"),
            ("Describe a time when you had to learn something quickly.", "Behavioral", "Medium"),
            ("How would you explain a technical concept to a non-technical person?", "Communication", "Medium"),
            (f"What would you do if you were asked to build a {career} solution with unclear requirements?", "Problem Solving", "Hard"),
            ("What would you improve in your strongest technical project if you had more time?", "Projects", "Medium"),
        ]

    return InterviewPrepResult(
        questions=[
            InterviewQuestion(question=q, category=c, difficulty=d)
            for q, c, d in questions
        ]
    )


def generate_interview_questions_with_gemini(career, skill_gaps=None, skills=""):
    """Generate interview questions with Gemini; use an explicitly labelled fallback if unavailable."""
    gaps = ", ".join(skill_gaps or []) or "None identified"
    entered = skills.strip() if skills and skills.strip() else "Not provided"

    prompt = f"""
You are the Interview Preparation Agent for CareerPilot AI.

TARGET CAREER:
{career}

STUDENT-ENTERED SKILLS:
{entered}

IDENTIFIED SKILL GAPS:
{gaps}

Create exactly 10 interview questions specifically for the target career.

Rules:
1. Questions must be relevant to the exact career.
2. Mix technical, practical/scenario, project, and behavioral questions.
3. If the career is UI/UX Developer, include UI/UX-specific questions such as
   design process, user research, wireframing/prototyping, usability, responsive
   design, accessibility, and design tools when appropriate.
4. Use supplied skill gaps to make some questions targeted to weaknesses.
5. Do not invent the student's experience.
6. Do not provide answers; return questions only.
7. Return exactly 10 questions with category and difficulty.

Return ONLY the requested structured JSON.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=InterviewPrepResult,
                temperature=0.2,
            ),
        )

        if not response.text:
            raise ValueError("Gemini returned an empty interview-preparation response.")

        result = InterviewPrepResult.model_validate_json(response.text)

        if len(result.questions) != 10:
            raise ValueError("Gemini did not return exactly 10 interview questions.")

        return result, "Gemini AI"

    except Exception as e:
        if is_quota_error(e):
            st.warning(
                "Gemini API quota is currently exhausted. "
                "The questions below are from CareerPilot AI's built-in practice "
                "question bank and are NOT presented as Gemini-generated content."
            )
            return get_builtin_interview_questions(career), "Built-in Practice Question Bank"

        st.error(f"Gemini interview preparation failed: {e}")
        return None, None


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background-color: #0f172a;
        color: white;
    }

    section[data-testid="stSidebar"] {
        background-color: #162447;
    }

    .card {
        background: #162447;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
    }

    h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }

    .evidence-box {
        background: #172554;
        border-left: 4px solid #4DA8FF;
        padding: 12px;
        border-radius: 8px;
        margin-top: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div style="
        background: linear-gradient(90deg,#162447,#1F4068);
        padding:25px;
        border-radius:15px;
        text-align:center;
        color:white;
    ">
        <h1>🚀 CareerPilot AI</h1>
        <h3>AI-Powered Career Guidance Platform</h3>
        <p>
            Analyze Skills • Learning Paths • Resume Review • Interview Preparation
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🚀 CareerPilot AI")
st.sidebar.markdown("### 👤 Krushnal Patil")
st.sidebar.markdown("Career Development Assistant")

page = st.sidebar.radio(
    "Navigation",
    [
        "Resume Review",
        "Skill Analysis",
        "Learning Path",
        "Interview Prep",
        "Dashboard",
    ],
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    st.title("🚀 CareerPilot AI Dashboard")

    skill_result = st.session_state.get("skill_analysis")

    if skill_result:

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                f"""
                <div class='card'>
                    <h3>Career Goal</h3>
                    <h2>{st.session_state["career"]}</h2>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
                <div class='card'>
                    <h3>Evidence-Based Match</h3>
                    <h2>{skill_result.overall_match}%</h2>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                f"""
                <div class='card'>
                    <h3>Skill Gaps</h3>
                    <h2>{len(skill_result.missing_skills)}</h2>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.subheader("🎯 Career Progress Score")

        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=skill_result.overall_match,
                title={"text": "Career Match"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#4DA8FF"},
                },
            )
        )

        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
        st.progress(skill_result.overall_match)

        if skill_result.overall_match >= 80:
            st.success("⭐ Strong evidence-based career alignment")
        elif skill_result.overall_match >= 60:
            st.info("📈 Good foundation. Continue improving the identified gaps.")
        else:
            st.warning("🎯 More skill development is recommended.")

        if st.session_state.get("resume_text"):
            st.success("📄 Reviewed resume evidence was included in the analysis.")

    else:
        st.info(
            "Run Skill Analysis first to generate your personalized dashboard."
        )


# ============================================================
# SKILL ANALYSIS
# ============================================================

elif page == "Skill Analysis":

    st.title("🔍 Skill Analysis")

    st.info(
        "Skill Analysis evaluates your skills against the selected career. "
        "Upload and review your resume first from the Resume Review section."
    )

    name = st.text_input(
        "Enter Your Name",
        value=st.session_state.get("student_name", ""),
    )

    career = st.text_input(
        "🎯 Enter Your Career Goal",
        value=st.session_state.get("career", ""),
        placeholder="Example: Backend Developer, Java Developer, Cloud Engineer",
        help="Enter any career goal. CareerPilot AI will generate the required skills dynamically.",
    )

    skills = st.text_area(
        "Enter Your Skills",
        value=st.session_state.get("student_skills", ""),
        placeholder="Example: Python, SQL, Git, Excel, Power BI",
        help="Enter skills you actually know or have used.",
    )

    if st.session_state.get("resume_text"):
        resume_name = st.session_state.get("resume_name") or "Uploaded resume"
        st.success(
            f"📄 Resume evidence available: {resume_name}. "
            "Skill Analysis will use the extracted resume content."
        )
    else:
        st.info(
            "📄 No resume evidence is currently available. "
            "You can still analyze manually entered skills."
        )

    st.markdown("---")

    if st.button(
        "🤖 Analyze Skills with Gemini AI",
        type="primary",
    ):

        resume_text = st.session_state.get("resume_text")

        if not career.strip():
            st.warning("Please enter your career goal.")

        elif not skills.strip() and not resume_text:
            st.warning(
                "Please enter your skills or complete Resume Review with a readable "
                "resume before starting the analysis."
            )

        else:

            st.session_state["career"] = career.strip()
            st.session_state["student_name"] = name
            st.session_state["student_skills"] = skills
            st.session_state["analyzed"] = False
            st.session_state["skill_analysis"] = None
            st.session_state["career_analysis"] = None

            with st.spinner(
                "🧠 Gemini AI is identifying the skills required for your career..."
            ):
                required_skills = generate_required_skills_with_gemini(
                    career.strip()
                )

            if not required_skills:
                st.error(
                    "Career requirements could not be generated. "
                    "Please try the analysis again."
                )

            else:

                st.session_state["required_skills"] = required_skills

                with st.expander("🎯 Career Skills Identified by AI"):
                    for skill in required_skills:
                        st.write(f"• {skill}")

                with st.spinner(
                    "🧠 Gemini AI is performing evidence-based skill analysis..."
                ):
                    result = analyze_skills_with_gemini(
                        name,
                        career.strip(),
                        skills,
                        required_skills,
                        resume_text,
                    )

                if result:
                    st.session_state["skill_analysis"] = result
                    st.session_state["analyzed"] = True

                    st.success(
                        "AI Skill Analysis Completed Successfully!"
                    )


    # ========================================================
    # DISPLAY AI SKILL ANALYSIS
    # ========================================================

    if st.session_state["skill_analysis"]:

        result = st.session_state["skill_analysis"]

        st.markdown("---")
        st.subheader("📊 AI Skill Analytics")

        chart_data = pd.DataFrame(
            {
                "Skill": [item.skill for item in result.evaluations],
                "Score": [item.score for item in result.evaluations],
            }
        )

        st.bar_chart(chart_data.set_index("Skill"))

        st.subheader("🔍 Skill-by-Skill Evaluation")

        for evaluation in result.evaluations:

            score = evaluation.score

            if score >= 80:
                status_icon = "🟢"
            elif score >= 60:
                status_icon = "🟡"
            elif score >= 30:
                status_icon = "🟠"
            else:
                status_icon = "🔴"

            st.markdown(
                f"""
                ### {status_icon} {evaluation.skill}

                **AI Score:** {score}/100

                **Status:** {evaluation.status}

                **Evidence Level:** {evaluation.evidence_level}

                **Evidence:** {evaluation.evidence}

                **Reason:** {evaluation.reason}
                """
            )

            st.progress(score)

        st.subheader("⚠️ Missing / Weak Skills")

        if result.missing_skills:
            for skill in result.missing_skills:
                st.write(f"• {skill}")
        else:
            st.success(
                "🎉 No major missing or weak skills identified."
            )

        st.subheader("📝 AI Summary")
        st.info(result.summary)

        # ====================================================
        # CAREER REPORT
        # ====================================================

        st.markdown("---")
        st.subheader("📋 Career Report")

        st.info(
            f"Career Goal: {st.session_state['career']}"
        )

        st.info(
            f"Evidence-Based Skill Match: {result.overall_match}%"
        )

        st.progress(result.overall_match)

        report_text = f"""
CAREERPILOT AI — CAREER REPORT

Student:
{st.session_state['student_name'] if st.session_state['student_name'].strip() else 'Student'}

Career Goal:
{st.session_state['career']}

Evidence-Based Skill Match:
{result.overall_match}%

SKILL EVALUATION:

"""

        for evaluation in result.evaluations:

            report_text += (
                f"{evaluation.skill}: "
                f"{evaluation.score}/100 - "
                f"{evaluation.status}\n"
            )

            report_text += (
                f"Evidence Level: {evaluation.evidence_level}\n"
            )

            report_text += (
                f"Evidence: {evaluation.evidence}\n"
            )

            report_text += (
                f"Reason: {evaluation.reason}\n\n"
            )

        report_text += "MISSING / WEAK SKILLS:\n"

        if result.missing_skills:
            for skill in result.missing_skills:
                report_text += f"- {skill}\n"
        else:
            report_text += "None\n"

        report_text += "\nAI SUMMARY:\n"
        report_text += result.summary

        if st.session_state.get("resume_text"):
            report_text += (
                "\n\nNOTE:\n"
                "Resume content was included in the AI analysis. "
                "Technical skills were not inferred from academic year."
            )

        st.download_button(
            "📥 Download Career Report",
            report_text,
            file_name="career_report.txt",
            mime="text/plain",
        )

        # ====================================================
        # GEMINI CAREER ANALYSIS
        # ====================================================

        st.markdown("---")
        st.subheader("🤖 AI Career Analysis")

        if st.button(
            "🧠 Generate Detailed AI Analysis"
        ):

            with st.spinner(
                "CareerPilot AI is preparing your detailed career report..."
            ):

                career_result = generate_ai_career_analysis(
                    st.session_state["student_name"],
                    st.session_state["career"],
                    st.session_state["student_skills"],
                    result.evaluations,
                    result.missing_skills,
                    st.session_state.get("resume_text"),
                )

            if career_result:
                st.session_state["career_analysis"] = career_result

        if st.session_state["career_analysis"]:

            ai_result = st.session_state["career_analysis"]

            st.markdown("### 🧠 Gemini AI Analysis")

            st.markdown(
                f"""
                **Student Name:** {st.session_state['student_name'] if st.session_state['student_name'].strip() else 'Student'}

                **Target Career:** {st.session_state['career']}
                """
            )

            if st.session_state.get("resume_text"):
                st.success(
                    "📄 Detailed career analysis also considered the reviewed resume evidence."
                )

            st.markdown("---")

            st.markdown("## 1. Strengths")

            for item in ai_result.strengths:
                st.write(f"• {item}")

            st.markdown("## 2. Skill Gaps")

            for item in ai_result.skill_gaps:
                st.write(f"• {item}")

            st.markdown("## 3. Priority Skills to Learn")

            for item in ai_result.priority_skills:
                st.write(f"• {item}")

            st.markdown("## 4. Recommended Next Steps")

            for index, item in enumerate(
                ai_result.recommended_steps,
                start=1,
            ):
                st.write(f"{index}. {item}")

            st.markdown("## 5. Career Readiness Advice")

            for item in ai_result.career_readiness_advice:
                st.write(f"• {item}")


# ============================================================
# LEARNING PATH
# ============================================================

elif page == "Learning Path":

    career = st.session_state.get("career")

    st.header("📚 Learning Path")

    if not career:
        st.info(
            "Set a target career in Skill Analysis first so CareerPilot AI knows your target career."
        )

    else:

        st.write(
            f"Personalized learning direction for: **{career}**"
        )

        skill_result = st.session_state.get("skill_analysis")

        if skill_result and skill_result.missing_skills:

            st.subheader("🎯 Your Priority Skill Gaps")

            for skill in skill_result.missing_skills:
                st.write(f"• Learn or strengthen **{skill}**")

        else:
            st.info(
                "Complete Skill Analysis to generate evidence-based learning priorities."
            )

        st.markdown("---")

        st.subheader("🛠️ Recommended Career-Building Sequence")

        roadmap = [
            f"Understand the fundamentals of {career}",
            "Strengthen the identified missing or weak skills",
            "Build 2–3 practical projects related to the target career",
            "Document projects clearly on GitHub",
            "Practice role-specific interview questions",
            "Build a career-focused resume",
            "Apply for relevant internships and entry-level opportunities",
        ]

        for index, step in enumerate(roadmap, start=1):
            st.write(f"### {index}. {step}")


# ============================================================
# RESUME REVIEW
# ============================================================

elif page == "Resume Review":

    st.header("📄 Resume Review")

    st.write(
        "Upload your resume here. CareerPilot AI will extract the readable text "
        "and review only the evidence contained in that resume."
    )

    resume = st.file_uploader(
        "Upload Resume",
        type=["pdf", "docx"],
        help="Upload a text-based PDF or DOCX resume.",
    )

    if resume:

        resume_signature = f"{resume.name}:{getattr(resume, 'size', 0)}"

        if resume_signature != st.session_state.get("resume_signature"):

            extracted_text = extract_resume_text(resume)

            if extracted_text:
                st.session_state["resume_text"] = extracted_text
                st.session_state["resume_name"] = resume.name
                st.session_state["resume_signature"] = resume_signature

                # Resume evidence changed, so previous AI results may no longer
                # represent the current resume.
                st.session_state["resume_analysis"] = None
                st.session_state["skill_analysis"] = None
                st.session_state["career_analysis"] = None
                st.session_state["analyzed"] = False

        if st.session_state.get("resume_text"):

            st.success(
                f"✅ Resume uploaded successfully: "
                f"{st.session_state.get('resume_name', resume.name)}"
            )

            with st.expander("🔎 View extracted resume text"):
                st.text_area(
                    "Resume text used by Gemini",
                    st.session_state["resume_text"],
                    height=350,
                    disabled=True,
                )

    elif st.session_state.get("resume_text"):

        st.info(
            f"📄 Previously uploaded resume is available for this session: "
            f"{st.session_state.get('resume_name', 'Resume')}"
        )

        with st.expander("🔎 View extracted resume text"):
            st.text_area(
                "Resume text used by Gemini",
                st.session_state["resume_text"],
                height=350,
                disabled=True,
            )

    else:

        st.info(
            "Upload a PDF or DOCX resume to begin the review."
        )

    if st.session_state.get("resume_text"):

        st.markdown("---")

        review_career = st.text_input(
            "🎯 Target Career for Resume Review (Optional)",
            value=st.session_state.get("career", ""),
            placeholder="Example: Data Analyst, Software Developer, Cloud Engineer",
            help=(
                "If provided, the review will also consider how clearly the "
                "resume supports this target career."
            ),
        )

        if st.button(
            "🧠 Analyze Resume with Gemini AI",
            type="primary",
        ):

            with st.spinner(
                "🧠 Gemini AI is reviewing your resume using evidence-only rules..."
            ):

                resume_result = analyze_resume_with_gemini(
                    st.session_state["resume_text"],
                    review_career,
                )

            if resume_result:
                st.session_state["resume_analysis"] = resume_result

                if review_career.strip():
                    st.session_state["career"] = review_career.strip()

                st.success(
                    "✅ Resume analysis completed successfully."
                )

    if st.session_state.get("resume_analysis"):

        resume_result = st.session_state["resume_analysis"]

        st.markdown("---")
        st.subheader("📊 Resume Readiness Score")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Overall Resume Score",
                f"{resume_result.overall_score}/100",
            )

        with col2:
            target = (
                st.session_state.get("career")
                if st.session_state.get("career")
                else "General resume review"
            )
            st.metric(
                "Review Context",
                target,
            )

        st.progress(resume_result.overall_score)

        st.subheader("📝 AI Resume Summary")
        st.info(resume_result.summary)

        st.subheader("✅ Resume Strengths")
        if resume_result.strengths:
            for item in resume_result.strengths:
                st.write(f"• {item}")
        else:
            st.write("No specific strengths were detected in the supplied text.")

        st.subheader("⚠️ Issues Detected")
        if resume_result.issues:
            for item in resume_result.issues:
                st.write(f"• {item}")
        else:
            st.success("No major issues were detected in the supplied text.")

        st.subheader("🧰 Skills Explicitly Detected")
        if resume_result.detected_skills:
            for item in resume_result.detected_skills:
                st.write(f"• {item}")
        else:
            st.write("No technical/professional skills were explicitly detected.")

        st.subheader("📌 Missing / Unclear Information")
        if resume_result.missing_or_unclear_sections:
            for item in resume_result.missing_or_unclear_sections:
                st.write(f"• {item}")
        else:
            st.success("No major missing or unclear sections were detected.")

        st.subheader("🚀 Recommended Improvements")
        for index, item in enumerate(
            resume_result.recommendations,
            start=1,
        ):
            st.write(f"{index}. {item}")

        resume_report = f"""
CAREERPILOT AI — RESUME REVIEW REPORT

Resume:
{st.session_state.get('resume_name', 'Uploaded Resume')}

Target Career:
{st.session_state.get('career') or 'Not specified'}

Overall Resume Score:
{resume_result.overall_score}/100

SUMMARY:
{resume_result.summary}

STRENGTHS:
"""

        for item in resume_result.strengths:
            resume_report += f"- {item}\n"

        resume_report += "\nISSUES:\n"
        for item in resume_result.issues:
            resume_report += f"- {item}\n"

        resume_report += "\nEXPLICITLY DETECTED SKILLS:\n"
        for item in resume_result.detected_skills:
            resume_report += f"- {item}\n"

        resume_report += "\nMISSING / UNCLEAR INFORMATION:\n"
        for item in resume_result.missing_or_unclear_sections:
            resume_report += f"- {item}\n"

        resume_report += "\nRECOMMENDATIONS:\n"
        for index, item in enumerate(resume_result.recommendations, start=1):
            resume_report += f"{index}. {item}\n"

        st.download_button(
            "📥 Download Resume Review Report",
            resume_report,
            file_name="resume_review_report.txt",
            mime="text/plain",
        )

        st.markdown("---")
        st.success(
            "📌 This reviewed resume can now be used as evidence in Skill Analysis. "
            "Go to Skill Analysis and enter your target career."
        )


# ============================================================
# INTERVIEW PREPARATION
# ============================================================

elif page == "Interview Prep":

    st.header("🎤 Interview Preparation")

    career = st.session_state.get("career", "").strip()
    skill_result = st.session_state.get("skill_analysis")
    skill_gaps = skill_result.missing_skills if skill_result else []
    current_skills = st.session_state.get("student_skills", "")

    if not career:
        st.info(
            "Set a target career in Skill Analysis first to personalize interview preparation."
        )
    else:
        st.write(f"Interview preparation for: **{career}**")

        if skill_gaps:
            st.info(
                "Gemini can personalize questions using your selected career and "
                "the skill gaps identified by Skill Analysis."
            )
        else:
            st.info(
                "Questions will be tailored to your selected career. "
                "Complete Skill Analysis first if you want questions targeted to skill gaps."
            )

        if st.button(
            "🎤 Generate Interview Questions with Gemini AI",
            type="primary",
        ):
            with st.spinner(
                "🧠 Gemini AI is generating role-specific interview questions..."
            ):
                interview_result, interview_source = (
                    generate_interview_questions_with_gemini(
                        career,
                        skill_gaps,
                        current_skills,
                    )
                )

            if interview_result:
                st.session_state["interview_questions"] = interview_result
                st.session_state["interview_source"] = interview_source

                if interview_source == "Gemini AI":
                    st.success("✅ Interview questions generated by Gemini AI.")
                else:
                    st.info(
                        "ℹ️ Built-in practice questions are being shown because Gemini "
                        "is temporarily unavailable. These are NOT AI-generated."
                    )

        interview_result = st.session_state.get("interview_questions")
        interview_source = st.session_state.get("interview_source")

        if interview_result:
            st.markdown("---")

            if interview_source == "Gemini AI":
                st.subheader("🤖 AI-Generated Interview Questions")
                st.caption(
                    "These questions were generated by Gemini from your selected career "
                    "and available profile evidence."
                )
            else:
                st.subheader("📚 Built-in Practice Questions")
                st.warning(
                    "These are built-in practice questions, NOT Gemini-generated. "
                    "They are shown only because the Gemini service is temporarily unavailable."
                )

            for index, item in enumerate(interview_result.questions, start=1):
                with st.expander(f"{index}. {item.question}"):
                    st.write(f"**Category:** {item.category}")
                    st.write(f"**Difficulty:** {item.difficulty}")

            questions_text = "CAREERPILOT AI — INTERVIEW QUESTIONS\n\n"
            questions_text += f"Target Career: {career}\n"
            questions_text += f"Source: {interview_source}\n\n"

            for index, item in enumerate(interview_result.questions, start=1):
                questions_text += (
                    f"{index}. {item.question}\n"
                    f"Category: {item.category}\n"
                    f"Difficulty: {item.difficulty}\n\n"
                )

            st.download_button(
                "📥 Download Interview Questions",
                questions_text,
                file_name="interview_questions.txt",
                mime="text/plain",
            )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <center>
        <h3>CareerPilot AI</h3>
        <p>AI Powered Career Guidance Platform</p>
    </center>
    """,
    unsafe_allow_html=True,
)