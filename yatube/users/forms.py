from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
        help_texts = {'username': "Обязательно. Не более 30 символов\n"
                                  "Буквы, цифры и символы"}
        labels = {'first_name': "Имя",
                  'last_name': "Фамилия",
                  'username': "Имя пользователя",
                  'email': "Email",
                  'password1': "Пароль",
                  'password2': "Подтверждение пароля"}
