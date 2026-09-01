import pandas as pd
import plotly.express as px
import streamlit as st

from agents import (
    business_agent,
    career_agent,
    interview_agent,
    learning_agent,
    orchestrator,
    recruitment_agent,
    resume_agent,
    screening_agent,
    skill_agent,
)
from database import (
    create_conversation,
    get_analytics,
    init_db,
    save_interview_result,
    save_message,
    save_resume_analysis,
)
from resume_parser import extract_text_from_upload
from utils import estimate_score, make_download_name, safe_text


st.set_page_config(page_title="Ardhanarishwar", page_icon="🤖", layout="wide")
init_db()


def init_state():
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("conversation_id", create_conversation())
    st.session_state.setdefault("last_response", "")
    st.session_state.setdefault("interview_history", [])
    st.session_state.setdefault("interview_scores", [])
    st.session_state.setdefault("skill_gap_score", 0)
    st.session_state.setdefault("learning_progress", 0)


def render_sidebar():
    st.sidebar.title("ARDHANARISHWAR")
    return st.sidebar.radio(
        "Navigation",
        [
            "Home",
            "AI Assistant",
            "Candidate",
            "Business",
            "Resume Analyzer",
            "Interview Preparation",
            "Skill Gap",
            "Learning",
            "Career Roadmap",
            "Candidate Screening",
            "Analytics",
        ],
        label_visibility="collapsed",
    )


def home_page():
    st.title("Ardhanarishwar")
    st.subheader("All-in-One AI Solution")
    st.write("Your AI assistant for career growth, recruitment and business solutions.")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Candidate")
        st.info("Career • Resume • Jobs • Interview • Skills • Learning")
    with col2:
        st.markdown("### Business")
        st.success("Recruitment • Hiring • HR • Workforce • Business")
    if st.button("Start AI Conversation"):
        st.session_state.page_hint = "AI Assistant"
        st.rerun()


def ai_assistant_page():
    st.header("AI Assistant")
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("Clear conversation"):
            st.session_state.messages = []
            st.session_state.last_response = ""
    with col2:
        if st.button("New conversation"):
            st.session_state.messages = []
            st.session_state.conversation_id = create_conversation()
    uploaded = st.file_uploader("Attach PDF, DOCX, or TXT", type=["pdf", "docx", "txt"])
    file_context = ""
    if uploaded:
        try:
            file_context = extract_text_from_upload(uploaded)
            st.caption(f"Loaded {len(file_context)} characters from {uploaded.name}")
        except ValueError as exc:
            st.error(str(exc))

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask a career, resume, hiring, or business question")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        save_message(st.session_state.conversation_id, "user", prompt)
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            result = orchestrator(prompt, file_context)
            st.caption(f"Intent: {result['intent']} | AI Agent: {result['agent']}")
            for step in result["steps"]:
                st.status(step, state="complete")
            st.markdown(result["response"])
            st.session_state.last_response = result["response"]
            st.session_state.messages.append({"role": "assistant", "content": result["response"]})
            save_message(st.session_state.conversation_id, "assistant", result["response"])

    if st.session_state.last_response:
        st.download_button(
            "Download response",
            st.session_state.last_response,
            file_name=make_download_name("ai_response"),
        )


def candidate_page():
    st.header("Candidate Mode")
    query = st.text_area("Ask for career guidance, job planning, resume advice, or professional growth.")
    if st.button("Get Candidate Guidance"):
        if not safe_text(query):
            st.warning("Please enter your question.")
        else:
            st.markdown(career_agent(query))


