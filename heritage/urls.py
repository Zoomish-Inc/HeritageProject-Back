from django.urls import path
from .views import HeritageListView, HeritageDetailView

urlpatterns = [
    path('heritage/', HeritageListView.as_view(), name='heritage-list'),
    path('heritage/<str:slug>/', HeritageDetailView.as_view(), name='heritage-detail'),
]
