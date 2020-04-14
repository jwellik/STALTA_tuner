def get_stream(datasource, scnl, tstart, tend, fill_value=0, filepattern='*',
    filter=None, samprate=100, verbose=False):
    """
    Generalized (and more robust) way to retrieve waveform data through ObsPy
    Download data from files in a folder, from IRIS, or a Earthworm waveserver
    
    A note on SAC/miniSEED files: as this makes no assumptions about the naming scheme of
    your data files, please ensure that your headers contain the correct SCNL information!
    tstart: UTCDateTime of beginning of period of interest
    tend: UTCDateTime of end of period of interest
    
    filepattern='*'
     You can specify a pattern for your files to reduce the files within the directory
     searched. For example, filepattern=2019.06.*.mseed if your files are miniSEED files
     named by date and you only want those from June 2019. Simple wildcarding is supported
     (i.e., * and ?, [] for ranges of values or lists) but not full regular expressions.
     
    samprate=100
     Resamples all waveforms to the same sample rate.
    
    Returns ObsPy stream objects
    
    Based on code by Alicia Hotovec-Ellis and Aaron Wech.
    
    Example:
    >>> get_stream(['vdap.org', 16024], ['HSR.EHZ.CC.--'], '2004-09-28T00:00:00', '2004-09-28T01:00:00')
    >>> get_stream(['file', '/Users/vdapseismo/data/'], ['HSR.EHZ.CC.--'], '2004-09-28T00:00:00', '2004-09-28T01:00:00')
    >>> get_stream(['IRIS'], ['HSR.EHZ.CC.--'], '2004-09-28T00:00:00', '2004-09-28T01:00:00')
    """    
    
    from obspy import UTCDateTime
    import obspy
    from obspy.clients.fdsn import Client
    from obspy.clients.earthworm import Client as EWClient
    from obspy.core.trace import Trace
    from obspy.core.stream import Stream
    from obspy.signal.trigger import coincidence_trigger
    import numpy as np
    from scipy import stats
    from scipy.fftpack import fft
    import glob, os, itertools
    
    #print(datasource)
    #print(scnl)
    #print(tstart)
    #print(tend)
    
    tstart = UTCDateTime(tstart)
    tend = UTCDateTime(tend)
    
    nets = []; stas = []; locs = []; chas = [];
    for s in scnl:
        #print(s)
        nets.append(s.split('.')[2])
        stas.append(s.split('.')[0])
        locs.append(s.split('.')[3])
        chas.append(s.split('.')[1])
    
    st = Stream()
    
    if '/' in datasource:
        # Retrieve data from file structure
    
        flist = list(itertools.chain.from_iterable(glob.iglob(os.path.join(
            root, filepattern)) for root, dirs, files in os.walk(datasource)))
                
        # Determine which subset of files to load based on start and end times and
        # station name; we'll fully deal with stations below
        flist_sub = []
        for f in flist:
            # Load header only
            stmp = obspy.read(f, headonly=True)
            # Check if station is contained in the stas list
            if stmp[0].stats.station in stas:
                # Check if contains either start or end time
                ststart = stmp[0].stats.starttime
                stend = stmp[0].stats.endtime
                if (ststart<=tstart and tstart<=stend) or (ststart<=tend and
                    tend<=stend) or (tstart<=stend and ststart<=tend):
                    flist_sub.append(f)
        
        # Fully load data from file
        stmp = Stream()
        for f in flist_sub:
            tmp = obspy.read(f, starttime=tstart, endtime=tend)
            if len(tmp) > 0:
                stmp = stmp.extend(tmp)
    
        # merge
        stmp = stmp.taper(max_percentage=0.01)
        for m in range(len(stmp)):
            if stmp[m].stats.sampling_rate != samprate:
                stmp[m] = stmp[m].resample(samprate)
        stmp = stmp.merge(method=1, fill_value=fill_value)
        
        # Only grab stations/channels that we want and in order
        netlist = []
        stalist = []
        chalist = []
        loclist = []
        for s in stmp:
            stalist.append(s.stats.station)
            chalist.append(s.stats.channel)
            netlist.append(s.stats.network)
            loclist.append(s.stats.location)
            
        # Find match of SCNL in header or fill empty
        for n in range(len(stas)):
            for m in range(len(stalist)):
                if (stas[n] in stalist[m] and chas[n] in chalist[m] and nets[n] in
                    netlist[m] and locs[n] in loclist[m]):
                    st = st.append(stmp[m])
            if len(st) == n:
                print('No data found for {}.{}.{}.{}'.format(stas[n],chas[n],nets[n],locs[n]))
                trtmp = Trace()
                trtmp.stats.sampling_rate = samprate
                trtmp.stats.station = stas[n]
                st = st.append(trtmp.copy())
    
    else:
        # retrieve data from server
     
        if '.' not in datasource:
            client = Client(datasource)
        else:
            datasource = datasource.split(':')
            client = EWClient(datasource[0], int(datasource[1]))
        
        for n in range(len(stas)):
            try:
                stmp = client.get_waveforms(nets[n], stas[n], locs[n], chas[n], tstart, tend)
                for m in range(len(stmp)):
                    #stmp[m].data = np.ma.masked_where(stmp[m].data == -2**31, stmp[m].data) # masks out all values of -2**31 (Winston NaN Token)
                    #stmp[m] = stmp[m].split().merge(method=0, fill_value='interpolate')[0] # splits trace at masked values; then re-merges using linear interpolation
                    stmp[m].data = np.where(stmp[m].data==-2**31,0,stmp[m].data)
                    if stmp[m].stats.sampling_rate != samprate:
                        stmp[m] = stmp[m].resample(samprate)
                stmp = stmp.taper(max_percentage=0.01)
                stmp = stmp.merge(method=1, fill_value=fill_value)
            except (obspy.clients.fdsn.header.FDSNException):
                try: # try again
                    stmp = client.get_waveforms(nets[n], stas[n], locs[n], chas[n],
                            tstart, tend)
                    for m in range(len(stmp)):
                        #stmp[m].data = np.ma.masked_where(stmp[m].data == -2**31, stmp[m].data) # masks out all values of -2**31 (Winston NaN Token)
                        #stmp[m] = stmp[m].split().merge(method=0, fill_value='interpolate')[0] # splits trace at masked values; then re-merges using linear interpolation
                        stmp[m].data = np.where(stmp[m].data==-2**31,0,stmp[m].data)
                        if stmp[m].stats.sampling_rate != samprate:
                            stmp[m] = stmp[m].resample(samprate)
                    stmp = stmp.taper(max_percentage=0.01)
                    stmp = stmp.merge(method=1, fill_value=fill_value)
                except (obspy.clients.fdsn.header.FDSNException):
                    print('No data found for {0}.{1}'.format(stas[n],nets[n]))
                    trtmp = Trace()
                    trtmp.stats.sampling_rate = samprate
                    trtmp.stats.station = stas[n]
                    stmp = Stream().extend([trtmp.copy()])
                                            
            # Last check for length; catches problem with empty waveserver
            if len(stmp) != 1:
                print('No data found for {}.{}.{}.{}'.format(stas[n],chas[n],nets[n],locs[n]))
                trtmp = Trace()
                trtmp.stats.sampling_rate = samprate
                trtmp.stats.station = stas[n]
                stmp = Stream().extend([trtmp.copy()])
                
            st.extend(stmp.copy()) 


    st = st.trim(starttime=tstart, endtime=tend, pad=True, fill_value=fill_value)
    
    return st
    
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
            for i in tr:
                i.data[i.data==-2**31] = fill_value
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
    
