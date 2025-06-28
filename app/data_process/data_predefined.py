target_type_num_mapping_en = {
    1: 'academicCertificate',       # Academic Qualification Certificate
    2: 'degreeCertificate',         # Degree Certificate
    3: 'legalLicense',              # Public Institution Legal Person Certificate
    4: 'businessLicense',           # Business License
    5: 'socialSecurityCertificate', # Social Security Certificate
    6: 'ID',                        # ID Identity Card
    7: 'ISO9001',                   # ISO 9001 Certification
    8: 'ISO14001',                  # ISO 14001 Certification
    9: 'SA8000',                    # SA 8000 Certification
    10: 'ISO45001',                 # ISO 45001 Certification
    11: 'CSCRC',                    # Computer Software Copyright Registration Certificate
    12: 'CESSCN_risk_eval',         # TNSSCC (Risk Assessment)
    13: 'CESSCN_emergency_resp',    # TNSSCC (Emergency Response)
    14: 'CESSCN_design_inte',       # TNSSCC (Design & Integration)
    15: 'CESSCN_safety_train',      # TNSSCC (Security Training)
    16: 'PCI'                       # Patent Certificate for Invention
}

target_type_list_en = list(target_type_num_mapping_en.values())

llm_extract_sys_text = "You can perform OCR on images and return specific key information in JSON format."

# LLM field extraction prompt templates
text1 = "\n1. Identify and extract key field information from the given license image, returning the information in JSON format. Required fields:"
text2 = "\n2. Return data strictly in JSON format without any non-JSON characters or structures, and without additional explanations."
text3 = "\n3. Do not modify the return fields. Return only specified fields. If a field is missing/unrecognized, return \"unidentified\"."
text4 = "\n4. Rotate the image to 0 degrees if text orientation is not horizontal."
text5 = "\nIf no signature is detected, set \"hasSignature\" to \"False\"; if detected, set to \"True\"."
text6 = "\nIf no seal is detected, set \"hasSeal\" to \"False\"; if detected, set to \"True\"."
text7 = "\nIf \"Business Scope\" content exceeds 50 Chinese characters, truncate to first 50 characters."

# Example templates with English field names matching the table
text_example_1 = "Return example: {\"Certificate Holder Name\": \"value\", \"Gender\": \"value\", \"DOB\": \"value\", \"Major/Field\": \"value\", \"Edu. Level\": \"value\", \"Grad. Date\": \"value\", \"Cert. No.\": \"value\", \"Sch. Name\": \"value\", \"hasSignature\": \"True/False\", \"hasSeal\": \"True/False\", \"Seal Name\": \"value\"}"
text_example_2 = "Return example: {\"Holder Name\": \"value\", \"Gender\": \"value\", \"DOB\": \"value\", \"Major/Field\": \"value\", \"Deg. Level\": \"value\", \"Grad. Date\": \"value\", \"Cert. No.\": \"value\", \"Sch. Name\": \"value\", \"hasSignature\": \"True/False\", \"hasSeal\": \"True/False\", \"Seal Name\": \"value\"}"
text_example_3 = "Return example: {\"Ent. Name\": \"value\", \"Unif. Soc. Credit Code\": \"value\", \"Reg. Addr.\": \"value\", \"Bus. Term\": \"value\", \"Leg. Rep.\": \"value\", \"Reg. Cap.\": \"value\", \"hasSeal\": \"True/False\", \"Registration Authority\": \"value\"}"
text_example_4 = "Return example: {\"Ent. Name\": \"value\", \"Unif. Soc. Credit Code\": \"value\", \"Reg. Addr.\": \"value\", \"Bus. Term\": \"value\", \"Leg. Rep.\": \"value\", \"Start-up Fund\": \"value\", \"hasSeal\": \"True/False\", \"Registration Authority\": \"value\"}"
text_example_5 = "Return example: {\"Ent. Name\": \"value\", \"NameofPH\": \"value\", \"Soc. Sec. No.\": \"value\", \"Ins. Type\": \"value\", \"Cont. Start M-Y\": \"value\", \"Cont. End M-Y\": \"value\", \"hasSeal\": \"True/False\", \"Seal Name\": \"value\"}"
text_example_6 = "Return example: {\"Hold. Name\": \"value\", \"ID No.\": \"value\", \"Gender\": \"value\", \"DOB\": \"value\"}"
text_example_7 = "Return example: {\"Ent. Name\": \"value\", \"Init. Iss. Date\": \"value\", \"Cur. Iss. Date\": \"value\", \"Exp. Date\": \"value\", \"Comp. Std.\": \"value\", \"hasSignature\": \"True/False\", \"hasSeal\": \"True/False\", \"Seal Name\": \"value\"}"  # ISO9001/14001/45001
text_example_8 = text_example_7  # SA8000 uses same fields
text_example_9 = text_example_7  # All ISO certs share same structure
text_example_10 = text_example_7 # Consistent with table
text_example_11 = "Return example: {\"SW Name\": \"value\", \"Copyr. Owner\": \"value\", \"Dev. Comp. Date\": \"value\", \"First Pub. Date\": \"value\", \"Acq. Rights Mode\": \"value\", \"Rights Scope\": \"value\", \"Reg. Num.\": \"value\"}"
text_example_12 = "Return example: {\"Ent. Name\": \"value\", \"Issuing Auth.\": \"value\", \"Comp. Std.\": \"value\", \"Init. Cert. Date\": \"value\", \"Validity\": \"value\", \"Cur. Iss. Date\": \"value\", \"Cert. Level\": \"value\", \"hasSeal\": \"True/False\", \"Seal Name\": \"value\"}"  # TNSSCC types
text_example_13 = text_example_12
text_example_14 = text_example_12
text_example_15 = text_example_12
text_example_16 = "Return example: {\"Inv. Name\": \"value\", \"Invtr.\": \"value\", \"Pat. Num.\": \"value\", \"Pat. Appl. Date\": \"value\", \"Patee\": \"value\", \"Addr.\": \"value\", \"Auth. Ann. Date\": \"value\", \"Auth. Ann. Num.\": \"value\"}"

