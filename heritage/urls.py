from django.urls import path
from .views import HeritageListView, HeritageDetailView, TourPackManifestView

urlpatterns = [
    path('heritage/', HeritageListView.as_view(), name='heritage-list'),
    path('heritage/<str:slug>/', HeritageDetailView.as_view(), name='heritage-detail'),
    path('tour-packs/', TourPackManifestView.as_view(), name='tour-packs-manifest'),
]
