from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from optparse import make_option
from database import models
import re

class Command(BaseCommand):
	help = 'Removes duplicates from the database.'

	def generic_remove_duplicates_(self, models, cmp, merge_into):
		'''
		Generic function to remove duplicates.
		  - 'models' is the queryset containing all objects to be deduped.
		    The order of the objects matters: duplicates are merged into
		    the one that appears first.
		  - 'cmp' is a function that returns True if the two objects are duplicates.
		  - 'merge' is a function that merges the second object into the first one.
		'''
		to_be_removed = []
		for obj_2 in models:
			for obj_1 in models:
				if obj_1 in to_be_removed:
					continue
				if obj_1 == obj_2:
					break
				if cmp(obj_1, obj_2):
					print 'Merging models: %s <- %s' % (obj_1, obj_2)
					merge_into(obj_1, obj_2)
					obj_1.save()
					to_be_removed.append(obj_2)
		for obj in to_be_removed:
			obj.delete()

	def handle(self, *args, **options):
		with transaction.atomic():
			print 'Processing Author'
			author_regexp = re.compile(r'[^a-zA-Z]')
			def cmp_author(x, y):
				return author_regexp.sub('', x.label.lower()) == author_regexp.sub('', y.label.lower())

			def merge_author(x, y):
				for study in y.study_set.all():
					x.study_set.add(study)

			self.generic_remove_duplicates_(
				models.Author.objects.all().order_by('pk'),
				cmp_author, merge_author)