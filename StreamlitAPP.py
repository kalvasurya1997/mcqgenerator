import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.mcqgeneratorproject.utils import read_file, get_table_data
import streamlit as st
from langchain.callbacks import get_openai_callback
from src.mcqgeneratorproject.mcqgenerator import generate_evaluate_chain
from src.mcqgeneratorproject.logger import logging

# loading Json file
with open('C:\Users\kalva\mcqgenerator\Response.json', 'r') as file:
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
                # Example function call to read the uploaded file
                text = read_file(uploaded_file)

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
                    # st.write(response)
                    st.write(f"Total Tokens: {cb.total_tokens}")

            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("Error")

            else:
                print(f"Total Tokens: {cb.total_tokens}")
                print(f"Prompt Tokens: {cb.prompt_tokens}")
                print(f"Completion Tokens: {cb.completion_tokens}")
                print(f"Total Cost: {cb.total_cost}")
                if isinstance(response, dict):
                    # Extract the quiz data from the response
                    quiz = response.get("quiz", None)
                    if quiz is not None:
                        table_data = get_table_data(quiz)
                        if table_data is not None:
                            # display the table data in a dataframe
                            df = pd.DataFrame(table_data)
                            df.index = df.index + 1
                            st.table(df)
                            # display the review in a text box as well
                            st.text_area(label="Review", value=response["review"])
                    else:
                        st.write("Error in the table data")
                else:
                    st.write(response)
