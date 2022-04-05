from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_year

USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'

ROLES = ((USER, USER), (ADMIN, ADMIN), (MODERATOR, MODERATOR))


class User(AbstractUser):
    """Модель пользователя"""

    password = models.CharField(max_length=128, blank=True, null=True)
    email = models.EmailField('E-mail', max_length=150, unique=True)
    username = models.CharField('Логин', max_length=254, unique=True)
    first_name = models.CharField(
        'Фамилия', max_length=150, blank=True, null=True
    )
    last_name = models.CharField('Имя', max_length=150, blank=True, null=True)
    bio = models.TextField('О пользователе', blank=True)
    role = models.CharField('Роль', choices=ROLES, max_length=10, default=USER)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR


class Category(models.Model):
    """Модель категории."""

    name = models.CharField('Название категории', max_length=256)
    slug = models.SlugField('Слаг категории', max_length=50, unique=True)

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return self.slug


class Genre(models.Model):
    """Модель жанров."""

    name = models.CharField('Название жанра', max_length=256)
    slug = models.SlugField('Слаг категории', max_length=50, unique=True)

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return self.slug


class Title(models.Model):
    """Модель произведения."""

    name = models.CharField('Название произведения', max_length=256)
    year = models.IntegerField(
        'Год выпуска', validators=[validate_year], db_index=True
    )
    description = models.TextField('Описание', blank=True, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='titles',
    )
    genre = models.ManyToManyField(Genre, through='TitleGenre')

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return self.name


class TitleGenre(models.Model):
    """Модель связывающая произведения и жанры."""

    title = models.ForeignKey(
        Title,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='titles',
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='genres',
    )


class Review(models.Model):
    """Модель рецензии."""

    text = models.TextField('отзыв')
    pub_date = models.DateTimeField('Время публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='рецензент',
    )
    score = models.IntegerField(
        verbose_name='оценка',
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
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='произведение',
    )

    class Meta:
        ordering = ['-pk']
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='review_unique',
            )
        ]


class Comment(models.Model):
    """Модель комментария."""

    text = models.TextField('комментарий')
    pub_date = models.DateTimeField('Время публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='комментатор',
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='отзыв',
    )

    class Meta:
        ordering = ['-pk']
