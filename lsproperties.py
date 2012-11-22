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
This module encapsulates the variables used to calculate the period of a curve
and the parameters related to the period that are used to classify a star.

"""

import numpy as np

class LSProperties(object):
    """ This class is used as a container for the parameters used to calculate
        the periodgram of a light curve and the proper periodgram.

"""

    def __init__(self, first_freq_ = 1, max_freq_to_seek_ = 10000, 
                 freq_to_calculate_ = 100000, number_of_freq_ = 3):
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
        self.pgram = []
        self.index_max_values = []          
        
    def __str__(self):
        """ The 'informal' string representation """
        return "LSProperties: %s(First freq = %.2f freq to calculate = %d)" % \
               (self.__class__.__name__, self.first_freq, self.freq_to_calculate)

    def __len__(self):
        """ Return the number of frequencies in the periodgram """
        return len(self.pgram)   