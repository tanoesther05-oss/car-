from django.db import models

class StudyLevel(models.Model):
    name = models.CharField("Licence", max_length=80, unique=True)
    slug = models.SlugField(unique=True)
    order = models.PositiveSmallIntegerField(default=0)
    def __str__(self): return self.name
    class Meta: ordering = ["order", "name"]

class Program(models.Model):
    level = models.ForeignKey(StudyLevel, on_delete=models.CASCADE, related_name="programs")
    name = models.CharField("Filière", max_length=80)
    slug = models.SlugField()
    order = models.PositiveSmallIntegerField(default=0)
    def __str__(self): return f"{self.level} — {self.name}"
    class Meta:
        ordering = ["level__order", "order", "name"]
        constraints = [models.UniqueConstraint(fields=["level", "name"], name="unique_program_per_level")]

class Student(models.Model):
    class BusChoice(models.TextChoices):
        YES = "yes", "Oui"
        NO = "no", "Non"
        REVIEW = "review", "À vérifier"
    last_name = models.CharField("Nom", max_length=120)
    first_names = models.CharField("Prénom(s)", max_length=160)
    commune = models.CharField("Commune", max_length=120, blank=True)
    level = models.ForeignKey(StudyLevel, null=True, blank=True, on_delete=models.SET_NULL, related_name="students")
    program = models.ForeignKey(Program, null=True, blank=True, on_delete=models.SET_NULL, related_name="students")
    class_group = models.CharField("Classe / groupe", max_length=120, blank=True)
    bus_choice = models.CharField("Souhaite prendre le car", max_length=10, choices=BusChoice.choices, default=BusChoice.REVIEW)
    submitted_at = models.DateTimeField("Date de soumission", null=True, blank=True)
    phone = models.CharField("Téléphone", max_length=40, blank=True)
    source_key = models.CharField(max_length=64, unique=True, null=True, blank=True, db_index=True)
    source_row = models.PositiveIntegerField(null=True, blank=True)
    local_override = models.BooleanField("Conserver les modifications locales", default=False)
    notes = models.TextField("Notes de vérification", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering = ["last_name", "first_names"]
    def __str__(self): return f"{self.last_name} {self.first_names}"
    @property
    def classification_needs_review(self): return not self.level_id or not self.program_id or self.program.level_id != self.level_id

class SyncLog(models.Model):
    source = models.CharField(max_length=20)
    started_at = models.DateTimeField(auto_now_add=True)
    created = models.PositiveIntegerField(default=0)
    updated = models.PositiveIntegerField(default=0)
    ignored = models.PositiveIntegerField(default=0)
    errors = models.PositiveIntegerField(default=0)
    details = models.TextField(blank=True)
