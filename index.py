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

#
# initialize the default view of hood2vec.
#
with open('chi-zip-code-tabulation-areas-2012.geojson','rt') as json_file:      # load geojson files as the background
    chi_json = json.load(json_file)

zipcodes = collections.defaultdict()



# record zipcodes in geojson into zipcodes list
for zip_idx in range(len(chi_json['features'])):
    zipcodes[chi_json['features'][zip_idx]['properties']['ZIP']] = zip_idx



chi_zipcode_to_dist = pd.read_pickle('chi_zipcode_to_dist_'+ 'midday')          # load parameters for default view

# chi_zipcode_to_dist stores the content of hood2vec statistical file. It is a dictionary, where keys are zip codes and values are closest zip codes with corresponding distances to key.

# pick up zip codes existing in both geojson file and hood2vec statistical file
shared_zips = collections.defaultdict(int)
for zipcode in chi_zipcode_to_dist:
    shared_zips[zipcode] +=1
for zipcode in zipcodes:
    shared_zips[zipcode] +=1


zipcodes_sorted = []

for zipcode in shared_zips:
    if shared_zips[zipcode] == 2:
        zipcodes_sorted.append(zipcode)

# sort the shared zip codes for users to select easily (left part of visualization)
zipcodes_sorted.sort()

initial_zipcodes = zipcodes_sorted[0]
initial_num = 3
initial_period = 'midday'

zipcodes_to_plot = initial_zipcodes
num_neighbor = initial_num
period_str = initial_period


with open('chi-zip-code-tabulation-areas-2012.geojson','rt') as json_file:          # load geojson files as the background
    chi_json = json.load(json_file)
chi_json['features'][zipcodes[zipcodes_to_plot]]['properties']['color_type'] = 2    # mark the target area a dark color "2"



chi_zipcode_to_dist = pd.read_pickle('chi_zipcode_to_dist_'+ period_str)


# if a zip code exists in both geojson file and hood2vec statistical file, then "YES", we can visualize it. Otherwise, "NO"
for zipcode in zipcodes:
    if shared_zips[zipcode] == 2:
        chi_json['features'][zipcodes[zipcode]]['properties']['has_data'] = 'YES'
    else:
        chi_json['features'][zipcodes[zipcode]]['properties']['has_data'] = 'NO'


# if closest zip codes are also in geojson file, we can visualize it. We set them to a lighter color "1"
distances = chi_zipcode_to_dist[zipcodes_to_plot]
num_neighbor_count = 0
for neighbor_idx in range(len(distances)):
    if shared_zips[distances[neighbor_idx][0]] == 2:
        num_neighbor_count +=1
        chi_json['features'][zipcodes[distances[neighbor_idx][0]]]['properties']['color_type'] = 1
    if num_neighbor_count == num_neighbor:
        break

# convert json to string
geojson = json.dumps(chi_json)
geo_source = GeoJSONDataSource(geojson = geojson)



#
# interactive view of hood2vec.
#
def make_map(zipcodes_to_plot = '60608', num_neighbor = 3, period_str = 'midday', cate= []):
    """
    input: updated parameters selected by users
    output: updated visualization of nearby neighbors
    """
    with open('chi-zip-code-tabulation-areas-2012.geojson','rt') as json_file:
        chi_json = json.load(json_file)
    chi_json['features'][zipcodes[zipcodes_to_plot]]['properties']['color_type'] = 2


    chi_zipcode_to_dist = pd.read_pickle('chi_zipcode_to_dist_'+ period_str)

    # for an updated period, check the shared zip codes with geojson
    shared_zips = collections.defaultdict(int)
    for zipcode in chi_zipcode_to_dist:
        shared_zips[zipcode] +=1
    for zipcode in zipcodes:
        shared_zips[zipcode] +=1

# if a zip code exists in both geojson file and hood2vec statistical file, then "YES", we can visualize it. Otherwise, "NO"
    for zipcode in zipcodes:
        if shared_zips[zipcode] == 2:
            chi_json['features'][zipcodes[zipcode]]['properties']['has_data'] = 'YES'
        else:
            chi_json['features'][zipcodes[zipcode]]['properties']['has_data'] = 'NO'

    # if user selects to visualize neighbors in venue type representation
    if cate == [0]:
        period_str = 'category'

    chi_zipcode_to_dist = pd.read_pickle('chi_zipcode_to_dist_'+ period_str)


