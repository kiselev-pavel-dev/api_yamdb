from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoriesViewSet,
    CommentViewSet,
    GenresViewSet,
    GetToken,
    ReviewViewSet,
    SendCode,
    TitlesViewSet,
    UsersViewCreateAdmin,
    UserView,
    UserViewPatchDelAdmin,
)

app_name = 'api'

router = DefaultRouter()

router.register('categories', CategoriesViewSet)
router.register('genres', GenresViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='review',
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment',
)
router.register('titles', TitlesViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/token/', GetToken.as_view()),
    path('v1/auth/signup/', SendCode.as_view()),
    path('v1/users/', UsersViewCreateAdmin.as_view()),
    path('v1/users/me/', UserView.as_view()),
    path('v1/users/<str:username>/', UserViewPatchDelAdmin.as_view()),
]