# Prompt templates for each certificate type
text_prompt_templates = {
    1: f"{text1} \"Certificate Holder Name\", \"Gender\", \"DOB\", \"Major/Field\", \"Edu. Level\", \"Grad. Date\", \"Cert. No.\", \"Sch. Name\", \"hasSignature\", \"hasSeal\", \"Seal Name\". {text2} {text_example_1} {text3} {text4} {text5} {text6}",
    2: f"{text1} \"Holder Name\", \"Gender\", \"DOB\", \"Major/Field\", \"Deg. Level\", \"Grad. Date\", \"Cert. No.\", \"Sch. Name\", \"hasSignature\", \"hasSeal\", \"Seal Name\". {text2} {text_example_2} {text3} {text4} {text5} {text6}",
    3: f"{text1} \"Ent. Name\", \"Unif. Soc. Credit Code\", \"Reg. Addr.\", \"Bus. Term\", \"Leg. Rep.\", \"Reg. Cap.\", \"hasSeal\", \"Registration Authority\". {text2} {text_example_3} {text3} {text4} {text6}",
    4: f"{text1} \"Ent. Name\", \"Unif. Soc. Credit Code\", \"Reg. Addr.\", \"Bus. Term\", \"Leg. Rep.\", \"Start-up Fund\", \"hasSeal\", \"Registration Authority\". {text2} {text_example_4} {text3} {text4} {text6} {text7}",
    5: f"{text1} \"Ent. Name\", \"NameofPH\", \"Soc. Sec. No.\", \"Ins. Type\", \"Cont. Start M-Y\", \"Cont. End M-Y\", \"hasSeal\", \"Seal Name\". {text2} {text_example_5} {text3} {text4} {text6}",
    6: f"{text1} \"Hold. Name\", \"ID No.\", \"Gender\", \"DOB\". {text2} {text_example_6} {text3} {text4}",
    7: f"{text1} \"Ent. Name\", \"Init. Iss. Date\", \"Cur. Iss. Date\", \"Exp. Date\", \"Comp. Std.\", \"hasSignature\", \"hasSeal\", \"Seal Name\". {text2} {text_example_7} {text3} {text4} {text5} {text6}",
    8: f"{text1} \"Ent. Name\", \"Init. Iss. Date\", \"Cur. Iss. Date\", \"Exp. Date\", \"Comp. Std.\", \"hasSignature\", \"hasSeal\", \"Seal Name\". {text2} {text_example_8} {text3} {text4} {text5} {text6}",
    9: f"{text1} \"Ent. Name\", \"Init. Iss. Date\", \"Cur. Iss. Date\", \"Exp. Date\", \"Comp. Std.\", \"hasSignature\", \"hasSeal\", \"Seal Name\". {text2} {text_example_9} {text3} {text4} {text5} {text6}",
    10: f"{text1} \"Ent. Name\", \"Init. Iss. Date\", \"Cur. Iss. Date\", \"Exp. Date\", \"Comp. Std.\", \"hasSignature\", \"hasSeal\", \"Seal Name\". {text2} {text_example_10} {text3} {text4} {text5} {text6}",
    11: f"{text1} \"SW Name\", \"Copyr. Owner\", \"Dev. Comp. Date\", \"First Pub. Date\", \"Acq. Rights Mode\", \"Rights Scope\", \"Reg. Num.\". {text2} {text_example_11} {text3} {text4}",
    12: f"{text1} \"Ent. Name\", \"Issuing Auth.\", \"Comp. Std.\", \"Init. Cert. Date\", \"Validity\", \"Cur. Iss. Date\", \"Cert. Level\", \"hasSeal\", \"Seal Name\". {text2} {text_example_12} {text3} {text4} {text6}",
    13: f"{text1} \"Ent. Name\", \"Issuing Auth.\", \"Comp. Std.\", \"Init. Cert. Date\", \"Validity\", \"Cur. Iss. Date\", \"Cert. Level\", \"hasSeal\", \"Seal Name\". {text2} {text_example_13} {text3} {text4} {text6}",
    14: f"{text1} \"Ent. Name\", \"Issuing Auth.\", \"Comp. Std.\", \"Init. Cert. Date\", \"Validity\", \"Cur. Iss. Date\", \"Cert. Level\", \"hasSeal\", \"Seal Name\". {text2} {text_example_14} {text3} {text4} {text6}",
    15: f"{text1} \"Ent. Name\", \"Issuing Auth.\", \"Comp. Std.\", \"Init. Cert. Date\", \"Validity\", \"Cur. Iss. Date\", \"Cert. Level\", \"hasSeal\", \"Seal Name\". {text2} {text_example_15} {text3} {text4} {text6}",
    16: f"{text1} \"Inv. Name\", \"Invtr.\", \"Pat. Num.\", \"Pat. Appl. Date\", \"Patee\", \"Addr.\", \"Auth. Ann. Date\", \"Auth. Ann. Num.\". {text2} {text_example_16} {text3} {text4}"
}

