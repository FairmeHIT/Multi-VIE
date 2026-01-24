import os
from paddleocr import PaddleOCR, draw_ocr
from PIL import Image
from paddlenlp import Taskflow
import time
import pandas as pd
import logging
import json


def ocr_fig(image_path, model_path):
    """
    Perform OCR recognition on the image at the given path
    :param image_path: Path of the image to be recognized
    :param model_path: Path of the OCR model
    :return: Recognized text content
    """
    try:
        ocr = PaddleOCR(det_model_dir=model_path + "/det",
                        cls_model_dir=model_path + "/cls",
                        rec_model_dir=model_path + "/rec", use_angle_cls=True, DEBUG=False)
        result = ocr.ocr(image_path)

        text = ""
        for line in result[0]:
            box, text_content = line
            text += str(text_content[0]) + ""
        return text
    except Exception as e:
        print(f"Error occurred during OCR processing of the image: {e}")
        return ""


def determine_licence_type(text):
    """
    Determine the certificate type and corresponding number based on the extracted text content
    :param text: Text content recognized by OCR
    :return: Tuple of certificate type and corresponding number
    """
    document_type = 'Unknown Type'
    max_matches = 0

    # Define keywords for determining licence type, corresponding to the Name column in the table
    keywords = {
        'Academic Qualification Certificate (Acad. Qual. Cert.)': ['Academic Qualification', 'Certificate', 'Holder Name', 'Gender', 'Date of Birth', 'Major/Filed of Study', 'Educational Level', 'Graduation Date', 'Certificate Number'],
        'Degree Certificate (Deg. Cert.)': ['Degree', 'Certificate', 'Holder Name', 'Gender', 'Date of Birth', 'Major/Filed of Study', 'Educational Level', 'Graduation Date', 'Certificate Number', 'School Name'],
        'Public Institution Legal Person Certificate (PILPC)': ['Entity Name', 'Registered Unified Social Credit Code', 'Name', 'Address', 'Business Term', 'Legal Representative', 'Start-up Fund', 'Registered Capital', 'Registration Authority'],
        'Business License (Bus. Lic.)': ['Entity Name', 'Registered Unified Social Credit Code', 'Name', 'Address', 'Business Term', 'Legal Representative', 'Start-up Fund', 'Registered Capital', 'Registration Authority'],
        'Social Security Certificate (Soc. Sec. Cert.)': ['Entity Name', 'Social Security Number', 'Insurance Type', 'Contribution End Number', 'Contribution End Start Month-Year', 'Contribution End Month-Year'],
        'ID Identity Card (ID Card)': ['Holder Name', 'Identity Card Number', 'Gender', 'Date of Birth'],
        'ISO9001 ISO 9001 Quality Management System Certification (ISO 9001 QMS Cert.)': ['ISO9001', 'Quality Management', 'System Certification', 'Certificate', 'Entity Name', 'Initial Issuance Date', 'Current Issuance Date', 'Expiration Date', 'Compliance Standard'],
        'ISO14001 ISO 14001 Environmental Management System Certification (ISO 14001 EMS Cert.)': ['ISO14001', 'Environmental Management', 'System Certification', 'Certificate', 'Entity Name', 'Initial Issuance Date', 'Current Issuance Date', 'Expiration Date', 'Compliance Standard'],
        'SA8000 SA 8000 Social Accountability Certification (SA Cert.)': ['SA8000', 'Social Accountability', 'Certification', 'Certificate', 'Entity Name', 'Initial Issuance Date', 'Current Issuance Date', 'Expiration Date', 'Compliance Standard'],
        'ISO45001 ISO 45001 Occupational Health and Safety Management System Certification (ISO 45001 OHSMS Cert.)': ['ISO45001', 'Occupational Health and Safety', 'Management System', 'Certification', 'Certificate', 'Entity Name', 'Initial Issuance Date', 'Current Issuance Date', 'Expiration Date', 'Compliance Standard'],
        'Computer Software Copyright Registration Certificate (CSCRC)': ['Software Name', 'Copyright Owner', 'Date of Completion of Development', 'Date of First Publication', 'Rights Scope', 'Registration Number', 'Acquisition Rights Mode', 'Registration Date'],
        'Telecommunication Network Security Service Capability Certificate (TNSSCC) (Risk Assessment)': ['Telecommunication', 'Network Security', 'Service Capability', 'Certificate', 'Risk Assessment', 'Entity Name', 'Issuing Authority', 'Compliance Standard', 'Initial Certification Date', 'Validity Period', 'Current Certification Date', 'Certificate Level'],
        'Telecommunication Network Security Service Capability Certificate (TNSSCC) (Emerg. Response)': ['Telecommunication', 'Network Security', 'Service Capability', 'Certificate', 'Emergency Response', 'Entity Name', 'Issuing Authority', 'Compliance Standard', 'Initial Certification Date', 'Validity Period', 'Current Certification Date', 'Certificate Level'],
        'Telecommunication Network Security Service Capability Certificate (TNSSCC) (Des. & Integration)': ['Telecommunication', 'Network Security', 'Service Capability', 'Certificate', 'Design and Integration', 'Entity Name', 'Issuing Authority', 'Compliance Standard', 'Initial Certification Date', 'Validity Period', 'Current Certification Date', 'Certificate Level'],
        'Telecommunication Network Security Service Capability Certificate (TNSSCC) (Sec. Training)': ['Telecommunication', 'Network Security', 'Service Capability', 'Certificate', 'Security Training', 'Entity Name', 'Issuing Authority', 'Compliance Standard', 'Initial Certification Date', 'Validity Period', 'Current Certification Date', 'Certificate Level'],
        'Patent Certificate for Invention (PCI)': ['Invention Name', 'Inventor', 'Patent Number', 'Date of Patent Application', 'Patentee', 'Address', 'Authorization Announcement Date', 'Authorization Announcement Number']
    }

    for doc_type, keyword_list in keywords.items():
        matches = sum(keyword in text for keyword in keyword_list)
        if matches > max_matches:
            max_matches = matches
            document_type = doc_type

    # Mapping of certificate types to numbers, corresponding to the No. column in the table
    type_num_mapping = {
        'Academic Qualification Certificate (Acad. Qual. Cert.)': 1,
        'Degree Certificate (Deg. Cert.)': 2,
        'Public Institution Legal Person Certificate (PILPC)': 3,
        'Business License (Bus. Lic.)': 4,
        'Social Security Certificate (Soc. Sec. Cert.)': 5,
        'ID Identity Card (ID Card)': 6,
        'ISO9001 ISO 9001 Quality Management System Certification (ISO 9001 QMS Cert.)': 7,
        'ISO14001 ISO 14001 Environmental Management System Certification (ISO 14001 EMS Cert.)': 8,
        'SA8000 SA 8000 Social Accountability Certification (SA Cert.)': 9,
        'ISO45001 ISO 45001 Occupational Health and Safety Management System Certification (ISO 45001 OHSMS Cert.)': 10,
        'Computer Software Copyright Registration Certificate (CSCRC)': 11,
        'Telecommunication Network Security Service Capability Certificate (TNSSCC) (Risk Assessment)': 12,
        'Telecommunication Network Security Service Capability Certificate (TNSSCC) (Emerg. Response)': 13,
        'Telecommunication Network Security Service Capability Certificate (TNSSCC) (Des. & Integration)': 14,
        'Telecommunication Network Security Service Capability Certificate (TNSSCC) (Sec. Training)': 15,
        'Patent Certificate for Invention (PCI)': 16
    }

    type_num = type_num_mapping.get(document_type, 0)
    return document_type, type_num


