import datetime as dt

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Avg
from rest_framework import serializers
from reviews.models import ROLES, Category, Comment, Genre, Review, Title, User

from api_yamdb.settings import DEFAULT_FROM_EMAIL

EMAIL_SUBJECT = 'Код подтверждения'
EMAIL_LOGIN = 'Логин - '
EMAIL_TOKEN = '\nКод подтверждения - '


DUPLICATE_REVIEW = 'Такая рецензия уже существует.'


def make_hash_value(user, timestamp):
    """Переопределение метода генерации кода"""

    login_timestamp = (
        ''
        if user.last_login is None
        else user.last_login.replace(microsecond=0, tzinfo=None)
    )
    return str(user.pk) + str(login_timestamp) + str(timestamp)


default_token_generator._make_hash_value = make_hash_value


def send_mail_token(user):
    """Отправка кода подтверждения на почту"""

    token = default_token_generator.make_token(user)
    EMAIL_MESSAGE = EMAIL_LOGIN + user.username + EMAIL_TOKEN + token
    send_mail(EMAIL_SUBJECT, EMAIL_MESSAGE, DEFAULT_FROM_EMAIL, (user.email,))


def check_username(data):
    """Проверка имени пользователя"""

    if data['username'].lower() == 'me':
        raise serializers.ValidationError(
            'Нельзя создать пользователя c таким именем'
        )

    elif User.objects.filter(username=data['username']):
        raise serializers.ValidationError(
            'Пользователь с таким именем уже существует'
        )


def check_user_email(data):
    """Проверка email пользователя"""

    if User.objects.filter(email=data['email']):
        raise serializers.ValidationError('Email уже зарегистрирован')


class UserAdminSerializer(serializers.ModelSerializer):
    """Сериализация пользователя для эндпоинтов администратора"""

    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    bio = serializers.CharField(required=False)
    role = serializers.ChoiceField(choices=ROLES, required=False)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )

    def validate(self, data):
        if 'username' in data:
            check_username(data)
        if 'email' in data:
            check_user_email(data)

        return data


class UserEditMeSerializer(serializers.ModelSerializer):
    """Сериализация пользователя для эндпоинтов пользователя"""

    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    bio = serializers.CharField(required=False)
    role = serializers.ChoiceField(choices=ROLES, read_only=True)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )

    def validate(self, data):
        if 'username' in data:
            check_username(data)
        if 'email' in data:
            check_user_email(data)

        return data


class SendCodeSerializer(serializers.ModelSerializer):
    """Сериализация пользователя для регистрации и получения
    проверочного кода"""

    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate(self, data):
        user = User.objects.filter(
            username=data['username'], email=data['email']
        ).last()
        if user:
            send_mail_token(user)
            raise serializers.ValidationError(
                'Код подтверждения отправлен на почту'
            )

        check_username(data)
        check_user_email(data)

        return data

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        send_mail_token(user)

        return user


class GetTokenSerializer(serializers.Serializer):
    """Сериализация выдачи токена"""

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class CategoriesSerializer(serializers.ModelSerializer):
    """Сериализор для категории."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenresSerializer(serializers.ModelSerializer):
    """Сериализор для жанра."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitlesSerializer(serializers.ModelSerializer):
    """Сериализор для произведений для чтения."""

    rating = serializers.SerializerMethodField()
    category = CategoriesSerializer(read_only=True)
    genre = GenresSerializer(many=True, read_only=True)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )

    def get_rating(self, obj):
        reviews = obj.reviews.all()
        rating = reviews.aggregate(Avg('score'))
        if reviews:
            return int(rating['score__avg'])
        return None


class TitlesAddSerializer(serializers.ModelSerializer):
    """Сериализор для произведений для записи."""

    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def validate_year(self, value):
        year = dt.date.today().year
        if value > year:
            raise serializers.ValidationError(
                'Год не может быть больше текущего!'
            )
        return value


class CurrentTitleDefault:
    """При вызове возвращает title_id из параметров запроса."""

    requires_context = True

    def __call__(self, serializer_field):
        return (
            serializer_field.context.get('request')
            .parser_context.get('kwargs')
            .get('title_id')
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализация рецензии."""

    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True,
        slug_field='username',
    )
    title = serializers.PrimaryKeyRelatedField(
        default=CurrentTitleDefault(),
        read_only=True,
    )
    score = serializers.IntegerField(
        validators=[
            MinValueValidator(
                limit_value=settings.MIN_SCORE,
                message=settings.INVALID_SCORE.format(
                    min=settings.MIN_SCORE, max=settings.MAX_SCORE
                ),
            ),
            MaxValueValidator(
                limit_value=settings.MAX_SCORE,
                message=settings.INVALID_SCORE.format(
                    min=settings.MIN_SCORE, max=settings.MAX_SCORE
                ),
            ),
        ],
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('author', 'title'),
                message=DUPLICATE_REVIEW,
            )
        ]


class CommentSerializer(serializers.ModelSerializer):
    """Сериализация комментария."""

    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True,
        slug_field='username',
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
