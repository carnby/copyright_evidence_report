<h2>Copyright Evidence Wiki Scraper</h2>

This module is used to scrape the Copyright Evidence Wiki.
It uses the scrapy library.


<h6>Common Functions</h6>
The output of the scraper is a JSON file, containing entries in the following format

class IngredientItem:
	url
	name
	description
	image
	item_type

class RecipeItem(scrapy.Item):
	url
	name
	description
	image
	ingredients
	ingredient_urls
	preparation
	item_type

class IngredientRecipeItem(scrapy.Item):
	'''
	This class relates the ingredientItem to its
	recipe.
	'''
	ingredient_url
	recipe_url
	item_type