# if closest zip codes are also in geojson file, we can visualize it. We set them to a lighter color "1"
    distances = chi_zipcode_to_dist[zipcodes_to_plot]
    num_neighbor_count = 0
    for neighbor_idx in range(len(distances)):
        if shared_zips[distances[neighbor_idx][0]] == 2:
            num_neighbor_count +=1
            chi_json['features'][zipcodes[distances[neighbor_idx][0]]]['properties']['color_type'] = 1
        if num_neighbor_count == num_neighbor:
            break

    geojson = json.dumps(chi_json)
    geo_source = GeoJSONDataSource(geojson = geojson)

    color_mapper = LinearColorMapper(palette=Viridis6)
    p = figure(title="Chicago",
#                    tools=TOOLS,\
#                    x_axis_location=None, y_axis_location=None,\
#                    x_range=(-9780000, -9745000), y_range=(5130000, 5160000),
               x_axis_type="mercator", y_axis_type="mercator",\
              )
    p.axis.visible = False
    p.grid.grid_line_color = None
#         https://bokeh.pydata.org/en/latest/docs/reference/tile_providers.html
#         p.add_tile(get_provider(Vendors.STAMEN_TERRAIN))
#         p.add_tile(CARTODBPOSITRON)
    p.grid.grid_line_color = None
    p.patches('xs', 'ys', fill_alpha=0.7, fill_color={'field': 'color_type', 'transform': color_mapper},
              source=geo_source,
             )

# information to hover
    hover = HoverTool(tooltips=[('Zip Code', '@ZIP'),
                                ('Has Data', '@has_data')
                    ])
    p.add_tools(hover)

# return the handler p to pass updated values to visualization
    return p



zipcode_selection = Select(options=zipcodes_sorted, value = initial_zipcodes)
num_selection = Select(options=['3','4','5'], value = str(initial_num))
period_selection = Select(options=['overnight',\
                                   'morning',\
                                   'midday',\
                                   'afternoon',\
                                   'night'], value = initial_period)
category_selection = CheckboxGroup(labels=[' category'], active = [])
# if active = [0], it means there are a total of 1 option, and it is checked;
# if active = [0,1], it means there are a total of 2 options, and they are both checked;

# webpage modules
div_title = Div(text=\
          """<h1><tt>hood2vec</tt> app</h1>"""+\
         "You can access <a href=\"https://github.com/xinliupitt/hood2vec\">source code</a> "+\
         "and <a href=\"https://arxiv.org/abs/1907.11951\">backend data generation</a> of this app. "+\
         "The whole project won Foursquare Data Challenge, 2019."
         )


div_zipcode = Div(text=\
                  "<br>Move cursor on the map for the data availability of a zip code. "+\
                  """For a zip code with "Has Data: Yes", you can select that <b>zip code</b> from this menu: """
         )

div_num = Div(text=\
                  "<br>For the selected zip code, you can select the <b>number</b> of nearest neighbors "+\
                  "to be visualized under <tt>hood2vec</tt> metric:"
         )


div_period = Div(text=\
                  "<br>You can select a <b>period</b> "+\
                  "to visualize period-dependent nearest neighbors of selected zip code:"
         )

div_cate = Div(text=\
                  "<br>You can <b>tick</b> to visualize nearest neighbors by "+\
                  "venue categories; "+\
                  "You can <b>untick</b> to visualize nearest neighbors by "+\
                  "<tt>hood2vec</tt> metric: "
         )


# pass user's selected parameters to backend
def update_plot(attr, old, new):
    layout.children[1] = make_map(zipcodes_to_plot = zipcode_selection.value, \
                                  num_neighbor = int(num_selection.value), \
                                  period_str = period_selection.value,\
                                  cate = category_selection.active)

# user's actions to update parameters
zipcode_selection.on_change('value', update_plot)
num_selection.on_change('value', update_plot)
period_selection.on_change('value', update_plot)
category_selection.on_change('active', update_plot)

# webpage layout
layout = row(Column(div_title,div_zipcode,zipcode_selection,div_num,num_selection,\
                    div_period,period_selection, div_cate, category_selection), make_map())
# doc.add_root(layout)
curdoc().add_root(layout)
