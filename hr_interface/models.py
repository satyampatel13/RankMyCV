from django.db import models

class Resume(models.Model):
    candidate_name = models.CharField(max_length=255)  # Candidate name ya file ka naam
    resume_text = models.TextField()  # Pura extracted resume ka text
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Upload ka timestamp

    def __str__(self):
        return self.candidate_name

