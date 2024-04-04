# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import DataPointType

def reset_definition(modeladmin, request, queryset): # pylint: disable=unused-argument
    queryset.update(definition='{}', first_seen=None, last_seen=None)

reset_definition.description = 'Reset definition'

def disable_point(modeladmin, request, queryset): # pylint: disable=unused-argument
    queryset.update(enabled=False)

disable_point.description = 'Disable data type'

def enable_point(modeladmin, request, queryset): # pylint: disable=unused-argument
    queryset.update(enabled=True)

enable_point.description = 'Enable data type'

@admin.register(DataPointType)
class DataPointTypeAdmin(admin.ModelAdmin):
    list_display = ('generator', 'name', 'category', 'enabled', 'first_seen', 'last_seen',)
    search_fields = ['generator', 'name', 'category', 'definition', 'description']
    list_filter = ('enabled', 'first_seen', 'last_seen', 'category',)

    actions = [enable_point, disable_point, reset_definition]
