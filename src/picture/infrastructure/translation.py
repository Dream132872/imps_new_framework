from modeltranslation.translator import TranslationOptions, register

from . import models


@register(models.Picture)
class PictureTranslation(TranslationOptions):
    fields = ("title", "alternative")
