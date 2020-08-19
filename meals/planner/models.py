from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator

class User(AbstractUser):
    allergies = models.CharField(max_length=100, blank=True)
    
class Ingredient(models.Model):
    owner = models.ForeignKey("User", on_delete=models.CASCADE, related_name="ingredients_by_owner")
    item = models.CharField(max_length=255)
    amount = models.IntegerField(validators=[MinValueValidator(0)], default=10000)
    def __str__(self):
        return f"{self.item}"

class Report(models.Model):
    owner = models.ForeignKey("User", on_delete=models.CASCADE, related_name="report_by_owner")
    recipes = models.ManyToManyField("Recipe", related_name="report_by_recipe")
    def __str__(self):
        return f"{self.owner}'s Report'"

class Recipe(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField(max_length=255)
    ingredients = models.CharField(max_length=2500)
    missing = models.CharField(max_length=2500)
    steps = models.CharField(max_length=5000)
    img = models.URLField(max_length=255)

    def __str__(self):
        return f"{self.title}"

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "ingredients": {x: x for x in self.ingredients.splitlines()},
            "missing": self.missing,
            "steps": {x: x for x in self.steps.splitlines()},
            "img": self.img
        }
