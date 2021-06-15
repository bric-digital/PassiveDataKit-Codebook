# pylint: disable=no-member,line-too-long

from __future__ import print_function

from django.core.management.base import BaseCommand

from passive_data_kit.decorators import handle_lock

from ...models import DataPointType

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--identifier',
                            type=str,
                            default='all',
                            help='Generator identifier of specific type to update.')

        parser.add_argument('--sample',
                            type=int,
                            default=25,
                            help='Number of points to sample to construct definition.')

    @handle_lock
    def handle(self, *args, **options):
        query = DataPointType.objects.all()

        if options['identifier'] != 'all':
            query = DataPointType.objects.filter(generator=options['identifier'])

        for point_type in query:
            point_type.update_definition(sample=options['sample'])
