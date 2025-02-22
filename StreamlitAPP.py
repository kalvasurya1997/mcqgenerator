import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
from langchain.callbacks import get_openai_callback

# Local imports
from src.mcqgeneratorproject.utils import read_file, get_table_data
from src.mcqgeneratorproject.mcqgenerator import generate_evaluate_chain
from src.mcqgeneratorproject.logger import logging


# loading Json file
with open(r"C:\Users\kalva\mcqgenerator\Response.json", "r") as file:
    RESPONSE_JSON = json.load(file)

# Creating a title for the app
st.title("MCQs Creator Application with LangChain")

# Create a form for user inputs
with st.form("user_inputs"):
    # File Upload
    uploaded_file = st.file_uploader("Upload a PDF or TXT file")

    # Input Fields
    mcq_count = st.number_input("No. of MCQs", min_value=3, max_value=50)
    subject = st.text_input("Insert Subject:", max_chars=25)
    tone = st.text_input(
        "Complexity Level Of Questions:",
        max_chars=20,
        placeholder="Simple"
    )

    # Add a submit button
    button = st.form_submit_button("Create MCQs")

# Handle form submission
if button and uploaded_file is not None and mcq_count and subject and tone:
    with st.spinner("loading..."):
        try:
            # Read the uploaded file (PDF or TXT) into text
            text = read_file(uploaded_file)

            # Call your LangChain chain
            with get_openai_callback() as cb:
                response = generate_evaluate_chain(
                    {
                        "text": text,
                        "number": mcq_count,
                        "subject": subject,
                        "tone": tone,
                        "response_json": json.dumps(RESPONSE_JSON)
                    }
                )
                st.write(f"Total Tokens: {cb.total_tokens}")

        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            st.error("Error")

        else:
            print(f"Total Tokens: {cb.total_tokens}")
            print(f"Prompt Tokens: {cb.prompt_tokens}")
            print(f"Completion Tokens: {cb.completion_tokens}")
            print(f"Total Cost: {cb.total_cost}")

            # Check if the chain returned a dict
            if isinstance(response, dict):
                # Extract the quiz data from the response
                quiz = response.get("quiz", None)

                if quiz is not None:
                    # 1) If `quiz` is a dict, convert it to JSON string
                    if isinstance(quiz, dict):
                        quiz = json.dumps(quiz)

                    # 2) If `quiz` is a string, remove the "### RESPONSE_JSON" prefix if present
                    if isinstance(quiz, str):
                        quiz_str = quiz.strip()
                        prefix = "### RESPONSE_JSON"
                        if quiz_str.startswith(prefix):
                            # Remove prefix + any leading/trailing whitespace
                            quiz = quiz_str[len(prefix):].strip()

                    # 3) Now pass the final string to get_table_data()
                    table_data = get_table_data(quiz)

                    if table_data is not None and isinstance(table_data, list):
                        # Create a DataFrame
                        df = pd.DataFrame(table_data)
                        df.index = df.index + 1
                        st.table(df)

                        # Display the review text area
                        review_text = response.get("review", "")
                        st.text_area(label="Review", value=review_text)
                    else:
                        st.write("Error in the table data")
                else:
                    st.write("Error in the table data (quiz is None)")
            else:
                # If the chain didn't return a dict, just display the raw response
                st.write(response)