def grab_file_data(filepath, scnl, tstart, tend, fill_value=0):
    import obspy
    from obspy import Stream, Trace
    import glob, os, itertools
    
    stas=[]; chas=[]; nets=[]; locs=[]
    for sta in scnl:
        stas.append(sta.split('.')[0])
        chas.append(sta.split('.')[1])
        nets.append(sta.split('.')[2])
        if len(sta)==4:
            locs.append(sta.split('.')[3])
        else:
            locs.append('')
    
    st = Stream()
    
    #if opt.server == 'file':
    if True:
    
        # Generate list of files
        #if opt.server == 'file':
        flist = list(itertools.chain.from_iterable(glob.iglob(os.path.join(
        	root,"*")) for root, dirs, files in os.walk(filepath)))
        # "*" takes the place of wildcard lists, see REDPy documentation
                
        # Determine which subset of files to load based on start and end times and
        # station name; we'll fully deal with stations below
        flist_sub = []
        for f in flist:
            # Load header only
            stmp = obspy.read(f, headonly=True)
            # Check if station is contained in the stas list
            if stmp[0].stats.station in stas:
                # Check if contains either start or end time
                ststart = stmp[0].stats.starttime
                stend = stmp[0].stats.endtime
                if (ststart<=tstart and tstart<=stend) or (ststart<=tend and
                    tend<=stend) or (tstart<=stend and ststart<=tend):
                    flist_sub.append(f)
        
        # Fully load data from file
        stmp = Stream()
        for f in flist_sub:
            tmp = obspy.read(f, starttime=tstart, endtime=tend)
            if len(tmp) > 0:
                stmp = stmp.extend(tmp)
    
        # Filter and merge
        #stmp = stmp.filter('bandpass', freqmin=opt.fmin, freqmax=opt.fmax, corners=2,
        #    zerophase=True)
        #stmp = stmp.taper(0.05,type='hann',max_length=opt.mintrig)
        #for m in range(len(stmp)):
        #    if stmp[m].stats.sampling_rate != opt.samprate:
        #        stmp[m] = stmp[m].resample(opt.samprate)
        stmp = stmp.merge(method=1, fill_value=fill_value)
        
        # Only grab stations/channels that we want and in order
        netlist = []
        stalist = []
        chalist = []
        loclist = []
        for s in stmp:
            stalist.append(s.stats.station)
            chalist.append(s.stats.channel)
            netlist.append(s.stats.network)
            loclist.append(s.stats.location)
            
        # Find match of SCNL in header or fill empty
        for n in range(len(stas)):
            for m in range(len(stalist)):
                if (stas[n] in stalist[m] and chas[n] in chalist[m] and nets[n] in
                    netlist[m] and locs[n] in loclist[m]):
                    st = st.append(stmp[m])
            if len(st) == n:
                print("Couldn't find "+stas[n]+'.'+chas[n]+'.'+nets[n]+'.'+locs[n])
                trtmp = Trace()
                trtmp.stats.station = stas[n]
                st = st.append(trtmp.copy())
        
        if len(st)>1:
            if fill_value==0 or fill_value==None:
                st.detrend('demean')
                st.taper(max_percentage=0.01)
            st.merge(fill_value=fill_value)
        st.trim(tstart,tend,pad=0)
        st.detrend('demean')

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