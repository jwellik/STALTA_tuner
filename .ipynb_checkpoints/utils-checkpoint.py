def grab_data(server, port, scnl, T1, T2, fill_value=0):
    from obspy import Stream
    from obspy.clients.earthworm import Client

    st=Stream()
    client = Client(server, port)
    for sta in scnl:
        station = sta.split('.')[0]
        channel = sta.split('.')[1]
        network = sta.split('.')[2]
        location = sta.split('.')[3]
        print(station, channel, network, location, T1, T2)
        try:
            tr=client.get_waveforms(network, station, location, channel, T1, T2)
            if len(tr)==0:
                tr=create_trace(sta, T1, T2)
            else:
                if len(tr)>1:
                    if fill_value==0 or fill_value==None:
                        tr.detrend('demean')
                        tr.taper(max_percentage=0.01)
                    tr.merge(fill_value=fill_value)
                tr.trim(T1,T2,pad=0)
                tr.detrend('demean')
        except Exception as err:
            print(err)
            print("No data found for "+sta)
            tr=create_trace(sta, T1, T2)
        st+=tr
    print(st)
    return st

def create_trace(sta, T1, T2):
    from obspy import Trace
    from numpy import zeros
    from numpy import empty, nan
    tr=Trace()
    tr.stats['station']=sta.split('.')[0]
    tr.stats['channel']=sta.split('.')[1]
    tr.stats['network']=sta.split('.')[2]
    tr.stats['location']=sta.split('.')[3]
    tr.stats['sampling_rate']=100
    tr.stats['starttime']=T1
    #tr.data=zeros(int((T2-T1)*tr.stats['sampling_rate']))
    tr.data=empty( int((T2-T1)*tr.stats['sampling_rate']) )
    tr.data[:] = nan
    return tr

def orgtrigsbychan(channels, triggers):
    ctrigs = []
    for chan in channels:
        ctimes = []
        for t in triggers:
            if chan in t['stations']:
                ctimes.append(t['time'])
        ctrigs.append({'station':chan, 'times':ctimes})
    return ctrigs

'''Converts list of trigger dictionaries to array of trigger times'''
def trigtimes(triggers):
    import numpy as np
    triggert = []
    for t in triggers:
        triggert.append(t['time'].timestamp)
    return np.array(triggert)