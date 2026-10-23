from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["last_name", "first_names", "commune", "level", "program", "class_group", "bus_choice", "submitted_at", "phone", "notes"]
        widgets = {"submitted_at": forms.DateTimeInput(attrs={"type": "datetime-local"}), "notes": forms.Textarea(attrs={"rows": 2})}
    def clean(self):
        data = super().clean()
        level, program = data.get("level"), data.get("program")
        if program and level and program.level_id != level.id:
            self.add_error("program", "Cette filière n'appartient pas à la licence choisie.")
        return data
