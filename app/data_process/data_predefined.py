target_type_num_mapping_en = {
    1: 'academicCertificate', # Academic Qualification Certificate
    2: 'degreeCertificate', # Degree Certificate
    3: 'legalLicense', # Public Institution Legal Person Certificate
    4: 'businessLicense', # Business License
    5: 'socialSecurityCertificate', # Social Security Certificate
    6: 'ID', # ID Identity Card
    7: 'ISO9001', # ISO 9001 Certification
    8: 'ISO14001', # ISO 14001 Certification
    9: 'SA8000', # SA 8000 Certification
    10: 'ISO45001', # ISO 45001 Certification
    11: 'CSCRC', # Computer Software Copyright Registration Certificate
    12: 'CESSCN_risk_eval', # TNSSCC (Risk Assessment)
    13: 'CESSCN_emergency_resp', # TNSSCC (Emergency Response)
    14: 'CESSCN_design_inte', # TNSSCC (Design & Integration)
    15: 'CESSCN_safety_train', # TNSSCC (Security Training)
    16: 'PCI' # Patent Certificate for Invention
}
target_type_list_en = list(target_type_num_mapping_en.values())

llm_extract_sys_text = "You can perform OCR on images and return specific key information in JSON format."


shared_prompt = """
You are an intelligent visual information extraction system that automatically extracts the content of specific entities from an image and outputs the results in a specified structured format. This is a {type_name} document from the Chinese mainland.

Document background and purpose: {background_description}
Typical layout & spatial hints: {layout_hints}

Strict rules:
1. Identify and extract key field information from the given document image, returning the information in JSON format. Required fields: {landmarks}
2. Return data strictly in JSON format without any non-JSON characters or structures, and without additional explanations.
3. Do not modify the return fields. Return only specified fields. If a field is missing/unrecognized, return "unidentified".
4. Rotate the image to 0 degrees if text orientation is not horizontal.
5. If no signature is detected, set "hasSignature" to "False"; if detected, set to "True".
6. If no seal is detected, set "hasSeal" to "False"; if detected, set to "True".
"""


