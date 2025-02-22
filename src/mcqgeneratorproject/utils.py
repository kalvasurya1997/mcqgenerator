import os
import PyPDF2
import json
import traceback

def read_file(file):
    """Reads content from a PDF or TXT file and returns text."""
    if file.name.endswith(".pdf"):
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            return text.strip() if text else "❌ No text extracted from the PDF."
        except Exception as e:
            raise Exception("❌ Error reading the PDF file:", str(e))
        
    elif file.name.endswith(".txt"):
        try:
            return file.read().decode("utf-8").strip()
        except Exception as e:
            raise Exception("❌ Error reading the TXT file:", str(e))
    
    else:
        raise Exception("❌ Unsupported file format. Only PDF and TXT files are supported.")

def get_table_data(quiz_str):
    """Parses a JSON string into a table-friendly format for Streamlit."""
    try:
        if not quiz_str or not quiz_str.strip():
            raise ValueError("❌ Error: Received empty `quiz_str`!")

        # --- NEW CODE: Remove "### RESPONSE_JSON" prefix if present ---
        quiz_str_stripped = quiz_str.strip()
        if quiz_str_stripped.startswith("### RESPONSE_JSON"):
            prefix = "### RESPONSE_JSON"
            quiz_str_stripped = quiz_str_stripped[len(prefix):].strip()

        # Convert cleaned JSON string to dictionary
        quiz_dict = json.loads(quiz_str_stripped)

        quiz_table_data = []
        for key, value in quiz_dict.items():
            mcq = value.get("mcq", "N/A")
            options = " || ".join(
                f"{opt} -> {val}"
                for opt, val in value.get("options", {}).items()
            )
            correct = value.get("correct", "N/A")
            quiz_table_data.append({"MCQ": mcq, "Choices": options, "Correct": correct})

        return quiz_table_data

    except json.JSONDecodeError as e:
        print("❌ JSONDecodeError: Invalid JSON format!", str(e))
        traceback.print_exception(type(e), e, e.__traceback__)
        return False

    except Exception as e:
        print("❌ General Error in `get_table_data()`:", str(e))
        traceback.print_exception(type(e), e, e.__traceback__)
        return False
