# import PyPDF2
# import docx

# def extract_text_from_pdf(file):
#     text = ""
#     reader = PyPDF2.PdfReader(file)
#     for page in reader.pages:
#         text += page.extract_text()
#     return text

# def extract_text_from_docx(file):
#     doc = docx.Document(file)
#     text = "\n".join([para.text for para in doc.paragraphs])
#     return text

# def extract_text_from_txt(file):
#     return file.read().decode('utf-8')

# def extract_text(file):
#     filename = file.name.lower()

#     if filename.endswith('.pdf'):
#         return extract_text_from_pdf(file)
#     elif filename.endswith('.docx'):
#         return extract_text_from_docx(file)
#     elif filename.endswith('.txt'):
#         return extract_text_from_txt(file)
#     else:
#         raise ValueError("Unsupported file format")


import spacy

# spaCy model load karein (Ensure karein ki yeh install ho)
nlp = spacy.load("en_core_web_sm")

# Predefined job domains ka ek mapping
JOB_DOMAINS = {
    "data scientist": ["machine learning", "data science", "deep learning", "AI", "analytics"],
    "software engineer": ["programming", "development", "software", "engineering"],
    "marketing": ["branding", "advertising", "SEO", "digital marketing"],
    "sales": ["selling", "customer relationship", "sales management"],
    "finance": ["accounting", "investment", "banking", "financial analysis"],
    "human resources": ["recruitment", "HR", "human resources", "employee relations"]
}

def extract_domain(text):
    """
    Resume ya Job Description ka domain extract karne ke liye NER-based function.
    """
    doc = nlp(text.lower())  # Lowercase convert karein for uniformity
    extracted_keywords = set([token.text for token in doc if token.is_alpha])

    for domain, keywords in JOB_DOMAINS.items():
        if any(keyword in extracted_keywords for keyword in keywords):
            return domain  # Pehli matching domain return karein

    return "unknown"  # Agar koi domain match nahi kare to unknown return karein
