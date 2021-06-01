# pylint: disable=no-member,line-too-long

from __future__ import print_function

from django.core.management.base import BaseCommand

from passive_data_kit.decorators import handle_lock

from passive_data_kit.models import DataGeneratorDefinition

from ...models import DataPointType

class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    @handle_lock
    def handle(self, *args, **options):
        added = 0

        for definition in DataGeneratorDefinition.objects.all():
            existing = DataPointType.objects.filter(generator=definition.generator_identifier).first()

            if existing is None:
                DataPointType.objects.create(generator=definition.generator_identifier)

                added += 1

        print('Added ' + str(added) + ' new data point type(s).')