# Field mapping definitions
certificate_id_name_predefined = {
    "academicCertificate": {
        "id_list": ['certiName', 'certHolderName', 'gender', 'dob', 'majorField', 'eduLevel', 'gradDate', 'certNo', 'schName', 'hasSignature', 'hasSeal', 'sealName'],
        "name_list": ['Certificate Name', 'Certificate Holder Name', 'Gender', 'Date of Birth', 'Major/Field of Study', 'Educational Level', 'Graduation Date', 'Certificate Number', 'School Name', 'hasSignature', 'hasSeal', 'Seal Name']
    },
    "degreeCertificate": {
        "id_list": ['certiName', 'holderName', 'gender', 'dob', 'majorField', 'degLevel', 'gradDate', 'certNo', 'schName', 'hasSignature', 'hasSeal', 'sealName'],
        "name_list": ['Certificate Name', 'Holder Name', 'Gender', 'Date of Birth', 'Major/Field of Study', 'Degree Level', 'Graduation Date', 'Certificate Number', 'School Name', 'hasSignature', 'hasSeal', 'Seal Name']
    },
    "legalLicense": {
        "id_list": ['certiName', 'entName', 'unifiedSocCreditCode', 'regAddr', 'busTerm', 'legRep', 'regCap', 'hasSeal', 'regAuthority'],
        "name_list": ['Certificate Name', 'Entity Name', 'Unified Social Credit Code', 'Registered Address', 'Business Term', 'Legal Representative', 'Registered Capital', 'hasSeal', 'Registration Authority']
    },
    "businessLicense": {
        "id_list": ['certiName', 'entName', 'unifiedSocCreditCode', 'regAddr', 'busTerm', 'legRep', 'startupFund', 'hasSeal', 'regAuthority'],
        "name_list": ['Certificate Name', 'Entity Name', 'Unified Social Credit Code', 'Registered Address', 'Business Term', 'Legal Representative', 'Start-up Fund', 'hasSeal', 'Registration Authority']
    },
    "socialSecurityCertificate": {
        "id_list": ['certiName', 'entName', 'nameOfPH', 'socSecNo', 'insType', 'contStartMY', 'contEndMY', 'hasSeal', 'sealName'],
        "name_list": ['Certificate Name', 'Entity Name', 'Name of Policyholder', 'Social Security Number', 'Insurance Type', 'Contribution Start Month-Year', 'Contribution End Month-Year', 'hasSeal', 'Seal Name']
    },
    "ID": {
        "id_list": ['certiName', 'holderName', 'idNo', 'gender', 'dob'],
        "name_list": ['Certificate Name', 'Holder Name', 'Identity Card Number', 'Gender', 'Date of Birth']
    },
    "ISO9001": {
        "id_list": ['certiName', 'entName', 'initIssDate', 'curIssDate', 'expDate', 'compStd', 'hasSignature', 'hasSeal', 'sealName'],
        "name_list": ['Certificate Name', 'Entity Name', 'Initial Issuance Date', 'Current Issuance Date', 'Expiration Date', 'Compliance Standard', 'hasSignature', 'hasSeal', 'Seal Name']
    },
    "ISO14001": {
        "id_list": ['certiName', 'entName', 'initIssDate', 'curIssDate', 'expDate', 'compStd', 'hasSignature', 'hasSeal', 'sealName'],
        "name_list": ['Certificate Name', 'Entity Name', 'Initial Issuance Date', 'Current Issuance Date', 'Expiration Date', 'Compliance Standard', 'hasSignature', 'hasSeal', 'Seal Name']
    },
    "SA8000": {
        "id_list": ['certiName', 'entName', 'initIssDate', 'curIssDate', 'expDate', 'compStd', 'hasSignature', 'hasSeal', 'sealName'],
        "name_list": ['Certificate Name', 'Entity Name', 'Initial Issuance Date', 'Current Issuance Date', 'Expiration Date', 'Compliance Standard', 'hasSignature', 'hasSeal', 'Seal Name']
    },
    "ISO45001": {
        "id_list": ['certiName', 'entName', 'initIssDate', 'curIssDate', 'expDate', 'compStd', 'hasSignature', 'hasSeal', 'sealName'],
        "name_list": ['Certificate Name', 'Entity Name', 'Initial Issuance Date', 'Current Issuance Date', 'Expiration Date', 'Compliance Standard', 'hasSignature', 'hasSeal', 'Seal Name']
    },
    "CSCRC": {
        "id_list": ['certiName', 'swName', 'copyrOwner', 'devCompDate', 'firstPubDate', 'acqRightsMode', 'rightsScope', 'regNum'],
        "name_list": ['Certificate Name', 'Software Name', 'Copyright Owner', 'Date of Completion of Development', 'Date of First Publication', 'Mode of Acquiring Rights', 'Scope of Rights', 'Registration Number']
    },
    "CESSCN_risk_eval": {
        "id_list": ['certiName', 'entName', 'issuingAuth', 'compStd', 'initCertDate', 'validity', 'curIssDate', 'certLevel', 'hasSeal', 'sealName'],
        "name_list": ['Certificate Name', 'Entity Name', 'Issuing Authority', 'Compliance Standard', 'Initial Certification Date', 'Validity Period', 'Current Issuance Date', 'Certificate Level', 'hasSeal', 'Seal Name']
    },
    "CESSCN_emergency_resp": {
        "id_list": ['certiName', 'entName', 'issuingAuth', 'compStd', 'initCertDate', 'validity', 'curIssDate', 'certLevel', 'hasSeal', 'sealName'],
        "name_list": ['Certificate Name', 'Entity Name', 'Issuing Authority', 'Compliance Standard', 'Initial Certification Date', 'Validity Period', 'Current Issuance Date', 'Certificate Level', 'hasSeal', 'Seal Name']
    },
    "CESSCN_design_inte": {
        "id_list": ['certiName', 'entName', 'issuingAuth', 'compStd', 'initCertDate', 'validity', 'curIssDate', 'certLevel', 'hasSeal', 'sealName'],
        "name_list": ['Certificate Name', 'Entity Name', 'Issuing Authority', 'Compliance Standard', 'Initial Certification Date', 'Validity Period', 'Current Issuance Date', 'Certificate Level', 'hasSeal', 'Seal Name']
    },
    "CESSCN_safety_train": {
        "id_list": ['certiName', 'entName', 'issuingAuth', 'compStd', 'initCertDate', 'validity', 'curIssDate', 'certLevel', 'hasSeal', 'sealName'],
        "name_list": ['Certificate Name', 'Entity Name', 'Issuing Authority', 'Compliance Standard', 'Initial Certification Date', 'Validity Period', 'Current Issuance Date', 'Certificate Level', 'hasSeal', 'Seal Name']
    },
    "PCI": {
        "id_list": ['certiName', 'invName', 'invtr', 'patNum', 'patApplDate', 'patee', 'addr', 'authAnnDate', 'authAnnNum'],
        "name_list": ['Certificate Name', 'Invention Name', 'Inventor', 'Patent Number', 'Date of Patent Application', 'Patentee', 'Address', 'Date of Authorization Announcement', 'Authorization Announcement Number']
    }
}