type_specific_info = {
    'academicCertificate': {
        'type_name': 'Academic Qualification Certificate',
        'background_description': 'Official certificate issued by educational authorities or institutions in mainland China to prove an individual\'s educational qualifications. It is commonly required for employment, further education, or professional qualification applications.',
        'layout_hints': 'Document typically has a prominent title at the top center (e.g., "毕业证书" or "学历证书"), followed by certificate number. Personal information (name, gender, date of birth) is usually in the left or middle section. Educational details (major, educational level, graduation date) follow. Institution name, signature, and official seal are at the bottom. Seal is typically red and circular, placed over photo or near signature.',
        'landmarks_list': ['Certificate Holder Name', 'Gender', 'DOB', 'Major/Field', 'Edu. Level', 'Grad. Date', 'Cert. No.', 'Sch. Name', 'hasSignature', 'hasSeal', 'Seal Name']
    },
    'degreeCertificate': {
        'type_name': 'Degree Certificate',
        'background_description': 'Official certificate issued by higher education institutions in mainland China to confer academic degrees (Bachelor, Master, Doctor). It certifies completion of degree requirements and is essential for employment verification and professional licensing.',
        'layout_hints': 'Typically begins with "学位证书" title at top center. Certificate number follows. Holder\'s personal details (name, gender, date of birth) are in upper section. Degree information (degree level, major, conferral date) in middle. University name, signature of university head, and official seal at bottom. Seal is usually circular red stamp placed over holder\'s photo or near bottom right.',
        'landmarks_list': ['Holder Name', 'Gender', 'DOB', 'Major/Field', 'Deg. Level', 'Grad. Date', 'Cert. No.', 'Sch. Name', 'hasSignature', 'hasSeal', 'Seal Name']
    },
    'legalLicense': {
        'type_name': 'Public Institution Legal Person Certificate',
        'background_description': 'Official registration certificate issued by institutional establishment authorities in mainland China for public institutions (事业单位). It certifies the legal person status, registration details, and operational scope of public institutions.',
        'layout_hints': 'Usually A4-sized with title "事业单位法人证书" at top. Key information is presented in a table format. Top section contains institution name and unified social credit code. Middle section includes registered address, legal representative, business term, and registered capital. Bottom has registration authority and issuance date. Official seal (typically circular) is stamped at bottom right or over photo.',
        'landmarks_list': ['Ent. Name', 'Unif. Soc. Credit Code', 'Reg. Addr.', 'Bus. Term', 'Leg. Rep.', 'Reg. Cap.', 'hasSeal', 'Registration Authority']
    },
    'businessLicense': {
        'type_name': 'Business License',
        'background_description': 'Standard business registration license issued by Chinese market regulation authorities (市场监管局) to legal entities. It certifies the enterprise\'s legal establishment, registration information, and permitted business scope.',
        'layout_hints': 'Rectangular document with "营业执照" title at top center. Unified social credit code is prominently displayed, often with QR code. Information is organized in a grid/table layout. Left side typically shows entity name, address, legal representative. Right side shows business term, registered capital/start-up fund. Official seal (circular red stamp) is usually at bottom right. Registration authority name is at bottom.',
        'landmarks_list': ['Ent. Name', 'Unif. Soc. Credit Code', 'Reg. Addr.', 'Bus. Term', 'Leg. Rep.', 'Start-up Fund', 'hasSeal', 'Registration Authority']
    },
    'socialSecurityCertificate': {
        'type_name': 'Social Security Certificate',
        'background_description': 'Official document issued by social security authorities in mainland China to certify an enterprise\'s social insurance contributions for its employees. Used for employment verification and social benefit claims.',
        'layout_hints': 'Document typically has title "社会保险登记证" or similar at top. Enterprise information (name, address) is in upper section. Middle section contains employee details in table format: policyholder names, social security numbers, insurance types. Bottom section shows contribution periods (start and end dates). Official seal (circular) is stamped at bottom right corner.',
        'landmarks_list': ['Ent. Name', 'NameofPH', 'Soc. Sec. No.', 'Ins. Type', 'Cont. Start M-Y', 'Cont. End M-Y', 'hasSeal', 'Seal Name']
    },
    'ID': {
        'type_name': 'Identity Card',
        'background_description': 'Official national identification card issued by Chinese public security authorities to citizens. Contains personal identification information and is used for identity verification in various official and commercial transactions.',
        'layout_hints': 'Standard credit-card sized document with polycarbonate material. Front side: National emblem at top left, "居民身份证" title, holder\'s photo on right, personal details (name, gender, ethnicity, date of birth, address, ID number) on left. Back side: Issuing authority, valid period, and citizen ID number barcode. All text is in Chinese with standardized layout.',
        'landmarks_list': ['Hold. Name', 'ID No.', 'Gender', 'DOB']
    },
    'ISO9001': {
        'type_name': 'ISO 9001 Quality Management Certification',
        'background_description': 'International quality management system certification issued by accredited certification bodies to organizations meeting ISO 9001 standards. Demonstrates commitment to quality management processes.',
        'layout_hints': 'Certificate typically has blue ISO logo at top left, certification body logo at top right. "Certificate of Registration" or similar title centered below. Main body contains organization name, address, scope of certification. Dates (initial issuance, current issuance, expiration) in lower section. Signatures of certification body officials at bottom. Official seals (usually multiple) stamped near signatures.',
        'landmarks_list': ['Ent. Name', 'Init. Iss. Date', 'Cur. Iss. Date', 'Exp. Date', 'Comp. Std.', 'hasSignature', 'hasSeal', 'Seal Name']
    },
    'ISO14001': {
        'type_name': 'ISO 14001 Environmental Management Certification',
        'background_description': 'International environmental management system certification issued to organizations meeting ISO 14001 standards. Demonstrates commitment to environmental management and sustainability.',
        'layout_hints': 'Similar to ISO9001 layout but with green color scheme. ISO logo at top, certification body logo. "Environmental Management System Certificate" title. Organization details in middle, certification scope, standard compliance. Dates and validity period clearly marked. Signatures and official seals at bottom.',
        'landmarks_list': ['Ent. Name', 'Init. Iss. Date', 'Cur. Iss. Date', 'Exp. Date', 'Comp. Std.', 'hasSignature', 'hasSeal', 'Seal Name']
    },
    'SA8000': {
        'type_name': 'SA 8000 Social Accountability Certification',
        'background_description': 'Social accountability certification based on international labor standards issued to organizations meeting SA8000 requirements. Focuses on working conditions, human rights, and ethical business practices.',
        'layout_hints': 'Certificate features SA8000 logo prominently. Layout similar to ISO certificates with certification body header. "SA8000 Certificate of Registration" title. Organization information, scope of certification, compliance standard. Validity dates and renewal information. Authorized signatures and certification body seal at bottom.',
        'landmarks_list': ['Ent. Name', 'Init. Iss. Date', 'Cur. Iss. Date', 'Exp. Date', 'Comp. Std.', 'hasSignature', 'hasSeal', 'Seal Name']
    },
    'ISO45001': {
        'type_name': 'ISO 45001 Occupational Health & Safety Certification',
        'background_description': 'International occupational health and safety management system certification for organizations meeting ISO 45001 standards. Demonstrates commitment to worker safety and health protection.',
        'layout_hints': 'Features ISO logo and certification body branding. "Occupational Health and Safety Management System Certificate" title. Organization details, certification scope, applicable standard. Key dates prominently displayed. Official signatures and certification body seals at bottom, often with multiple stamps.',
        'landmarks_list': ['Ent. Name', 'Init. Iss. Date', 'Cur. Iss. Date', 'Exp. Date', 'Comp. Std.', 'hasSignature', 'hasSeal', 'Seal Name']
    },
    'CSCRC': {
        'type_name': 'Computer Software Copyright Registration Certificate',
        'background_description': 'Official certificate issued by China National Copyright Administration (CNCA) for registered computer software copyrights. Provides legal protection for software intellectual property in China.',
        'layout_hints': 'Standard certificate format with "计算机软件著作权登记证书" red title at top. Certificate number below title. Software details (name, version) in upper section. Copyright owner information in middle. Development completion date, first publication date, rights information. Registration number at bottom. Official seal of Copyright Protection Center at bottom right.',
        'landmarks_list': ['SW Name', 'Copyr. Owner', 'Dev. Comp. Date', 'First Pub. Date', 'Acq. Rights Mode', 'Rights Scope', 'Reg. Num.']
    },
    'CESSCN_risk_eval': {
        'type_name': 'TNSSCC (Risk Assessment)',
        'background_description': 'Telecommunication Network Security Service Capability Certificate for risk assessment services, issued by Ministry of Industry and Information Technology (MIIT) authorized agencies. Certifies capability to provide cybersecurity risk assessment services.',
        'layout_hints': 'Certificate with blue theme, featuring MIIT/cybersecurity logos. "网络安全服务资质证书" title. Certificate level (一级/二级/三级) prominently displayed. Organization information, issuing authority, compliance standard. Validity period and dates clearly shown. Official seal of issuing authority at bottom center.',
        'landmarks_list': ['Ent. Name', 'Issuing Auth.', 'Comp. Std.', 'Init. Cert. Date', 'Validity', 'Cur. Iss. Date', 'Cert. Level', 'hasSeal', 'Seal Name']
    },
    'CESSCN_emergency_resp': {
        'type_name': 'TNSSCC (Emergency Response)',
        'background_description': 'Telecommunication Network Security Service Capability Certificate for emergency response services, issued by authorized agencies under MIIT. Certifies capability to provide cybersecurity emergency response services.',
        'layout_hints': 'Similar to risk assessment certificate but with different service type indicated. "网络安全服务资质证书" title with "应急处理" subtype. Certificate level displayed. Organization details, issuing authority information. Validity dates. Official seal of certification body at bottom.',
        'landmarks_list': ['Ent. Name', 'Issuing Auth.', 'Comp. Std.', 'Init. Cert. Date', 'Validity', 'Cur. Iss. Date', 'Cert. Level', 'hasSeal', 'Seal Name']
    },
    'CESSCN_design_inte': {
        'type_name': 'TNSSCC (Design & Integration)',
        'background_description': 'Telecommunication Network Security Service Capability Certificate for security design and integration services, issued by MIIT authorized agencies. Certifies capability to provide cybersecurity system design and integration services.',
        'layout_hints': 'Certificate format similar to other TNSSCC certificates with "设计集成" service type indicated. Blue/white color scheme with official logos. Certificate level, organization information, issuing authority. Validity period. Official seal stamped at bottom center or right.',
        'landmarks_list': ['Ent. Name', 'Issuing Auth.', 'Comp. Std.', 'Init. Cert. Date', 'Validity', 'Cur. Iss. Date', 'Cert. Level', 'hasSeal', 'Seal Name']
    },
    'CESSCN_safety_train': {
        'type_name': 'TNSSCC (Security Training)',
        'background_description': 'Telecommunication Network Security Service Capability Certificate for security training services, issued by authorized agencies under MIIT. Certifies capability to provide cybersecurity training and education services.',
        'layout_hints': 'Similar to other TNSSCC certificates with "安全培训" service type. Official logos, "网络安全服务资质证书" title. Certificate level, organization details, issuing authority information. Validity dates clearly marked. Official seal of certification body at bottom.',
        'landmarks_list': ['Ent. Name', 'Issuing Auth.', 'Comp. Std.', 'Init. Cert. Date', 'Validity', 'Cur. Iss. Date', 'Cert. Level', 'hasSeal', 'Seal Name']
    },
    'PCI': {
        'type_name': 'Patent Certificate for Invention',
        'background_description': 'Official patent certificate issued by China National Intellectual Property Administration (CNIPA) for granted invention patents. Provides legal protection for patented inventions in China.',
        'layout_hints': 'Certificate with golden decorative border, "发明专利证书" title in red at top. Patent number prominently displayed. Invention details (name, inventor, patentee) in upper section. Application date, authorization announcement details. Patentee address. Official seal of CNIPA at bottom right. Certificate number at bottom left.',
        'landmarks_list': ['Inv. Name', 'Invtr.', 'Pat. Num.', 'Pat. Appl. Date', 'Patee', 'Addr.', 'Auth. Ann. Date', 'Auth. Ann. Num.']
    }
}


