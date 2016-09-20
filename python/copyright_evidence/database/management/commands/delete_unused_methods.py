from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from optparse import make_option
from database import models
import re

class Command(BaseCommand):
	help = 'Removes methods that are not used.'

	def handle(self, *args, **options):
		with transaction.atomic():
			to_delete = []
			for method in models.Method.objects.all():
				if method.study_set.count() > 0:
					continue
				if method.anaysis_method_study_set.count() > 0:
					continue
				if method.collection_method_study_set	.count() > 0:
					continue
				print 'Deleting method: %s' % method
				to_delete.append(method)

			for method in to_delete:
				method.delete()