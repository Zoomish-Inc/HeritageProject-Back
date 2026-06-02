from django.urls import path
from .schema_views import spectacular_schema_view, swagger_ui_view

urlpatterns = [
    path('api/schema/', swagger_ui_view, name='api-schema'),
    path('api/schema/openapi.yaml', spectacular_schema_view, name='openapi-yaml'),
]


