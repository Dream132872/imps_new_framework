from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Todo(models.Model):
    """Model definition for Todo."""

    title = models.CharField(_("Title"), max_length=50)

    class Meta:
        """Meta definition for Todo."""

        verbose_name = "Todo"
        verbose_name_plural = "Todos"

    def __str__(self):
        """Unicode representation of Todo."""
        return self.title
