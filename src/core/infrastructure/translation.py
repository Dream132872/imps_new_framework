from modeltranslation.translator import TranslationOptions, register

from . import models


@register(models.Picture)
class ObserverTranslation(TranslationOptions):
    fields = ("title", "alternative")
