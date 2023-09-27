from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from app.models import Room, Profile
from django.contrib.auth.models import User

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model=User
        fields=['username','email','password1','password2']


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        # fields = '__all__'
        fields = ['avatar', 'name',  'email', 'bio']
