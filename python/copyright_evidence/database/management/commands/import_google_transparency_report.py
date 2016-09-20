from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from optparse import make_option
from database import models
import csv
import dateutil.parser

class Command(BaseCommand):
	''' Imports the Google transparency report CSV files. '''
	help = 'Imports the Google transparency report CSV files.'

	def add_arguments(self, parser):
		parser.add_argument('request_file', type=str)
		parser.add_argument('domain_file', type=str)

	def create_domain_(self, domain):
		if domain == '':
			return models.Domain.objects.get(label = '')
		obj, created = models.Domain.objects.get_or_create(
			label = domain)
		if created:
			# Add parent.
			domain_split = domain.rsplit('.', 1)
			if len(domain_split) > 1:
				assert len(domain_split) == 2
				parent_domain = self.create_domain_(domain_split[1])
			else:
				parent_domain = self.create_domain_('')
			obj.parent = parent_domain
		return obj

	def handle(self, *args, **options):
		with transaction.atomic():
			# Remove all existing data.
			print 'Deleting all models...'
			models.GoogleDMCARequestDomain.objects.all().delete()
			models.Domain.objects.all().delete()
			models.GoogleDMCARequest.objects.all().delete()
			
			print 'Importing requests...'
			FROM_ABUSER_DICT = {
				'true': True,
				'false': False
			}
			with open(options['request_file']) as f:
				reader = csv.reader(f, delimiter = ',', quotechar = '"')
				row_count = 0
				for row in reader:
					row_count += 1
					if row_count <= 1:
						continue
					elif row_count % 1000 == 0:
						print 'Imported %d rows.' % row_count
					request = models.GoogleDMCARequest.objects.create(
						code = int(row[0]),
						date = dateutil.parser.parse(row[1]),
						lumen_url = row[2],
						from_abuser = FROM_ABUSER_DICT[row[10]])

			print 'Importing domains...'
			root_domain = models.Domain.objects.create(
				label = '',
				parent = None)
			with open(options['domain_file']) as f:
				reader = csv.reader(f, delimiter = ',', quotechar = '"')
				row_count = 0
				for row in reader:
					row_count += 1
					if row_count <= 1:
						continue
					elif row_count % 1000 == 0:
						print 'Imported %d rows.' % row_count
					request = models.GoogleDMCARequest.objects.get(
						code = row[0])
					domain = self.create_domain_(row[1])
					request_domain = models.GoogleDMCARequestDomain.objects.create(
						request = request,
						domain = domain,
						removed_count = int(row[2]),
						no_action_count = int(row[3]),
						under_review_count = int(row[4]))

			