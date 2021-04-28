def plot_triggers(st, cft, triggers, THRESH_ON, THRESH_OFF, figsize=(15,8), title='STA/LTA Triggers', zorder=0.5):     # PLOT_TRIGGERS
    import matplotlib.pyplot as plt
    import numpy as np
    fig = plt.figure(figsize=figsize)                                                                      # Create figure
    ax = fig.add_subplot(111)                                            
    ax.plot(cft[0].times('timestamp'), cft[0].data,                                                        # Plot STA/LTA Function
            lw=2.5, color='darkgrey')
    ax.plot(st[0].times('timestamp'), st[0].data/max(abs(st[0].data))+np.mean(cft[0].data),                # Plot normalized seismic trace
            lw=1, color='black')
    ax.axhline(THRESH_ON,color='red',ls=':',alpha=0.5)                                                     # Plot trigger ON line
    ax.axhline(THRESH_OFF,color='blue',ls=':',alpha=0.5)                                                   # Plot trigger OFF line
    for trig in triggers:                                                                                  # For each trigger:
        #ax.axvline(trig['time'].timestamp, color='red', lw=2)
        #ax.axvline((trig['time']+trig['duration']).timestamp, color='blue', lw=2)
        ax.axvspan(trig['time'].timestamp, (trig['time']+trig['duration']).timestamp,                      #     Plot trigger highlight
                   facecolor='yellow', alpha=0.3, zorder=zorder)
    ax.set_title(title)
    
def plot_waveform(st, figsize=(15,8)):                                                                     # PLOT_WAVEFORM
    import matplotlib.pyplot as plt
    import numpy as np
    fig = plt.figure(figsize=figsize)                                                                      # Create figure
    ax = fig.add_subplot(111)                                            
    ax.plot(st[0].times('timestamp'), st[0].data,                                                          # Plot seismic trace
            lw=1, color='black')