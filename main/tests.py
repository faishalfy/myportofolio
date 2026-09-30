from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Education, Experience, Project


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")

    def test_education_url_uses_correct_template(self) :
        response = self.client.get(reverse("main:show_education"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education.html")

    def test_education_data_appears_on_page(self) :
        Education.objects.create(
            institution="SMA Semesta",
            education_level="SMA",
            study_program="Science",
            start_year=2022,
            end_year=2025,
            logo_url="https://semesta.sch.id/wp-content/uploads/2025/09/cropped-Logo-Semesta-2017-200x200-1-1.png",
        )

        response = self.client.get(reverse("main:show_education"))

        self.assertContains(response, "SMA Semesta")
        self.assertContains(response, "SMA")
        self.assertContains(response, "Science")

    def test_empty_education_page_shows_message(self) :
        response = self.client.get(reverse("main:show_education"))

        self.assertContains(
            response,
            "Belum ada riwayat pendidikan yang ditambahkan"
        )


class AuthorizationAndStarTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title="Portfolio Project",
            description="Project description",
            tech_stack="Django",
        )
        self.education = Education.objects.create(
            institution="Universitas Indonesia",
            education_level="S1",
            study_program="Ilmu Komputer",
            start_year=2022,
            end_year=2026,
        )

        self.regular = User.objects.create_user(
            username="regular",
            password="password",
        )
        self.editor_group = Group.objects.create(name="Editor")
        self.editor = User.objects.create_user(
            username="editor",
            password="password",
        )
        self.editor.groups.add(self.editor_group)
        self.superuser = User.objects.create_superuser(
            username="superuser",
            password="password",
            email="superuser@example.com",
        )

    def project_payload(self, title="Updated Project"):
        return {
            "title": title,
            "description": "Updated description",
            "tech_stack": "Django, Python",
            "project_url": "",
            "project_image_url": "",
        }

    def education_payload(self, institution="Updated University"):
        return {
            "institution": institution,
            "education_level": "S1",
            "study_program": "Ilmu Komputer",
            "start_year": 2022,
            "end_year": 2026,
            "logo_url": "",
        }

    def test_anonymous_write_actions_redirect_to_login(self):
        urls = [
            reverse("main:create_project"),
            reverse("main:create_education"),
            reverse("main:update_project", args=[self.project.id]),
            reverse("main:update_education", args=[self.education.id]),
            reverse("main:delete_project", args=[self.project.id]),
            reverse("main:delete_education", args=[self.education.id]),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse("main:login"), response["Location"])

    def test_regular_user_cannot_create_update_or_delete(self):
        self.client.force_login(self.regular)
        create_actions = [
            (reverse("main:create_project"), self.project_payload()),
            (reverse("main:create_education"), self.education_payload()),
        ]
        update_actions = [
            reverse("main:update_project", args=[self.project.id]),
            reverse("main:update_education", args=[self.education.id]),
        ]
        delete_actions = [
            reverse("main:delete_project", args=[self.project.id]),
            reverse("main:delete_education", args=[self.education.id]),
        ]

        for url, data in create_actions:
            with self.subTest(action="create", url=url):
                self.assertEqual(self.client.post(url, data).status_code, 403)
        for url in update_actions:
            with self.subTest(action="update", url=url):
                self.assertEqual(self.client.get(url).status_code, 403)
        for url in delete_actions:
            with self.subTest(action="delete", url=url):
                self.assertEqual(self.client.post(url).status_code, 403)

    def test_editor_can_update_but_cannot_create_or_delete(self):
        self.client.force_login(self.editor)

        self.assertEqual(
            self.client.post(
                reverse("main:create_project"), self.project_payload()
            ).status_code,
            403,
        )
        self.assertEqual(
            self.client.post(
                reverse("main:create_education"), self.education_payload()
            ).status_code,
            403,
        )
        self.assertEqual(
            self.client.post(
                reverse("main:delete_project", args=[self.project.id])
            ).status_code,
            403,
        )
        self.assertEqual(
            self.client.post(
                reverse("main:delete_education", args=[self.education.id])
            ).status_code,
            403,
        )

        project_response = self.client.post(
            reverse("main:update_project", args=[self.project.id]),
            self.project_payload("Editor Project"),
        )
        education_response = self.client.post(
            reverse("main:update_education", args=[self.education.id]),
            self.education_payload("Editor University"),
        )

        self.assertRedirects(project_response, reverse("main:show_projects"))
        self.assertRedirects(education_response, reverse("main:show_education"))
        self.assertEqual(Project.objects.get(pk=self.project.id).title, "Editor Project")
        self.assertEqual(
            Education.objects.get(pk=self.education.id).institution,
            "Editor University",
        )

    def test_superuser_can_create_update_and_delete(self):
        self.client.force_login(self.superuser)

        create_project_response = self.client.post(
            reverse("main:create_project"), self.project_payload("New Project")
        )
        create_education_response = self.client.post(
            reverse("main:create_education"),
            self.education_payload("New University"),
        )
        self.assertRedirects(create_project_response, reverse("main:show_projects"))
        self.assertRedirects(create_education_response, reverse("main:show_education"))
        self.assertTrue(Project.objects.filter(title="New Project").exists())
        self.assertTrue(Education.objects.filter(institution="New University").exists())

        update_project_response = self.client.post(
            reverse("main:update_project", args=[self.project.id]),
            self.project_payload("Superuser Project"),
        )
        update_education_response = self.client.post(
            reverse("main:update_education", args=[self.education.id]),
            self.education_payload("Superuser University"),
        )
        self.assertRedirects(update_project_response, reverse("main:show_projects"))
        self.assertRedirects(update_education_response, reverse("main:show_education"))

        delete_project_response = self.client.post(
            reverse("main:delete_project", args=[self.project.id])
        )
        delete_education_response = self.client.post(
            reverse("main:delete_education", args=[self.education.id])
        )
        self.assertRedirects(delete_project_response, reverse("main:show_projects"))
        self.assertRedirects(delete_education_response, reverse("main:show_education"))
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())
        self.assertFalse(Education.objects.filter(pk=self.education.id).exists())

    def test_star_can_be_added_cancelled_and_counted(self):
        self.project.starred_by.add(self.editor)
        self.client.force_login(self.regular)
        url = reverse("main:toggle_star", args=[self.project.id])

        add_response = self.client.post(url)
        self.assertRedirects(add_response, reverse("main:show_projects"))
        self.assertTrue(self.project.starred_by.filter(pk=self.regular.pk).exists())
        self.assertEqual(self.project.starred_by.count(), 2)

        cancel_response = self.client.post(url)
        self.assertRedirects(cancel_response, reverse("main:show_projects"))
        self.assertFalse(self.project.starred_by.filter(pk=self.regular.pk).exists())
        self.assertEqual(self.project.starred_by.count(), 1)

    def test_projects_api_does_not_expose_starred_by(self):
        self.project.starred_by.add(self.editor)

        response = self.client.get(reverse("main:get_projects_json"))

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("starred_by", response.content.decode())
        self.assertEqual(
            set(response.json()[0]["fields"]),
            {
                "title",
                "description",
                "tech_stack",
                "project_url",
                "project_image_url",
            },
        )

    def test_action_buttons_are_hidden_by_role(self):
        project_edit_url = reverse("main:update_project", args=[self.project.id])
        project_delete_url = reverse("main:delete_project", args=[self.project.id])
        education_edit_url = reverse(
            "main:update_education", args=[self.education.id]
        )
        education_delete_url = reverse(
            "main:delete_education", args=[self.education.id]
        )
        roles = [
            ("anonymous", None, False, False),
            ("regular", self.regular, False, True),
            ("editor", self.editor, True, True),
            ("superuser", self.superuser, True, True),
        ]

        for name, user, can_edit, can_star in roles:
            self.client.logout()
            if user:
                self.client.force_login(user)
            with self.subTest(role=name):
                project_response = self.client.get(reverse("main:show_projects"))
                education_response = self.client.get(reverse("main:show_education"))

                for response, marker, visible in [
                    (project_response, 'popovertarget="add-project-modal"', user and user.is_superuser),
                    (project_response, f'href="{project_edit_url}"', can_edit),
                    (project_response, f'action="{project_delete_url}"', user and user.is_superuser),
                    (education_response, reverse("main:create_education"), user and user.is_superuser),
                    (education_response, f'href="{education_edit_url}"', can_edit),
                    (education_response, f'action="{education_delete_url}"', user and user.is_superuser),
                ]:
                    if visible:
                        self.assertContains(response, marker)
                    else:
                        self.assertNotContains(response, marker)

                star_url = reverse("main:toggle_star", args=[self.project.id])
                if can_star:
                    self.assertContains(project_response, f'action="{star_url}"')
                    self.assertNotContains(project_response, "Login untuk memberi star")
                else:
                    self.assertContains(project_response, "Login untuk memberi star")
