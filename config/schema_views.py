from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


spectacular_schema_view = SpectacularAPIView.as_view()

swagger_ui_view = SpectacularSwaggerView.as_view(url_name='api-schema')


