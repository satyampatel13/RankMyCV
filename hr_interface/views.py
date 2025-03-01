from django.shortcuts import render
from django.http import HttpResponse
import PyPDF2
import fitz
import docx
import spacy
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Load NLP models
nlp = spacy.load("en_core_web_sm")
bert_model = SentenceTransformer('bert-base-nli-mean-tokens')

# Sample skills list
SKILL_LIST = ["Python", "Django", "Machine Learning", "Deep Learning", "NLP",
              "SQL", "Java", "JavaScript", "React", "Node.js", "TensorFlow",
              "PyTorch", "HTML", "CSS", "Data Analysis", "AWS", "Docker"]

# 🔹 Function to extract skills
def extract_skills(text):
    doc = nlp(text)
    extracted_skills = set()

    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT", "WORK_OF_ART"]:
            extracted_skills.add(ent.text)

    for token in doc:
        if token.text in SKILL_LIST:
            extracted_skills.add(token.text)

    return list(extracted_skills)

# 🔹 Function to extract job title and domain
def extract_domain(text):
    doc = nlp(text)
    job_titles = []
    education = []
    
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG"]:  # Extract job-related entities
            job_titles.append(ent.text)
        if ent.label_ in ["EDUCATION", "DEGREE"]:  # Extract education
            education.append(ent.text)

    return {
        "job_titles": job_titles,
        "education": education
    }


def extract_text(file):
    extension = file.name.split('.')[-1].lower()
    try:
        if extension == 'pdf':
            text = ""
            with fitz.open(stream=file.read(), filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text("text")  # Better structured extraction
            return text

        elif extension == 'docx': 
            doc = docx.Document(file)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text

        elif extension == 'txt':
            return file.read().decode('utf-8')

    except Exception as e:
        return ""


# 🔹 BERT-based similarity function
def get_bert_similarity(job_desc, resumes):
    texts = [job_desc] + resumes
    embeddings = bert_model.encode(texts)
    job_embedding = embeddings[0].reshape(1, -1)
    resume_embeddings = embeddings[1:]
    similarities = cosine_similarity(job_embedding, resume_embeddings).flatten()
    return similarities

# 🔥 Main Function: Job Description Processing
def job_description(request):
    if request.method == 'POST':
        request.session['uploaded_resumes'] = []

        job_desc = request.POST.get('job_description', "").strip()
        if not job_desc:
            return render(request, 'hr_interface/job_description.html', {
                'error_message': "Job description cannot be empty."
            })

        uploaded_files = request.FILES.getlist('resumes')
        if not uploaded_files:
            return render(request, 'hr_interface/job_description.html', {
                'error_message': "No resumes uploaded. Please upload at least one resume."
            })

        max_file_size = 5 * 1024 * 1024  
        for file in uploaded_files:
            if file.size > max_file_size:
                return render(request, 'hr_interface/job_description.html', {
                    'error_message': f"File {file.name} is too large. Max allowed size is 5 MB."
                })

        extracted_data = []
        for file in uploaded_files:
            extracted_text = extract_text(file)
            skills = extract_skills(extracted_text)  
            domain_info = extract_domain(extracted_text)  # 🔥 Extract job title & education
            
            extracted_data.append({
                'file_name': file.name,
                'extracted_text': extracted_text,
                'extracted_skills': skills,
                'domain_info': domain_info
            })

        request.session['uploaded_resumes'] = extracted_data

        # 🔥 Extract Required Skills & Domain from Job Description
        required_skills = extract_skills(job_desc)
        job_domain = extract_domain(job_desc)  # 🔥 Extract domain from JD

        resume_texts = [data['extracted_text'] for data in extracted_data]
        candidate_names = [data['file_name'] for data in extracted_data]

        # 🔥 Compute BERT Similarity Score
        similarity_scores = get_bert_similarity(job_desc, resume_texts)

        # 🔥 Apply Domain-Based Filtering
        final_scores = []
        for idx, data in enumerate(extracted_data):
            resume_domain = data['domain_info']
            domain_matched = False

            # 🔹 Compare extracted job titles & education
            for job_title in resume_domain["job_titles"]:
                if job_title in job_domain["job_titles"]:
                    domain_matched = True
                    break

            for edu in resume_domain["education"]:
                if edu in job_domain["education"]:
                    domain_matched = True
                    break

            # 🔥 If domain does NOT match, set score near-zero
            if not domain_matched:
                final_scores.append(0.01)
            else:
                final_scores.append(similarity_scores[idx])

        # 🔥 Rank resumes based on final scores
        ranked_results = sorted(zip(candidate_names, final_scores, extracted_data), key=lambda x: x[1], reverse=True)
        ranked_results_with_ranks = [(index + 1, result[0], result[1], result[2]) for index, result in enumerate(ranked_results)]

        return render(request, 'hr_interface/ranked_results.html', {
            'ranked_results': ranked_results_with_ranks,
            'required_skills': required_skills
        })

    return render(request, 'hr_interface/job_description.html')