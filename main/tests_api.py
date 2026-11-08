import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from main.models import Education, Project


class ProjectAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser("owner", "owner@example.com", "test-password")
        self.visitor = User.objects.create_user("visitor", password="test-password")
        self.project = Project.objects.create(title="Portfolio", description="My website", tech_stack="Django")
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse("api:project-detail", args=[self.project.id])
        self.star_url = reverse("api:project-star", args=[self.project.id])
        self.payload = {
            "title": "New project", "description": "A useful app", "tech_stack": "Python",
            "project_url": "https://example.com/", "project_image_url": "",
        }

    def test_public_list_and_detail(self):
        self.project.starred_by.add(self.visitor)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["id"], str(self.project.id))
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])
        self.assertEqual(response.data[0]["starred_by_names"], "visitor")
        self.assertNotIn("email", response.data[0])
        self.assertNotIn("password", response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, 200)

    def test_search_and_empty_results(self):
        self.assertEqual(len(self.client.get(self.list_url, {"title": "PORT"}).data), 1)
        self.assertEqual(self.client.get(self.list_url, {"title": "missing"}).data, [])

    def test_missing_project(self):
        self.assertEqual(self.client.get(reverse("api:project-detail", args=[uuid.uuid4()])).status_code, 404)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio")

    def test_staff_and_editor_cannot_manage_tutorial_projects(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.visitor.groups.add(Group.objects.create(name="Editor"))
        self.client.force_authenticate(user=self.visitor)
        self.assertEqual(self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code, 403)

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists())

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"project_url": "javascript:alert(1)"}, "project_url"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, 400)
            self.assertIn(field, response.data)
        self.assertEqual(Project.objects.count(), 1)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True,
            "starred_by_names": "forged", "starred_by": [self.visitor.id],
        }, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.description, "My website")
        self.assertEqual(self.client.put(self.detail_url, {"title": "Incomplete"}, format="json").status_code, 400)
        self.assertEqual(self.client.put(self.detail_url, self.payload, format="json").status_code, 200)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, 405)

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, 403)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        self.assertEqual(client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        self.assertEqual(client.get(self.list_url, HTTP_ACCEPT="text/html").status_code, 200)
        token = client.cookies["csrftoken"].value
        self.assertEqual(client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        ).status_code, 201)


class EducationAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser("owner", "owner@example.com", "password")
        self.editor = User.objects.create_user("editor", password="password")
        self.editor.groups.add(Group.objects.create(name="Editor"))
        self.visitor = User.objects.create_user("visitor", password="password")
        self.education = Education.objects.create(
            institution="Universitas Indonesia", education_level="S1", start_year=2025,
        )
        self.list_url = reverse("api:education-list")
        self.detail_url = reverse("api:education-detail", args=[self.education.id])
        self.star_url = reverse("api:education-star", args=[self.education.id])
        self.payload = {"institution": "New School", "education_level": "S1", "start_year": 2026}

    def test_public_read_and_search(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.data[0]["institution"], "Universitas Indonesia")
        self.assertEqual(response.data[0]["star_count"], 0)
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("email", response.data[0])
        self.assertNotIn("password", response.data[0])
        self.assertEqual(len(self.client.get(self.list_url, {"q": "UNIVERSITAS"}).data), 1)
        self.assertEqual(self.client.get(self.list_url, {"q": "missing"}).data, [])
        self.assertEqual(self.client.get(self.detail_url).status_code, 200)
        self.client.force_authenticate(user=self.visitor)
        self.assertEqual(self.client.get(self.detail_url).status_code, 200)

    def test_guest_and_regular_user_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"institution": "Changed"}, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.education.refresh_from_db()
        self.assertEqual(self.education.institution, "Universitas Indonesia")
        self.assertEqual(Education.objects.count(), 1)

    def test_editor_can_patch_but_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(Education.objects.count(), 1)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertTrue(Education.objects.filter(pk=self.education.pk).exists())
        self.assertEqual(self.client.patch(self.detail_url, {"institution": "Updated"}, format="json").status_code, 200)
        self.education.refresh_from_db()
        self.assertEqual(self.education.institution, "Updated")

    def test_owner_can_create_update_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, 201)
        new_education_id = response.data["id"]
        self.assertTrue(Education.objects.filter(pk=new_education_id).exists())
        new_url = reverse("api:education-detail", args=[new_education_id])
        self.assertEqual(self.client.put(new_url, {
            **self.payload, "institution": "Replaced School",
        }, format="json").status_code, 200)
        self.assertEqual(self.client.delete(new_url).status_code, 204)
        self.assertFalse(Education.objects.filter(pk=new_education_id).exists())

    def test_validation_and_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        for invalid in ({"institution": "<b></b>"}, {"institution": "   "}):
            response = self.client.post(self.list_url, {**self.payload, **invalid}, format="json")
            self.assertEqual(response.status_code, 400)
            self.assertIn("institution", response.data)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True,
        }, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(Education.objects.count(), 2)

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, 403)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertTrue(self.education.starred_by.filter(pk=self.visitor.pk).exists())
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

        self.client.force_authenticate(user=self.editor)
        response = self.client.post(self.star_url)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)

    def test_missing_education_returns_404(self):
        self.assertEqual(self.client.get(reverse(
            "api:education-detail", args=[uuid.uuid4()],
        )).status_code, 404)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Education.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="password"))
        self.assertEqual(client.get(self.list_url, HTTP_ACCEPT="text/html").status_code, 200)
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 201)
