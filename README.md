# fitness-ai-agent
AI Health and Fitness Planning Agent
Overview

This project is an AI-based fitness planning tool that generates a personalized plan based on user input. Instead of following general advice, the goal is to give users something that actually fits their situation. The app takes in information like age, weight, height, activity level, and fitness goals, then returns calorie targets, protein recommendations, a workout plan, cardio suggestions, and recovery guidance.

This started as a simple front-end interface, but it has been expanded into a full system with multiple agents working together. It also includes an AI-generated summary that makes the final output easier to read and more engaging.

How the System Works

The system is organized into a multi-agent workflow so that each part has a clear role. The Controller Agent manages the overall flow of the system. The Planner Agent reviews the input and looks for risks such as injuries or very high training frequency. The Analysis Agent performs the calculations and builds the actual plan, including calories, workouts, and nutrition guidance. The Verifier Agent then checks the output and adds warnings if needed.

After the agents finish, the system makes a single OpenAI API call to generate a more natural summary using “Coach Bob.” This step improves readability but does not change the actual values or recommendations.

Tech Stack

The project is built using Python and Streamlit. Python handles all calculations and logic, while Streamlit is used to create the user interface. The OpenAI API is used to generate the final summary. GitHub is used for version control, and the app is deployed using Streamlit Cloud.

Running the App

To run the app locally, install the required dependencies using pip install -r requirements.txt. After that, set your OpenAI API key in your environment. Once that is done, run the application using streamlit run app.py.

Using the App

The app is designed to be simple to use. The user enters their personal information, including age, weight, height, activity level, and fitness goal. Additional details like training days, equipment, and injuries can also be included. After submitting the form, the system generates a full plan with calories, protein, workouts, and other recommendations. The output is displayed directly on the screen along with a summary written in a more natural tone.

Evaluation

The system was tested using ten different cases that represent a variety of users. These include beginners, more experienced individuals, users with injuries, and different diet preferences. Each output was reviewed manually and scored based on how helpful, correct, and safe it was.

The system achieved a 100 percent success rate, meaning it produced a full plan for every test case. The average helpfulness score was 4.3 out of 5, correctness was 4.5 out of 5, and safety was 4.6 out of 5. Overall, the system performed consistently and produced clear and usable results.

Cost and Latency

Most of the system runs locally, so there is no cost for the multi-agent logic. The only cost comes from a single OpenAI API call used to generate the summary.

Each request uses around 1000 input tokens and about 250 output tokens. Based on current pricing, this comes out to approximately 0.0019 dollars per request. Running all ten test cases cost about 0.018 dollars in total, which is under two cents.

The system is also relatively fast. The agent workflow runs almost instantly since it is handled in Python. The only noticeable delay comes from the API call, which usually takes between two and four seconds. Overall, the full response time is about two to five seconds.

Limitations

The system works well for general use, but it does have some limitations. Some recommendations can feel a bit general, especially for more advanced users. Injury handling is basic and mostly provides guidance instead of fully customized plans. The quality of the output also depends on how detailed the user input is.

Future Improvements

There are several ways this system could be improved. The next steps would be to make the plans more personalized, especially for experienced users. Injury handling could be more detailed, and the system could eventually connect to real fitness tracking data. Another improvement would be allowing the plan to update over time based on user progress.

Disclaimer

This project provides general fitness guidance and should not be considered medical advice.
