from django.forms import ModelForm, Select, Textarea, TextInput

from .models import Snippet


class SnippetForm(ModelForm):
    class Meta:
        model = Snippet
        fields = ["name", "description", "language", "public", "snippet"]
        labels = {
            "name": "Nombre",
            "description": "Descripción",
            "language": "Lenguaje",
            "public": "Público",
            "snippet": "Snippet",
        }
        widgets = {
            "name": TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre del snippet"}
            ),
            "description": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Descripción del snippet",
                }
            ),
            "language": Select(attrs={"class": "form-control"}),
            "snippet": Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "/* Código del snippet */",
                }
            ),
        }
