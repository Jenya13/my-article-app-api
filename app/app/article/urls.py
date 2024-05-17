""" 
URL mapping for the article API.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from article import views

router = DefaultRouter()
router.register('all', views.ArticleVS, basename='articles')
router.register('topics', views.TopicViewSet)
router.register('', views.ArticleMVS, basename='article')

app_name = 'article'

urlpatterns = [
    path('', include(router.urls)),
    path('<int:pk>/comments/',
         views.CommentListCreateView.as_view(), name='comment-list-create'),
    path('comment/<int:pk>/',
         views.CommentRetrieveUpdateDestroyView.as_view(), name='comment-detail'),
]
