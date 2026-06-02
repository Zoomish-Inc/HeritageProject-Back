from drf_spectacular.contrib.rest_framework_simplejwt import SpectacularSwaggerAutoSchema


SPECTACULAR_BASE = {
    # Conventions: backend returns snake_case
    'COMPONENT_SPLIT_REQUEST': True,
    'COMPONENT_NO_READ_ONLY_REQUIRED': True,
    'SCHEMA_PATH_PREFIX': '',
    'TITLE': 'Heritage API',
    'SERVE_INCLUDE_SCHEMA': False,
    'DISABLE_ERRORS': False,

    # Ensure spectacular scans urls properly.
    'SERVE_PERMISSIONS': False,
}

