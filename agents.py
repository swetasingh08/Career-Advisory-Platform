from ai import ask_ai


CAREER_SYSTEM = "You are a practical career guidance agent. Give clear, student-friendly career advice."
RESUME_SYSTEM = "You are a resume improvement agent. Analyze resumes and provide ATS-friendly, job-focused improvements."
INTERVIEW_SYSTEM = "You are an interview coach. Ask useful questions, score answers, and give constructive feedback."
SKILL_SYSTEM = "You are a skill-gap analyst. Compare current skills with target roles and prioritize learning."
LEARNING_SYSTEM = "You are a learning planner. Create realistic learning plans, projects, and weekly schedules."
RECRUITMENT_SYSTEM = "You are a recruitment agent. Help with hiring, job descriptions, screening, and interview planning."
BUSINESS_SYSTEM = "You are a business assistant for HR, workforce planning, training, and practical business advice."
SCREENING_SYSTEM = (
    "You are a fair candidate screening agent. Evaluate only job-related qualifications. "
    "Do not use gender, religion, race, age, disability, caste, or other protected characteristics."
)


def career_agent(prompt):
    return ask_ai(prompt, CAREER_SYSTEM)


def resume_agent(prompt):
    return ask_ai(prompt, RESUME_SYSTEM)


def interview_agent(prompt):
    return ask_ai(prompt, INTERVIEW_SYSTEM)


def skill_agent(prompt):
    return ask_ai(prompt, SKILL_SYSTEM)


def learning_agent(prompt):
    return ask_ai(prompt, LEARNING_SYSTEM)


def recruitment_agent(prompt):
    return ask_ai(prompt, RECRUITMENT_SYSTEM)


def business_agent(prompt):
    return ask_ai(prompt, BUSINESS_SYSTEM)


def screening_agent(prompt):
    return ask_ai(prompt, SCREENING_SYSTEM)


def detect_intent(text):
    lowered = text.lower()
    if any(word in lowered for word in ["resume", "cv", "ats"]):
        return "Resume Improvement", ["resume"]
    if any(word in lowered for word in ["interview", "mock", "question", "feedback"]):
        return "Interview Preparation", ["interview"]
    if any(word in lowered for word in ["skill gap", "missing skill", "skills needed"]):
        return "Skill Gap Analysis", ["skill"]
    if any(word in lowered for word in ["learn", "course", "training", "roadmap", "study"]):
        return "Learning Plan", ["learning", "career"]
    if any(word in lowered for word in ["hire", "recruit", "job description", "screen", "candidate"]):
        return "Recruitment", ["recruitment"]
    if any(word in lowered for word in ["business", "workforce", "employee", "hr", "company"]):
        return "Business Advice", ["business"]
    return "General Career/Business Guidance", ["career"]


def orchestrator(user_message, context=""):
    intent, agent_keys = detect_intent(user_message + " " + context)
    agent_map = {
        "career": ("Career Agent", career_agent, "Preparing career recommendations..."),
        "resume": ("Resume Agent", resume_agent, "Analyzing resume..."),
        "interview": ("Interview Agent", interview_agent, "Preparing interview guidance..."),
        "skill": ("Skill Gap Agent", skill_agent, "Checking skill gap..."),
        "learning": ("Learning Agent", learning_agent, "Preparing learning recommendations..."),
        "recruitment": ("Recruitment Agent", recruitment_agent, "Preparing recruitment guidance..."),
        "business": ("Business Agent", business_agent, "Preparing business recommendations..."),
        "screening": ("Screening Agent", screening_agent, "Screening candidate profile..."),
    }

    prompt = f"User request:\n{user_message}\n\nAdditional context:\n{context}".strip()
    responses = []
    steps = []
    used_agents = []

    for key in agent_keys:
        name, fn, status = agent_map[key]
        steps.append(status)
        used_agents.append(name)
        responses.append(f"### {name}\n{fn(prompt)}")

    final = "\n\n".join(responses)
    return {
        "intent": intent,
        "agent": " + ".join(used_agents),
        "steps": steps,
        "response": final,
    }
