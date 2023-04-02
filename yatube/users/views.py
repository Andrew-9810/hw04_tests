from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CreationForm, ContactForm
from django.shortcuts import redirect, render


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


def authorized_only(func):
    """Проверка авторизации."""
    def check_user(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        return redirect('/auth/login/')
    return check_user


def user_contact(request):
    """Контакты"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:thank_you')
        return render(request, 'users/contact.html', {'form': form})
    form = ContactForm()
    return render(request, 'users/contact.html', {'form': form})


def thank(request):
    """Успешное заполнение формы Контакты"""
    return render(request, 'users/thankyou.html')
