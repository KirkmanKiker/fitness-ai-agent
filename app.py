import math
import os

import streamlit as st
from openai import OpenAI


# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title="AI Fitness Agent",
    page_icon="🏋️",
    layout="wide"
)


# -------------------------------------------------
# Simple styling
# -------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background: #f8fbff;
    }

    .block-container {
        max-width: 1000px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3, h4, h5, h6, p, label, span {
        color: #111827 !important;
    }

    .hero {
        background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 55%, #60a5fa 100%);
        padding: 1.5rem 1.75rem;
        border-radius: 20px;
        margin-bottom: 1rem;
    }

    .hero h1, .hero p {
        color: white !important;
        margin: 0;
    }

    .card {
        background: white;
        border: 1px solid #dbeafe;
        border-radius: 18px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.06);
    }

    .summary-box {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    .stButton > button, .stFormSubmitButton > button {
        background: linear-gradient(135deg, #1d4ed8, #3b82f6);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.7rem 1.2rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def get_openai_client():
    api_key = None

    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return None

    return OpenAI(api_key=api_key)


def calculate_bmr(weight_lbs, height_ft, height_in, age, sex):
    weight_kg = weight_lbs * 0.453592
    total_inches = (height_ft * 12) + height_in
    height_cm = total_inches * 2.54

    if sex == "Male":
        return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161


def get_activity_multiplier(activity_level):
    return {
        "Sedentary (little or no exercise)": 1.2,
        "Lightly active (1-3 days/week)": 1.375,
        "Moderately active (3-5 days/week)": 1.55,
        "Very active (6-7 days/week)": 1.725,
        "Extremely active (hard exercise + physical job)": 1.9
    }[activity_level]


def calculate_targets(weight_lbs, height_ft, height_in, age, sex, activity_level, goal):
    bmr = calculate_bmr(weight_lbs, height_ft, height_in, age, sex)
    tdee = bmr * get_activity_multiplier(activity_level)

    if goal == "Lose fat":
        calories = tdee - 500
    elif goal == "Build muscle":
        calories = tdee + 250
    else:
        calories = tdee

    protein_low = round(weight_lbs * 0.7)
    protein_high = round(weight_lbs * 1.0)

    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
        "calories": round(calories),
        "protein_low": protein_low,
        "protein_high": protein_high
    }


def build_prompt(profile, targets):
    return f"""
You are a practical fitness coach helping generate a workout and nutrition plan inside a Streamlit fitness app.

Write a personalized response using the user's details below.

Rules:
- Be clear, realistic, and human.
- Organize the answer with markdown headings.
- Include:
  1. Short overall summary
  2. Workout split
  3. Detailed workout plan by day
  4. Cardio recommendation
  5. Nutrition guidance
  6. Recovery guidance
  7. Injury / limitation adjustments if relevant
  8. One short motivational closing line
- Keep it useful and not overly long.
- Do not make up medical claims.
- Use the calorie and protein targets exactly as provided.
- If equipment is limited, make the exercises realistic.
- If the user entered injuries or limitations, adjust the plan accordingly.
- If the user selected preferred training days, use them.
- Make the workout easy to read.
- Use bullet points under each workout day.

User profile:
Name: {profile["name"] or "User"}
Age: {profile["age"]}
Sex: {profile["sex"]}
Weight: {profile["weight_lbs"]} lbs
Height: {profile["height_ft"]}'{profile["height_in"]}"
Goal: {profile["goal"]}
Activity level: {profile["activity_level"]}
Training days per week: {profile["training_days"]}
Workout time: {profile["workout_time"]}
Equipment: {profile["equipment"]}
Diet preference: {profile["diet"]}
Experience level: {profile["experience_level"]}
Preferred focus: {profile["preferred_focus"]}
Preferred cardio: {profile["cardio_preference"]}
Preferred training days: {", ".join(profile["selected_days"]) if profile["selected_days"] else "No preference"}
Injuries / limitations: {profile["injuries"] if profile["injuries"].strip() else "None"}
Additional notes: {profile["notes"] if profile["notes"].strip() else "None"}

Calculated targets:
BMR: {targets["bmr"]}
TDEE: {targets["tdee"]}
Target calories: {targets["calories"]}
Protein: {targets["protein_low"]} to {targets["protein_high"]} grams per day
""".strip()


def generate_plan(profile, targets):
    client = get_openai_client()

    if client is None:
        return None, "Missing OPENAI_API_KEY in Streamlit secrets."

    prompt = build_prompt(profile, targets)

    try:
        response = client.responses.create(
            model="gpt-5.4",
            input=prompt
        )
        return response.output_text, None
    except Exception as e:
        return None, f"OpenAI error: {e}"


# -------------------------------------------------
# UI
# -------------------------------------------------
st.markdown("""
<div class="hero">
    <h1>🏋️ AI Fitness Agent</h1>
    <p>Build a personalized workout, nutrition, and recovery plan with a much simpler setup.</p>
</div>
""", unsafe_allow_html=True)

with st.form("fitness_form"):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Personal Information")
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=13, max_value=80, value=21, step=1)
        sex = st.selectbox("Sex", ["Male", "Female"])

        st.subheader("Body Stats")
        weight_lbs = st.number_input("Weight (lbs)", min_value=80.0, max_value=500.0, value=180.0, step=1.0)
        h1, h2 = st.columns(2)
        with h1:
            height_ft = st.number_input("Height - Feet", min_value=3, max_value=8, value=6, step=1)
        with h2:
            height_in = st.number_input("Height - Inches", min_value=0, max_value=11, value=0, step=1)

        st.subheader("Goal and Activity")
        goal = st.selectbox(
            "Primary Goal",
            ["Lose fat", "Build muscle", "Maintain weight", "Improve general fitness"]
        )
        activity_level = st.selectbox(
            "Daily Activity Level",
            [
                "Sedentary (little or no exercise)",
                "Lightly active (1-3 days/week)",
                "Moderately active (3-5 days/week)",
                "Very active (6-7 days/week)",
                "Extremely active (hard exercise + physical job)"
            ]
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Workout Preferences")
        training_days = st.slider("Training Days Per Week", 1, 7, 4)
        workout_time = st.selectbox(
            "Time Available Per Workout",
            ["20-30 minutes", "30-45 minutes", "45-60 minutes", "60+ minutes"]
        )
        equipment = st.selectbox(
            "Equipment Access",
            ["Full gym", "Home gym", "Dumbbells only", "Bodyweight only"]
        )
        diet = st.selectbox(
            "Diet Preference",
            ["No preference", "High protein", "Vegetarian", "Low carb", "Budget-friendly"]
        )
        experience_level = st.selectbox(
            "Training Experience",
            ["Beginner", "Intermediate", "Advanced"]
        )
        preferred_focus = st.selectbox(
            "Preferred Muscle Focus",
            ["No preference", "Chest", "Back", "Legs", "Shoulders", "Arms"]
        )
        cardio_preference = st.selectbox(
            "Preferred Cardio",
            ["No preference", "Walking", "Bike", "Running", "Other"]
        )
        selected_days = st.multiselect(
            "Preferred Training Days",
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            default=["Monday", "Tuesday", "Thursday", "Friday"]
        )
        injuries = st.text_area("Injuries / Limitations")
        notes = st.text_area("Anything else we should know?")
        st.markdown('</div>', unsafe_allow_html=True)

    submitted = st.form_submit_button("Generate My Plan")


# -------------------------------------------------
# Output
# -------------------------------------------------
if submitted:
    profile = {
        "name": name,
        "age": int(age),
        "sex": sex,
        "weight_lbs": float(weight_lbs),
        "height_ft": int(height_ft),
        "height_in": int(height_in),
        "goal": goal,
        "activity_level": activity_level,
        "training_days": int(training_days),
        "workout_time": workout_time,
        "equipment": equipment,
        "diet": diet,
        "experience_level": experience_level,
        "preferred_focus": preferred_focus,
        "cardio_preference": cardio_preference,
        "selected_days": selected_days,
        "injuries": injuries,
        "notes": notes
    }

    targets = calculate_targets(
        weight_lbs=profile["weight_lbs"],
        height_ft=profile["height_ft"],
        height_in=profile["height_in"],
        age=profile["age"],
        sex=profile["sex"],
        activity_level=profile["activity_level"],
        goal=profile["goal"]
    )

    st.markdown('<div class="summary-box">', unsafe_allow_html=True)
    st.subheader("Your Numbers")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("BMR", targets["bmr"])
    with c2:
        st.metric("TDEE", targets["tdee"])
    with c3:
        st.metric("Target Calories", targets["calories"])
    with c4:
        st.metric("Protein", f'{targets["protein_low"]}-{targets["protein_high"]}g')
    st.markdown('</div>', unsafe_allow_html=True)

    with st.spinner("Building your plan..."):
        plan_text, error_message = generate_plan(profile, targets)

    if error_message:
        st.error(error_message)
    elif plan_text:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Your Personalized Plan")
        st.markdown(plan_text)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("Something went wrong while generating the plan.")