def nlp_text(text, local_model_path, schema):
    """
    Use the NLP model to extract information from the given text based on the specified schema
    :param text: Text content to be processed (usually the result of OCR recognition)
    :param local_model_path: Local path of the NLP model
    :param schema: Schema configuration for information extraction
    :return: Dictionary of extracted information results
    """
    result_dict = {}
    ie = Taskflow('information_extraction', schema=schema, task_path=local_model_path)
    nlp_result = ie(text)

    for key in schema:
        if key in nlp_result[0] and nlp_result[0][key]:
            value = nlp_result[0][key][0]['text']
            result_dict[key] = value
        else:
            result_dict[key] = None

    return result_dict


def is_image_file(filename):
    """
    Determine whether the given filename is an image file (supports common image extensions)
    :param filename: Filename
    :return: Boolean value indicating whether it is an image file
    """
    image_extensions = ['.png', '.jpg', '.jpeg']
    return any(filename.lower().endswith(ext) for ext in image_extensions)


def save_ocr_text(ocr_text, file_path, txt_dir_path):
    """
    Save the text recognized by OCR to a.txt file named after the filename in the specified directory
    :param ocr_text: Text content recognized by OCR
    :param file_path: Filename (including path) corresponding to the original image
    :param txt_dir_path: Target directory path for saving text files
    """
    try:
        file_name = os.path.splitext(os.path.basename(file_path))[0] + ".txt"
        with open(os.path.join(txt_dir_path, file_name), 'w', encoding='utf-8') as f:
            f.write(ocr_text)
        print(f"Successfully saved OCR text to {os.path.join(txt_dir_path, file_name)}")
    except Exception as e:
        print(f"Error occurred while saving OCR text: {e}")


