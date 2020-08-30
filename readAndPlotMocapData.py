from pylab import *
import mocaptoolbox as mc

#importing tsv file into an instance of mc.data class
mcdata1 = mc.data.readTsv('pianist.tsv')



#creating a couple of other mc.data instances, derivates of the original
veldata1 = mc.timeder(mcdata1)
accdata1 = mc.timeder(veldata1)


#creating a mc.normData instance
normveldata1 = mc.normData(veldata1)


#plotting...
figure()
subplot(4,1,1)
mc.plottimeseries(mcdata1,8,2)
title('Vertical position data of marker 8')

subplot(4,1,2)
mc.plottimeseries(veldata1,8,2)
title('Vertical velocity data of marker 8')


subplot(4,1,3)
mc.spectrogram(normveldata1,8)
title('Spectrogram of marker 8 velocity norm')
ylim([0, 5])

subplot(4,1,4)
#there's a trimming function here:
mc.plottimeseries(mc.trim(normveldata1,20,30), [5, 6, 7, 8], 2)
title('Trimmed norm velocity data for four markers')



show()