# Additional configuration dictionaries
fig_class_keywords = {
    'academicCertificate': ['Academic', 'Qualification', 'Certificate', 'Holder', 'Gender', 'DOB', 'Major', 'Field', 'Educational', 'Level', 'Graduation', 'Date', 'Number', 'School'],
    'degreeCertificate': ['Degree', 'Certificate', 'Holder', 'Gender', 'DOB', 'Major', 'Field', 'Degree', 'Level', 'Graduation', 'Date', 'Number', 'School'],
    'legalLicense': ['Public', 'Institution', 'Legal', 'Person', 'Entity', 'Unified', 'Social', 'Credit', 'Code', 'Registered', 'Address', 'Business', 'Term', 'Legal', 'Representative', 'Registered', 'Capital'],
    'businessLicense': ['Business', 'License', 'Entity', 'Unified', 'Social', 'Credit', 'Code', 'Registered', 'Address', 'Business', 'Term', 'Legal', 'Representative', 'Start-up', 'Fund'],
    'socialSecurityCertificate': ['Social', 'Security', 'Certificate', 'Entity', 'Policyholder', 'Social', 'Security', 'Number', 'Insurance', 'Type', 'Contribution', 'Start', 'End', 'Month-Year'],
    'ID': ['ID', 'Identity', 'Card', 'Holder', 'Identity', 'Card', 'Number', 'Gender', 'DOB'],
    'ISO9001': ['ISO9001', 'Quality', 'Management', 'System', 'Certification', 'Entity', 'Initial', 'Issuance', 'Date', 'Current', 'Expiration', 'Compliance', 'Standard'],
    'ISO14001': ['ISO14001', 'Environmental', 'Management', 'System', 'Certification', 'Entity', 'Initial', 'Issuance', 'Date', 'Current', 'Expiration', 'Compliance', 'Standard'],
    'SA8000': ['SA8000', 'Social', 'Accountability', 'Certification', 'Entity', 'Initial', 'Issuance', 'Date', 'Current', 'Expiration', 'Compliance', 'Standard'],
    'ISO45001': ['ISO45001', 'Occupational', 'Health', 'Safety', 'Management', 'System', 'Certification', 'Entity', 'Initial', 'Issuance', 'Date', 'Current', 'Expiration', 'Compliance', 'Standard'],
    'CSCRC': ['Computer', 'Software', 'Copyright', 'Registration', 'Certificate', 'Software', 'Name', 'Copyright', 'Owner', 'Completion', 'Development', 'First', 'Publication', 'Mode', 'Acquiring', 'Rights', 'Scope', 'Registration', 'Number'],
    'CESSCN_risk_eval': ['Telecommunication', 'Network', 'Security', 'Service', 'Capability', 'Certificate', 'Risk', 'Assessment', 'Entity', 'Issuing', 'Authority', 'Compliance', 'Standard', 'Initial', 'Certification', 'Date', 'Validity', 'Current', 'Issuance', 'Date', 'Certificate', 'Level'],
    'CESSCN_emergency_resp': ['Telecommunication', 'Network', 'Security', 'Service', 'Capability', 'Certificate', 'Emergency', 'Response', 'Entity', 'Issuing', 'Authority', 'Compliance', 'Standard', 'Initial', 'Certification', 'Date', 'Validity', 'Current', 'Issuance', 'Date', 'Certificate', 'Level'],
    'CESSCN_design_inte': ['Telecommunication', 'Network', 'Security', 'Service', 'Capability', 'Certificate', 'Design', 'Integration', 'Entity', 'Issuing', 'Authority', 'Compliance', 'Standard', 'Initial', 'Certification', 'Date', 'Validity', 'Current', 'Issuance', 'Date', 'Certificate', 'Level'],
    'CESSCN_safety_train': ['Telecommunication', 'Network', 'Security', 'Service', 'Capability', 'Certificate', 'Security', 'Training', 'Entity', 'Issuing', 'Authority', 'Compliance', 'Standard', 'Initial', 'Certification', 'Date', 'Validity', 'Current', 'Issuance', 'Date', 'Certificate', 'Level'],
    'PCI': ['Patent', 'Certificate', 'Invention', 'Invention', 'Name', 'Inventor', 'Patent', 'Number', 'Application', 'Date', 'Patentee', 'Address', 'Authorization', 'Announcement', 'Date', 'Number']
}