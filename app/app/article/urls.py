""" 
URL mapping for the article API.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from article import views

router = DefaultRouter()
router.register('articles', views.ArticleMVS)
router.register('topics', views.TopicViewSet)
router.register('articles-all', views.ArticleVS, basename='articles')

app_name = 'article'

urlpatterns = [
    path('', include(router.urls)),
]
