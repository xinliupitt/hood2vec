from bokeh.io import show, output_notebook, output_file
from bokeh.models import (
    GeoJSONDataSource,
    HoverTool,
    LinearColorMapper
)
from bokeh.plotting import figure
from bokeh.palettes import Viridis6
from bokeh.tile_providers import CARTODBPOSITRON
from bokeh.models.widgets import CheckboxGroup, Slider, RangeSlider, Tabs
import json
import collections

import bokeh

from bokeh.io import show, output_notebook, push_notebook
from bokeh.plotting import figure

from bokeh.models import CategoricalColorMapper, HoverTool, ColumnDataSource, Panel
from bokeh.models.widgets import CheckboxGroup, Slider, RangeSlider, Tabs

from bokeh.layouts import column, row, WidgetBox
from bokeh.palettes import Category20_16

from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application


import pandas as pd
import numpy as np
from numpy.random import random

from bokeh.core.properties import Instance, Dict, JSON, Any

from bokeh import events
from bokeh.models import (Select, Column, Row, ColumnDataSource, HoverTool,
                          Range1d, LinearAxis, GeoJSONDataSource, ColumnarDataSource)
from bokeh.plotting import figure
from bokeh.io import curdoc

# import os
# import datetime
from collections import OrderedDict
from bokeh.models.widgets import Select
from numpy.random import random, normal, lognormal

from bokeh import events
from bokeh.models import (Select, Column, Row, ColumnDataSource, HoverTool,
                          Range1d, LinearAxis, GeoJSONDataSource, ColumnarDataSource)

from bokeh.models import CheckboxGroup, RadioGroup, Toggle

from bokeh.palettes import Blues9, OrRd9

from bokeh.models import (
    BasicTicker, ColumnDataSource, ColorBar,
    ColorMapper, CustomJS, Div,
    HBar, HoverTool, LinearColorMapper,
    LogColorMapper, MultiSelect, PrintfTickFormatter,
    Select
)

from bokeh.themes import Theme
import yaml
from bokeh.tile_providers import get_provider, Vendors
from bokeh.io import curdoc

with open('chi-zip-code-tabulation-areas-2012.geojson','rt') as json_file:
    chi_json = json.load(json_file)

zipcodes = collections.defaultdict()

zipcodes_sorted = []

for zip_idx in range(len(chi_json['features'])):
    zipcodes[chi_json['features'][zip_idx]['properties']['ZIP']] = zip_idx



chi_zipcode_to_dist = pd.read_pickle('chi_zipcode_to_dist_'+ 'midday')
for zipcode in chi_zipcode_to_dist:
    if zipcode in zipcodes:
        zipcodes_sorted.append(zipcode)
del zipcode


zipcodes_sorted.sort()

initial_zipcodes = zipcodes_sorted[0]
initial_num = 3
initial_period = 'midday'

zipcodes_to_plot = initial_zipcodes
num_neighbor = initial_num
period_str = initial_period


with open('chi-zip-code-tabulation-areas-2012.geojson','rt') as json_file:
    chi_json = json.load(json_file)
chi_json['features'][zipcodes[zipcodes_to_plot]]['properties']['color_type'] = 2


chi_zipcode_to_dist = pd.read_pickle('chi_zipcode_to_dist_'+ period_str)

for zipcode in zipcodes:
    if zipcode in chi_zipcode_to_dist:
        chi_json['features'][zipcodes[zipcode]]['properties']['has_data'] = 'YES'
    else:
        chi_json['features'][zipcodes[zipcode]]['properties']['has_data'] = 'NO'


if zipcodes_to_plot in chi_zipcode_to_dist:
    distances = chi_zipcode_to_dist[zipcodes_to_plot]
    num_neighbor_count = 0
    for neighbor_idx in range(len(distances)):
        if distances[neighbor_idx][0] in zipcodes:
            num_neighbor_count +=1
            chi_json['features'][zipcodes[distances[neighbor_idx][0]]]['properties']['color_type'] = 1
        if num_neighbor_count == num_neighbor:
            break

# convert json to string
geojson = json.dumps(chi_json)
geo_source = GeoJSONDataSource(geojson = geojson)

def make_map(zipcodes_to_plot = '60608', num_neighbor = 3, period_str = 'midday'):
    with open('chi-zip-code-tabulation-areas-2012.geojson','rt') as json_file:
        chi_json = json.load(json_file)
    chi_json['features'][zipcodes[zipcodes_to_plot]]['properties']['color_type'] = 2


    chi_zipcode_to_dist = pd.read_pickle('chi_zipcode_to_dist_'+ period_str)

    for zipcode in zipcodes:
        if zipcode in chi_zipcode_to_dist:
            chi_json['features'][zipcodes[zipcode]]['properties']['has_data'] = 'YES'
        else:
            chi_json['features'][zipcodes[zipcode]]['properties']['has_data'] = 'NO'


    if zipcodes_to_plot in chi_zipcode_to_dist:
        distances = chi_zipcode_to_dist[zipcodes_to_plot]
        num_neighbor_count = 0
        for neighbor_idx in range(len(distances)):
            if distances[neighbor_idx][0] in zipcodes:
                num_neighbor_count +=1
                chi_json['features'][zipcodes[distances[neighbor_idx][0]]]['properties']['color_type'] = 1
            if num_neighbor_count == num_neighbor:
                break

    # convert json to string
    geojson = json.dumps(chi_json)
    geo_source = GeoJSONDataSource(geojson = geojson)
#         geo_source.geojson = geo_source_new.geojson

    color_mapper = LinearColorMapper(palette=Viridis6)
    p = figure(title="Chicago",
#                    tools=TOOLS,\
#                    x_axis_location=None, y_axis_location=None,\
               x_range=(-9780000, -9745000), y_range=(5130000, 5160000),
               x_axis_type="mercator", y_axis_type="mercator",\
              )
    p.axis.visible = False
    p.grid.grid_line_color = None
#         https://bokeh.pydata.org/en/latest/docs/reference/tile_providers.html
#         p.add_tile(get_provider(Vendors.STAMEN_TERRAIN))
    p.add_tile(CARTODBPOSITRON)
    p.grid.grid_line_color = None
    p.patches('xs', 'ys', fill_alpha=0.7, fill_color={'field': 'color_type', 'transform': color_mapper},
              source=geo_source,
             )

    hover = HoverTool(tooltips=[('Zip Code', '@ZIP'),
                                ('Has Data', '@has_data')
                    ])
    p.add_tools(hover)

    return p



zipcode_selection = Select(options=zipcodes_sorted, value = initial_zipcodes, title = 'Zip code area')
num_selection = Select(options=['3','4','5'], value = str(initial_num), title = 'Number of neareast neighbors')
period_selection = Select(options=['overnight',\
                                   'morning',\
                                   'midday',\
                                   'afternoon',\
                                   'night',\
                                   'category'], value = initial_period, title = 'Period')

def update_plot(attr, old, new):
    layout.children[1] = make_map(zipcodes_to_plot = zipcode_selection.value, \
                                  num_neighbor = int(num_selection.value), \
                                  period_str = period_selection.value)


zipcode_selection.on_change('value', update_plot)
num_selection.on_change('value', update_plot)
period_selection.on_change('value', update_plot)


layout = row(Column(zipcode_selection,num_selection, period_selection), make_map())
# doc.add_root(layout)
curdoc().add_root(layout)
