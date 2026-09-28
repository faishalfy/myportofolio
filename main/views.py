from django.shortcuts import redirect, render
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required  # Tambahkan baris ini
from django.core.exceptions import PermissionDenied        # Tambahkan baris ini
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
import datetime

from main.models import Education, Experience, Project
from main.forms import ProjectForm, EducationForm
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse, HttpResponseNotAllowed
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
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)


def show_education(request):
    json_response = get_education_json(request)

    educations = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    educations = [education.object for education in educations]

    context = {
        "name": "Faishal Falih",
        "education_list": educations,
        "is_editor": is_editor(request.user),
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
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize(
        "json",
        projects,
        fields=[
            "title",
            "description",
            "tech_stack",
            "project_url",
            "project_image_url",
        ],
    )
    return HttpResponse(projects_json, content_type="application/json")

def get_education_json(request):
    education = Education.objects.all()
    education_json = serializers.serialize("json", education)
    return HttpResponse(education_json, content_type="application/json")

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
