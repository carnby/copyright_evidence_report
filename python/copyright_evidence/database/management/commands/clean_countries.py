from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from optparse import make_option
from database import models
from django_countries import countries

class Command(BaseCommand):
	help = 'Adds the 3-letter iso code to all countries.'

	def handle(self, *args, **options):
		# Mapping from mispelled country names to the correct ones.
		COUNTRY_NAME_MAP = {
			'European Community': 'European Union',
			# 'European Union': None,
			'Global': None,
			'Korea': 'North Korea',
			'Kosovo': None,
			'Morrocco': 'Morocco',
			'Netherland': 'Netherlands',
			'The Netherlands': 'Netherlands',
			'Russian Federation': 'Russia',
			'UK': 'United Kingdom',
			'England': 'United Kingdom',
			'United States': 'United States of America',
			'Vatican City': None}

		EUROPEAN_UNION_COUNTRIES = (
			'Austria',
			'Belgium',
			'Bulgaria',
			'Croatia',
			'Cyprus',
			'Czech Republic',
			'Denmark',
			'Estonia',
			'Finland',
			'France',
			'Germany',
			'Greece',
			'Hungary',
			'Ireland',
			'Italy',
			'Latvia',
			'Lithuania',
			'Luxembourg',
			'Malta',
			'Netherlands',
			'Poland',
			'Portugal',
			'Romania',
			'Slovakia',
			'Slovenia',
			'Spain',
			'Sweden',
			'United Kingdom')

		with transaction.atomic():
			print 'Correcting country names'
			for country in models.Country.objects.all():
				if country.label in COUNTRY_NAME_MAP:
					new_label = COUNTRY_NAME_MAP[country.label]
					print '%s -> %s' % (country.label, new_label)
					if new_label is not None:
						# Move all studies to the new country.
						new_country, _ = models.Country.objects.get_or_create(label = new_label)
						for study in country.study_set.all():
							new_country.study_set.add(study)
					country.delete()

			print 'Splitting European Union'
			eu = models.Country.objects.get(label = 'European Union')
			for label in EUROPEAN_UNION_COUNTRIES:
				country, _ = models.Country.objects.get_or_create(label = label)
				for study in eu.study_set.all():
					country.study_set.add(study) 
			eu.delete()

			print 'Adding country codes'
			for country in models.Country.objects.all():
				code = countries.by_name(country.label)
				if code == '':
					print 'Invalid: %s (%d)' % (country, country.study_set.count())
					country.delete()
					continue
				alpha3 = countries.alpha3(code)
				assert alpha3 is not None
				country.alpha3 = alpha3
				country.save()
