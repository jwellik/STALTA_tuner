''' Creates an interactive tuner for multiple STA/LTA algorithms
Choose STA/LTA algorithms in the drop down widgets, and compare how triggers are
 identified on the seismic trace.

Specify the datasource, channels, and timeperiod in the configuration file.

USAGE
$ ./run.sh agung_dev

Help on running Bokeh server:
Use the ``bokeh serve`` command to run the example and open in a browser by executing:
    bokeh serve . --show
If the GUI does not open automatically, navigate to the URL
    http://localhost:5006/stalta_tuner
'''

from os.path import dirname, join

import pandas as pd
import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, Span, BoxZoomTool
from bokeh.models.widgets import PreText, Select, RangeSlider
from bokeh.plotting import figure

import utils
from obspy import UTCDateTime
#from obspy.signal.trigger import coincidence_trigger

import sys
import importlib

try:
    config = importlib.import_module("configs."+sys.argv[1])
except:
    print('Configuration file not found: {}'.format(sys.argv[1]))

settings = {}
settings['server'] = config.server
settings['port'] = config.port
settings['scnl'] = config.scnl
settings['startstop'] = config.startstop

print(settings)

#####################
## LOCAL VARIABLES ##

# sta/lta variables
STALTA_ALGORITHMS = ['Classic STA/LTA', 'Recursive STA/LTA', 'Delayed STA/LTA', 'Z-Detect', 'Carl-Sta-Trig']
STALTA_ALGORITHMS = {
    'Classic STA/LTA':
        {'name':'classicstalta',
        'implemented':True},
    'Recursive STA/LTA':
        {'name':'recstalta',
        'implemented':True},    
    'Delayed STA/LTA':
        {'name':'delayedstalta',
        'implemented':False},
    'Carl-Sta-Trig':
        {'name':'carlstatrig',
        'implemented':False},
    'Z-detect':
        {'name':'zdetect',
        'implemented':False},
}

# original values
# Classic: 5/10 sec
# Recursive: 3/8
STALTA_SEC = [3, 8]

# Timeseries plot variables
TSPLOTW = 900
TSPLOTH = 200
TSTOOLS = 'pan,reset'

# Trigger settings
ntriggersta = 2 # number of required channels w a coincident detection for a trigger

#####################

# Initialize data download and cft calculation

st = utils.grab_data(settings['server'], settings['port'], settings['scnl'],
    UTCDateTime(settings['startstop'][0]), UTCDateTime(settings['startstop'][1]))

from obspy.signal.trigger import coincidence_trigger

from obspy.signal.trigger import classic_sta_lta
cft = classic_sta_lta(st[0].data, int(3 * st[0].stats.sampling_rate), int(8 * st[0].stats.sampling_rate))


# set up widgets

ticker_alg = Select(value= list(STALTA_ALGORITHMS.keys())[0] , options = list(STALTA_ALGORITHMS.keys()) )
stalta_slider = RangeSlider(start=1, end=15, value=(3,8), step=1, title="STA/LTA (seconds)")
trigger_slider = RangeSlider(start=0, end=4, value=(0.8, 1.4), step=0.1, title="Trigger On/Off")

# set up plots

# datasources for STA/LTA functions, detection times, and trigger times
#source_waveform = ColumnDataSource(data=dict(times=[], data=[]))
source_stalta = ColumnDataSource(data=dict(times=[], cft=[]))
source_triggers = ColumnDataSource(data=dict(ontimes=[], y=[]))

print(source_stalta)

# wave trace plot
#waveplot = figure(plot_width=TSPLOTW, plot_height=TSPLOTH, tools=TSTOOLS, x_axis_type='datetime')
#waveplot.line(st[0].times(), st[0].data, line_width=2, color='black')
#waveplot.circle('ontimes','y', source=source_triggers, size=10, color='red')
##waveplot.circle('offtimes','y', source=source_triggers, size=10, color='blue')
#waveplot.add_tools(BoxZoomTool(dimensions="width"))

waveplot = figure(plot_width=TSPLOTW, plot_height=TSPLOTH, tools=TSTOOLS, x_axis_type='datetime')
waveclr = 'black'
offset = 0
for s in st:
    waveplot.line(s.times('timestamp'), s.data/max(s.data)+offset, line_width=2, color=waveclr)
    offset += 2
waveplot.circle('ontimes','y', source=source_triggers, size=10, color='red')
#waveplot.circle('offtimes','y', source=source_triggers, size=10, color='blue')
waveplot.add_tools(BoxZoomTool(dimensions="width"))



# STA/LTA functions
cftplot = figure(plot_width=TSPLOTW, plot_height=TSPLOTH, tools=TSTOOLS, x_axis_type='datetime')
cftline = cftplot.line('times', 'cft', source=source_stalta, line_width=2, color='black')
cftplot.add_tools(BoxZoomTool(dimensions="width"))
cftplot.x_range = waveplot.x_range
sta_on  = Span(location=None, dimension='width', line_color='red', line_dash='dashed', line_width=2)
sta_off = Span(location=None, dimension='width', line_color='blue',line_dash='dashed', line_width=2)
cftplot.add_layout(sta_on)
cftplot.add_layout(sta_off)

# set up callbacks

def ticker_alg_change(attrname, old, new):
    update_cft(old)
    
def trigger_slider_change(attrname, old, new):
    update_cft(old)
    
def stalta_slider_change(attrname, old, new):
    update_cft(old)

    
#coincidence_trigger(trigger_type, thr_on, thr_off, stream, thr_coincidence_sum, trace_ids=None, max_trigger_length=1000000.0, #delete_long_trigger=False, trigger_off_extension=0, details=False, event_templates={}, similarity_threshold=0.7, **options)#[source]¶
    
def update_cft(prev_val, selected=None):
    print(ticker_alg.value)
    print(STALTA_ALGORITHMS[ticker_alg.value]['name'])
    if STALTA_ALGORITHMS[ticker_alg.value]['implemented']:
        from trigger import coincidence_trigger

        #print(st)
        #print(trigger_slider.value)
        #print(stalta_slider.value)
    
        cft, triggers = coincidence_trigger(
                    STALTA_ALGORITHMS[ticker_alg.value]['name'], # Converts human-readable algorithm name to obspy algorithm type
                    trigger_slider.value[1], trigger_slider.value[0],   # threshold for on/off value of the cft
                    st, # stream object
                    ntriggersta, # thr_coincidence_sum : number of stations required to have detection
                    sta=stalta_slider.value[0], lta=stalta_slider.value[1] # sta/lta windows
                                                   )
        print('# Required Stations: {}'.format(ntriggersta))
        print('Number of Triggers: {}'.format(len(triggers)))
        print('')
        print(max(cft[0].data))
        print('')
        #print(triggers)
        #print('')
        
        triggert = utils.trigtimes(triggers)
        source_triggers.data = dict(ontimes=triggert, y=np.zeros(triggert.shape))
        for c in cft:
            source_stalta.data = dict(times=c.times(), cft=c.data)
            
    else:
        print(ticker_alg.value + ' is not yet implemented.')
        ticker_alg.value = prev_val

ticker_alg.on_change('value', ticker_alg_change)
trigger_slider.on_change('value', trigger_slider_change)
stalta_slider.on_change('value', stalta_slider_change)

# set up layout
header = row(ticker_alg, stalta_slider, trigger_slider)
seisplots = column(waveplot, cftplot)
layout = column(header, seisplots)

# initialize
update_cft(None)

curdoc().add_root(layout)
curdoc().title = "STA/LTA Tuner"