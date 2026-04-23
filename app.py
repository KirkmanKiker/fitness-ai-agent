import math
import os
import streamlit as st
from openai import OpenAI


# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="AI Fitness Agent", layout="wide")


# -----------------------------
# SIMPLE BLACK / WHITE THEME
# -----------------------------
st.markdown("""
<style>
.stApp {
    background-color: #ffffff;
    color: #111111;
}

h1, h2, h3, h4 {
    color: #111111 !important;
}

p, label, span {
    color: #333333 !important;
}

.block-container {
    max-width: 900px;
}

</style>
""", unsafe_allow_html=True)


# -----------------------------
# OPENAI SETUP
# -----------------------------
def get_client():
    try:
        key = st.secrets["OPENAI_API_KEY"]
    except:
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

    return round(bmr), round(tdee), round(cal)


# -----------------------------
# PROMPT (IMPORTANT)
# -----------------------------
def build_prompt(data, bmr, tdee, cal):

    return f"""
You are a realistic gym coach.

Write a CLEAN and EASY TO READ workout plan.

REQUIREMENTS:
- ALWAYS include sets and reps (example: 3 sets of 8-10 reps)
- Use bullet points
- Use clear sections
- Make it readable (no huge paragraphs)

STRUCTURE:

1. Short summary

2. Workout plan by day:
Format like:
Monday – Upper Body
- Bench Press: 3 sets of 8-10 reps
- Incline DB Press: 3 sets of 8-10 reps

3. Cardio

4. Nutrition

5. Recovery

USER:
Goal: {data['goal']}
Weight: {data['weight']} lbs
Height: {data['height_ft']} ft {data['height_in']} in
Experience: {data['experience']}
Equipment: {data['equipment']}
Days: {data['days']}
Injuries: {data['injuries'] or "None"}

NUMBERS:
BMR: {bmr}
TDEE: {tdee}
Calories: {cal}
""".strip()


# -----------------------------
# UI
# -----------------------------
st.title("🏋️ AI Fitness Agent")

with st.form("form"):

    col1, col2 = st.columns(2)

    with col1:
        weight = st.number_input("Weight (lbs)", 100, 400, 180)
        height_ft = st.number_input("Height (ft)", 4, 7, 6)
        height_in = st.number_input("Height (in)", 0, 11, 0)
        age = st.number_input("Age", 16, 60, 21)
        sex = st.selectbox("Sex", ["Male", "Female"])

    with col2:
        goal = st.selectbox("Goal", ["Lose fat", "Build muscle", "Maintain"])
        activity = st.selectbox("Activity", ["Sedentary", "Light", "Moderate", "Very Active"])
        experience = st.selectbox("Experience", ["Beginner", "Intermediate", "Advanced"])
        equipment = st.selectbox("Equipment", ["Full gym", "Dumbbells", "Bodyweight"])
        days = st.slider("Days per week", 1, 6, 4)

    injuries = st.text_area("Injuries (optional)")

    submit = st.form_submit_button("Generate Plan")


# -----------------------------
# OUTPUT
# -----------------------------
if submit:

    bmr, tdee, cal = calc_targets(weight, height_ft, height_in, age, sex, activity, goal)

    st.subheader("Your Numbers")
    st.write(f"BMR: {bmr}")
    st.write(f"TDEE: {tdee}")
    st.write(f"Calories: {cal}")

    data = {
        "goal": goal,
        "weight": weight,
        "height_ft": height_ft,
        "height_in": height_in,
        "experience": experience,
        "equipment": equipment,
        "days": days,
        "injuries": injuries
    }

    client = get_client()

    if not client:
        st.error("Missing API key")
    else:
        with st.spinner("Generating..."):
            try:
                res = client.responses.create(
                    model="gpt-5.4",
                    input=build_prompt(data, bmr, tdee, cal)
                )

                st.subheader("Your Plan")
                st.markdown(res.output_text)

            except Exception as e:
                st.error(str(e))
