from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.db import IntegrityError

User = get_user_model()


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError('This user does not exist')
            if not user.check_password(password):
                raise forms.ValidationError('Incorrect password')
            if not user.is_active:
                raise forms.ValidationError('This user is not active')
        return super(UserLoginForm, self).clean(*args, **kwargs)


class UserRegisterForm(forms.ModelForm):
    email = forms.EmailField(label='Email address')
    email2 = forms.EmailField(label='Confirm Email')
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'email2',
            'password'
        ]

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)
        email = cleaned_data.get('email')
        email2 = cleaned_data.get('email2')
        username = cleaned_data.get('username')

        if email != email2:
            raise forms.ValidationError("Emails must match")

        email_qs = User.objects.filter(email=email)
        if email_qs.exists():
            raise forms.ValidationError("This email has already been registered")

        username_qs = User.objects.filter(username=username)
        if username_qs.exists():
            raise forms.ValidationError("This username is already taken")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            try:
                user.save()
            except IntegrityError:
                # Handle IntegrityError here, maybe redirect or show an error message
                raise forms.ValidationError("IntegrityError occurred. User could not be registered.")
        return user


# forms.py




