from django import forms

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True  # Enabling multiple file selection

class ResumeUploadForm(forms.Form):
    job_title = forms.CharField(
        max_length=255,
        label="Job Title",
        widget=forms.TextInput(attrs={"placeholder": "Enter Job Title"})
    )

    resumes = forms.FileField(
        widget=MultipleFileInput(attrs={'multiple': True}),
        label="Upload Resumes (PDF, DOCX, TXT only)"
    )

    def clean_resumes(self):
        files = self.files.getlist('resumes')
        allowed_extensions = ['pdf', 'docx', 'txt']

        for file in files:
            if not any(file.name.lower().endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError(f"Invalid file type: {file.name}. Only PDF, DOCX, and TXT files are allowed.")
        return files
