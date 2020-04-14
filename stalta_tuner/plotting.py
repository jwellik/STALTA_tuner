#from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, Span, BoxZoomTool
#from bokeh.models.widgets import PreText, Select, RangeSlider
from bokeh.plotting import figure, show

TSPLOTW = 900
TSPLOTH = 200
TSTOOLS = 'pan,reset'


#def multiplot(st):
#    # Timeseries plot variables
#    stplot = st
#    TSPLOTW = 900
#    TSPLOTH = max(100 + (len(stplot)+1)*100, 300)
#    TSTOOLS = 'pan,reset'
#    
#    # normalize plot traces
#    stplot = stplot.normalize()
#    
#    # set up figure
#    waveplot = figure(plot_width=TSPLOTW, plot_height=TSPLOTH, tools=TSTOOLS,
#                 title='Seismic Traces')
#    
#    # plot data
#    ylabels = {}
#    for idx, tr in enumerate(stplot):
#        yval = len(stplot)-idx
#        waveplot.line(tr.times(), tr.data+yval, line_width=2, color='black', line_alpha=0.7)
#       ylabels[yval] = tr.stats.station
#
#    # customize
#    waveplot.yaxis.ticker = list(ylabels.keys())
#    waveplot.yaxis.major_label_overrides = ylabels
#    waveplot.add_tools(BoxZoomTool(dimensions="width"))
#    
#    return waveplot


#def cft_multiplot(source_list, cft_thresh=[None, None], link_xaxes=True, s=False):
#    cft_plots = []
#    for s in source_list:
#        cftplot = figure(plot_width=TSPLOTW, plot_height=TSPLOTH, tools=TSTOOLS, x_axis_type='datetime')
#        cftline = cftplot.line('times', 'cft', source=s, line_width=2, color='black')
#        cftplot.add_tools(BoxZoomTool(dimensions="width"))
#        trig_on_thresh  = Span(location=cft_thresh[1], dimension='width', line_color='red', line_dash='dashed', line_width=2)
#        trig_off_thresh = Span(location=cft_thresh[0], dimension='width', line_color='blue',line_dash='dashed', line_width=2)
#        cftplot.add_layout(trig_on_thresh)
#        cftplot.add_layout(trig_off_thresh)
#        cft_plots.append(cftplot)
#    
#    if link_xaxes:
#        for c in cft_plots[1:]:
#            c.x_range = cft_plots[0].x_range
#    
#    if s:
#        show(column(cft_plots))
#    
#    return cft_plots
