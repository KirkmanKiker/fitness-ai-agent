import os
import streamlit as st
from openai import OpenAI


# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="AI Fitness Agent",
    page_icon="🏋️",
    layout="wide"
)


# -----------------------------
# DARK ACCESSIBLE THEME
# -----------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #0b0b0f;
        color: #f5f5f5;
    }

    .block-container {
        max-width: 980px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        letter-spacing: 0.2px;
    }

    p, label, div, span {
        color: #e8e8e8;
    }

    .hero {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        border: 1px solid #2f2f39;
        border-radius: 20px;
        padding: 1.3rem 1.4rem;
        margin-bottom: 1rem;
    }

    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        color: #ffffff !important;
        margin-bottom: 0.4rem;
    }

    .hero-sub {
        font-size: 1rem;
        color: #d1d5db !important;
        line-height: 1.5;
    }

    .section-card {
        background: #12131a;
        border: 1px solid #2b2d36;
        border-radius: 18px;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    .info-card {
        background: #151821;
        border: 1px solid #343746;
        border-radius: 16px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.8rem;
    }

    .info-title {
        font-weight: 800;
        color: #ffffff !important;
        margin-bottom: 0.25rem;
    }

    .info-text {
        color: #d1d5db !important;
        line-height: 1.45;
        font-size: 0.96rem;
    }

    .metric-card {
        background: #12131a;
        border: 1px solid #2b2d36;
        border-radius: 16px;
        padding: 0.9rem;
        text-align: left;
        height: 100%;
    }

    .metric-label {
        font-size: 0.9rem;
        color: #cbd5e1 !important;
        margin-bottom: 0.2rem;
        font-weight: 700;
    }

    .metric-value {
        font-size: 1.5rem;
        font-weight: 800;
        color: #ffffff !important;
    }

    .metric-help {
        font-size: 0.88rem;
        color: #aeb7c6 !important;
        line-height: 1.35;
        margin-top: 0.45rem;
    }

    .plan-card {
        background: #12131a;
        border: 1px solid #2b2d36;
        border-radius: 18px;
        padding: 1rem 1rem 0.8rem 1rem;
        margin-top: 1rem;
    }

    .small-note {
        color: #b8c0cc !important;
        font-size: 0.93rem;
        line-height: 1.4;
    }

    .stButton > button, .stFormSubmitButton > button {
        background: #ffffff !important;
        color: #0b0b0f !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.72rem 1.15rem !important;
        font-weight: 800 !important;
    }

    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {
        background-color: #0f1117 !important;
        color: #ffffff !important;
        border: 1px solid #343746 !important;
        border-radius: 12px !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #0f1117 !important;
        color: #ffffff !important;
        border: 1px solid #343746 !important;
        border-radius: 12px !important;
    }

    div[data-testid="stSlider"] {
        padding-top: 0.2rem;
    }

    details {
        background: #12131a;
        border: 1px solid #2b2d36;
        border-radius: 14px;
        padding: 0.3rem 0.7rem;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------
# OPENAI
# -----------------------------
def get_client():
    try:
        key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        key = os.getenv("OPENAI_API_KEY")

    if not key:
        return None

    return OpenAI(api_key=key)


# -----------------------------
# CALCULATIONS
# -----------------------------
def calc_targets(weight, height_ft, height_in, age, sex, activity, goal):
    kg = weight * 0.453592
    cm = ((height_ft * 12) + height_in) * 2.54

    if sex == "Male":
        bmr = (10 * kg) + (6.25 * cm) - (5 * age) + 5
    else:
        bmr = (10 * kg) + (6.25 * cm) - (5 * age) - 161

    mult = {
        "Sedentary": 1.2,
        "Light": 1.375,
        "Moderate": 1.55,
        "Very Active": 1.725
    }[activity]

    tdee = bmr * mult

    if goal == "Lose fat":
        cal = tdee - 500
    elif goal == "Build muscle":
        cal = tdee + 250
    else:
        cal = tdee

    protein_low = round(weight * 0.7)
    protein_high = round(weight * 1.0)

    return round(bmr), round(tdee), round(cal), protein_low, protein_high


# -----------------------------
# PROMPT
# -----------------------------
def build_prompt(data, bmr, tdee, cal, protein_low, protein_high):
    return f"""
You are a realistic fitness coach writing a plan inside a fitness app.

Write a clean, easy-to-read response in markdown.

Rules:
- Be practical, not overly dramatic
- Always include sets and reps for exercises
- Always include exercise names clearly
- Use headings and bullet points
- Keep formatting neat and readable
- Make the plan realistic for the user's equipment, experience, and number of training days
- Include a short summary first
- Then include a workout plan by day
- Then cardio
- Then nutrition
- Then recovery
- Then one short motivational closing line
- Do not make medical claims
- If injuries are listed, make reasonable exercise adjustments
- Use the calories and protein targets exactly as provided

Workout format example:
Monday – Upper Body
- Bench Press: 3 sets of 8-10 reps
- Incline Dumbbell Press: 3 sets of 8-10 reps

User details:
Goal: {data['goal']}
Weight: {data['weight']} lbs
Height: {data['height_ft']} ft {data['height_in']} in
Age: {data['age']}
Sex: {data['sex']}
Activity: {data['activity']}
Experience: {data['experience']}
Equipment: {data['equipment']}
Training days: {data['days']}
Injuries: {data['injuries'] or "None"}

Targets:
BMR: {bmr}
TDEE: {tdee}
Calories: {cal}
Protein: {protein_low} to {protein_high} grams
""".strip()


# -----------------------------
# UI HEADER
# -----------------------------
st.markdown("""
<div class="hero">
    <div class="hero-title">🏋️ AI Fitness Agent</div>
    <div class="hero-sub">
        Build a personalized workout, cardio, nutrition, and recovery plan with a cleaner and easier-to-read interface.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="small-note">This tool gives general fitness guidance. It is not medical advice.</div>',
    unsafe_allow_html=True
)


# -----------------------------
# FORM
# -----------------------------
with st.form("fitness_form"):
    left, right = st.columns(2)

    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Your Info")
        weight = st.number_input("Weight (lbs)", min_value=90, max_value=450, value=180)
        height_ft = st.number_input("Height (feet)", min_value=4, max_value=7, value=6)
        height_in = st.number_input("Height (inches)", min_value=0, max_value=11, value=0)
        age = st.number_input("Age", min_value=16, max_value=70, value=21)
        sex = st.selectbox("Sex", ["Male", "Female"])
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Goal")
        goal = st.selectbox("Primary goal", ["Lose fat", "Build muscle", "Maintain"])
        activity = st.selectbox("Daily activity level", ["Sedentary", "Light", "Moderate", "Very Active"])
        days = st.slider("Training days per week", 1, 6, 4)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Training Preferences")
        experience = st.selectbox("Experience level", ["Beginner", "Intermediate", "Advanced"])
        equipment = st.selectbox("Equipment access", ["Full gym", "Dumbbells", "Bodyweight"])
        injuries = st.text_area("Injuries or limitations", placeholder="Optional")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Accessibility and Clarity")
        st.caption("The app uses high-contrast colors, simple sections, and plain language explanations for the numbers below.")
        st.markdown('</div>', unsafe_allow_html=True)

    submitted = st.form_submit_button("Generate Plan")


# -----------------------------
# OUTPUT
# -----------------------------
if submitted:
    bmr, tdee, cal, protein_low, protein_high = calc_targets(
        weight, height_ft, height_in, age, sex, activity, goal
    )

    st.subheader("Your Numbers")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">BMR</div>
            <div class="metric-value">{bmr}</div>
            <div class="metric-help">Your estimated calories burned at rest just to keep your body functioning.</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">TDEE</div>
            <div class="metric-value">{tdee}</div>
            <div class="metric-help">Your estimated daily calories after including normal activity and exercise.</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Target Calories</div>
            <div class="metric-value">{cal}</div>
            <div class="metric-help">A practical daily calorie target based on your current goal.</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Protein</div>
            <div class="metric-value">{protein_low}-{protein_high}g</div>
            <div class="metric-help">A solid daily protein range to support recovery, muscle retention, and progress.</div>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("What do these numbers mean?"):
        st.markdown("""
**BMR** is your Basal Metabolic Rate.  
It is the rough number of calories your body would burn even if you rested all day.

**TDEE** is your Total Daily Energy Expenditure.  
It adds your movement and activity on top of your BMR.

**Target Calories** is the calorie goal the app uses based on whether you want to lose fat, build muscle, or maintain.

**Protein** is a daily range that helps support muscle recovery and overall training progress.
""")

    data = {
        "goal": goal,
        "weight": weight,
        "height_ft": height_ft,
        "height_in": height_in,
        "age": age,
        "sex": sex,
        "activity": activity,
        "experience": experience,
        "equipment": equipment,
        "days": days,
        "injuries": injuries
    }

    client = get_client()

    if not client:
        st.error("Missing OPENAI_API_KEY in Streamlit secrets.")
    else:
        with st.spinner("Building your plan..."):
            try:
                res = client.responses.create(
                    model="gpt-5.4",
                    input=build_prompt(data, bmr, tdee, cal, protein_low, protein_high)
                )

                st.markdown('<div class="plan-card">', unsafe_allow_html=True)
                st.subheader("Your Personalized Plan")
                st.markdown(res.output_text)
                st.markdown('</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"OpenAI error: {e}")
