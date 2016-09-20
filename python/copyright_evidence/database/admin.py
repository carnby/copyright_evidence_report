from django.contrib import admin

import models

admin.site.register(models.Method)
admin.site.register(models.Author)
admin.site.register(models.FundamentalIssue)
admin.site.register(models.EvidenceBasedPolicy)
admin.site.register(models.Discipline)
admin.site.register(models.Country)
admin.site.register(models.Industry)
admin.site.register(models.Study)
admin.site.register(models.Dataset)

admin.site.register(models.Domain)
admin.site.register(models.GoogleDMCARequest)
admin.site.register(models.GoogleDMCARequestDomain)
