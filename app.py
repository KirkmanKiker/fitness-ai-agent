import os
import streamlit as st
from openai import OpenAI


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="AI Fitness Agent",
    page_icon="🏋️",
    layout="wide"
)


# -----------------------------
# STYLING
# -----------------------------
st.markdown("""
<style>
    .stApp {
        background: #0a0a0d;
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

    p, label, span, div {
        color: #e5e7eb;
    }

    .hero {
        background: linear-gradient(135deg, #111111 0%, #171717 100%);
        border: 1px solid #262626;
        border-radius: 24px;
        padding: 1.35rem 1.4rem;
        margin-bottom: 1rem;
    }

    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #ffffff !important;
        margin-bottom: 0.35rem;
    }

    .hero-sub {
        color: #d1d5db !important;
        font-size: 1rem;
        line-height: 1.5;
    }

    .section-card {
        background: #111214;
        border: 1px solid #26282d;
        border-radius: 20px;
        padding: 1.1rem;
        margin-bottom: 1rem;
    }

    .metric-card {
        background: #111214;
        border: 1px solid #26282d;
        border-radius: 18px;
        padding: 1rem;
        height: 100%;
    }

    .metric-label {
        color: #cbd5e1 !important;
        font-size: 0.9rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }

    .metric-value {
        color: #ffffff !important;
        font-size: 1.55rem;
        font-weight: 800;
        margin-bottom: 0.35rem;
    }

    .metric-help {
        color: #aeb7c6 !important;
        font-size: 0.9rem;
        line-height: 1.4;
    }

    .plan-card {
        background: #111214;
        border: 1px solid #26282d;
        border-radius: 20px;
        padding: 1.1rem;
        margin-top: 1rem;
    }

    .note {
        color: #b7bec9 !important;
        font-size: 0.93rem;
        line-height: 1.45;
        margin-bottom: 0.8rem;
    }

    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {
        background: #0d0f14 !important;
        color: #ffffff !important;
        border: 1px solid #2f3440 !important;
        border-radius: 14px !important;
    }

    div[data-baseweb="select"] > div {
        background: #0d0f14 !important;
        color: #ffffff !important;
        border: 1px solid #2f3440 !important;
        border-radius: 14px !important;
    }

    div[data-testid="stSlider"] {
        padding-top: 0.35rem;
        padding-bottom: 0.2rem;
    }

    div[data-testid="stSlider"] [role="slider"] {
        background-color: #ffffff !important;
        border: 2px solid #ffffff !important;
        box-shadow: none !important;
    }

    div[data-testid="stSlider"] > div {
        color: #ffffff !important;
    }

    .stButton > button,
    .stFormSubmitButton > button {
        width: 100%;
        background: #ffffff !important;
        color: #111111 !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 0.85rem 1rem !important;
        font-weight: 800 !important;
        font-size: 1rem !important;
        box-shadow: none !important;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background: #e5e7eb !important;
        color: #000000 !important;
    }

    .stButton > button:disabled,
    .stFormSubmitButton > button:disabled {
        background: #d1d5db !important;
        color: #111111 !important;
        opacity: 1 !important;
    }

    details {
        background: #111214;
        border: 1px solid #26282d;
        border-radius: 14px;
        padding: 0.4rem 0.75rem;
    }

    hr {
        border-color: #23262d;
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
- Be practical and human
- Always include sets and reps for every exercise
- Use headings and bullet points
- Keep formatting neat and readable
- Make the plan realistic for the user's equipment, experience, and number of training days
- Include a short summary first
- Then a workout plan by day
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
# HEADER
# -----------------------------
st.markdown("""
<div class="hero">
    <div class="hero-title">🏋️ AI Fitness Agent</div>
    <div class="hero-sub">
        Build a personalized workout, cardio, nutrition, and recovery plan with a cleaner dark interface.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="note">This tool gives general fitness guidance. It is not medical advice.</div>',
    unsafe_allow_html=True
)


# -----------------------------
# FORM
# -----------------------------
with st.form("fitness_form"):
    left, right = st.columns(2, gap="large")

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
        st.subheader("Clarity")
        st.caption("High-contrast colors, simpler sections, and plain language explanations are built into the app.")
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

    c1, c2, c3, c4 = st.columns(4, gap="medium")

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">BMR</div>
            <div class="metric-value">{bmr}</div>
            <div class="metric-help">Estimated calories your body burns at rest to keep you alive and functioning.</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">TDEE</div>
            <div class="metric-value">{tdee}</div>
            <div class="metric-help">Estimated total daily calories after normal activity and training are included.</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Target Calories</div>
            <div class="metric-value">{cal}</div>
            <div class="metric-help">A practical daily calorie goal based on whether you want to lose, build, or maintain.</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Protein</div>
            <div class="metric-value">{protein_low}-{protein_high}g</div>
            <div class="metric-help">A daily protein range to help support recovery, training, and muscle retention.</div>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("What do these numbers mean?"):
        st.markdown("""
**BMR** is your Basal Metabolic Rate.  
It is the rough number of calories your body would burn even if you rested all day.

**TDEE** is your Total Daily Energy Expenditure.  
It adds movement and activity on top of your BMR.

**Target Calories** is the calorie goal based on your current goal.

**Protein** is a daily range that helps support recovery and progress.
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
