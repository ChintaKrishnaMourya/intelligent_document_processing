import streamlit as st
import tempfile
import os
import openai
import pandas as pd
from ocr import *
from gptparser import *

# Define your OpenAI API key
api_key = st.secrets["api_key"]
openai.api_key = api_key



st.set_page_config(page_title="Document Parser", page_icon="📄")
st.header("Document Parsing")
docu = st.file_uploader("Upload Document", accept_multiple_files=False)

if st.button("Submit"):
    if docu:
        try:
            temp_dir = tempfile.TemporaryDirectory()
            file_path = os.path.join(temp_dir.name, docu.name)

            with open(file_path, "wb") as f:
                f.write(docu.read())

            extracted_text = process_pdf(file_path)
            st.write("Text Extracted\n")
            parsed_df = gpt_parser(extracted_text)
            st.write("Information Parsed\n")
            # Display the parsed JSON

        # Display a message before showing the parsed JSON
            st.write("Parsed info from the doc: \n")
            st.dataframe(parsed_df)
            
            # Save the DataFrame to a CSV file
            csv_path = os.path.join(temp_dir.name, 'parsed_doc.csv')
            parsed_df.to_csv(csv_path, index=False)
            
            # Provide a download link for the CSV file
            # Provide a download link for the CSV file with the correct MIME type
            st.download_button("Download Parsed Document (CSV)", data=open(csv_path, 'rb'), key='parsed_doc', mime='text/csv')


        except Exception as e:
            st.error(f"An error occurred: {e}")
