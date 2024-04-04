# pylint: disable=no-member
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import django

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from .models import DataPointType

@login_required
def pdk_codebook_page(request, generator):
    data_type = get_object_or_404(DataPointType, generator=generator)
    
    categories = {}
    category_names = []
    
    data_types = DataPointType.objects.exclude(first_seen=None).exclude(enabled=False).order_by('name', 'generator')
    
    for category_data_type in data_types:
        category = category_data_type.category
        
        if category is None:
            category = 'Unknown'
            
        point_category = categories.get(category, None)
        
        if point_category is None:
            point_category = []
            
            categories[category] = point_category

            category_names.append(category)
            
        point_category.append(category_data_type)
        
    if 'Unknown' in category_names:
        category_names.remove('Unknown')
    
    category_names.sort()
    
    if categories.get('Unknown', None) is not None:
        category_names.append('Unknown')    
        
    data_categories = []
    
    for category in category_names:
        data_category = {
            'name': category,
            'data_types': []
        }
        
        for category_data_type in categories.get(category, []):
            data_category['data_types'].append(category_data_type)
            
        data_categories.append(data_category)

    context = {
        'data_type': data_type,
        'data_categories': data_categories
    }

    if django.VERSION[0] < 3:
        return render(request, 'pdk_codebook_page_lts11.html', context=context)

    return render(request, 'pdk_codebook_page.html', context=context)

@login_required
def pdk_codebook_sitemap(request): # pylint: disable=unused-argument
    return HttpResponse(json.dumps({}, indent=2), content_type='application/json', status=200)

def pdk_codebook_page_start(request): # pylint: disable=unused-argument
    first_type = DataPointType.objects.all().order_by('generator').first()

    return redirect(first_type)
