''' Creates an interactive tuner for multiple STA/LTA algorithms
Choose STA/LTA algorithms in the drop down widgets, and compare how triggers are
 identified on the seismic trace.
..note:
    This is an example GUI. Data are automatically chosen and can not be changed.
Use the ``bokeh serve`` command to run the example and open in a browser by executing:
    bokeh serve . --show
If the GUI does not open automatically, navigate to the URL
    http://localhost:5006/stocks_hack
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
from obspy.signal.trigger import coincidence_trigger

#####################
## STUB INPUT VARIABLES

settings = {}
settings['server'] = 'vdap.org'
settings['port'] = 16024
settings['scnl'] = ['TMKS.EHZ.VG.00', 'GTOH.EHZ.VG.00', 'YKHR.BHZ.VG.00']
settings['startstop'] = ['2017/10/18 00:00:00', '2017/10/18 00:30:00']


#####################
## LOCAL VARIABLES ##

# sta/lta variables
STALTA_ALGORITHMS = ['Classic STA/LTA', 'Recursive STA/LTA', 'Delayed STA/LTA', 'Z-Detect', 'Carl-Sta-Trig']

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

from obspy.signal.trigger import classic_sta_lta
cft = classic_sta_lta(st[0].data, int(3 * st[0].stats.sampling_rate), int(8 * st[0].stats.sampling_rate))


# set up widgets

ticker_alg = Select(value='Classic STA/LTA', options=STALTA_ALGORITHMS)
stalta_slider = RangeSlider(start=1, end=15, value=(3,8), step=1, title="STA/LTA (seconds)")
trigger_slider = RangeSlider(start=0, end=4, value=(0.8, 1.4), step=0.1, title="CFT Threshold")

# set up plots

source_stalta = ColumnDataSource(data=dict(times=[], cft=[]))
source_triggers = ColumnDataSource(data=dict(ontimes=[], y=[]))

waveplot = figure(plot_width=TSPLOTW, plot_height=TSPLOTH, tools=TSTOOLS, x_axis_type='datetime')
waveplot.line(st[0].times(), st[0].data, line_width=2, color='black')
waveplot.circle('ontimes','y', source=source_triggers, size=10, color='red')
waveplot.add_tools(BoxZoomTool(dimensions="width"))

#waveplot.circle('offtimes','y', source=source_triggers, size=10, color='blue')

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

def update_cft(prev_val, selected=None):
    print(ticker_alg.value)
    if ticker_alg.value == 'Classic STA/LTA':
        from obspy.signal.trigger import classic_sta_lta, trigger_onset
        on = trigger_slider.value[1]; off=trigger_slider.value[0]
        cft = classic_sta_lta(st[0].data, 
                              int(stalta_slider.value[0] * st[0].stats.sampling_rate),
                              int(stalta_slider.value[1] * st[0].stats.sampling_rate))
        on_off = np.array(trigger_onset(cft, on, off))

        source_stalta.data = dict(times=st[0].times(), cft=cft)
        source_triggers.data = dict(ontimes=st[0].times()[on_off[:,0]], y=np.zeros(on_off[:,0].shape))
        #source_triggers.data = dict(offtimes=st[0].times()[on_off[:,1]], y=np.zeros(on_off[:,1].shape))

        sta_on.location = on
        sta_off.location = off
        
    elif ticker_alg.value == 'Recursive STA/LTA':
        from obspy.signal.trigger import recursive_sta_lta, trigger_onset
        on = trigger_slider.value[1]; off=trigger_slider.value[0]
        cft = recursive_sta_lta(st[0].data,
                                int(stalta_slider.value[0] * st[0].stats.sampling_rate),
                                int(stalta_slider.value[1] * st[0].stats.sampling_rate))
        on_off = np.array(trigger_onset(cft, on, off))

        source_stalta.data = dict(times=st[0].times(), cft=cft)
        source_triggers.data = dict(ontimes=st[0].times()[on_off[:,0]], y=np.zeros(on_off[:,0].shape))
        #source_triggers.data = dict(offtimes=st[0].times()[on_off[:,1]], y=np.zeros(on_off[:,1].shape))

        sta_on.location = on
        sta_off.location = off

    elif ticker_alg.value == 'Carl-Sta-Trig [Not Yet Implemented]':
        from obspy.signal.trigger import carl_sta_trig, trigger_onset
        on = 3000; off=-500
        cft = carl_sta_trig(st[0].data, int(5 * st[0].stats.sampling_rate), int(10 * st[0].stats.sampling_rate), 0.8, 0.8)
        on_off = np.array(trigger_onset(cft, on, off))

        source_stalta.data = dict(times=st[0].times(), cft=cft)
        source_triggers.data = dict(ontimes=st[0].times()[on_off[:,0]], y=np.zeros(on_off[:,0].shape))

        sta_on.location = on
        sta_off.location = off

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