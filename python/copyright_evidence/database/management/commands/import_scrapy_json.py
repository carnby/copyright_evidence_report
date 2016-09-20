from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from optparse import make_option
from database import models
import json
import re
import itertools

class Command(BaseCommand):
	''' Imports a scrapy JSON file. '''
	help = 'Imports a scrapy JSON file.'

	def add_arguments(self, parser):
		parser.add_argument('scrapy_json', type=str)

	def split_mediawiki_list(self, text, delimiter = ';'):
		for token in text.split(delimiter):
			token = token.strip()
			if token != '':
				yield token.strip()

	def import_method_(self, item):
		'''
		Constructs a Method model from the omonimous Scrapy item.
		'''
		label = item['page_title']
		# Check if there is another method with the same name.
		objs = models.Method.objects.filter(label__iexact = label)
		if objs.exists():
			obj = objs[0]
		else:
			obj = models.Method.objects.create(
				label = item['page_title'])
		if 'qualitative' in item:
			assert item['qualitative'] == 'true'
			obj.qualitative = True
		obj.save()

	def import_author_(self, study):
		'''
		Constructs an Artist model from study Scrapy item.
		'''
		if 'author' not in study:
			print 'Skipping author'
			return
		for author in self.split_mediawiki_list(study['author']):
			obj, _ = models.Author.objects.get_or_create(
				label = author)
			obj.save()
			yield obj

	def import_discipline_(self, study):
		'''
		Constructs a Discipline model from study Scrapy item.
		'''
		if 'discipline' not in study:
			print 'Skipping discipline'
			return
		for discipline in self.split_mediawiki_list(study['discipline'], ','):
			code_label = discipline.strip().split(': ', 1)
			if len(code_label) < 2:
				code_label = code_label * 2
			obj, _ = models.Discipline.objects.get_or_create(
				code = code_label[0].strip(),
				defaults = {'label': code_label[1].strip()})
			obj.save()
			yield obj

	def import_country_(self, study):
		'''
		Constructs a Country model from study Scrapy item.
		'''
		if 'country' not in study:
			print 'Skipping country'
			return
		for country in self.split_mediawiki_list(study['country']):
			obj, _ = models.Country.objects.get_or_create(
				label = country)			
			obj.save()
			yield obj

	def import_industry_(self, study):
		'''
		Constructs an Industry model from study Scrapy item.
		'''
		if 'industry' not in study:
			print 'Skipping industry'
			return
		for industry in self.split_mediawiki_list(study['industry']):
			obj, _ = models.Industry.objects.get_or_create(
				label = industry)
			yield obj

	def import_datasets_(self, item, study_obj):
		'''
		Constructs a Dataset models from study Scrapy item.
		'''
		study = item['source']
		years_regexp = re.compile('[0-9]{4}')
		for dataset in item.get('dataset', []):
			sample_size = dataset.get('sample_size', study.get('sample_size', None))
			if sample_size is None or sample_size.lower() in [
			'not stated', 'global', 'more than 200', 'none', '300+']:
				sample_size = None
			else:
				sample_size = sample_size.replace(',', '')
				sample_size = sample_size.replace('.', '')
				sample_size = sample_size.replace(' ', '')
				sample_size = int(sample_size)
			years = dataset.get('data_material_year', 
				study.get('data_material_year',
					study.get('data_year', None)))
			start_year = None
			end_year = None
			if years is not None:
				years_match = years_regexp.findall(years)
				assert len(years_match) <= 3
				if len(years_match) > 0:
					start_year = int(min(years_match))
					end_year = int(max(years_match))
			
			obj = models.Dataset.objects.create(
				study = study_obj,
				sample_size = sample_size,
				start_material_year = start_year,
				end_material_year = end_year)
			obj.study = study_obj
			obj.save()
		# 	yield obj

	def import_study_(self, study, url):
		'''
		Constructs a Study model from study Scrapy item.
		'''
		yes_no_map = {
			'Yes': True,
			'No': None
		}
		code = url.replace('http://www.copyrightevidence.org/evidence-wiki/index.php/', '')
		# Parse year of it is a number.
		year = study.get('year', None)
		year = year if year is None or year.isdigit() else None
		# Id the study already exists, append the missing information.
		objs = models.Study.objects.filter(
			label = study.get('name_of_study', study['title']))
		if objs.exists():
			assert len(objs) == 1
			obj = objs[0]
			print 'Replacing existing study: %s' % obj.code
			assert obj.title.lower() == study['title'].lower()
		else:
			obj = models.Study.objects.create(
				code = code)
		obj.label = study.get('name_of_study', study['title']) or obj.label
		obj.url = url or obj.url
		obj.year = year or obj.year
		obj.title = study['title'] or obj.title
		obj.abstract  = study.get('abstract', None) or obj.abstract 
		obj.plain_text_proposition = study.get('plain_text_proposition', None) or obj.plain_text_proposition
		obj.intervention_response = study.get('intervention_response', None) or obj.intervention_response
		obj.data_description = study.get('description_of_data', None) or obj.data_description
		obj.link = study.get('link', None) or obj.link
		obj.authentic_link = study.get('authentic_link', None) or obj.authentic_link
		obj.comparative = yes_no_map[study.get('comparative', 'No')] or obj.comparative
		obj.government_or_policy = yes_no_map[study.get('comparative', 'No')] or obj.government_or_policy
		obj.save()

		# Add related fields.
		for issue in self.split_mediawiki_list(study.get('fundamental_issue', ''), ','):
			obj.fundamental_issues.add(models.FundamentalIssue.objects.get(
				code = issue[0]))
		for policy in self.split_mediawiki_list(study.get('evidence_based_policy', ''), ','):
			obj.evidence_based_policies.add(models.EvidenceBasedPolicy.objects.get(
				code = policy[0]))
		# The following models are created on-demand.
		for author in self.import_author_(study):
			obj.authors.add(author)
		for discipline in self.import_discipline_(study):
			obj.disciplines.add(discipline)
		for country in self.import_country_(study):
			obj.countries.add(country)
		for industry in self.import_industry_(study):
			obj.industries.add(industry)
		return obj
		# The other fields require a first pass to be completed.

	def finish_import_study_(self, study):
		'''
		Should be called after all foreign keys are initialized.
		'''
		obj = models.Study.objects.get(label = study.get('name_of_study', study['title']))

		for reference in self.split_mediawiki_list(study.get('reference', '')):
			referenced_study = models.Study.objects.filter(label = reference)
			if referenced_study.exists():
				assert len(referenced_study) == 1
				obj.references.add(referenced_study[0])
			else:
				print 'Referenced study does not exist: %s' % reference
		for method in self.split_mediawiki_list(study.get('method_of_analysis', ''), ','):
			method_obj, _ = models.Method.objects.get_or_create(
				label = method)
			obj.analysis_methods.add(method_obj)
			method_obj.save()
		for method in self.split_mediawiki_list(study.get('method', ''), ','):
			method_obj, _ = models.Method.objects.get_or_create(
				label = method)
			obj.methods.add(method_obj)
			method_obj.save()
		for method in self.split_mediawiki_list(study.get('method_of_collection', ''), ','):
			method_obj, _ = models.Method.objects.get_or_create(
				label = method)
			obj.collection_methods.add(method_obj)
			method_obj.save()

	def handle(self, *args, **options):
		with transaction.atomic():
			# Remove all existing models.
			print 'Deleting all models...'
			models.Method.objects.all().delete()
			models.Author.objects.all().delete()
			models.Discipline.objects.all().delete()
			models.Country.objects.all().delete()
			models.Industry.objects.all().delete()
			models.Study.objects.all().delete()
			models.Dataset.objects.all().delete()

			print 'Importing...'
			for item in json.load(open(options['scrapy_json'])):
				if item['item_type'] == '<class \'copyright_evidence.items.Method\'>':
					print 'Importing method: %s' % item['url']
					self.import_method_(item)
				elif item['item_type'] == '<class \'copyright_evidence.items.Study\'>':
					print 'Importing study: %s' % item['url']
					obj = self.import_study_(item['source'], item['url'])
					print 'Importing datasets'
					self.import_datasets_(item, obj)
				else:
					print 'Skipped generic page: %s' % item['url']

			# Do a second pass to include additional fields.
			for item in json.load(open(options['scrapy_json'])):
				if item['item_type'] == '<class \'copyright_evidence.items.Study\'>':
					print 'Finishing study: %s' % item['url']
					self.finish_import_study_(item['source'])
			print 'Committing...'