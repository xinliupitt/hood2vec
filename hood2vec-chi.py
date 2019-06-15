# running command:
# bokeh serve hood2vec-chi.py --show

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

def make_dataset(zipcodes_to_plot, num_neighbor, period_str):
    with open('chi-zip-code-tabulation-areas-2012.geojson','rt') as json_file:
        chi_json = json.load(json_file)
    chi_json['features'][zipcodes[zipcodes_to_plot]]['properties']['color_type'] = 2

#         print(zipcodes_to_plot)

    chi_zipcode_to_dist = pd.read_pickle('chi_zipcode_to_dist_'+ period_str)

    for zipcode in zipcodes:
        if zipcode in chi_zipcode_to_dist:
            chi_json['features'][zipcodes[zipcode]]['properties']['has_data'] = 'YES'
        else:
            chi_json['features'][zipcodes[zipcode]]['properties']['has_data'] = 'NO'


    if zipcodes_to_plot in chi_zipcode_to_dist:
        distances = chi_zipcode_to_dist[zipcodes_to_plot]
#         print (distances)
        num_neighbor_count = 0
        for neighbor_idx in range(len(distances)):
            if distances[neighbor_idx][0] in zipcodes:
                num_neighbor_count +=1
                chi_json['features'][zipcodes[distances[neighbor_idx][0]]]['properties']['color_type'] = 1
            if num_neighbor_count == num_neighbor:
                break
#             for zipcode_near in distances[:num_neighbor]:
#                 if zipcode_near[0] in zipcodes:
#                     chi_json['features'][zipcodes[zipcode_near[0]]]['properties']['color_type'] = 1
#             print (chi_json['features'][zipcodes[zipcode_near[0]]])

#         for zip_idx in range(len(chi_json['features'])):
#             if 'color_type' not in chi_json['features'][zip_idx]['properties']:
#                 chi_json['features'][zip_idx]['properties']['color_type'] = -1

    # with open('chi_json_update.json', 'w') as fp:
    #     json.dump(chi_json, fp)
    # with open(r'chi_json_update.json','r') as f:
    geojson = json.dumps(chi_json)
    geo_source = GeoJSONDataSource(geojson = geojson)
    return geo_source


def update_to(attr, old, new):
    geo_source_new = make_dataset(zipcode_selection.value, int(num_selection.value), period_selection.value)
#         with open('chi_json_update.json','rt') as json_file:
#             chi_new = json.load(json_file)
#         geo_source.update(geo_source_new)

    geo_source.geojson = geo_source_new.geojson

def make_plot(geo_source):
    color_mapper = LinearColorMapper(palette=Viridis6)
#         color_mapper = LogColorMapper(palette=OrRd9[::-1])
#         TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
    p = figure(title="Chicago",
#                    tools=TOOLS,\
#                    x_axis_location=None, y_axis_location=None,\
               x_axis_type="mercator", y_axis_type="mercator",\
#                    x_range=(-9820000, -9735000), y_range=(5130000, 5160000)
#                     plot_height=1200, plot_width=1000
              )
#         p.grid.grid_line_color = None
    p.axis.visible = False
    p.grid.grid_line_color = None
#         https://bokeh.pydata.org/en/latest/docs/reference/tile_providers.html
    p.add_tile(get_provider(Vendors.STAMEN_TERRAIN))
    p.grid.grid_line_color = None
    p.patches('xs', 'ys', fill_alpha=0.7, fill_color={'field': 'color_type', 'transform': color_mapper},
#                   line_color='white', line_width=0.5,
              source=geo_source,
             )

    hover = HoverTool(tooltips=[('Zip Code', '@ZIP'),
                                ('Has Data', '@has_data')
                    ])
    p.add_tools(hover)

    return p

with open('chi-zip-code-tabulation-areas-2012.geojson','rt') as json_file:
    chi_json = json.load(json_file)

zipcodes = collections.defaultdict()

zipcodes_sorted = []

for zip_idx in range(len(chi_json['features'])):
    zipcodes[chi_json['features'][zip_idx]['properties']['ZIP']] = zip_idx
#         zipcodes_sorted.append(chi_json['features'][zip_idx]['properties']['ZIP'])

# with open('chi_json_update.json', 'w') as fp:
#     json.dump(chi_json, fp)



chi_zipcode_to_dist = pd.read_pickle('chi_zipcode_to_dist_'+ 'midday')
for zipcode in chi_zipcode_to_dist:
    if zipcode in zipcodes:
        zipcodes_sorted.append(zipcode)
del zipcode


zipcodes_sorted.sort()

initial_zipcodes = zipcodes_sorted[0]
initial_num = 3
initial_period = 'midday'

zipcode_selection = Select(options=zipcodes_sorted, value = initial_zipcodes, title = 'Zip code area')
num_selection = Select(options=['3','4','5'], value = str(initial_num), title = 'Number of neareast neighbors')
period_selection = Select(options=['overnight',\
                                   'morning',\
                                   'midday',\
                                   'afternoon',\
                                   'night',\
                                   'category'], value = initial_period, title = 'Period')


zipcode_selection.on_change('value', update_to)
num_selection.on_change('value', update_to)
period_selection.on_change('value', update_to)



geo_source = make_dataset(initial_zipcodes, initial_num, initial_period)

p = make_plot(geo_source)

layout = row(Column(zipcode_selection,num_selection, period_selection), p)
curdoc().add_root(layout)
#     doc.theme = Theme(json=yaml.load(
#             """ attrs:
#                     Figure:

#                         outline_line_color: white
#                         toolbar_location: above
#             """
#         ))
