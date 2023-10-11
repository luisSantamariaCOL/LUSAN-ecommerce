from django.shortcuts import render
from django.http import request, HttpResponse


def home(request):
    return render(request, 'home.html')

 