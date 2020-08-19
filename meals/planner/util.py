import requests
from bs4 import BeautifulSoup
import random
import time

# Lower and upper bound for ingredients search
lower = 2
upper = 4

# This helps figure out where a recipe ends after I
# combine all the ingredients in several recipes and
# send them to Nutrionix API.
DELIMITER_NAME = "pomegranate molasses"
DELIMITER = f"\n1 gallon of {DELIMITER_NAME}"

# Bad text for cleaning
undesired_text = ["Add all ingredients to list", "Advertisement"]
BRAND = [" - Allrecipes.com", " | Allrecipes", " Recipe"]

# Sensitivty of recipe ingredient aptness
THRESHOLD = .4
APT_RECIPES = 2

DEF_IMG = "https://www.moma.org/media/W1siZiIsIjM5MTE4OCJdLFsicCIsImNvbnZlcnQiLCItcXVhbGl0eSA5MCAtcmVzaXplIDIwMDB4MjAwMFx1MDAzZSJdXQ.jpg?sha=6d102ab5909153d5"


def clean(text):
    """
    Splits lines and removes white space and undesired text
    from scraped text.
    """
    # Handles cleaning title pages
    if isinstance(text, str):
        for x in BRAND:
            text = text.replace(x, '')
        return text
    # Handles cleaning lists of text
    better_text = []
    for item in text:
        cleaned = ''.join([line.strip() for line in item.splitlines()])
        # Remove any thin spaces that abound on the site
        better_text.append(cleaned.replace(u"\u2009", " "))
    return [x for x in better_text if x and x not in undesired_text]


def get_recipe(url):
    """
    Scrapes the relevant data from Allrecipes website. Handles
    a couple different formats that the site has for displaying
    recipes, instructions, and images.
    """
    page = requests.get(url, timeout=12)
    soup = BeautifulSoup(page.content, 'html.parser')
    print(f"LOADED: {url}")

    title = clean(soup.title.string)
    img = soup.find('img', {'class': 'rec-photo'})
    if not img:
        # Set dummy url
        img_url = DEF_IMG
    else:
        img_url = img.get('src')

    # First method the site sometimes shows recipes
    ingredients = soup.find_all('li', {'class': 'ingredients-item'})
    steps = soup.select(".instructions-section .section-body")

    # Second method recipes are displayed
    if not ingredients:
        ingredients = soup.find_all('li', {'class': 'checkList__line'})
    if not steps:
        steps = soup.find_all('li', {'class': 'step'})

    # Loop over and clean the items and steps
    cleaned_ingredients = "\n".join(clean([item.get_text() for item in ingredients]))
    cleaned_ingredients += DELIMITER
    cleaned_steps = "\n".join(clean([step.get_text() for step in steps]))
    return (title, url, img_url, cleaned_ingredients, cleaned_steps)


def get_search_results(include, exclude, num_recipes):
    include = ",".join(include)
    exclude = exclude
    url = f"http://www.allrecipes.com/search/results/?ingIncl={include}&ingExcl={exclude}"
    print(f"SEARCHING ON {url}")
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Find and save the recipe links in a list
    results = soup.find_all('article', {'class': 'fixed-recipe-card'})
    if not results:
        results = soup.find_all('div', {'class': 'fixed-recipe-card'})

    links = [result.find('a').get('href') for result in results]

    # Had some problems with this function and the timing
    # This seemed to fix it
    if num_recipes > 1:
        time.sleep(2)
    return links


def naive_aptness(pantry, ingredients):
    """
    Determines whether a given list of ingredients is
    suitable for the user based on some globally-set
    threshold. To reduce API calls, it naively searches
    whether the user has an ingredient just based on whether
    one of their pantry items appears anywhere in the string
    of the ingredients line.
    """
    have = 0
    total = len([x for x in ingredients.splitlines() if "optional" not in x.lower()])
    for x in ingredients.splitlines():
        if [y for y in pantry if y.lower() in x.lower()]:
            have += 1
    aptness = have / total
    print(aptness)
    if aptness < THRESHOLD:
        return False
    return True


def load_apt_recipes(pantry, exclude, num_recipes):
    '''
    Does the final heavy lifting of calling the helper
    functions and acquring the recipe data from
    allrecipes.com.
    '''
    good_options = []
    for x in range(num_recipes):
        apt_number = 0
        # Randomly choose search query based on user's pantry
        include = random.sample(pantry, random.randint(lower, upper))
        exclude = exclude
        # Query and store search results
        recipes = get_search_results(include, exclude, num_recipes)
        # Sometimes there are no recipes found
        # Perform another search in this event
        while (len(recipes) < APT_RECIPES):
            print("Could not find enough: searching again")
            include = random.sample(pantry, random.randint(lower, upper))
            recipes = get_search_results(include, exclude, num_recipes)

        for recipe in recipes:
            # Continue analyzing the recipes until cutoff met
            if apt_number < APT_RECIPES:
                option = get_recipe(recipe)
                apt = naive_aptness(pantry, option[3])
                # Only save ones that meet aptness threshold
                if apt:
                    apt_number += 1
                    good_options.append(option)
            else:
                continue
    combined_ingredients = [x[3] for x in good_options]
    return (good_options, combined_ingredients)


def separate(input):
    '''
    Separates the large result of all ingredients
    received by API call back into individual recipes
    as known by the hard-coded delimiter.
    '''
    separated = []
    temp = {}
    for x in input:
        if x[0].lower() == DELIMITER_NAME.lower():
            # Attach temp dict to central list and reset it
            separated.append(temp)
            temp = {}
        else:
            # Updated dict based on x, which is an (item, quantity) tuple
            temp[x[0]] = x[1]
    return separated
