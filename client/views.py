from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http.request import HttpRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.urls import reverse

# Create your views here.


def home_login(request: HttpRequest):
    if request.method == "GET":
        print(request.user)
        return render(request,  'login.html', {'title': 'login'})

    elif request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if not user:
            return render(request,  'login.html', {
                'title': 'login',
                'message': 'Dados inválidos.'
            })
        login(request, user)
        return HttpResponseRedirect(reverse('user', args=[]))

    else:
        print(f'Method {request.method} not allowed.')
        return HttpResponseRedirect("<h1>Método não permitido</h1>")


def home(request: HttpRequest):
    return render(request,  'home.html', {'title': 'home'})


def user_logout(request: HttpRequest):
    logout(request)
    return HttpResponseRedirect(reverse('home', args=[]))


@login_required(login_url='login')
def home_user(request: HttpRequest):
    return render(request, 'user.html', {'title': 'user'})
