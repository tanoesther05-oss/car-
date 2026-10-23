import io
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import StudyLevel, Program, Student
from .services import import_rows

class ImportTests(TestCase):
    def setUp(self):
        self.l1 = StudyLevel.objects.get(slug="licence-1")
        self.l2 = StudyLevel.objects.get(slug="licence-2")

    def test_same_rows_update_instead_of_duplicate(self):
        headers = ["Nom", "Prénom(s)", "Commune", "Niveau", "Filière", "Car"]
        rows = [["Doe", "Jane", "Abobo", "Licence 2", "DSER", "Oui"]]
        first = import_rows(headers, rows)
        second = import_rows(headers, rows)
        self.assertEqual(first.created, 1)
        self.assertEqual(second.updated, 1)
        self.assertEqual(Student.objects.count(), 1)

    def test_gare_classifies_in_level_one_and_two_but_not_three(self):
        headers = ["Nom", "Prénom", "Niveau", "Filière"]
        import_rows(headers, [["One", "A", "Licence 1", "GARE"], ["Two", "B", "Licence 2", "GARE"]])
        one = Student.objects.get(last_name="One")
        two = Student.objects.get(last_name="Two")
        self.assertIsNotNone(one.program)
        self.assertEqual(one.program.level, self.l1)
        self.assertIsNotNone(two.program)
        self.assertEqual(two.program.level, self.l2)

    def test_catalog_has_three_levels_and_gare_only_in_first_two(self):
        l3 = StudyLevel.objects.get(slug="licence-3")
        self.assertTrue(Program.objects.filter(level=self.l1, name="GARE").exists())
        self.assertTrue(Program.objects.filter(level=self.l2, name="GARE").exists())
        self.assertFalse(Program.objects.filter(level=l3, name="GARE").exists())

    def test_level_page_renders_for_authenticated_admin(self):
        get_user_model().objects.create_user(username="viewer", password="strong-password-123")
        self.client.login(username="viewer", password="strong-password-123")
        response = self.client.get("/licence/licence-1/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "DSER")
        self.assertContains(response, "Afficher les étudiants")

    def test_missing_choice_is_review(self):
        import_rows(["Nom", "Prénom"], [["A", "B"]])
        self.assertEqual(Student.objects.get().bus_choice, Student.BusChoice.REVIEW)

    def test_local_edit_is_preserved_by_next_import(self):
        headers = ["Nom", "Prénom", "Commune", "Niveau", "Filière", "Car"]
        row = ["Doe", "Jane", "Abobo", "Licence 2", "DSER", "Oui"]
        import_rows(headers, [row])
        student = Student.objects.get()
        student.commune = "Cocody"
        student.local_override = True
        student.save()
        log = import_rows(headers, [row])
        student.refresh_from_db()
        self.assertEqual(student.commune, "Cocody")
        self.assertEqual(log.ignored, 1)

    def test_admin_pages_require_authentication(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_dashboard_shows_database_counts_when_logged_in(self):
        user = get_user_model().objects.create_user(username="admin", password="strong-password-123")
        self.client.login(username="admin", password="strong-password-123")
        Student.objects.create(last_name="Doe", first_names="Jane", level=self.l2, program=Program.objects.get(level=self.l2, name="DSER"), bus_choice="yes")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Répartition par licence")