def pro_uie(ocr_model_path, image_path, lic_type):
    """
    Function to process images, perform OCR recognition, determine certificate type, extract information with NLP, and save to Excel
    :param ocr_model_path: Path of the OCR model
    :param image_path: Path of the image file
    :param lic_type: Type of the certificate (for logging)
    :return: Response dictionary containing processing results
    """
    filename = os.path.basename(image_path)
    if is_image_file(filename) and os.path.isfile(image_path):
        print(f"Processing image: {image_path}")

        ocr_text = ocr_fig(image_path, ocr_model_path)

        try:
            document_category, certificate_type_number = determine_licence_type(ocr_text)
            print(f"Certificate type: {lic_type}, Classification result: {document_category}")

        except Exception as e:
            print(f"Error occurred while determining certificate type: {e}")
            logging.error(f"Error occurred while determining certificate type for image {image_path}: {str(e)}")
            return {"name": None, "type": None, "data": None}

        # Schema configuration corresponding to certificate type numbers, mapping to fields in Landmark
        schema_config = {
            1: ['Holder Name', 'Date of Birth', 'Major/Filed of Study', 'Educational Level', 'Graduation Date', 'Certificate Number'],
            2: ['Holder Name', 'Date of Birth', 'Major/Filed of Study', 'Educational Level', 'Graduation Date', 'Certificate Number', 'School Name'],
            3: ['Entity Name', 'Registered Unified Social Credit Code', 'Name', 'Address', 'Business Term', 'Legal Representative', 'Start-up Fund', 'Registered Capital', 'Registration Authority'],
            4: ['Entity Name', 'Registered Unified Social Credit Code', 'Name', 'Address', 'Business Term', 'Legal Representative', 'Start-up Fund', 'Registered Capital', 'Registration Authority'],
            5: ['Entity Name', 'Social Security Number', 'Insurance Type', 'Contribution End Number', 'Contribution End Start Month-Year', 'Contribution End Month-Year'],
            6: ['Holder Name', 'Identity Card Number', 'Gender', 'Date of Birth'],
            7: ['Entity Name', 'Initial Issuance Date', 'Current Issuance Date', 'Expiration Date', 'Compliance Standard'],
            8: ['Entity Name', 'Initial Issuance Date', 'Current Issuance Date', 'Expiration Date', 'Compliance Standard'],
            9: ['Entity Name', 'Initial Issuance Date', 'Current Issuance Date', 'Expiration Date', 'Compliance Standard'],
            10: ['Entity Name', 'Initial Issuance Date', 'Current Issuance Date', 'Expiration Date', 'Compliance Standard'],
            11: ['Software Name', 'Copyright Owner', 'Date of Completion of Development', 'Date of First Publication', 'Rights Scope', 'Registration Number', 'Acquisition Rights Mode', 'Registration Date'],
            12: ['Entity Name', 'Issuing Authority', 'Compliance Standard', 'Initial Certification Date', 'Validity Period', 'Current Certification Date', 'Certificate Level'],
            13: ['Entity Name', 'Issuing Authority', 'Compliance Standard', 'Initial Certification Date', 'Validity Period', 'Current Certification Date', 'Certificate Level'],
            14: ['Entity Name', 'Issuing Authority', 'Compliance Standard', 'Initial Certification Date', 'Validity Period', 'Current Certification Date', 'Certificate Level'],
            15: ['Entity Name', 'Issuing Authority', 'Compliance Standard', 'Initial Certification Date', 'Validity Period', 'Current Certification Date', 'Certificate Level'],
            16: ['Invention Name', 'Inventor', 'Patent Number', 'Date of Patent Application', 'Patentee', 'Address', 'Authorization Announcement Date', 'Authorization Announcement Number']
        }

        schema = schema_config.get(int(certificate_type_number), [])

        print(f"lic_type=={lic_type}, schema=={schema}")
        # Mapping of type numbers to subdirectory numbers of the model path (example, adjust according to actual situation)
        type_num_to_model_subdir = {
            1: "00",
            2: "01",
            3: "02",
            4: "03",
            5: "04",
            6: "05",
            7: "06",
            8: "07",
            9: "08",
            10: "09",
            11: "10",
            12: "11",
            13: "12",
            14: "13",
            15: "14",
            16: "15"
        }
        uie_model_path = "E:/03_Codes/08_paddle_ocr_nlp/data_uie_file/checkpoint/"
        model_subdir = type_num_to_model_subdir.get(int(certificate_type_number), "")
        uie_model_path = uie_model_path + model_subdir + "/" + "model_best/checkpoint-800"

        response = {
            "name": None,
            "type": None,
            "data": None
        }
        if schema:
            nlp_text_result = nlp_text(ocr_text, uie_model_path, schema)
            response["name"] = filename
            response["type"] = lic_type
            response["data"] = nlp_text_result

        else:
            print("No valid NLP processing schema set.")

        return response


