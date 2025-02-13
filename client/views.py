from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http.request import HttpRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.urls import reverse

from client.models import User


def home_login(request: HttpRequest):
    if request.method == "GET":
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('home_user', args=[]))
        return render(request,  'login.html', {'title': 'login'})

    elif request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if not user:
            return render(request,  'login.html', {
                'title': 'Entrar',
                'message': ['Dados inválidos.']
            })
        login(request, user)
        return HttpResponseRedirect(reverse('home_user', args=[]))

    else:
        print(f'Method {request.method} not allowed.')
        return HttpResponseRedirect("<h1>Método não permitido</h1>")


def home(request: HttpRequest):
    return render(request,  'home.html', {'title': 'Início', 'user': request.user})


def user_logout(request: HttpRequest):
    logout(request)
    return HttpResponseRedirect(reverse('home', args=[]))


@login_required(login_url='login')
def home_user(request: HttpRequest):
    return render(request, 'user.html', {'title': 'Perfil'})


def new_user(request: HttpRequest):
    if request.method == "GET":
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('home_user', args=[]))
        return render(request, 'new_user.html', {'title': 'Novo Usuário'})
    elif request.method == "POST":
        isFormOk = True
        messages = []
        warnings = []
        successes = []
        username = request.POST.get("username")
        if len(User.objects.filter(username=username)) != 0:
            isFormOk = False
            warnings.append('Username already in use.')
            username = ''
        email = request.POST.get("email")
        if email:
            if len(User.objects.filter(email=email)) != 0:
                isFormOk = False
                warnings.append('E-mail already in use.')
                email = ''
        else:
            isFormOk = False
            warnings.append('E-mail can not be empty.')
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        if password != password2:
            isFormOk = False
            warnings.append('Passwords do not matches.')
            password = password2 = ''
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        if isFormOk:
            new_user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=firstname,
                last_name=lastname
            )
            new_user.save()
            request.user = new_user
            login(request, new_user)
            return HttpResponseRedirect(reverse('login', args=[]))
        return render(request, 'new_user.html', {
            'title': 'Novo Usuário',
            'messages': messages,
            'warnings': warnings,
            'successes': successes,
            'form': {
                'username': username,
                "email": email,
                "password": password,
                "password2": password2,
                "firstname": firstname,
                "lastname": lastname,
            }
        })
