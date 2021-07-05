from django.contrib.auth import authenticate, login, logout
from django.shortcuts import HttpResponseRedirect
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from django.views.generic.base import View
from django.views.generic import ListView
from django.db.models import Value, IntegerField

from user.forms import LoginForm
from user.forms import SignUpForm
from .models import CustomUser


class LoginFormView(FormView):
    form_class = LoginForm
    template_name = 'user/login.html'
    success_url = '/'

    def form_valid(self, form):
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user is not None:
            login(self.request, user)
            return HttpResponseRedirect('/')

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect('/')
        return super().get(request, *args, *kwargs)


class SignupFormView(FormView):
    form_class = SignUpForm
    template_name = 'user/signup.html'
    success_url = '/'

    def form_valid(self, form):
        if not CustomUser.objects.filter(username=form.cleaned_data['username']).exists():
            CustomUser.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                birth_date=form.cleaned_data['birth_date'],
            )
            return HttpResponseRedirect('/')

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect('/')
        return super(SignupFormView, self).get(request, *args, **kwargs)


class LogoutView(View):

    def get(self, request, *args, **kwargs):
        if request.method == 'GET' and request.user.is_authenticated:
            logout(request)
            return HttpResponseRedirect('/')


class ProfileListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'user/profile.html'
    context_object_name = 'user'
    user = None

    def get_queryset(self):
        self.user = CustomUser.objects.filter(username=self.request.user)
        return self.user.annotate(
            age=Value(timezone.now().year - self.user.first().birth_date.year, output_field=IntegerField())
        ).first()
