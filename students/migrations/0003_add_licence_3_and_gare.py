from django.db import migrations

def add_programs(apps, schema_editor):
    Level = apps.get_model("students", "StudyLevel")
    Program = apps.get_model("students", "Program")
    l1 = Level.objects.get(slug="licence-1")
    l2 = Level.objects.get(slug="licence-2")
    l3, _ = Level.objects.get_or_create(
        slug="licence-3",
        defaults={"name": "Licence 3", "order": 3},
    )
    for level in (l1, l2):
        Program.objects.get_or_create(
            level=level,
            name="GARE",
            defaults={"slug": "gare", "order": 5},
        )
    for order, name in enumerate(("DSER", "MDIG", "LNUM", "FDIG"), 1):
        Program.objects.get_or_create(
            level=l3,
            name=name,
            defaults={"slug": name.lower(), "order": order},
        )

def remove_programs(apps, schema_editor):
    Level = apps.get_model("students", "StudyLevel")
    Program = apps.get_model("students", "Program")
    Program.objects.filter(level__slug="licence-1", name="GARE").delete()
    Level.objects.filter(slug="licence-3").delete()

class Migration(migrations.Migration):
    dependencies = [("students", "0002_student_local_override")]
    operations = [migrations.RunPython(add_programs, remove_programs)]
