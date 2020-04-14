'''
Creates an interactive tuner for multiple STA/LTA algorithms
Choose STA/LTA algorithms in the drop down menu, and compare how triggers are
 identified on the seismic trace.

Specify the datasource, channels, and timeperiod in the configuration file.

USAGE
$ ./run.sh dev_agung_multi

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
from bokeh.layouts import row, column, widgetbox
from bokeh.models import ColumnDataSource, Span, BoxZoomTool, Div
from bokeh.models.widgets import PreText, Select, RangeSlider, TextInput, Button
from bokeh.plotting import figure

from stalta_tuner import utils
from stalta_tuner import plotting

from obspy import UTCDateTime
from obspy.signal.trigger import coincidence_trigger
from obspy.core import Stream

import sys
import importlib

from pprint import pprint

try:
    config = importlib.import_module("configs."+sys.argv[1])
except:
    print('Configuration file not found: {}'.format(sys.argv[1]))

settings = {}
settings['datasource'] = config.datasource
settings['scnl'] = config.scnl
settings['start'] = config.start
settings['ntriggersta'] = config.ntriggersta
if '/' in config.datasource:
    print('File Structure currently not yet supported')
    sys.exit()

print('STA/LTA Tuner')
pprint(settings)
print('')


###########################################################
### LOCAL VARIABLES

# sta/lta variables
#STALTA_ALGORITHMS = ['Classic STA/LTA', 'Recursive STA/LTA', 'Delayed STA/LTA', 'Z-Detect', 'Carl-Sta-Trig']
STALTA_ALGORITHMS = {
    'Classic STA/LTA':
        {'name':'classicstalta',
         'default_stalta': [3, 8],
         'default_trigonoff':[0.8, 1.4],
         'stalta_range':[0,15],
         'trigonoff_range':[0,4],
         'implemented':True},
    'Recursive STA/LTA':
        {'name':'recstalta',
         'default_stalta': [5, 10],
         'default_trigonoff':[0.8, 1.4],
         'stalta_range':[0,15],
         'trigonoff_range':[0,4],
         'implemented':True},    
    'Delayed STA/LTA':
        {'name':'delayedstalta',
         'default_stalta': [5, 10],
         'default_trigonoff':[2.0, 2.5],
         'stalta_range':[0,25],
         'trigonoff_range':[0,10],
         'implemented':True},
   'Carl-Sta-Trig':
       {'name':'carlstatrig',
        'implemented':False},
   'Z-detect':
       {'name':'zdetect',
       'implemented':False},
}


# original values
# STALTA_SEC = [5, 10] # Classic defaults
STALTA_SEC = [3, 8] # Recursive defaults
FREQMIN = 0.5
FREQMAX = 3

# Timeseries plot variables
TSPLOTW = 900
TSPLOTH = 200
TSTOOLS = 'pan,reset'

###########################################################


###########################################################
#### LOAD DATA & INIT CFT

t1 = UTCDateTime(settings['start'][0]); t2 = t1 + 30*60 # limit displayed time to 30'
st = utils.get_stream(settings['datasource'], settings['scnl'], t1, t2)    
st = st.filter('bandpass', freqmin=FREQMIN, freqmax=FREQMAX)

###########################################################


###########################################################
### SET UP WIDGETS
datasource_input   = TextInput(title="Datasource", value="127.0.0.1:16022")
nslc_input         = TextInput(title="NSLCs (comma separated)", value="NN.SSSSS.LL.CCC, ...")
load_data_button = Button(label="Load Data", sizing_mode='stretch_height')
start_input        = TextInput(title="Start Time", value=settings['start'][0])
forward_button     = Button(label=">", sizing_mode='stretch_height')
back_button        = Button(label="<", sizing_mode='stretch_height')
ticker_alg         = Select(value= list(STALTA_ALGORITHMS.keys())[0] , options = list(STALTA_ALGORITHMS.keys()), sizing_mode='stretch_height')
stalta_slider      = RangeSlider(start=1, end=15, value=(3,8), step=1, title="STA/LTA (seconds)")
trigger_slider     = RangeSlider(start=0, end=4, value=(0.8, 1.4), step=0.1, title="Trigger On/Off")
status_msg         = Div(text="""<font color='blue'>STA/LTA Tuner: Status Message.</font>""", width=200, height=25)

print(stalta_slider)
print(stalta_slider.start)
###########################################################


###########################################################
### INIT SOURCE DATA

# Initialize datasource for detection time sand trigger times
source_triggers = ColumnDataSource(data=dict(ontimes=[], y=[]))

# Initialize data sources for CFT
sourcelist_cft = []
for s in st:
    sourcelist_cft.append( ColumnDataSource(data=dict( times=[], cft=[] )) )

# Initialize data source for raw waveforms
offset = len(st)*2-2 # offset is defined and incremented such that (e.g.) four channels will be plotted top to bottom at center values 6,4,2,0    
times = []; traces = [];
for s in st:
    times.append(s.times('timestamp'))
    traces.append(s.data/max(s.data)+offset)
    offset -= 2
waveclr = ['black']*len(st)
source_waveforms = ColumnDataSource( {'times':times, 'traces':traces, 'color':waveclr} )

    
###########################################################



#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv#
### WAVE PLOTS FROM DATASOURCE
waveplot = figure(plot_width=TSPLOTW, plot_height=TSPLOTH, tools=TSTOOLS, x_axis_type='datetime',
    title='Channels listed in same order as STALTA plots below (empty channels not shown)')
waveplot.multi_line('times', 'traces', color='color', source=source_waveforms)
waveplot.circle('ontimes', 'y', source=source_triggers, size=10, color='red')
waveplot.add_tools(BoxZoomTool(dimensions="width"))
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#



###########################################################
### CFT PLOTS
#cft_plots = plotting.cft_multiplot(sourcelist_cft)
trig_on_thresh = []
trig_off_thresh = []
cft_plots = []
i=0
for s in sourcelist_cft:
    title='{}.{}.{}.{}'.format(st[i].stats['station'], st[i].stats['channel'], st[i].stats['network'], st[i].stats['location'])
    cftplot = figure(title=title, plot_width=TSPLOTW, plot_height=TSPLOTH, tools=TSTOOLS, x_axis_type='datetime')
    cftline = cftplot.line('times', 'cft', source=s, line_width=2, color='black')
    cftplot.add_tools(BoxZoomTool(dimensions="width"))
    cftplot.x_range = waveplot.x_range
    trig_on_thresh.append( Span(location=None, dimension='width', line_color='red', line_dash='dashed', line_width=2) )
    trig_off_thresh.append( Span(location=None, dimension='width', line_color='blue', line_dash='dashed', line_width=2) )    
    cftplot.add_layout(trig_on_thresh[-1])
    cftplot.add_layout(trig_off_thresh[-1])
    cft_plots.append(cftplot)
    i+=1
############################################################


###########################################################
### SET UP CALLBACKS

def start_input_change(attrname, old, new):
    print('Changing time')
    update_waveform()

def forward_button_click():
    print('Move time foward 30min')
    start_input.value = (UTCDateTime(start_input.value)+30*60).strftime('%Y-%m-%dT%H:%M:%S')
    
def back_button_click():
    print('Move time back 30min')
    start_input.value = (UTCDateTime(start_input.value)-30*60).strftime('%Y-%m-%dT%H:%M:%S')

def ticker_alg_change(attrname, old, new):
    ### STALTA_ALGORITHMS[ticker_alg.value] is the same as 'new'
    trigger_slider.start = STALTA_ALGORITHMS[ticker_alg.value]['trigonoff_range'][0]
    trigger_slider.end = STALTA_ALGORITHMS[ticker_alg.value]['trigonoff_range'][1]
    update_cft(old)
    
def trigger_slider_change(attrname, old, new):
    update_cft(old)
    
def stalta_slider_change(attrname, old, new):
    update_cft(old)
        
def update_waveform():

    # Load new data
    global st
    st = Stream()

    st = utils.get_stream(settings['datasource'], settings['scnl'], UTCDateTime(start_input.value), UTCDateTime(start_input.value)+30*60)
    st = st.filter('bandpass', freqmin=FREQMIN, freqmax=FREQMAX)

    # Initialize data source for filtered waveform plotting
    st_plot = st.copy()
    st_plot.filter('lowpass', freq=20.0)
    offset = len(st)*2-2 # offset is defined and incremented such that (e.g.) four channels will be plotted top to bottom at center values 6,4,2,0    
    times = []; traces = []
    for s in st_plot:
        times.append(s.times('timestamp'))
        traces.append(s.data/max(s.data)+offset)
        offset -= 2
    waveclr = ['black']*len(st)
    source_waveforms.data = {'times':times, 'traces':traces, 'color':waveclr}
    
    # Update the CFT
    update_cft(ticker_alg.value)

def update_cft(prev_val, selected=None):
    print('{} ({})'.format(ticker_alg.value, STALTA_ALGORITHMS[ticker_alg.value]['name'])) # print algorithm used
    if STALTA_ALGORITHMS[ticker_alg.value]['implemented']:
        
        print('')
        print(st)
        print('')
        
        from stalta_tuner.trigger import coincidence_trigger
        cft, triggers = coincidence_trigger(
                    STALTA_ALGORITHMS[ticker_alg.value]['name'], # Converts human-readable algorithm name to obspy algorithm type
                    trigger_slider.value[1], trigger_slider.value[0],   # threshold for on/off value of the cft
                    st, # stream object # stream for computing data
                    settings['ntriggersta'], # thr_coincidence_sum : number of stations required to have detection
                    sta=stalta_slider.value[0], lta=stalta_slider.value[1] # sta/lta windows
                                                   )
        print('{} Stations required: {} triggers'.format(settings['ntriggersta'], len(triggers))) # print results
        print('')

        i=0
        for p in cft_plots:
            sourcelist_cft[i].data = dict(times=cft[i].times('timestamp'), cft=cft[i].data)
            trig_on_thresh[i].location = trigger_slider.value[1]
            trig_off_thresh[i].location = trigger_slider.value[0]
            i+=1
        #cft_plots = plotting.cft_multiplot(sourcelist_cft, cft_thresh=[stalta_slider.value[0], stalta_slider.value[1]] )
        
        triggert = utils.trigtimes(triggers)
        source_triggers.data = dict(ontimes=triggert, y=np.zeros(triggert.shape))
        
        # Change setting for minimum and maximum Trigger On/Off
        cft_min = []
        cft_max = []
        for c in cft:
            c = c.data[100:] # eliminate the first 100 samples bc those are goofy
            cft_min.append( (min(c)//1) + min(c)%1*10//1/10-.1 ) # weird way to do rounding (probably an easier way)
            cft_max.append( (max(c)//1) + max(c)%1*10//1/10+.1 ) # weird way to do rounding (probably an easier way)
            #print( (max(c.data)//1) + max(c.data)%1*10//1/10+.1 )
        print('new CFT min/max: {},{}'.format(min(cft_min), max(cft_max)))
            
    else:
        print(ticker_alg.value + ' is not yet implemented.')
        ticker_alg.value = prev_val


###########################################################
### INITIALIZE

start_input.on_change('value', start_input_change)        
ticker_alg.on_change('value', ticker_alg_change)
trigger_slider.on_change('value', trigger_slider_change)
stalta_slider.on_change('value', stalta_slider_change)
forward_button.on_click(forward_button_click)
back_button.on_click(back_button_click)

# set up layout
data_header = row(datasource_input, nslc_input, widgetbox(load_data_button, width=40)  ) 
timing_header = row( widgetbox(back_button, width=40), widgetbox(start_input, width=175), widgetbox(forward_button, width=40) ) 
stalta_header = row(ticker_alg, stalta_slider, trigger_slider)
seisplots = column(waveplot, column(cft_plots))
layout = column(data_header, timing_header, stalta_header, status_msg, seisplots)

# initialize
update_cft('Classic STA/LTA')

curdoc().add_root(layout)
curdoc().title = "STA/LTA Tuner"

###########################################################