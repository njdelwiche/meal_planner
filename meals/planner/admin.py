from django.contrib import admin
from .models import User, Ingredient, Report, Recipe

# Sources: https://docs.djangoproject.com/en/3.0/ref/contrib/admin/#django.contrib.admin.InlineModelAdmin
# https://stackoverflow.com/questions/21763977/my-admin-tabularinline-class-returns-exception-object-has-no-attribute-urls
class IngredientInline(admin.TabularInline):
    model = Ingredient

class UserAdmin(admin.ModelAdmin):
    inlines = [
        IngredientInline,
    ]

# Register your models here.
admin.site.register(Ingredient)
admin.site.register(User, UserAdmin)
admin.site.register(Report)
admin.site.register(Recipe)
