import os
import time
# from celery import Celery
from .app import celery_app
import os
import sys
import urllib.parse
import os
import PyPDF2
from PIL import Image
from io import BytesIO


@celery_app.task(name="create_task")
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    return True



@celery_app.task(name="image_extraction")
def extract_images_from_pdf():
    output_folder = "extracted_images_pdf"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    pdf_path = "app/celery/AMZN-Q3-2023-Earnings-Release.pdf"
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page_number in range(len(reader.pages)):
            page = reader.pages[page_number]
            if '/XObject' in page['/Resources']:
                xObject = page['/Resources']['/XObject']
                for obj in xObject:
                    xObject_obj = xObject[obj]
                    if xObject_obj['/Subtype'] == '/Image':
                        img_data = xObject_obj.get_data()
                        img_extension = xObject_obj['/Filter'][1:] if '/Filter' in xObject_obj else 'jpg'
                        img_extension = img_extension.lower()
                        if img_extension == 'dctdecode':
                            img_extension = 'jpg'
                        elif img_extension == 'jp2decode':
                            img_extension = 'jp2'
                        elif img_extension == 'ccittfaxdecode':
                            img_extension = 'tiff'
                        elif img_extension == 'flate':
                            img_extension = 'png'
                        else:
                            continue  # Skip unknown image types

                        img_path = os.path.join(output_folder, f"page_{page_number+1}_image_{obj[1:]}.{img_extension}")
                        with open(img_path, "wb") as img_file:
                            img_file.write(img_data)
                        print(f"Extracted image: {img_path}")


