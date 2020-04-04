def multiplot(st):
    # Timeseries plot variables
    stplot = st
    TSPLOTW = 900
    TSPLOTH = max(100 + (len(stplot)+1)*100, 300)
    TSTOOLS = 'pan,reset'
    
    # normalize plot traces
    stplot = stplot.normalize()
    
    # set up figure
    waveplot = figure(plot_width=TSPLOTW, plot_height=TSPLOTH, tools=TSTOOLS,
                 title='Seismic Traces')
    
    # plot data
    ylabels = {}
    for idx, tr in enumerate(stplot):
        yval = len(stplot)-idx
        waveplot.line(tr.times(), tr.data+yval, line_width=2, color='black', line_alpha=0.7)
        ylabels[yval] = tr.stats.station

    # customize
    waveplot.yaxis.ticker = list(ylabels.keys())
    waveplot.yaxis.major_label_overrides = ylabels
    waveplot.add_tools(BoxZoomTool(dimensions="width"))
    
    return waveplot
