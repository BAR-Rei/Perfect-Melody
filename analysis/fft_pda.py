# coding: utf-8
from builtins import staticmethod
import matplotlib.pyplot as pplt
from scipy.fftpack import rfft
from scipy.io import wavfile

class FFT_PitchDetector:
    """ This class is a toolbox for pitch detection based on Discrete Fourier Transforms.
        It is meant to be used by calling trackPitch() directly.
        The functioning of this class relies on the assertion that FFT data is a list of frequencies.
    """

    @staticmethod
    def trackPitch(fileName, windowSize):
        """ params :
                - fileName (str) : Name of the file of interest
                - windowSize (int) : size of the windows used by FFT (in samples)
            return :
                - pitches : a list of pitches detected by the PDA.
            description :
                trackPitch() will apply a PDA based solely on the FFT to the signal in the
                file described by fileName and return the result as a list of pitches.
        """
        ffts = FFT_PitchDetector.doFFTs(fileName, windowSize);
        pitches=[]
        for fft in ffts:
            pitches.append(FFT_PitchDetector.extractFundamental(fft));
        return pitches;

    @staticmethod
    def doFFTs(fileName, windowSize):
        """ params :
                - fileName (str) : Name of the file of interest
                - windowSize (int) : size of the windows used by FFT (in samples)
            return :
                - ffts : a generator on the list of ffts ran.
            description :
                doFFTs() will run FFTs on every window of size windowSize on the
                file described by fileName and yield the result of each FFT.
                Partially based on Shenghui's answer on Stakh Overflow
                http://stackoverflow.com/questions/23377665/python-scipy-fft-wav-files
        """
        hw = int(windowSize/2)  # from here on out, we are more interested in windowSize/2. hw stands for "half window". hw is quicker to type, and avoids redundant calculi.
        (samplingRate, data) = wavfile.read(fileName);  # loading the file
        for i in range(hw, len(data)-hw, 25*samplingRate/1000):  # here, we isolate one sub-list of data of size windowSize every 25 ms and fft it.
            window = data[i-hw:i+hw]  # get a sublist of data centered around i of length windowSize
            ############ SHENGHUI'S CODE ############
            b = [(ele/2**8.)*2-1 for ele in window]  # this is 8-bit track, b is now normalized on [-1,1)
            c = rfft(b)  # calculate real fourier transform (real numbers list)
            ######### END OF SHENGHUI'S CODE #########
            yield(abs(c)) # generator that will contain the FFTs


    @staticmethod
    def extractFundamental(fftData):
        """ params :
                - fftData: Array of data returned by an fft in which the fundamental frequency is to be found
            return :
                - fundamental: The value of the fundamental
            description :
                extractFundamental() will extract and return the fundamental frequency
                of any signal described by an FFT output. The fundamental frequency is
                assumed to be present in the signal, and thus the first peak in the FFT.
        """
        indexOfFirstPeak = FFT_PitchDetector.findLocalMaximums(fftData)[0];  # get the first peak's index in fftData
        print(indexOfFirstPeak)
        print(fftData)
        return fftData[indexOfFirstPeak];  # return value of the first peak in fftData

    @staticmethod
    def findLocalMaximums(fftData):
        """ params :
                - fftData: Array of data returned by an fft in which the local maximums (peaks) are to be found
            return :
                - peaks: A generator on an array of integers. Each element is the index of a peak in fftData.
            description :
                findLocalMaximums() will find and yield the indices of
                the peaks of any signal described by an FFT output.
        """
        """ idea :
            1) find the mean value of fftData. all values under that are floored to 0, as they are most likely not part of a peak and therefore not interesting.
            Theoretically, we should get alternating 0 ranges and peaks. It should look a little something like:
                [0,...,0,x,x,x,x,x,x,x,x,0,...,0,x,x,x,x,x,x,x,x,0,...,0]
            2) make a list of the indices of the maximums of each range of nonzero data within fftData (hopefully peaks)
        """
        #pplt.plot(fftData)
        mean = fftData.mean()
        print(mean)
        #fftData=[0 for el in fftData if el<mean] # application of step 1)
        for i in range(len(fftData)):
            if fftData[i]<mean:
                fftData[i]=0
        #pplt.plot(fftData)
        #pplt.show()
        """
        We want to isolate individual peaks to process them individually.
        In practice, the 0 ranges won't affect the processing, so we just
        need to seperate peaks from each other, not from 0 ranges.
        """
        keyIndices=[]  # we look for all the indices where a peak starts <=> where a zero range starts.
        for i in range(1,len(fftData)): #we're going to access fftData[i-1] so we start range() at 1 to avoid out of bound exceptions
            if fftData[i]!=0 and fftData[i-1]==0:
                keyIndices.append(i)
        # Assumes fftData starts with zeroes, keyIndices now contains all the indices where peaks start.
        # This allows us to find the index of the max value of each peak.
        peakIndices=[]
        for i in range(len(keyIndices)):
            try:
                peakValue = max(fftData[keyIndices[i]:keyIndices[i+1]])  # find the center of the peak
                # now we have the peak value, we need to find the index associated to that value.
                for j in range(keyIndices[i], keyIndices[i+1]): # we go thru the peak in fftData and yield the index of the max
                    if fftData[j]==peakValue:
                        peakIndices.append(j)
            except IndexError:  # we use the next peak as the end of the search range. if there is no next peak, an IndexError is raised and we go to the end of the list.
                peakValue = max(fftData[keyIndices[i]:])
                for j in range(keyIndices[i], len(fftData)): # we go thru the peak in fftData and yield the index of the max
                    if fftData[j]==peakValue:
                        peakIndices.append(j)

        return peakIndices;
