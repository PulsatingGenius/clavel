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
This module calculates the parameters for a light curve.
Some of these parameters are derived from the curve period and other are
statistical calculations from the curve values. 
These parameters are intended to be used as entries for a intelligent
system that classify automatically stars into variable classes according 
to their periodic light variations.

"""

import numpy as np
import scipy.signal
import pylab

class LombScargle(object):
    """ Encapsulates the calculation of parameters from a light curve.

This class is used as a container to calculate the periodgram of a 
light curve using the Lomb Scargle method.

"""

    def __init__(self, id_, pfilter_, curve_, lsprop_):
        """ Instantiation method for the LombScargle class.

Arguments:
curve_ - values of the light curve.
curveperiods_ - 

"""

        self.id = id_
        self.pfilter = pfilter_
        self.curve = curve_

        self.lsprop = lsprop_
        self.max_freq_calculated = 0.0  
        self.nmags = []
        self.ntimes = []

    def __str__(self):
        """ The 'informal' string representation """
        return "LombScargle: %s(star id = %s, filter = %s, %d measurements)" % \
               (self.__class__.__name__, self.id, self.pfilter, len(self))

    def __len__(self):
        """ Return the number of measurements for the star """
        return len(self.curve) # number of values in the curve

    def get_index_max_values(self):
        """ Calculate the maximums of the periodgram """

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

        # Se crea un array con una lista de enteros que crecen de uno en uno 
        # para representar graficamente el tiempo.
        inc = np.linspace(1, len(ntimes), len(ntimes))

        # Grafica 1: valor de las medidas con respecto al tiempo.
        pylab.subplot(4, 1, 1)
        pylab.xlabel('Time')
        pylab.ylabel('Amplitude')
        pylab.plot(ntimes, nmags, 'b+')

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
        for n_imv in range(len(self.lsprop.index_max_value)):
            index = self.lsprop.index_max_value[n_imv]
            freq_pdgram[index] = self.lsprop.pgram[index]     

        # Grafica 4: periodograma, densidad de frecuencias del espectro 
        # que se obtienen de las medidas usando el metodo de Lomb-Scargle
        pylab.subplot(4, 1, 4)
        pylab.xlabel('Frequency')
        pylab.ylabel('Magnitude')
        pylab.plot(freqs, freq_pdgram)

        pylab.show()

    def calculate_periodgram(self, plot = False):
        """ Calculates the periodgram using the Lomb Scargle method """
        unix_times, mags, snrs = zip(*self.curve)

        # Calculates the time of each measurement as increments of time
        # regarding the time of the first measurement. First time value is 0.
        first_time = unix_times[0]
        times = [first_time - first_time]

        # Rest of times are increments regarding the first time.
        for i in range(1, len(unix_times)):
            times.append(unix_times[i] - first_time)

        self.nmags = np.asarray(mags)
        self.ntimes = np.asarray(times)

        # The periodgram is calculates searching for frecuencia only in the 
        # follwing range of frecuencies. A sample frecuency is calculated
        # using the Nyquist Theorem.
        sample_freq = len(self.nmags) / ( unix_times[-1] - unix_times[0] )

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

        if plot:
            self.__plot_periodgram(self.nmags, self.ntimes, freqs)
            
        return self.lsprop.pgram, self.nmags, self.ntimes
