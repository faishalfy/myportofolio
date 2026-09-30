from django.forms import ModelForm, TextInput, Textarea, URLInput
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
from main.models import Education, Project

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "tech_stack",
            "project_url",
            "project_image_url",
        ]

        labels = {
            "title": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "tech_stack": "Teknologi yang Digunakan",
            "project_url": "URL Proyek",
            "project_image_url": "URL Gambar Proyek",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Portfolio Website",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan Proyekmu",
                    "rows": 3,
                }
            ),
            "tech_stack": TextInput(
                attrs={
                    "placeholder": "Django, Python, HTML, CSS",
                }
            ),
            "project_url": URLInput(
                attrs={
                    "placeholder": "https://github.com/kakBurhan/burhanquestv4",
                }
            ),
            "project_image_url": URLInput(
                attrs={
                    "placeholder": "https://drive.google.com/thumbnail?id=FILE_ID&sz=w1000",
                }
            ),
        }

    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()
        if not title:
            raise ValidationError("Nama proyek tidak boleh hanya berisi tag HTML.")
        return title

    def clean_tech_stack(self):
        return strip_tags(self.cleaned_data["tech_stack"]).strip()

    def clean_description(self):
        return strip_tags(self.cleaned_data["description"]).strip()

class EducationForm(ModelForm):
    class Meta:
        model = Education
        fields = [
            "institution",
            "education_level",
            "study_program",
            "start_year",
            "end_year",
            "logo_url",
        ]

        labels = {
            "institution" : "Nama Universitas",
            "education_level" : "Strata",
            "study_program" : "Program Studi",
            "start_year" : "Tahun Masuk",
            "end_year" : "Tahun Lulus",
            "logo_url" : "URL Gambar Universitas",            
        }

        widgets = {
        "institution": TextInput(
            attrs={
                "placeholder": "Standford University",
                "maxlength": 255,
            }
        ),
        "education_level": TextInput(
            attrs={
                "placeholder": "PhD",
            }
        ),
        "study_program": TextInput(
            attrs={
                "placeholder": "Computer Science",
            }
        ),
        "start_year": TextInput(
            attrs={
                "placeholder": "2025",
            }
        ),
        "end_year": TextInput(
            attrs={
                "placeholder": "2029",
            }
        ),
        "logo_url": URLInput(
            attrs={
                "placeholder": "https://id.wikipedia.org/wiki/Universitas_Stanford",
            }
        ),        
    }       
