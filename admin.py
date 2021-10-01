# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import DataPointType

def reset_definition(modeladmin, request, queryset): # pylint: disable=unused-argument
    queryset.update(definition='{}', first_seen=None, last_seen=None)

reset_definition.description = 'Reset definition'

@admin.register(DataPointType)
class DataPointTypeAdmin(admin.ModelAdmin):
    list_display = ('generator', 'first_seen', 'last_seen',)
    search_fields = ['generator', 'definition', 'description']
    list_filter = ('first_seen', 'last_seen',)

    actions = [reset_definition]
