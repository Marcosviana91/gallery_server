from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http.request import HttpRequest
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.urls import reverse

from client.models import User


def home_login(request: HttpRequest):
    if request.method == "GET":
        if request.user.is_authenticated:
            messages.add_message(request, messages.INFO, 'Usuário já logado.', extra_tags='primary')
            return HttpResponseRedirect(reverse('home_user', args=[]))
        return render(request,  'login.html', {'title': 'login'})

    elif request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if not user:
            messages.add_message(request, messages.WARNING, 'Dados inválidos.', extra_tags='danger')
            return render(request,  'login.html', {
                'title': 'Entrar',
            })
        login(request, user)
        messages.add_message(request, messages.SUCCESS, 'Login realizado com sucesso.', extra_tags='success')
        return HttpResponseRedirect(reverse('home_user', args=[]))

    else:
        print(f'Method {request.method} not allowed.')
        return HttpResponseRedirect("<h1>Método não permitido</h1>")


def home(request: HttpRequest):
    return render(request,  'home.html', {'title': 'Início', 'user': request.user})


def user_logout(request: HttpRequest):
    logout(request)
    messages.add_message(request, messages.WARNING, 'Logout realizado.', extra_tags='danger')
    return HttpResponseRedirect(reverse('home', args=[]))


def reset_password(request: HttpRequest):
    if request.method == 'GET':
        messages.add_message(request, messages.WARNING, 'Resetar a senha?.', extra_tags='danger')
        return render(request, 'reset_password.html', {'title': 'Resetar Senha'})
    elif request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        try:
            user = User.objects.get(username=username_or_email)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=username_or_email)
            except User.DoesNotExist:
                messages.add_message(request, messages.WARNING, 'Usuário não encontrado.', extra_tags='danger')
                return render(request, 'reset_password.html', {'title': 'Resetar Senha'})
        # TODO implementar solicitação de nova senha
        messages.add_message(request, messages.SUCCESS, 'E-mail enviado.', extra_tags='success')
        return HttpResponseRedirect(reverse('login', args=[]))

@login_required(login_url='login')
def home_user(request: HttpRequest):
    return render(request, 'user.html', {'title': 'Perfil'})


def new_user(request: HttpRequest):
    if request.method == "GET":
        if request.user.is_authenticated:
            messages.add_message(request, messages.WARNING, 'Usuário já está logado. Faça logout para criar um novo usuário.', extra_tags='danger')
            return HttpResponseRedirect(reverse('home_user', args=[]))
        return render(request, 'new_user.html', {'title': 'Novo Usuário'})
    elif request.method == "POST":
        isFormOk = True
        username = request.POST.get("username")
        if len(User.objects.filter(username=username)) != 0:
            isFormOk = False
            messages.add_message(request, messages.WARNING, 'Nome de usuário indisponível.', extra_tags='danger')
            username = ''
        email = request.POST.get("email")
        if email:
            if len(User.objects.filter(email=email)) != 0:
                isFormOk = False
                messages.add_message(request, messages.WARNING, 'Endereço de e-mail indisponível.', extra_tags='danger')
                email = ''
        else:
            isFormOk = False
            messages.add_message(request, messages.WARNING, 'Endereço de e-mail não pode estar vazio.', extra_tags='danger')
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        if password != password2:
            isFormOk = False
            messages.add_message(request, messages.WARNING, 'As senhas não coincidem.', extra_tags='danger')
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
            messages.add_message(request, messages.SUCCESS, 'Novo usuário cadastrado.', extra_tags='success')
            request.user = new_user
            login(request, new_user)
            messages.add_message(request, messages.SUCCESS, 'Login realizado com sucesso.', extra_tags='success')
            return HttpResponseRedirect(reverse('home_user', args=[]))
        return render(request, 'new_user.html', {
            'title': 'Novo Usuário',
            'messages': messages,
            'form': {
                'username': username,
                "email": email,
                "password": password,
                "password2": password2,
                "firstname": firstname,
                "lastname": lastname,
            }
        })
