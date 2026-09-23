from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    """
    Kök dizine (localhost:8000/) gelen istekleri yakalayıp 
    geçici ana sayfa şablonunu (index.html) render eden view fonksiyonu.
    """
    return render(request, "index.html")


def about(request):
    """
    /about/ rotasına gelen istekleri yakalayıp 
    geçici hakkında sayfasını (about.html) render eden view fonksiyonu.
    """
    return render(request, "about.html")



def hello(request, name="World"):
    """
    /hello rotasında 'Hello, World!',
    /hello/<name>/ rotasında dinamik olarak 'Hello, {name}!' basan view fonksiyonu.
    """
    return HttpResponse(f"Hello, {name}!")


def calculate_sum(request, num1, num2):
    """
    /sum/<num1>/<num2>/ rotasına gelen iki sayının toplamını ekrana basan view fonksiyonu.
    """
    total = num1 + num2
    return HttpResponse(str(total))



