#! /usr/bin/env python

# Copyright (c) 2012 Felipe Gallego. All rights reserved.
#
# CLAVEL is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
This module calculates the Lomb Scargle periodgram of a light curve.

"""

import numpy as np
import scipy.signal
import pylab

class LSProperties(object):
    """ This class is used as a container for the parameters used to calculate
        the periodgram of a light curve and the proper periodgram.

"""

    def __init__(self, first_freq_ = 1, max_freq_to_seek_ = 10000, 
                 freq_to_calculate_ = 200, number_of_freq_ = 3):
        """ Instantiation method for the CurvePeriods class.

Arguments:
first_freq - First frequency to search.
max_freq_to_seek - maximum frequency to calculate.
freq_to_calculate - number of frequencies to calculate.
max_freq - Maximum frequency calculated.
pgram - periodgram of the light curve.
index_max_value - indexes of the maximum values of the periodgram, these
values are frequencies in the range of frequencies used to calculate the 
periodgram.

"""

        self.first_freq = first_freq_  
        self.max_freq_to_seek = max_freq_to_seek_         
        self.freq_to_calculate = freq_to_calculate_
        self.number_of_freq = number_of_freq_
        self.max_freq = 0.0
        self.index_max_values = []      
        
    def __str__(self):
        """ The 'informal' string representation """
        return "LSProperties: %s(First freq = %.2f freq to calculate = %d)" % \
               (self.__class__.__name__, self.first_freq, self.freq_to_calculate)

class LombScargle(object):
    """ Encapsulates the calculation of parameters from a light curve.
        This class is used as a container to calculate the periodgram 
        of a light curve using the Lomb Scargle method.

    """

    def __init__(self, lsprop_):
        """ Instantiation method for the LombScargle class.  """     

        self.lsprop = lsprop_
        self.max_freq_calculated = 0.0  
        self.nmags = []
        self.ntimes = []

    def __len__(self):
        """ Return the number of measurements for the star. """
        
        return len(self.curve) # number of values in the curve

    def get_index_max_values(self):
        """ Calculate the maximums of the periodgram. """

        # During calculations the series are modified, so a numpy array copy
        # is created, as numpy functions are used in calculations.
        series_copy = np.copy(self.lsprop.pgram)

        # Search for 'number_of_freq' maximums.
        self.lsprop.index_max_values = []
        # Get the first maximum.
        self.lsprop.index_max_values.append(np.argmax(series_copy))

        # Search the next n - 1 maximums.
        for n in range(self.lsprop.number_of_freq - 1):

            # Set to 0 previous maximum.
            series_copy[self.lsprop.index_max_values[n]] = 0

            # Get next maximum
            self.lsprop.index_max_values.append(np.argmax(series_copy))

    def __plot_periodgram(self, nmags, ntimes, freqs):
        """ Plot the periodgram. """

        # Se crea un array con una lista de enteros que crecen de uno en uno 
        # para representar graficamente el tiempo.
        inc = np.linspace(1, len(ntimes), len(ntimes))

        # Grafica 1: valor de las medidas con respecto al tiempo.
        pylab.subplot(4, 1, 1)
        pylab.xlabel('Time')
        pylab.ylabel('Amplitude')
        pylab.plot(ntimes, nmags)

        # Grafica 2: instantes en los que se ha hecho cada medida, un
        # incremento en la curva es una medida, cuando es plana no hay medidas
        pylab.subplot(4, 1, 2)
        pylab.xlabel('Time')
        pylab.ylabel('Num. Meas.')
        pylab.plot(ntimes, inc)

        # Grafica 3: Periodograma, densidad de frecuencias del espectro 
        # que se obtienen de las medidas usando el metodo de Lomb-Scargle
        pylab.subplot(4, 1, 3)
        pylab.xlabel('Frequency')
        pylab.ylabel('Magnitude')
        pylab.plot(freqs, np.sqrt(4*(self.lsprop.pgram/nmags.shape[0])))

        # Se crea un array que solo contiene los maximos.
        freq_pdgram = np.zeros(len(self.lsprop.pgram))
        for n_imv in range(len(self.lsprop.index_max_values)):
            index = self.lsprop.index_max_values[n_imv]
            freq_pdgram[index] = self.lsprop.pgram[index]     

        # Grafica 4: periodograma, densidad de frecuencias del espectro 
        # que se obtienen de las medidas usando el metodo de Lomb-Scargle
        pylab.subplot(4, 1, 4)
        pylab.xlabel('Frequency')
        pylab.ylabel('Magnitude')
        pylab.plot(freqs, freq_pdgram)

        pylab.show()    
    
    def discard_first_measures_far_in_time(self, unix_times):
        """ Analyzes first measure if these are too fat in time from
            the rest of measures. 
        
        """
        
        first_measure = 0
        
        intervals = []

        for i in range(1, len(unix_times)):
            intervals.append(unix_times[i] - unix_times[i - 1])
        
        intervals_a = np.array(intervals)
         
        m = np.mean(intervals_a)
        
        i = 1
        found = False
        
        while not found and i < len(intervals):
            new_m = np.mean(intervals_a[i:])
            dev = new_m + 0.1 * new_m 
            
            if m < new_m + dev and m > new_m - dev:
                found = True
                first_measure = i - 1
            else:
                m = new_m
                
            i += 1
            
        return first_measure
        
    def calculate_periodgram_from_curve(self, unix_times, mags):
        """ Calculates the periogram for one curve. """
        
        first_measure = self.discard_first_measures_far_in_time(unix_times)    
        
        # Calculates the time of each measurement as increments of time
        # regarding the time of the first measurement. First time value is 0.
        first_time = unix_times[first_measure]
        times = [0]  

        # Rest of times are increments regarding the first time.
        for i in range(first_measure + 1, len(unix_times)):
            times.append(unix_times[i] - first_time)

        self.nmags = np.asarray(mags[first_measure:len(unix_times)])
        self.ntimes = np.asarray(times)

        # The periodgram is calculated searching for frecuencia only in the 
        # follwing range of frecuencies. A sample frecuency is calculated
        # using the Nyquist Theorem.
        sample_freq = (len(unix_times) - 1 - first_measure) / \
            ( unix_times[-1] - unix_times[first_measure] )

        # The maximum frequency to search is chosen as the maximum between 
        # the calculated one and the maximum frequency received as argument.
        max_freq_seek = sample_freq / 2
        
        self.lsprop.max_freq_calculated = \
            max_freq_seek if max_freq_seek > self.lsprop.max_freq_to_seek \
            else self.lsprop.max_freq_to_seek

        freqs = np.linspace(0.01, self.lsprop.max_freq_calculated, 
                            self.lsprop.freq_to_calculate)

        # Calculte the periodgram using the Lomb Scargle method 
        # implemented in scipy.
        self.lsprop.pgram = scipy.signal.lombscargle(self.ntimes, self.nmags, freqs)

        # Get the indexes of the maximums in periodgram.
        self.get_index_max_values()     

        return freqs            

    def calculate_periodgram(self, pfilter, curve, plot = False):
        """ Calculates the periodgram using the Lomb Scargle method. """
        
        unix_times, mags, snrs = zip(*curve)

        # Calculate periodgram using times and magnitudes of the curve.
        freqs = self.calculate_periodgram_from_curve(unix_times, mags)

        # Plot the periodgram if indicated so.
        if plot:
            self.__plot_periodgram(self.nmags, self.ntimes, freqs)
            
        return self.lsprop.pgram, self.nmags, self.ntimes