text1 = "\n1. Identify and extract key field information from the given license image, returning the information in JSON format. Required fields:"
text2 = "\n2. Return data strictly in JSON format without any non-JSON characters or structures, and without additional explanations."
text3 = "\n3. Do not modify the return fields. Return only specified fields. If a field is missing/unrecognized, return \"unidentified\"."
text4 = "\n4. Rotate the image to 0 degrees if text orientation is not horizontal."
text5 = "\nIf no signature is detected, set \"hasSignature\" to \"False\"; if detected, set to \"True\"."
text6 = "\nIf no seal is detected, set \"hasSeal\" to \"False\"; if detected, set to \"True\"."


text_example_1 = "Return example: {\"Certificate Holder Name\": \"value\", \"Gender\": \"value\", \"DOB\": \"value\", \"Major/Field\": \"value\", \"Edu. Level\": \"value\", \"Grad. Date\": \"value\", \"Cert. No.\": \"value\", \"Sch. Name\": \"value\", \"hasSignature\": \"True/False\", \"hasSeal\": \"True/False\", \"Seal Name\": \"value\"}"
text_example_2 = "Return example: {\"Holder Name\": \"value\", \"Gender\": \"value\", \"DOB\": \"value\", \"Major/Field\": \"value\", \"Deg. Level\": \"value\", \"Grad. Date\": \"value\", \"Cert. No.\": \"value\", \"Sch. Name\": \"value\", \"hasSignature\": \"True/False\", \"hasSeal\": \"True/False\", \"Seal Name\": \"value\"}"
text_example_3 = "Return example: {\"Ent. Name\": \"value\", \"Unif. Soc. Credit Code\": \"value\", \"Reg. Addr.\": \"value\", \"Bus. Term\": \"value\", \"Leg. Rep.\": \"value\", \"Reg. Cap.\": \"value\", \"hasSeal\": \"True/False\", \"Registration Authority\": \"value\"}"
text_example_4 = "Return example: {\"Ent. Name\": \"value\", \"Unif. Soc. Credit Code\": \"value\", \"Reg. Addr.\": \"value\", \"Bus. Term\": \"value\", \"Leg. Rep.\": \"value\", \"Start-up Fund\": \"value\", \"hasSeal\": \"True/False\", \"Registration Authority\": \"value\"}"
text_example_5 = "Return example: {\"Ent. Name\": \"value\", \"NameofPH\": \"value\", \"Soc. Sec. No.\": \"value\", \"Ins. Type\": \"value\", \"Cont. Start M-Y\": \"value\", \"Cont. End M-Y\": \"value\", \"hasSeal\": \"True/False\", \"Seal Name\": \"value\"}"
text_example_6 = "Return example: {\"Hold. Name\": \"value\", \"ID No.\": \"value\", \"Gender\": \"value\", \"DOB\": \"value\"}"
text_example_7 = "Return example: {\"Ent. Name\": \"value\", \"Init. Iss. Date\": \"value\", \"Cur. Iss. Date\": \"value\", \"Exp. Date\": \"value\", \"Comp. Std.\": \"value\", \"hasSignature\": \"True/False\", \"hasSeal\": \"True/False\", \"Seal Name\": \"value\"}"   
text_example_8 = text_example_7   
text_example_9 = text_example_7  
text_example_10 = text_example_7  
text_example_11 = "Return example: {\"SW Name\": \"value\", \"Copyr. Owner\": \"value\", \"Dev. Comp. Date\": \"value\", \"First Pub. Date\": \"value\", \"Acq. Rights Mode\": \"value\", \"Rights Scope\": \"value\", \"Reg. Num.\": \"value\"}"
text_example_12 = "Return example: {\"Ent. Name\": \"value\", \"Issuing Auth.\": \"value\", \"Comp. Std.\": \"value\", \"Init. Cert. Date\": \"value\", \"Validity\": \"value\", \"Cur. Iss. Date\": \"value\", \"Cert. Level\": \"value\", \"hasSeal\": \"True/False\", \"Seal Name\": \"value\"}"   
text_example_13 = text_example_12
text_example_14 = text_example_12
text_example_15 = text_example_12
text_example_16 = "Return example: {\"Inv. Name\": \"value\", \"Invtr.\": \"value\", \"Pat. Num.\": \"value\", \"Pat. Appl. Date\": \"value\", \"Patee\": \"value\", \"Addr.\": \"value\", \"Auth. Ann. Date\": \"value\", \"Auth. Ann. Num.\": \"value\"}"



