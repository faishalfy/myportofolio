from django.shortcuts import redirect, render
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required  # Tambahkan baris ini
from django.core.exceptions import PermissionDenied        # Tambahkan baris ini
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
import datetime
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from main.models import Education, Experience, Project
from main.forms import ProjectForm, EducationForm
from django.contrib import messages
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

def show_main(request):
    last_login = request.COOKIES.get('last_login', 'Belum ada sesi login / Cookie tidak ditemukan')
    context = {
        "name": "Faishal Falih",
        "npm": "2506612064",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "As a Computer Science student, I'm driven to build robust and scalable systems that effectively solve complex problems."
        ),
        "last_login": last_login,
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Faishal Falih",
    }
    return render(request, "experience.html", context)


def show_education(request):
    context = {
        "name": "Faishal Falih",
    }
    return render(request, "education.html", context)


def show_projects(request):
    projects = Project.objects.prefetch_related("starred_by")
    title_query = request.GET.get("title", "").strip()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    context = {
        "name": "Faishal Falih",
        "project_list": projects,
        "form": ProjectForm(),
        "title_query": title_query,
        "is_editor": is_editor(request.user),
    }
    return render(request, "project.html", context)

@login_required(login_url="/login/")
def create_project(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_projects")

    context = {
        "name": "Faishal Falih",
        "form": form,
    }
    return render(request, "projects_form.html", context)

@login_required(login_url="/login/")
def create_education(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    form = EducationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Education baru berhasil ditambahkan!")
        return redirect("main:show_education")

    context = {
        "name" : "Faishal Falih",
        "form" : form,
    }
    return render(request, "education_form.html", context)

@login_required(login_url="/login/")
def delete_project(request, project_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    if not request.user.is_superuser:
        raise PermissionDenied
    project = get_object_or_404(Project, pk=project_id)

    project.delete()
    messages.success(request, "Project berhasil dihapus!")
    return redirect("main:show_projects")

@login_required(login_url="/login/")
def delete_education(request, education_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    if not request.user.is_superuser:
        raise PermissionDenied
    education = get_object_or_404(Education, pk=education_id)

    education.delete()
    messages.success(request, "Education berhasil dihapus!")
    return redirect("main:show_education")

def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.prefetch_related('starred_by').all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    # Konstruksi data JSON secara manual agar bisa menyisipkan logika Star
    data = []
    for project in projects:
        starred_users = project.starred_by.all()
        is_starred = request.user in starred_users if request.user.is_authenticated else False
        starred_by_names = ", ".join([u.username for u in starred_users])

        data.append({
            "pk": str(project.id),
            "fields": {
                "title": project.title,
                "description": project.description,
                "tech_stack": project.tech_stack,
                "project_url": project.project_url,
                "project_image_url": project.project_image_url,
                "star_count": starred_users.count(),
                "is_starred": is_starred,
                "starred_by_names": starred_by_names,
            }
        })

    return JsonResponse(data, safe=False)

@require_GET
def get_education_json(request):
    query = request.GET.get("q", "").strip()
    educations = Education.objects.all()
    if query:
        educations = educations.filter(institution__icontains=query)

    may_edit = can_edit(request.user)
    may_delete = request.user.is_superuser
    data = [
        {
            "id": str(education.pk),
            "institution": education.institution,
            "education_level": education.education_level,
            "study_program": education.study_program,
            "start_year": education.start_year,
            "end_year": education.end_year,
            "logo_url": education.logo_url,
            "edit_url": reverse("main:update_education", args=[education.pk]) if may_edit else None,
            "delete_url": reverse("main:delete_education", args=[education.pk]) if may_delete else None,
        }
        for education in educations
    ]
    return JsonResponse(data, safe=False)


@require_GET
def get_experience_json(request):
    query = request.GET.get("q", "").strip()
    experiences = Experience.objects.all()
    if query:
        experiences = experiences.filter(title__icontains=query)

    data = [
        {
            "id": str(experience.pk),
            "title": experience.title,
            "description": experience.description,
            "category": experience.get_category_display(),
            "thumbnail": experience.thumbnail,
            "started_at": experience.started_at.isoformat(),
            "ended_at": experience.ended_at.isoformat() if experience.ended_at else None,
            "is_ongoing": experience.is_ongoing,
        }
        for experience in experiences
    ]
    return JsonResponse(data, safe=False)

@login_required(login_url="/login/")
def update_education(request, education_id):
    if not can_edit(request.user):
        raise PermissionDenied
    education = get_object_or_404(Education, pk=education_id)
    # GET otomatis mengisi data lama melalui instance=education
    form = EducationForm(request.POST or None, instance=education)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Education berhasil diperbarui!")
        return redirect("main:show_education")

    context = {
        "name": "Faishal Falih",
        "form": form,
    }
    return render(request, "education_form.html", context)

@login_required(login_url="/login/")
def update_project(request, project_id):
    if not can_edit(request.user):
        raise PermissionDenied

    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(request.POST or None, instance=project)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Project berhasil diperbarui")
        return redirect("main:show_projects")

    context = {
        "name": "Faishal Falih",
        "form": form,
    }
    return render(request, "projects_form.html", context)
        
def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Faishal",
        "form": form,
    }
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "name": "Burhan",
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response

# Tanpa cek is_superuser: semua akun yang sudah login boleh memberi star
@login_required(login_url="/login/")
def toggle_star(request, project_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    project = get_object_or_404(Project, pk=project_id)

    # Kalau akun ini sudah pernah memberi star, batalkan star-nya.
    # Kalau belum, tambahkan star.
    if project.starred_by.filter(pk=request.user.pk).exists():
        project.starred_by.remove(request.user)
    else:
        project.starred_by.add(request.user)

    return redirect("main:show_projects")

def is_editor(user):
    return user.is_authenticated and user.groups.filter(name="Editor").exists()

def can_edit(user):
    return user.is_superuser or is_editor(user)

@require_POST
def create_project_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan proyek."},
            status=403,
        )

    form = ProjectForm(request.POST)
    if form.is_valid():
        project = form.save()
        return JsonResponse(
            {"message": "Proyek berhasil ditambahkan.", "pk": str(project.id)},
            status=201,
        )

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)
