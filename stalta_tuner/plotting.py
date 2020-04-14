#from bokeh.io import curdoc
#from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource
#from bokeh.models.widgets import PreText, Select, RangeSlider
#from bokeh.plotting import figure, show

TSPLOTW = 900
TSPLOTH = 200
TSTOOLS = 'pan,reset'



#def create_waveform_plot_source(st):
#    offset = len(st)*2-2 # offset is defined and incremented such that (e.g.) four channels will be plotted top to bottom at center values 6,4,2,0    
#    times = []; traces = [];
#    st_plot = st.copy()
#    st_plot.filter('lowpass', freq=20.0)
#    for s in st_plot:
#        times.append(s.times('timestamp'))
#        traces.append(s.data/max(s.data)+offset)
#        offset -= 2
#    waveclr = ['black']*len(st)
#    return ColumnDataSource( {'times':times, 'traces':traces, 'color':waveclr} )