text_prompt_templates = {}
for type_num, doc_type in target_type_num_mapping_en.items():
    config = type_specific_info.get(doc_type, {'background_description': 'General certificate.', 'layout_hints': 'Standard document layout.', 'landmarks_list': []})
    landmarks_str = '", "'.join(config['landmarks_list'])
    

    type_shared = shared_prompt.format(
        type_name=config['type_name'],
        background_description=config['background_description'],
        layout_hints=config['layout_hints'],
        landmarks=landmarks_str
    )
    

    
    if type_num == 1:
        prompt = type_shared + f"{text1} \"{landmarks_str}\". {text2} {text_example_1} {text3} {text4} {text5} {text6}"
    elif type_num == 2:
        prompt = type_shared + f"{text1} \"{landmarks_str}\". {text2} {text_example_2} {text3} {text4} {text5} {text6}"
    elif type_num == 3:
        prompt = type_shared + f"{text1} \"{landmarks_str}\". {text2} {text_example_3} {text3} {text4} {text5} {text6}"
    elif type_num == 4:
        prompt = type_shared + f"{text1} \"{landmarks_str}\". {text2} {text_example_4} {text3} {text4} {text5} {text6}"
    elif type_num == 5:
        prompt = type_shared + f"{text1} \"{landmarks_str}\". {text2} {text_example_5} {text3} {text4} {text5} {text6}"
    elif type_num == 6:
        prompt = type_shared + f"{text1} \"{landmarks_str}\". {text2} {text_example_6} {text3} {text4} {text5} {text6}"
    elif type_num == 7:
        prompt = type_shared + f"{text1} \"{landmarks_str}\". {text2} {text_example_7} {text3} {text4} {text5} {text6}"
    elif type_num == 8:
        prompt = type_shared + f"{text1} \"{landmarks_str}\". {text2} {text_example_8} {text3} {text4} {text5} {text6}"
    elif type_num == 9:
        prompt = type_shared + f"{text1} \"{landmarks_str}\". {text2} {text_example_9} {text3} {text4} {text5} {text6}"
    elif type_num == 10:
        prompt = type_shared + f"{text1} \"{landmarks_str}\". {text2} {text_example_10} {text3} {text4} {text5} {text6}"
    elif type_num == 11:
        prompt = type_shared + f"{text1} \"{landmarks_str}\". {text2} {text_example_11} {text3} {text4} {text5} {text6}"
    elif type_num == 12:
        prompt = type_shared + f"{text1} \"{landmarks_str}\". {text2} {text_example_12} {text3} {text4} {text5} {text6}"
    elif type_num == 13:
        prompt = type_shared + f"{text1} \"{landmarks_str}\". {text2} {text_example_13} {text3} {text4} {text5} {text6}"
    elif type_num == 14:
        prompt = type_shared + f"{text1} \"{landmarks_str}\". {text2} {text_example_14} {text3} {text4} {text5} {text6}"
    elif type_num == 15:
        prompt = type_shared + f"{text1} \"{landmarks_str}\". {text2} {text_example_15} {text3} {text4} {text5} {text6}"
    elif type_num == 16:
        prompt = type_shared + f"{text1} \"{landmarks_str}\". {text2} {text_example_16} {text3} {text4} {text5} {text6}"
    else:
        prompt = type_shared + f"{text1} \"{landmarks_str}\". {text2} {text3} {text4} {text5} {text6}"
    
    text_prompt_templates[type_num] = prompt


def build_dynamic_prompt(type_num: int, num_examples: int = 3):
    doc_type = target_type_num_mapping_en[type_num]
    config = type_specific_info.get(doc_type, {})
    landmarks_str = '", "'.join(config.get('landmarks_list', []))
    
    prompt = shared_prompt.format(
        type_name=config.get('type_name', doc_type),
        background_description=config.get('background_description', 'Document from Chinese mainland.'),
        layout_hints=config.get('layout_hints', 'Standard document layout with title at top, information in middle, and seals/signatures at bottom.'),
        landmarks=landmarks_str
    )
    
    
    prompt += f"\nRequired fields: \"{landmarks_str}\"."
    
    
    return prompt


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