import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from .models import User, Ingredient, Report, Recipe
from .api import *
from .logic import *

COMMON_INGREDIENTS = ["all purpose flour", "baking powder", "baking soda",
                    "balsamic vinegar", "bananas", "brown sugar",
                    "butter", "cheddar cheese", "chili flakes",
                    "chili powder", "cinnamon", "coffee", "eggs",
                    "oats", "olive oil", "oregano", "pepper",
                    "rice", "salt", "thyme",
                    "white bread", "white sugar", "whole milk"]
max_recipes = 7

def index(request):
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        report = Report.objects.all().filter(owner=user).last()
        if report:
            recipes = report.recipes.all()
        else:
            recipes = None
    # Only users get to see index route
    else:
        return HttpResponseRedirect(reverse('register'))
    return render(request, "planner/index.html", {
        "ingredients": user.ingredients_by_owner.all().order_by("item"),
        "recipes": recipes,
        "num_days": [x + 1 for x in range(7)]
    })


# Login and Logout code borrowed from CS33 psets
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "planner/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "planner/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


def register(request):
    # Logged in users cannot access registration
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "planner/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "planner/register.html", {
                "message": "Username already taken."
            })
        
        # Add their initial pantry items:
        for y in [x for x in COMMON_INGREDIENTS if x in request.POST.keys()]:
            Ingredient.objects.create(owner=user, item=y)
        # Add their allergies
        if request.POST["allergies"]:
            user.allergies = request.POST["allergies"]
            user.save()

        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "planner/register.html", {
            # Pre-load common ingredients during signup
            "common": COMMON_INGREDIENTS
        })


@login_required
def add_items(request):

    # Can only add ingredients via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    user = User.objects.get(username=request.user.username)

    # Get contents of the Post
    data = json.loads(request.body)
    ingredients = data.get('body')

    # Send API call to get info
    analyzed = get_info(ingredients)
    for ingredient in analyzed:
        # Try to update it if it already exists
        try:
            modify = Ingredient.objects.get(owner=user, item=ingredient[0])
            modify.amount += ingredient[1]
            modify.save()
        # Otherwise add new entry
        except Ingredient.DoesNotExist:
            Ingredient.objects.create(owner=user, item=ingredient[0], amount=ingredient[1])

    return JsonResponse({"message": "Ingredients added successfully."}, status=201)


@login_required
def edit_quantity(request, id):

    # Can only edit ingredients via PUT
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)

    user = User.objects.get(username=request.user.username)

    # Get contents of the Post
    data = json.loads(request.body)
    try:
        modify = Ingredient.objects.get(id=id)
        # Validate the amount is not negative
        modify.amount = data.get('value') if int(data.get('value')) >= 0 else modify.amount
        modify.save()

    except Ingredient.DoesNotExist:
        return JsonResponse({"error": "Could not find ingredient."}, status=400)
    # If user passes a non integer
    except ValueError:
        return JsonResponse({"error": "Please enter an integer >= 0."}, status=400)

    return JsonResponse({"message": "Ingredient edited successfully."}, status=201)


@login_required
def generate_report(request, number):
    if number > max_recipes or number < 1:
        return HttpResponseRedirect(reverse('error'))

    # 1. Query Allrecipes for applicable recipes
    user = User.objects.get(username=request.user.username)
    pantry_items = [x.item for x in Ingredient.objects.all().filter(owner=user)]
    exclude = user.allergies if user.allergies else ''
    apt_recipes = load_apt_recipes(pantry_items, exclude, number)
    # If the searching failed, return an error page
    if not apt_recipes:
        return HttpResponseRedirect(reverse('error'))

    # 2. Send data to Nutrionix API
    analyzed = get_info("\n".join(apt_recipes[1]))
    separated = separate(analyzed)
    assert(len(separated) == len(apt_recipes[0]))

    # 3. Re-Construct and create the recipe objects
    recipe_objects = []
    intermediate = []
    counter = 1
    for recipe, analyzed_bit in zip(apt_recipes[0], separated):
        intermediate.append(Recipe_var(recipe[0], recipe[1], recipe[2], recipe[3], recipe[4], analyzed_bit))
        if len(intermediate) % APT_RECIPES == 0:
            recipe_objects.append(intermediate)
            intermediate = []
        counter += 1

    # 4. Solve the constraint satisfaction problem
    pantry_dict = {x.item: x.amount for x in
                    Ingredient.objects.all().filter(owner=user)}
    solved = final_solve(recipe_objects, pantry_dict)
    # If the solve failed, return an error page
    if not solved.values():
        return HttpResponseRedirect(reverse('error'))

    # 5. Create the model for a report
    # If the user swapped one item, don't make new report
    if request.GET.get('swap'):
        # Just remove the bad recipe and swap in the new one
        swap_out = Recipe.objects.get(id=int(request.GET.get('swap')))
        report = swap_out.report_by_recipe.first()
        report.recipes.remove(swap_out)
        recipe = list(solved.values())[0]
        new_recipe = Recipe.objects.create(title=recipe.title, url=recipe.url,
                                            ingredients=recipe.original_ingredients.replace(DELIMITER, ''),
                                            steps=recipe.steps, img=recipe.image,
                                            missing=", ".join(recipe.missing))
        report.recipes.add(new_recipe)
        # Return it as a json object
        return JsonResponse(new_recipe.serialize())

    # Otherwise make a new report
    new_report = Report.objects.create(owner=user)
    for recipe in solved.values():
        # Create the solved recipe in the models
        new_recipe = Recipe.objects.create(title=recipe.title, url=recipe.url,
                                            ingredients=recipe.original_ingredients.replace(DELIMITER, ''),
                                            steps=recipe.steps, img=recipe.image,
                                            missing=", ".join(recipe.missing))
        # Add each recipe to the report model
        new_report.recipes.add(new_recipe)
    new_report.save()

    # Hard re-direct to index after making a new report
    return HttpResponseRedirect(reverse('index'))


def error(request):
    return render(request, "planner/error.html")


@login_required
def get_recipe(request, id):
    # Returns data on any given recipe
    try:
        recipe = Recipe.objects.get(id=int(id))
        return JsonResponse(recipe.serialize())
    except Recipe.DoesNotExist:
        return JsonResponse({"error": "Recipe doesn't exist."}, status=400)
