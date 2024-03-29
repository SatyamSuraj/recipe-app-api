from django.urls import path, include
from rest_framework import urlpatterns
from rest_framework.routers import DefaultRouter

from recipe import views


router = DefaultRouter()
router.register('tag', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet) 
router.register('recipes', views.RecipeViewSet)


app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls))
] 
