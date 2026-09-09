from django.shortcuts import render

from main.models import Experience


def show_main(request):
    context = {
        "name": "Faishal Falih",
        "npm": "2506612064",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "As a Computer Science student, I'm driven to build robust and scalable systems that effectively solve complex problems."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Faishal Falih",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)