def business_page():
    st.header("Business Mode")
    tab1, tab2 = st.tabs(["Business Assistant", "Job Description Generator"])
    with tab1:
        query = st.text_area("Ask about hiring, HR, workforce planning, training, or business advice.")
        if st.button("Get Business Guidance"):
            if not safe_text(query):
                st.warning("Please enter your business question.")
            else:
                st.markdown(business_agent(query))
    with tab2:
        title = st.text_input("Job Title")
        industry = st.text_input("Company/Industry")
        experience = st.text_input("Experience")
        skills = st.text_area("Skills")
        location = st.text_input("Location")
        responsibilities = st.text_area("Responsibilities")
        if st.button("Generate Job Description"):
            prompt = f"Create a professional job description for {title} in {industry}. Experience: {experience}. Skills: {skills}. Location: {location}. Responsibilities: {responsibilities}."
            jd = recruitment_agent(prompt)
            st.markdown(jd)
            st.download_button("Download job description", jd, "job_description.md")


def resume_analyzer_page():
    st.header("Resume Analyzer")
    target_role = st.text_input("Target role", "Python Developer")
    uploaded = st.file_uploader("Upload resume", type=["pdf", "docx", "txt"])
    if st.button("Analyze Resume"):
        if not uploaded:
            st.warning("Please upload a resume.")
            return
        try:
            resume_text = extract_text_from_upload(uploaded)
        except ValueError as exc:
            st.error(str(exc))
            return
        if not resume_text:
            st.warning("No readable text found in the resume.")
            return
        prompt = f"""Analyze this resume for a {target_role} role.
Return: Resume Score /100, Strengths, Weaknesses, Missing Skills, ATS Suggestions, Formatting Suggestions, Improved Summary, Suggested Bullet Points, Recommended Skills.

Resume:
{resume_text}
"""
        with st.spinner("Analyzing resume..."):
            analysis = resume_agent(prompt)
        score = estimate_score(analysis, 75)
        st.metric("Resume Score", f"{score}/100")
        st.markdown(analysis)
        save_resume_analysis(uploaded.name, score, analysis)
        st.download_button("Download analysis", analysis, "resume_analysis.md")


def interview_page():
    st.header("Interview Preparation")
    role = st.text_input("Job role", "Python Developer")
    level = st.selectbox("Experience level", ["Fresher", "Junior", "Mid-level", "Senior"])
    interview_type = st.selectbox("Interview type", ["Technical", "HR", "Behavioral", "Mixed"])
    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

    if st.button("Generate Interview Questions"):
        prompt = f"Generate 8 {difficulty} {interview_type} interview questions for a {level} {role}."
        st.markdown(interview_agent(prompt))

    st.divider()
    st.subheader("Simple Mock Interview")
    answer = st.text_area("Your answer")
    if st.button("Submit Mock Answer"):
        if not safe_text(answer):
            st.warning("Please enter an answer.")
        else:
            prompt = f"Role: {role}. Interview type: {interview_type}. Evaluate this answer. Return Score /10, Feedback, Next Question.\n\nAnswer: {answer}"
            feedback = interview_agent(prompt)
            score = estimate_score(feedback, 8)
            st.session_state.interview_scores.append(min(score, 10))
            st.session_state.interview_history.append(feedback)
            save_interview_result(role, min(score, 10), feedback)
            st.markdown(feedback)

    if st.session_state.interview_scores:
        avg = sum(st.session_state.interview_scores) / len(st.session_state.interview_scores)
        st.metric("Overall Score", f"{avg:.1f}/10")
        st.write("Technical Skills, Communication, Confidence, and Areas to Improve are included in the feedback.")


def skill_gap_page():
    st.header("Skill Gap Analyzer")
    current = st.text_area("Current Skills")
    target = st.text_input("Target Job Role")
    experience = st.text_input("Experience")
    if st.button("Analyze Skill Gap"):
        if not current or not target:
            st.warning("Please enter current skills and target role.")
            return
        prompt = f"Current skills: {current}\nTarget role: {target}\nExperience: {experience}\nReturn Current Skills, Missing Skills, Priority, Recommended Learning, and a Skill Gap Score /100."
        result = skill_agent(prompt)
        score = estimate_score(result, 60)
        st.session_state.skill_gap_score = score
        st.metric("Skill Gap Readiness", f"{score}/100")
        st.markdown(result)
        chart = pd.DataFrame({"Area": ["Current readiness", "Gap"], "Score": [score, 100 - score]})
        st.plotly_chart(px.bar(chart, x="Area", y="Score", color="Area"), use_container_width=True)


