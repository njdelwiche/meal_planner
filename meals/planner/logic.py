import random
from .util import *

'''
I heavily derive The logic and contents of this file
from lectures, practice, and homework in CS E-80.
Brian Yu approved this if I cite the origins as such.
'''
# Set how many re-tries wanted if no perfect solution
RERUNS = 10

class Recipe_var():

    def __init__(self, title, url, image, original_ingredients, steps, ingredients):
        self.title = title
        self.url = url
        self.image = image
        self.original_ingredients = original_ingredients
        self.steps = steps
        self.ingredients = ingredients
        self.missing = []

    def __str__(self):
        return f"RECIPE: {self.ingredients}"

class Recipe_solver():
    # Takes as input a list of lists of recipe objects
    def __init__(self, recipes, pantry_dict, acceptable='ALL'):
        self.domains = {
            recipes.index(recipe): recipe
            for recipe in recipes
        }
        self.pantry = pantry_dict
        self.best = 0
        self.acceptable = acceptable

    def solve(self):
        return self.backtrack(dict())

    def update_best(self, number_assigned):
        if number_assigned > self.best:
            self.best = number_assigned
  
    def assignment_complete(self, assignment):
        if self.acceptable == 'ALL':
            return True if len(assignment) == len(self.domains.keys()) else False
        else:
            return True if len(assignment) == self.acceptable else False

    def select_unassigned_variable(self, assignment):
        # Shuffle the order of variables
        # This will help on re-runs to calculate best option
        # if there are no perfect solutions.
        return random.sample([x for x in self.domains.keys() if x not in assignment.keys()], k=1)[0]

    def update_pantry(self, recipe):
        for ingredient in recipe.ingredients.keys():
            # Ideally the naive aptness function doesn't let
            # through many ingredients the user lacks
            # But I will just ignore them if they slipped through
            try:
                pantry_amount = self.pantry[ingredient]
            except KeyError:
                recipe.missing.append(ingredient)
                continue
            # Update the value in the pantry
            recipe_amount = recipe.ingredients.get(ingredient)
            # If any ingredient falls below 0 then assignment fails
            if pantry_amount - recipe_amount >= 0:
                self.pantry[ingredient] -= recipe.ingredients.get(ingredient)
            else:
                return False
        return True

    def revert_pantry(self, recipe):
        for ingredient in recipe.ingredients.keys():
            # Update the pantry back to its original values
            try:
               self.pantry[ingredient] += recipe.ingredients.get(ingredient)
            except KeyError:
                continue

    def backtrack(self, assignment):
        # Return assignment if completed
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.domains.get(var):
            # Add value to assignment and check
            new_assignment = assignment.copy()
            new_assignment[var] = value
            # Check if recipe calls for more of the ingredient
            # than is in the pantry
            if self.update_pantry(value):
                self.update_best(len(new_assignment.values()))
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result
                else:
                    # Re-set the pantry back one state if assignment fails
                    self.revert_pantry(value)
        return None


def final_solve(recipe_objects, pantry_dict):
    # Initialize the solver
    solver = Recipe_solver(recipe_objects, pantry_dict)
    assignment = solver.solve()

    if assignment:
        print("PERFECT ASSIGNMENT")
        return assignment
    else:
        reruns_best = 0
        # Rerun the algorithm, tracking the farthest
        # it gets to a perfect solution
        for x in range(RERUNS):
            solver = Recipe_solver(recipe_objects, pantry_dict)
            solver.solve()
            if solver.best > reruns_best:
                reruns_best = solver.best
        print(f"BEST OF THE RERUNS: {reruns_best}")
        # Initialize a new solver that is content
        # with the imperfect, but best so-far option
        new_solver = Recipe_solver(recipe_objects, pantry_dict, acceptable=reruns_best)
        new_assignment = new_solver.solve()
        while new_solver.best < reruns_best:
            # Find the best imperfect option
            new_solver = Recipe_solver(recipe_objects, pantry_dict, acceptable=reruns_best)
            new_assignment = new_solver.solve()
            if new_assignment:
                print(f"SUCCESS: {new_solver.best}")
        return new_assignment
