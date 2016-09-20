# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class GenericPage(scrapy.Item):
	'''
	Any page that does not fit in another category.
	'''
	url = scrapy.Field()
	page_title = scrapy.Field()
	text = scrapy.Field()
	item_type = scrapy.Field()

class Method(GenericPage):
	'''
	Same as template Method.
	'''
	qualitative = scrapy.Field()

class Study(GenericPage):
	'''
	The information about a copyright evidence Study.
	'''
	class Dataset(scrapy.Item):
		'''
		Same as template Dataset.
		'''
		sample_size = scrapy.Field()
		level_of_aggregation = scrapy.Field()
		data_material_year = scrapy.Field()

	class Source(scrapy.Item):
		'''
		Same as template Source.
		'''
		name_of_study = scrapy.Field()
		author = scrapy.Field()
		title = scrapy.Field()
		year = scrapy.Field()
		full_citation = scrapy.Field()
		abstract = scrapy.Field()
		link = scrapy.Field()
		authentic_link = scrapy.Field()
		reference = scrapy.Field()
		plain_text_proposition = scrapy.Field()
		fundamental_issue = scrapy.Field()
		evidence_based_policy = scrapy.Field()
		discipline = scrapy.Field()
		data_type = scrapy.Field()
		method_of_analysis = scrapy.Field()
		data = scrapy.Field()
		data_source = scrapy.Field()
		intervention_response = scrapy.Field()
		data_year = scrapy.Field()
		data_material_year = scrapy.Field()
		country = scrapy.Field()
		cross_country = scrapy.Field()
		comparative = scrapy.Field()
		industry = scrapy.Field()
		level_of_aggregation = scrapy.Field()
		description_of_data = scrapy.Field()
		sample_size = scrapy.Field()
		method_of_collection = scrapy.Field()
		funded_by = scrapy.Field()
		method = scrapy.Field()
		literature_review = scrapy.Field()
		government_or_policy = scrapy.Field()
	# This is of type Source.
	source = scrapy.Field()
	# This is of type Dataset.
	dataset = scrapy.Field()