def learning_page():
    st.header("Learning / Education")
    target = st.text_input("Target Career")
    skills = st.text_area("Current Skills")
    hours = st.number_input("Available Hours Per Day", min_value=1, max_value=12, value=2)
    deadline = st.text_input("Deadline", "90 days")
    if st.button("Create Learning Plan"):
        prompt = f"Create a learning roadmap for {target}. Current skills: {skills}. Time: {hours} hours/day. Deadline: {deadline}. Include topics, practice, projects, resources, weekly plan, and 30/60/90-day roadmap. Do not claim resources are live/current."
        result = learning_agent(prompt)
        st.session_state.learning_progress = 10
        st.markdown(result)
        st.download_button("Download learning plan", result, "learning_plan.md")


def roadmap_page():
    st.header("Career Roadmap")
    current = st.text_input("Current Position")
    target = st.text_input("Target Position")
    skills = st.text_area("Current Skills")
    if st.button("Generate Roadmap"):
        prompt = f"Generate a career roadmap from {current} to {target}. Current skills: {skills}. Include Skill Gap -> Learning -> Projects -> Resume -> Interview Preparation -> Job Applications -> Career Growth."
        roadmap = career_agent(prompt)
        st.markdown(roadmap)
        st.download_button("Download roadmap", roadmap, "career_roadmap.md")


def screening_page():
    st.header("Candidate Screening")
    jd_file = st.file_uploader("Job Description", type=["pdf", "docx", "txt"], key="jd")
    resume_file = st.file_uploader("Candidate Resume", type=["pdf", "docx", "txt"], key="candidate")
    if st.button("Screen Candidate"):
        if not jd_file or not resume_file:
            st.warning("Please upload both files.")
            return
        try:
            jd_text = extract_text_from_upload(jd_file)
            resume_text = extract_text_from_upload(resume_file)
        except ValueError as exc:
            st.error(str(exc))
            return
        prompt = f"""Evaluate this candidate only on job-related qualifications.
Do not use protected characteristics such as gender, religion, race, age, disability, caste, or similar traits.
Return Candidate Match Score, Skills Match, Experience Match, Education Match, Strengths, Missing Requirements, Recommendation.

Job Description:
{jd_text}

Resume:
{resume_text}
"""
        st.markdown(screening_agent(prompt))


def analytics_page():
    st.header("Analytics")
    data = get_analytics()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Resume score", f"{data['resume_score']}/100")
    col2.metric("Interview score", f"{data['interview_score']}/10")
    col3.metric("Skill-gap score", f"{st.session_state.skill_gap_score}/100")
    col4.metric("Learning progress", f"{st.session_state.learning_progress}%")
    business = pd.DataFrame(
        {
            "Metric": ["Candidates screened", "Average candidate score", "Hiring requirements"],
            "Value": [data["resume_count"], data["resume_score"], 3],
        }
    )
    st.plotly_chart(px.bar(business, x="Metric", y="Value", title="Business Analytics"), use_container_width=True)


init_state()
page = getattr(st.session_state, "page_hint", None) or render_sidebar()
st.session_state.page_hint = None

pages = {
    "Home": home_page,
    "AI Assistant": ai_assistant_page,
    "Candidate": candidate_page,
    "Business": business_page,
    "Resume Analyzer": resume_analyzer_page,
    "Interview Preparation": interview_page,
    "Skill Gap": skill_gap_page,
    "Learning": learning_page,
    "Career Roadmap": roadmap_page,
    "Candidate Screening": screening_page,
    "Analytics": analytics_page,
}

pages.get(page, home_page)()
