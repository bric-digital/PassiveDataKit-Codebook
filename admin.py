# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import DataPointType

@admin.register(DataPointType)
class DataPointTypeAdmin(admin.ModelAdmin):
    list_display = ('generator', 'first_seen', 'last_seen')
    search_fields = ['generator', 'definition', 'description']
    list_filter = ('first_seen', 'last_seen',)
