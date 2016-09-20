from __future__ import unicode_literals

from django.db import models

class Method(models.Model):
	'''
	Methodologiy used in a Study.
	'''
	label = models.CharField(
		primary_key = True,
		max_length = 255)
	qualitative = models.BooleanField(
		default = False,
		help_text = 'Whether the method is qualitative.')

	def __unicode__(self):
		return self.label

class Author(models.Model):
	label = models.CharField(
		primary_key = True,
		max_length = 255)

	def __unicode__(self):
		return self.label

class FundamentalIssue(models.Model):
	code = models.CharField(
		primary_key = True,
		max_length = 1)
	label = models.CharField(
		max_length = 511)
	description = models.CharField(
		max_length = 511)

	def __unicode__(self):
		return self.label

class EvidenceBasedPolicy(models.Model):
	code = models.CharField(
		primary_key = True,
		max_length = 1)
	label = models.CharField(
		max_length = 511)
	description = models.CharField(
		max_length = 511)

	def __unicode__(self):
		return self.label

class Discipline(models.Model):
	code = models.CharField(
		primary_key = True,
		max_length = 63)
	label = models.CharField(
		max_length = 511)

	def __unicode__(self):
		return '%s: %s' % (self.code, self.label)

class Country(models.Model):
	label = models.CharField(
		primary_key = True,
		max_length = 255)
	alpha3 = models.CharField(
		unique = True,
		max_length = 3,
		# Can be null at the beginning.
		null = True,
		help_text = 'The three letter country code for this country.')

	def __unicode__(self):
		return self.label

class Industry(models.Model):
	label = models.CharField(
		primary_key = True,
		max_length = 255)

	def __unicode__(self):
		return self.label

class Study(models.Model):
	code = models.CharField(
		primary_key = True,
		max_length = 255)
	label = models.CharField(
		max_length = 511)
	url = models.CharField(
		max_length = 511,
		help_text = 'URL to the corresponding Wiki page.')
	year = models.IntegerField(
		null = True,
		help_text = 'Year of publication.')
	title = models.CharField(
		max_length = 511,
		help_text = 'Title of the study.')
	abstract = models.TextField(
		null = True,
		help_text = 'Abstract of the study.')
	plain_text_proposition = models.TextField(
		null = True,
		help_text = 'Main results of the study.')
	intervention_response = models.TextField(
		null = True,
		help_text = 'Policy implications as stated by author.')
	data_description = models.TextField(
		help_text = 'Description of the data.')
	link = models.CharField(
		max_length = 511,
		null = True,
		help_text = 'URL to the PDF of the study.')
	authentic_link = models.CharField(
		null = True,
		max_length = 511,
		help_text = 'URL to the original version of the study.')
	comparative = models.BooleanField(
		default = False,
		help_text = 'Whether the study is comparative.')
	literature_review = models.BooleanField(
		default = False,
		help_text = 'Whether the study contains a literature review.')
	government_or_policy = models.BooleanField(
		default = False,
		help_text = 'Whether the study is a governament or policy study.')
	authors = models.ManyToManyField('Author')
	references = models.ManyToManyField(
		'Study',
		related_name = 'referencing_study_set',
		help_text = 'Other works referenced in the study.')
	fundamental_issues = models.ManyToManyField(
		'FundamentalIssue',
		help_text = 'Fundamental issue(s) covered in the study.')
	evidence_based_policies = models.ManyToManyField(
		'EvidenceBasedPolicy',
		help_text = 'Evidence based policies covered in the study.')
	disciplines = models.ManyToManyField(
		'Discipline',
		help_text = 'Discipline(s) of the study.')
	analysis_methods = models.ManyToManyField(
		'Method',
		related_name = 'anaysis_method_study_set',
		help_text = 'Analysis method(s) of the study.')
	methods = models.ManyToManyField(
		'Method',
		related_name = 'study_set',
		help_text = 'Method(s) of the study.')
	collection_methods = models.ManyToManyField(
		'Method',
		related_name = 'collection_method_study_set',
		help_text = 'Collection method(s) of the study.')
	countries = models.ManyToManyField(
		'Country',
		help_text = 'Countries mentioned in the study.')
	industries = models.ManyToManyField(
		'Industry',
		help_text = 'Industry(ies) involved in the study.')

	def __unicode__(self):
		return self.label
	
class Dataset(models.Model):
	'''
	Dataset used in a Study.
	'''
	study = models.ForeignKey('Study')
	sample_size = models.IntegerField(
		null = True,
		help_text = 'Sample size of the dataset.')
	start_material_year = models.IntegerField(
		null = True,
		help_text = 'The year when the data collection began.')
	end_material_year = models.IntegerField(
		null = True,
		help_text = 'The year when the data collection ended.')

	def __unicode__(self):
		return '%s, %s' % (self.id, self.study.label)

##############################################
# Models from the Google Transparency report #
##############################################

class Domain(models.Model):
	'''
	An internet domain.
	The root domain ('') is the only domain without a parent.
	'''
	label = models.CharField(
		primary_key = True,
		max_length = 255,
		help_text = 'Name of the domain.')
	parent = models.ForeignKey('Domain',
		null = True,
		related_name = 'children',
		help_text = 'Name of the parent domain.')

	def _get_root_domain(self):
		return Domain.objects.get(label = '')

	''' Returns the root domain. '''
	root_domain = property(_get_root_domain)

	def __unicode__(self):
		return self.label


class GoogleDMCARequest(models.Model):
	'''
	A request sent to Google to remove copyrighted material.
	'''
	code = models.IntegerField(
		primary_key = True,
		help_text = 'The ID of the request in Google.')
	date = models.DateTimeField(
		help_text = 'The date of the request.')
	lumen_url = models.CharField(
		max_length = 511,
		help_text = 'URL in Lumen of the request.')
	from_abuser = models.BooleanField(
		help_text = 'Whether the request came from an abuser.')

	def __unicode__(self):
		return str(self.code)

class GoogleDMCARequestDomain(models.Model):
	request = models.ForeignKey('GoogleDMCARequest')
	domain = models.ForeignKey('Domain')
	removed_count = models.IntegerField(
		help_text = 'Number of URLs that have been removed.')
	no_action_count = models.IntegerField(
		help_text = 'Number of URLs for which no action was taken.')
	under_review_count = models.IntegerField(
		help_text = 'Number of URLs currently under review.')

	class Meta:
		unique_together = [('request', 'domain')]

	def __unicode__(self):
		return '%s, %s' % (self.request, self.domain)
