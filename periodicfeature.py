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
This module calculates the features for a light curve derived from the 
periodgram.These parameters are intended to be used as entries to a system 
that classifies automatically stars into variable classes according to their
periodic light variations.

"""

class PeriodicFeature(object):
    """ Encapsulates the calculation of periodic features of a light curve.

        This class is used as a container for the calculation of periodic features
        from a light curve.
        
    """

    # Names of the features calculated.
    __FUND_FREQ_FEAT_NAME = "Fund_Freq_"
    __FUND_AMP_FEAT_NAME= "Fund_Amp_"
    __AMP_HARM_FEAT_NAME = "Amp_Harm_"
    __FREQ_OFFSET_FEAT_NAME = "Freq_Offset"

    def __init__(self, pgram_, lsprop_, num_freq_ = 3):
        """ Instantiation method for the PeriodicFeature class.

            Arguments:
            num_freq - number of frequencies to sample in the range of frequencies

            """

        self.num_freq = num_freq_
        self.lsprop = lsprop_;
        self.__pgram = pgram_
        
    def __str__(self):
        """ The 'informal' string representation """
        return "PeriodicFeature: %s(numero de frec = %s)" % \
               (self.__class__.__name__, len(self.pgram))

    def __len__(self):
        """ Return the number of frequencies in the periodgram. """
        
        return len(self.pgram)   
    
    def __get_freq_from_index(self, index):
        """ Returns the frequency corresponding to an index of the 
            periodgram. 
        
        """

        freq = 0

        # Check that frequency requested is in the range of frequencies 
        # calculated in periodgram.
        if index >= len(self.__pgram):
            msg = "Index %d is out of range of periodgram[0:%d]" % \
                (index, len(self.__pgram) - 1)
            raise IndexError(msg)
        else:
            # Calculate the interval of frequencies used in periodgram.
            interval = (self.lsprop.max_freq - self.lsprop.first_freq) \
                / self.lsprop.freq_to_calculate

            freq = self.lsprop.first_freq + (index * interval)

        return freq

    def __get_freq_n(self, num_freq):
        """ Return the n frequency of the periodgram. """

        # Check frequency requested is in the range of frequencies calculated,
        # and in that case get the frequency.
        try:
            index = self.lsprop.index_max_values[num_freq]
            return self.__get_freq_from_index(index)
        except IndexError:
            msg = "Frequency index %d is out of range" % num_freq
            raise IndexError(msg)

    def __get_amplitude_n(self, num_freq):
        """ Return the amplitude of the n frequency of periodgram. """

        # Check that at least the number of frequency indicated has been 
        # calculated.
        if num_freq < len(self.lsprop.index_max_values):
            # Get the index for this frequency.
            index = self.lsprop.index_max_values[num_freq]

            # Return the value in th periodgram for the index of the 
            # frequency requested.
            return self.__pgram[index]
        else:
            msg = "Amplitude index %d is out of range" % num_freq
            raise IndexError(msg)

    def __get_freq_harm_n(self, num_freq, harm):
        """ Return the frequency of the harmonic requested if this harmonic 
            exists in the periodgram calculated, otherwise returns 0.
            
            num_freq - Number of the frequency whose harmonic is returned. 
            harm -  Number of the harmonic to return for the frequency indicated.
        
        """

        # Frequency returned is 0 if this harmonic has not been calculated in the
        # periodgram.
        freq_harm = 0

        # Number of maximum frequencies calculated.
        size = len(self.lsprop.max_values)

        # Check frequency requested is in the range of frequencies calculated.
        if num_freq >= size:
            msg = "Frequency index %d is out of range" % num_freq
            raise IndexError(msg)
        else:
            # Only 1, 2 .. num_freq - 1 harmonic are used.
            if harm < 1 or harm > num_freq:
                msg = "Harmonic index %d is out of range (1-%d)" % \
                    (harm, num_freq)
                raise IndexError(msg)

            # The harmonic is calculated as the product of the fundamental 
            # frequency and the number of the harmonic requested plus 1. 
            # i.e. first harmonic is twice the fundamental frequency, second 
            # harmonic is three times and so on.
            actual_harm_index = num_freq * (harm + 1)

            # Check if this harmonic in in the periodgram calculated.
            if actual_harm_index < len(self.__pgram):
                # Calculate the frequency for this index.
                freq_harm = self.__get_freq_from_index(actual_harm_index)

        return freq_harm

    def __get_amp_harm_n(self, num_freq, harm):
        """ Returns the amplitude of the harmonic requested if this harmonic 
            exists in the periodgram calculated, otherwise returns 0.
        
            num_freq - Number of the frequency whose harmonic amplitude is returned. 
            harm -  Number of the harmonic to get for the frequency indicated.        
        
        """

        # Amplitude returned is 0 if this harmonic has not been calculated in the
        # periodgram.
        amplitude = 0

        # Number of manimum frequencies calculated.
        size = len(self.lsprop.index_max_values)

        # Check frequency requested is in the range of frequencies calculated.
        if num_freq >= size:
            msg = "Frequency index %d is out of range (0,%d)" % \
                (num_freq, size-1)
            raise IndexError(msg)

        # The harmonic is calculated as the product of the fumdamental frequency
        # and the number of the harmonic requested plus 1. i.e. first harmonic 
        # is twice the fundamental frequency, second harmonic is triple and so 
        # on.
        actual_harm_index = self.lsprop.index_max_values[num_freq] * (harm + 1)

        # Check if this harmonic exists in the periodgram calculated.
        if actual_harm_index < len(self.__pgram):
            amplitude = self.__pgram[actual_harm_index]

        return amplitude

    def get_fund_freq(self, n):
        """ Return the n maximum frequency of the periodgram. """

        param_name = "%s%d" % (PeriodicFeature.__FUND_FREQ_FEAT_NAME, n)

        if n < self.num_freq:
            return self.__get_freq_n(n), param_name
        else:
            msg = "Fundamental frequency requested %d is out of range (0-%d)" \
                % (n, self.num_freq)
            raise IndexError(msg)

    def get_amplitude(self, n):
        """ Return the amplitude of the n maximum frequency of periodgram """

        param_name = "%s%d" % (PeriodicFeature.__FUND_AMP_FEAT_NAME, n)

        return self.__get_amplitude_n(n), param_name

    def get_amplitude_firsts_harm(self, fund_freq):
        """ Return the amplitude for the three first harmonics related to the
            indicated fundamental frequency. If the harmonic does not exists in
            the periodgram, the value of amplitude returned is 0.
        
            fund_freq - Fundamental frequency used to return the values.
        
        """
        
        param_name = []
        harm_amps = []

        for n in range(4):
            harm_amps.append(self.__get_amp_harm_n(fund_freq, n))
            param_name.append("%s%d" % (PeriodicFeature.__AMP_HARM_FEAT_NAME, n))

        return harm_amps, param_name
    
    def freq_y_offset(self):
        """ Calculates the offset of the values in the periodgram, this offset
            is calculated as the minimum value in the periodgram.
            
        """
                        
        offset = self.__pgram[0]
        
        for i in range(len(self.__pgram)):
            if self.__pgram[i] < offset:
                offset = self.__pgram[i]
        
        return offset, PeriodicFeature.__FREQ_OFFSET_FEAT_NAME