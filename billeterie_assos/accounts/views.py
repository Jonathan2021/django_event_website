from django.urls import reverse_lazy
from django.views import generic
from . import forms

# Create your views here.


class SignUp(generic.CreateView):
    form_class = forms.MyUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'
