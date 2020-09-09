[Edited from a project for a Spring 2020 course.]
# Meal_planner
This site automatically generates meal schedules based on a user's pantry. After inputting their  items, users can query for a recipe plan. The site converts the user's pantry entries into standardized names and weights with Nutrionix's API. It then crawls allrecipes.com to find potentially apt recipes. Finally, it runs an algorithm to solve a constraint satisfaction problem, maximizing the number of recipes it can return based on the quantity of ingredients each recipe uses.

Although there is no theoretical limit to the length of a report the project can generate, allrecipes.com appears to slow down users who make repeated requests. Thus, the site caps the number of days at 7, but allows users to swap recipes in and out and generate new reports. 
## What's Contained
Beyond standard Django development files, the project uses three main files:
1. **util.py**
> First, randomly samples several items a user has in their pantry and searches Allrecipes.com. Then, analyzes each recipe in the query results to check if the user's pantry likely contains 51% or more of the listed ingredients. Captures relevant images, ingredients, steps, and other information for each recipe. Repeats until it has found the number of desired recipes. Finally, pre-processes all of the ingredients for Nutrionix API.
2. **api.py**
> Sends ingredients (either from recipes or a user's pantry inputs) to Nutrionix API. Compiles standard names and weights (gr.) for every item.
3. **logic.py**
>Creates and solves a constraint satisifaction problem where the variables are recipes and the constraints involve whether the user has enough ingredients. If it cannot find a perfect solution, it returns the best solution it has found in a set number of re-runs.
## Getting Started
* Install all requirements in requirements.txt.
* Acquire a Nutrionix API Key at https://developer.nutritionix.com/. Set OS environment variables accordingly:
````
API_key = os.environ["nutrix_key"]
API_id = os.environ["nutrix_id"]
````
* Create an account.
* Add items to your pantry.
* Generate a recipe report.
## Sources
* Allrecipes.com
* Nutrionix API (https://developer.nutritionix.com/)
* Artwork: Colors on a Grid, Ellsworth Kelly (1976), Museum of Modern Art
* Logic.py draws heavily from a related project in CS E-80 (Spring 2020), Introduction to Artificial Intelligence.
