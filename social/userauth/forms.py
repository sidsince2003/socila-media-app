from django import forms
from social.userauth.models import Profile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['picture' 'bio', 'profileimg', 'location']