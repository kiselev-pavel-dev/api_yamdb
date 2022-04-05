import datetime as dt
from django.conf import settings
from django.core.exceptions import ValidationError


def validate_year(value):
    """Проверка на корректность года."""
    year = dt.date.today().year
    if value > year:
        raise ValidationError(settings.INVALID_YEAR)
    return value
