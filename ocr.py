import cv2
import os
from pdf2image import convert_from_path
import pytesseract
from pytesseract import Output
import time
import os
import streamlit as st
import pandas as pd

# poppler_path = r'C:\Users\Mourya\Downloads\poppler-23.08.0\Library\bin'# Replace with the actual path to Poppler's bin directory and also download poppler



def process_image(image):
    # Record the start time
    start_time = time.time()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    custom_config = r'-l eng --oem 1 --psm 6 '
    d = pytesseract.image_to_data(thresh, config=custom_config, output_type=Output.DICT)
    df = pd.DataFrame(d)

    df1 = df[(df.conf != '-1') & (df.text != ' ') & (df.text != '')]

    sorted_blocks = df1.groupby('block_num').first().sort_values('top').index.tolist()
    result_text = ''
    for block in sorted_blocks:
        curr = df1[df1['block_num'] == block]
        sel = curr[curr.text.str.len() > 3]
        char_w = (sel.width / sel.text.str.len()).mean()
        prev_par, prev_line, prev_left = 0, 0, 0
        text = ''
        for ix, ln in curr.iterrows():
            if prev_par != ln['par_num']:
                text += '\n'
                prev_par = ln['par_num']
                prev_line = ln['line_num']
                prev_left = 0
            elif prev_line != ln['line_num']:
                text += '\n'
                prev_line = ln['line_num']
                prev_left = 0

            added = 0
            if ln['left'] / char_w > prev_left + 1:
                added = int((ln['left']) / char_w) - prev_left
                text += ' ' * added
            text += ln['text'] + ' '
            prev_left += len(ln['text']) + added + 1
        text += '\n'
        result_text += text
    # Record the end time
    end_time = time.time()

    # Calculate the elapsed time
    extraction_time = end_time - start_time
    st.write(f"Time Taken for Extracting Text from PDF Image: {extraction_time}")
    return result_text

def process_pdf(pdf_path):
    # Record the start time
    start_time = time.time()
    images = convert_from_path(pdf_path)
    output_dir = "output_images"
    os.makedirs(output_dir, exist_ok=True)
    pdf_text=''
    for index, image in enumerate(images):
        image_filename = f'page-{index}.png'
        image_filepath = os.path.join(output_dir, image_filename)
        image.save(image_filepath)
        imagee=cv2.imread(image_filepath)
        pdf_text+=process_image(imagee)
        # Record the end time
    end_time = time.time()

    # Calculate the elapsed time
    elapsed_time = end_time - start_time
    st.write(f"Total Time Taken For Extracting text from PDF : {elapsed_time}")
    return pdf_text
