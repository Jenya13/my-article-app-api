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
    # path('articles/<int:article_id>/comments/',
    #      views.CommnetListCreateAV.as_view(), name='comment-list-create'),
    path('<int:pk>/comments/',
         views.CommentListCreateView.as_view(), name='comment-list-create'),

    path('<int:article_id>/comments/<int:pk>/',
         views.CommentRetrieveUpdateDestroyView.as_view(), name='comment-detail'),
]
