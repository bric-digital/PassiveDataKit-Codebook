# pylint: disable=line-too-long
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import importlib
import json
import sys
import traceback

import markdown
import six

from deepdiff import DeepDiff

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe

from passive_data_kit.models import DataGeneratorDefinition, DataPoint

def update_definition_primitive(definition, value, path):
    if isinstance(value, float) and ('real' in definition[path]['types']) is False:
        definition[path]['types'].append('real')
    elif isinstance(value, int) and ('integer' in definition[path]['types']) is False:
        definition[path]['types'].append('integer')
    if isinstance(value, six.string_types) and ('string' in definition[path]['types']) is False:
        definition[path]['types'].append('string')

    if isinstance(value, (int, float)) and (('real' in definition[path]['types']) or ('integer' in definition[path]['types'])):
        if ('range' in definition) is False:
            definition[path]['range'] = [value, value]
        else:
            if value < definition[path]['range'][0]:
                definition[path]['range'][0] = value

            if value > definition[path]['range'][1]:
                definition[path]['range'][1] = value

    if isinstance(value, six.string_types) and ('string' in definition[path]['types']):
        if ('observed' in definition[path]) is False:
            definition[path]['observed'] = []

        if ('is_freetext' in definition[path]) and definition[path]['is_freetext']:
            pass # Freetext - no need to enumerate values
        else:
            if (value in definition[path]['observed']) is False:
                definition[path]['observed'].append(value)


def update_definition(definition, element, prefix=None): # pylint: disable=too-many-branches
    for key in element:
        value = element[key]

        path = key

        if prefix is not None:
            path = prefix + key

        if (path in definition) is False:
            definition[path] = {}

        existing_def = definition[path]

        if ('types' in existing_def) is False:
            existing_def['types'] = []

        if ('pdk_variable_name' in existing_def) is False:
            existing_def['pdk_variable_name'] = 'Unknown (TODO)'

        if ('pdk_variable_description' in existing_def) is False:
            existing_def['pdk_variable_description'] = 'Unknown (TODO)'

        if isinstance(value, dict):
            if ('object' in existing_def['types']) is False:
                existing_def['types'].append('object')

            update_definition(definition, value, prefix=(path + '.'))
        elif isinstance(value, list):
            if ('list' in existing_def['types']) is False:
                existing_def['types'].append('list')

            for item in value:
                if isinstance(item, (float, int, six.string_types)):
                    update_definition_primitive(definition, value, path + '[]')
                elif isinstance(item, dict):
                    update_definition(definition, item, prefix=(path + '[].'))
                elif isinstance(item, list):
                    print(u'LIST WITHIN LIST[{}]: {} ({})'.format(path, item, type(item)))
                else:
                    print(u'UKNKOWN IN LIST[{}]: {} ({})'.format(path, item, type(item)))

        elif isinstance(value, (float, int, six.string_types)):
            update_definition_primitive(definition, value, path)
        else:
            print(u'UNKNOWN ITEM[{}]: {}'.format(path, value))


class DataPointType(models.Model):
    generator = models.CharField(max_length=1024, unique=True)

    description = models.TextField(max_length=67108864, default='')

    definition = models.TextField(max_length=67108864, default='{}')

    first_seen = models.DateTimeField(null=True, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    def markdown(self):
        return mark_safe(markdown.markdown(self.description)) # nosec

    def get_absolute_url(self):
        return reverse('pdk_codebook_page', args=[self.generator])

    def update_definition(self, sample=25, override_existing=False): # pylint: disable=unused-argument
        definition = json.loads(self.definition)

        data_generator = DataGeneratorDefinition.definition_for_identifier(self.generator)

        point_query = DataPoint.objects.filter(generator_definition=data_generator)[:sample]

        for point in point_query:
            point_def = point.fetch_properties()

            update_definition(definition, point_def)

        original_definition = json.loads(self.definition)

        for app in settings.INSTALLED_APPS:
            try:
                pdk_api = importlib.import_module(app + '.pdk_api')

                pdk_api.update_data_type_definition(definition)
            except ImportError:
                pass
            except AttributeError:
                pass
            except: #pylint: disable=bare-except
                traceback.print_exc()

        diff = DeepDiff(original_definition, definition)

        print(self.generator + ': ' + json.dumps(definition, indent=2))

        to_delete = []

        python_version = sys.version_info[0]

        if 'type_changes' in diff:
            for key in diff['type_changes']:
                if python_version >= 3:
                    if diff['type_changes'][key]['new_type'] == str and diff['type_changes'][key]['old_type'] == unicode: # pylint: disable=undefined-variable
                        to_delete.append(key)
                    elif diff['type_changes'][key]['new_type'] == unicode and diff['type_changes'][key]['old_type'] == str: # pylint: disable=undefined-variable
                        to_delete.append(key)

        for key in to_delete:
            del diff['type_changes'][key]

        print(diff)

        self.definition = json.dumps(definition, indent=2)
        self.save()

    def ordered_variables(self):
        definition = json.loads(self.definition)

        ordered_variables = []
        unordered_variables = []

        for key in definition:
            variable = definition[key]

            variable['pdk_codebook_json'] = json.dumps(variable, indent=2)

            variable['pdk_codebook_key'] = key

            if 'order' in variable:
                ordered_variables.append(variable)
            else:
                unordered_variables.append(variable)

        ordered_variables.sort(key=lambda variable: variable['order'])

        unordered_variables.sort(key=lambda variable: variable['pdk_variable_name'])

        ordered_variables.extend(unordered_variables)

        return ordered_variables