if __name__ == "__main__":
    # Directory list, corresponding to certificate type names in the table
    dir_list = ['Academic Qualification Certificate (Acad. Qual. Cert.)',
                'Degree Certificate (Deg. Cert.)',
                'Public Institution Legal Person Certificate (PILPC)',
                'Business License (Bus. Lic.)',
                'Social Security Certificate (Soc. Sec. Cert.)',
                'ID Identity Card (ID Card)',
                'ISO9001 ISO 9001 Quality Management System Certification (ISO 9001 QMS Cert.)',
                'ISO14001 ISO 14001 Environmental Management System Certification (ISO 14001 EMS Cert.)',
                'SA8000 SA 8000 Social Accountability Certification (SA Cert.)',
                'ISO45001 ISO 45001 Occupational Health and Safety Management System Certification (ISO 45001 OHSMS Cert.)',
                'Computer Software Copyright Registration Certificate (CSCRC)',
                'Telecommunication Network Security Service Capability Certificate (TNSSCC) (Risk Assessment)',
                'Telecommunication Network Security Service Capability Certificate (TNSSCC) (Emerg. Response)',
                'Telecommunication Network Security Service Capability Certificate (TNSSCC) (Des. & Integration)',
                'Telecommunication Network Security Service Capability Certificate (TNSSCC) (Sec. Training)',
                'Patent Certificate for Invention (PCI)']

    model_path = r"model/path"

    with open('output.txt', 'w') as file:
        pass

    files = os.listdir(image_dir_path)
    for file in files:
        image_path = os.path.join(image_dir_path, file)

        start_time = time.time()
        res = pro_uie(model_path, image_path, item)
        print(res)
        end_time = time.time()
        print(f"All execution time: {end_time - start_time} seconds")
        with open('output.txt', 'a', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False)
            f.write('\n')
