import scipy.signal as sig
import numpy as np
import matplotlib.pyplot as plt


# todos:
#
# It seems that the current distinction between normData and data class causes some problems. 
# It would probably be better to have just one data class, with some attribute indicating the type
#


#---- The mocap data class ----
class data:
    
    timederOrder = 0;
    filename = ''
            
    #--- initializer ---
    def __init__(self, freq, nMarkers, nFrames, markerNames, data, filename):
        self.freq = freq
        self.nMarkers = nMarkers
        self.nFrames = nFrames
        self.markerNames = markerNames
        self.data = data
        self.filename = filename

    #--- class method to read tsv files ---
    @classmethod
    def readTsv(cls, filename):
        
        file = open(filename)
        
        #reading tsv header until marker names line
        line = 'asdfasdfa'
        while line[0:8] != 'MARKER_N':
            line = file.readline()
            
            if line[0:8] == 'NO_OF_FR':
                nFrames     = int(line.split()[1])
            if line[0:8] == 'NO_OF_MA':
                nMarkers     = int(line.split()[1])
            if line[0:8] == 'FREQUENC':
                freq     = float(line.split()[1])
        
        #line is now marker names line
        markerNames = line.split()[1:]
        
        #the rest is marker data
        data = np.genfromtxt(file)
        
        file.close
            
        return cls(freq, nMarkers, nFrames, markerNames, data, filename)


#---- A norm data class ---- ### this class should probably be removed see todo comment at the top.. 
class normData:
        
    #--- initializer ---
    def __init__(self, data):
        self.freq = data.freq
        self.nMarkers = data.nMarkers
        self.nFrames = data.nFrames
        self.markerNames = data.markerNames
        self.filename = data.filename
        self.timederOrder = data.timederOrder
        
        # A bit of a hack below that makes it possible to convert a normData instance into a data instance without processing.. 
        # This happens if the number of columns in the data matrix is equal to the nFrames of the input data. 
        # It was necessary to make the mc.trim function work on normData. 
        if data.data.shape[1] > data.nMarkers:
            d2 = np.array(zip(*[np.sqrt((data.data[:,[xInd, xInd+1, xInd+2]]*data.data[:,[xInd, xInd+1, xInd+2]]).sum(axis=1)) for xInd in range(data.nMarkers*3) if xInd%3 == 0]))
        elif data.data.shape[1] == data.nMarkers:
            d2 = data.data
            
        self.data = d2
        

####### --- mc functions below --- #######

#---- Time derivative function ----
def timeder(d):
    #This function is not complete:
    #   Needs derivative level as input argument
    #   Needs proper unit scaling (e.g. position unit per second as in the Mocap Toolbox)
    
    #Trying to run savitzky-golay filter. This requires a recent version of scipy
    #if the savitzky-golay function is not found, then do a simple differentiation
    try:
        #running savitzky-golay filter if it is installed on the system
        window_length = int(round(d.freq)) #1 second window length
        if window_length%2 == 0:
            window_length = window_length-1   #reduce window length by one if even
            
        ddata = sig.savgol_filter(d.data, window_length, 1, deriv=1, delta=1.0, axis=0)
        a = data(d.freq, d.nMarkers, d.nFrames, d.markerNames, ddata, d.filename)
    except AttributeError:
        #if scipy version is to old, fall back to the simple differentiation verison
        a = data(d.freq, d.nMarkers, d.nFrames-1, d.markerNames, diff(d.data, axis=0), d.filename)
    
    a.timederOrder = d.timederOrder + 1
    
    return a
    


#---- Plotting function. Temporary version: only a single dimension and a combination of markers ----
def plottimeseries(d, marker, dim): 

    
    t = [x / d.freq for x in range(0,d.nFrames)] # seconds time array
    
    #find the relavant data:
    if d.__class__.__name__ == 'data':
        if np.size(dim) > 1:
            print('for now, plottimeseries only accepts a single dimension 0, 1, or 2')
            return
        relevant_cols = np.array(marker)*3+dim  # columns in data array
    elif d.__class__.__name__ == 'normData':
        relevant_cols = np.array(marker)        # columns in normData array
    else:
        print('could not determine class of mocap data')
        return
    
    #plot the data
    plt.plot(t, d.data[:,relevant_cols])
    
    #plot legend
    if type(marker) is int:
        plt.legend([d.markerNames[marker],])
    elif type(marker) is list:
        plt.legend(list( d.markerNames[i] for i in marker ))
    else:
        pass
    
    #plot title
    if d.timederOrder == 0:
        plt.title('Position data, dim: ' + str(dim))
    elif d.timederOrder == 1:
        plt.title('Velocity data, dim: ' + str(dim))
    elif d.timederOrder == 2:
        plt.title('Acceleration data, dim: ' + str(dim))
    else:
        plt.title('data, timederorder = ' + str(d.timederOrder) + ', dim: ' + str(dim))
    
    plt.xlabel('time (seconds)')
    plt.xlim([0, d.nFrames/d.freq])
    
    plt.draw()
    


#---- Trimming function ----
def trim(d,t1,t2):
    
    
    t = [x / d.freq for x in range(0,d.nFrames)]

    valid_rows = [num for num in range(d.nFrames) if t[num] > t1 and t[num] < t2]
        
    tdata = d.data[valid_rows,:]

    a = data(d.freq, d.nMarkers, np.size(tdata[:,1]), d.markerNames, tdata, d.filename)

    if d.__class__.__name__ == 'data':
        return a  
    elif d.__class__.__name__ == 'normData':
        return normData(a)
         #not a good solution above....
    

#---- Cut two data instances to the length of the shorter one (mccut) ----
def cut(d1,d2):
    #for now, this doesn't work on norm data types.. 
    
    if d1.nFrames < d2.nFrames:
        print('d2 has been shortened')
    elif d1.nFrames > d2.nFrames:
        print('d1 has been shortened')
    else:
        print('d1 and d2 have the same length')
    
    if d1.nFrames != d2.nFrames:

        N = min(d1.nFrames, d2.nFrames)
        dd1Data = d1.data[0:N,:]
        dd2Data = d2.data[0:N,:]
    
    dd1 = data(d1.freq, d1.nMarkers, N, d1.markerNames, dd1Data, d1.filename)
    dd2 = data(d2.freq, d2.nMarkers, N, d2.markerNames, dd2Data, d2.filename)
    
    return dd1, dd2


#---- Cut two data instances to the length of the shorter one (mccut) ----
def spectrogram(d,marker):
    
    
    wsize = 512     # window size and overlap should be included as
    overlap = 500   # optional arguments to the function

    if d.__class__.__name__ == 'data':
        f, t, x = sig.spectrogram(normData(d).data[:,marker],fs=d.freq,nperseg=wsize,noverlap=overlap)
    elif d.__class__.__name__ == 'normData':
        f, t, x = sig.spectrogram(d.data[:,marker],fs=d.freq,nperseg=wsize,noverlap=overlap)
    else:
        return
    
    plt.pcolormesh(t,f,x)
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.xlim([0, d.nFrames/d.freq])
    
    plt.draw()
            

