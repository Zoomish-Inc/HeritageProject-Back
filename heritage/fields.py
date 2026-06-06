import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

URL_MAX_LENGTH = 2048


def validate_flexible_url(value):
    if value in (None, ''):
        return
    if not isinstance(value, str):
        raise ValidationError(_('Некорректный URL.'))

    value = value.strip()
    if not value:
        return
    if '\n' in value or '\r' in value:
        raise ValidationError(_('URL не должен содержать переносы строк.'))
    if value.startswith('/'):
        return
    if re.match(r'^https?://', value, re.IGNORECASE):
        return

    raise ValidationError(
        _('Введите URL вида https://example.com/path или относительный путь /path/to/file.')
    )


class FlexibleUrlField(models.CharField):
    description = _('URL (абсолютный или относительный)')

    def __init__(self, verbose_name=None, name=None, **kwargs):
        kwargs.setdefault('max_length', URL_MAX_LENGTH)
        validators = kwargs.pop('validators', [])
        super().__init__(
            verbose_name,
            name,
            validators=[validate_flexible_url, *validators],
            **kwargs,
        )

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if kwargs.get('max_length') == URL_MAX_LENGTH:
            del kwargs['max_length']
        return name, path, args, kwargs
