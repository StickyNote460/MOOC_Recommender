from django.shortcuts import render,HttpResponse

def index(request):
    return HttpResponse("hello world!")

# Create your views here.
