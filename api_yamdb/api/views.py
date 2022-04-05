from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    filters,
    generics,
    mixins,
    permissions,
    status,
    viewsets,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Review, Title, User

from .filters import TitleFilter
from .permissions import AdminOnly, AdminOrReadOnly, AuthorOrHigher
from .serializers import (
    CategoriesSerializer,
    CommentSerializer,
    GenresSerializer,
    GetTokenSerializer,
    ReviewSerializer,
    SendCodeSerializer,
    TitlesAddSerializer,
    TitlesSerializer,
    UserAdminSerializer,
    UserEditMeSerializer,
)

TITLE_ID_KWARG = 'title_id'

REVIEW_ID_KWARG = 'review_id'


class SendCode(generics.CreateAPIView):
    """Отправка проверочного кода"""

    queryset = User.objects.all()
    serializer_class = SendCodeSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(response.data, status=status.HTTP_200_OK)


class GetToken(APIView):
    """Выдача токена"""

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data['username']
        token = serializer.data['confirmation_code']
        user = get_object_or_404(User, username=username)
        check_token = default_token_generator.check_token(user, token)
        if not check_token:
            return Response(
                {'message': 'Invalid confirmation_code or username'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)


class BaseViewSetCategoriesGenres(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Вьюсет для категорий и жанров базовый."""

    permission_classes = (AdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoriesViewSet(BaseViewSetCategoriesGenres):
    """Просмотр и редактирование категорий."""

    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer


class GenresViewSet(BaseViewSetCategoriesGenres):
    """Просмотр и редактирование жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenresSerializer


class TitlesViewSet(viewsets.ModelViewSet):
    """Просмотр и редактирование произведений."""

    queryset = Title.objects.all()
    serializer_class = TitlesSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return TitlesAddSerializer
        return super().get_serializer_class()


class UsersViewCreateAdmin(generics.ListCreateAPIView):
    """Просмотр и создание пользователей администратором"""

    queryset = User.objects.all()
    serializer_class = UserAdminSerializer
    filter_backends = (filters.SearchFilter,)
    permission_classes = (AdminOnly,)
    search_fields = ('username',)
    lookup_field = 'username'


class UserViewPatchDelAdmin(generics.RetrieveUpdateDestroyAPIView):
    """Просмотр, редактирование и удаление пользователя администратором"""

    serializer_class = UserAdminSerializer
    permission_classes = (AdminOnly,)
    lookup_field = 'username'

    def get_queryset(self):
        user = User.objects.filter(username=self.kwargs['username'])
        return user


class UserView(APIView):
    """Просмотр и редактироване профиля пользователя"""

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        serializer = UserEditMeSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = UserEditMeSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewViewSet(viewsets.ModelViewSet):
    """Просмотр и редактирование рецензий."""

    serializer_class = ReviewSerializer
    permission_classes = (
        AuthorOrHigher,
        permissions.IsAuthenticatedOrReadOnly,
    )

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            pk=self.kwargs.get(TITLE_ID_KWARG),
        )
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            pk=self.kwargs.get(TITLE_ID_KWARG),
        )
        serializer.save(
            author=self.request.user,
            title=title,
        )


class CommentViewSet(viewsets.ModelViewSet):
    """Просмотр и редактирование комментариев."""

    serializer_class = CommentSerializer
    permission_classes = (
        AuthorOrHigher,
        permissions.IsAuthenticatedOrReadOnly,
    )

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            pk=self.kwargs.get(TITLE_ID_KWARG),
        )
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get(REVIEW_ID_KWARG),
            title=title,
        )
        return review.comments.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            pk=self.kwargs.get(TITLE_ID_KWARG),
        )
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get(REVIEW_ID_KWARG),
            title=title,
        )
        serializer.save(
            author=self.request.user,
            review=review,
        )
