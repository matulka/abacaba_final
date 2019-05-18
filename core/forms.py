from django import forms
from django.contrib.auth.hashers import check_password
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from core.models import Addresses, Question, Product


class SearchForm(forms.Form):
    input = forms.CharField(label='Поиск',
                            min_length=1,
                            max_length=100,
                            empty_value='Продукция abacaba')


class SignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.', label='Имя')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.', label='Фамилия')
    email = forms.EmailField(max_length=254, required=True)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError(u'Этот email уже зарегистрирован')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2' )


class ProfileForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


class PasswordProfileForm(forms.Form):
   password1 = forms.CharField(widget=forms.PasswordInput, required=True)
   password2 = forms.CharField(widget=forms.PasswordInput, required=True)


class AddressForm(forms.ModelForm):
    class Meta:
        model = Addresses
        fields = ['city', 'street', 'building', 'flat', 'entrance', 'description']


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['topic', 'content']


class AddProductForm(forms.ModelForm):
    # name = forms.CharField(min_length=1, error_messages={'required': 'Поле должно быть заполнено!'})
    # price = forms.FloatField(min_value=0, error_messages={'required': 'Поле должно быть заполнено!', 'invalid': 'LOL'})
    # rating = forms.IntegerField(required=False, min_value=0, max_value=5, error_messages={'required': 'Поле должно быть заполнено!', 'invalid': 'LOL'})
    class Meta:
        model = Product
        fields = ['name', 'price', 'rating']
        error_messages = {'name':{'required': 'Поле должно быть заполнено!'}, 'price':{'required': 'Поле должно быть заполнено!'},}


class AddImgForm(forms.Form):
    img = forms.FileField(label="Картинка:", required=False)

    def clean_img(self):
        img = self.cleaned_data['img']
        if img != None:
            if not img.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                raise forms.ValidationError("Только форматы .jpg, .png, .jpeg разрешены")
            return img
        else:
            return None


class AddSeveralImgForm(forms.Form):
    img = forms.FileField(label="Картинка:", required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))
    def clean_img(self):
        img = self.cleaned_data['img']
        if img != None:
            if not img.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                raise forms.ValidationError("Только форматы .jpg, .png, .jpeg разрешены")
            return img
        else:
            return None


class ProfileAddressForm(forms.Form):
    id = forms.CharField()
    city = forms.CharField(max_length=30, required=True)
    street = forms.CharField(max_length=30, required=True)
    building = forms.CharField(max_length=30, required=True)
    entrance = forms.CharField(required=True)
    flat = forms.CharField(required=True)
    description = forms.CharField(max_length=150, required=True)

