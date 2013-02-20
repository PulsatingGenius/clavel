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
magnitude measurements. These features are intended to be used as entries 
to a system that classifies automatically stars into variable classes 
according to their periodic light variations.

"""

import math
import numpy as np
import scipy.stats

class NonPeriodicFeature(object):
    """ Encapsulates the calculation of periodic features of a light curve.

        This class is used as a container for the calculation of non periodic 
        features from a light curve. It calculates features based in statistical 
        calculations from curve values.

    """

    # Names of the features calculated.
    __AMP_DIF_FEAT_NAME = "Amp_diff"
    __BEY1ST_FEAT_NAME = "Beyond1st"
    __LINEAR_TREND_FEAT_NAME = "Linear_Tren"
    __MAX_SLOPE_FEAT_NAME = "Max_Slope"
    __MED_ABS_DEV_FEAT_NAME = "Median_Abs_Dev"
    __MED_BUF_RAN_PER_FEAT_NAME = "Median_Buff_Range_Percent"
    __PAIR_SLOPE_TREND_FEAT_NAME = "Pair_Slope_Trend"
    __PER_AMP_FEAT_NAME = "Percent_Amplitude"
    __PER_DIF_FLUX_PER_FEAT_NAME = "Percent_Diff_flux_Percentile"
    __SKEW_FEAT_NAME = "Skew"
    __KURTOSIS_FEAT_NAME = "Kurtosis"
    __STD_FEAT_NAME = "Stand_Dev"
    __FLUX_PERC_RAT_MID20_FEAT_NAME = "Flux_Percentile_Ratio_Mid20"
    __FLUX_PERC_RAT_MID35_FEAT_NAME = "Flux_Percentile_Ratio_Mid35"
    __FLUX_PERC_RAT_MID50_FEAT_NAME = "Flux_Percentile_Ratio_Mid50"
    __FLUX_PERC_RAT_MID65_FEAT_NAME = "Flux_Percentile_Ratio_Mid65"
    __FLUX_PERC_RAT_MID80_FEAT_NAME = "Flux_Percentile_Ratio_Mid80"      

    def __init__(self, nmags_, ntimes_):
        """ Instantiation method for the NonPeriodicFeature class.

            Arguments:
            nmags - magnitudes of the light curve.
            ntimes - time tics for the light curve, beginning at time 0.
            
        """

        self.nmags = nmags_
        self.ntimes = ntimes_
        
    def __str__(self):
        """ The 'informal' string representation """
        
        return "NonPeriodicFeature: %s(numero de frec = %s)" % \
               (self.__class__.__name__, len(self.pgram))

    def __len__(self):
        """ Return the number of frequencies in the periodgram. """
        
        return len(self.pgram)   
    
    def amplitude_dif(self):
        """ Return half the difference between the maximum and the minimum
            magnitude.
            
        """

        # Get the maximum and minimum values of the magnitude.
        max_mag = self.nmags[np.argmax(self.nmags)]
        min_mag = self.nmags[np.argmin(self.nmags)]

        return (max_mag - min_mag) / 2, NonPeriodicFeature.__AMP_DIF_FEAT_NAME

    def beyond1st(self):
        """ Percentage of points beyond one standard deviation from the 
            weighted mean.
            
        """

        number_of_points = 0
        percentage = 0

        # Calculate weighted average and standard deviation of the flux.
        avg = np.average(self.nmags)
        std = np.std(self.nmags)

        # Count the number of measures beyond average plus-minus std.
        for n in range(len(self.nmags)):
            if (self.nmags[n] < avg - std) or (self.nmags[n] > avg + std):
                number_of_points += 1

        if ( number_of_points > 0 ):
            percentage = number_of_points * 100.0 / len(self.nmags)

        return percentage, NonPeriodicFeature.__BEY1ST_FEAT_NAME

    def linear_trend(self):
        """ Slope of a linear fit to the light curve flux. """

        slope, intercept, r_value, p_value, std_err = \
            scipy.stats.linregress(self.ntimes, self.nmags)

        return slope, NonPeriodicFeature.__LINEAR_TREND_FEAT_NAME

    def __interval_avg_and_std(self):
        """ Calculate average and standard deviation of time intervals. """
        
        intervals = []

        # As iterations use current index plus 1, range must be reduced in 1.
        for n in range(len(self.ntimes) - 1):
            intervals.append(self.ntimes[n + 1] - self.ntimes[n])

        interval_avg = np.average(intervals)
        interval_std = np.std(intervals)

        return interval_avg, interval_std

    def __calculate_slope(self, x1, x2, y1, y2):
        """ Calculate the slope for two points. """

        return (y2 - y1) / (x2 - x1)

    def max_slope(self):
        """ Maximum absolute of the flux slope between two consecutive 
        observations. As the curve is unevenly sampled the slope must be
        calculated avoiding gaps in time, as this gaps do not relate to true
        variations between values.
        
        """

        max_slp = 0

        # Calculate average and standard deviation of time intervals.
        interval_avg, interval_std = self.__interval_avg_and_std()

        # The maximum interval considered is the weighted average plus
        # standard deviation.
        interval_max_size = interval_avg + interval_std

        # Search the max slope.
        for n in range(len(self.ntimes) - 1):

            # If the interval must be taken in account.
            if self.ntimes[n + 1] - self.ntimes[n] < interval_max_size:

                # Calculate slope
                current_slope = self.__calculate_slope(
                    self.ntimes[n], self.ntimes[n + 1],
                    self.nmags[n], self.nmags[n + 1])

                if current_slope > max_slp:
                    max_slp = current_slope

        return max_slp, NonPeriodicFeature.__MAX_SLOPE_FEAT_NAME

    def median_absolute_deviation(self):
        """ Median discrepancy of the fluxes from the median flux. """

        num_elements = len(self.nmags)
        med_calc = []

        median = np.median(self.nmags)

        for n in range(num_elements):
            med_calc.append(math.fabs(self.nmags[n] - median))
                       
        return np.median(med_calc), NonPeriodicFeature.__MED_ABS_DEV_FEAT_NAME

    def median_buffer_range_percentage(self):
        """ Percentage of fluxes within 10% of the amplitude from the median. """

        # Number of values out of the range of 20% from the median.
        number_values = 0

        # Get the median.
        median = np.median(self.nmags)

        # Range with the maximum and minimum value.
        upper_value = median + 0.1 * median
        lower_value = median - 0.1 * median

        # Search for values out of range in the periodgram.
        for n in range(len(self.nmags) - 1):
            current_val = self.nmags[n]

            # If current value is out of range, increment the count.
            if current_val < lower_value or current_val > upper_value:
                number_values += 1

        # Calculate the percentage of value out of range.
        return number_values * 100.0 / len(self.nmags), NonPeriodicFeature.__MED_BUF_RAN_PER_FEAT_NAME

    def pair_slope_trend(self, number = 30):
        """ Percentage of all pairs of consecutive flux measurements that have 
            positive slope.
            
        """
        
        # If the number of values to use is bigger than number of values,
        # use the number of values.
        if number > len(self.ntimes):
            number = len(self.ntimes)

        num_positive_slopes = 0

        # Calculate average and standard deviation of time intervals.
        interval_avg, interval_std = self.__interval_avg_and_std()

        # The maximum interval considered is the weighted average plus
        # standard deviation.
        interval_max_size = interval_avg + interval_std

        # Search the number of consecutive intervals with positive slope.
        # The search uses two elements of the array, current element and 2, 
        # so the range to iterate must be reduced in 1 element.
        for n in range(len(self.ntimes) - number, len(self.ntimes) - 1):

            # If the interval must be taken in account.
            if self.ntimes[n + 1] - self.ntimes[n] < interval_max_size:

                # Calculate slope
                current_slope = self.__calculate_slope(
                    self.ntimes[n], self.ntimes[n + 1],
                    self.nmags[n], self.nmags[n + 1])

                if current_slope > 0:
                    num_positive_slopes += 1

        # Calculate the percentage using the number of positive slopes and
        # the total number of intervals, this is the number of samples minus 1.
        return num_positive_slopes * 100.0 / (number - 1), NonPeriodicFeature.__PAIR_SLOPE_TREND_FEAT_NAME
    
    def percent_amplitude(self):
        """ Largest percentage difference between either the max or min 
            magnitude and the median.
            
        """
            
        # Get the median.
        median = np.median(self.nmags)    
        
        # Get max and min values of the curve.
        max_mag = self.nmags[np.argmax(self.nmags)]
        min_mag = self.nmags[np.argmin(self.nmags)]
        
        # Calculate the difference between maximum and minimum values
        # and the median.
        dif_max_med = max_mag - median
        dif_min_med = median - min_mag
               
        max_dif = dif_max_med if dif_max_med > dif_min_med else dif_min_med
        
        return max_dif * 100.0 / (max_mag - min_mag), NonPeriodicFeature.__PER_AMP_FEAT_NAME

    def percent_difference_flux_percentile(self):
        """ Difference between the 5th & 95th flux percentiles, 
            converted to magnitude.
            
        """
            
        percentile_05 = scipy.stats.scoreatpercentile(self.nmags, 5)
        percentile_95 = scipy.stats.scoreatpercentile(self.nmags, 95)
        
        return np.median(self.nmags)  * 100 / (percentile_95 - percentile_05), \
            NonPeriodicFeature.__PER_DIF_FLUX_PER_FEAT_NAME

    def skew(self):
        """ Skew of the flux. """
        
        return scipy.stats.skew(self.nmags), NonPeriodicFeature.__SKEW_FEAT_NAME
    
    def kurtosis(self):
        """ Kurtosis of the fluxes. """
        
        return scipy.stats.kurtosis(self.nmags), NonPeriodicFeature.__KURTOSIS_FEAT_NAME
    
    def std(self):
        """ Standard deviation of the fluxes. """
        
        return np.std(self.nmags), NonPeriodicFeature.__STD_FEAT_NAME
    
    def __flux_percentile_ratio_midXX(self, lower_perc, upper_perc):
        """ The difference between upper_perc and lower_perc percentiles flux 
            values divided by the difference between 5% and 95% flux values.
            
        """
            
        return (scipy.stats.scoreatpercentile(self.nmags, upper_perc) - \
                    scipy.stats.scoreatpercentile(self.nmags, lower_perc)) / \
                    (scipy.stats.scoreatpercentile(self.nmags, 95) - \
                    scipy.stats.scoreatpercentile(self.nmags, 5))    
    
    def flux_percentile_ratio_mid20(self):
        """ The difference between 60% and 40% flux values divided by 
            the difference between 5% and 95% flux values.
            
        """
            
        return self.__flux_percentile_ratio_midXX(40, 60), \
            NonPeriodicFeature.__FLUX_PERC_RAT_MID20_FEAT_NAME
                    
    def flux_percentile_ratio_mid35(self):
        """ The difference between 60% and 40% flux values divided by 
            the difference between 5% and 95% flux values. """
            
        return self.__flux_percentile_ratio_midXX(32.5, 67.5), \
            NonPeriodicFeature.__FLUX_PERC_RAT_MID35_FEAT_NAME
                    
    def flux_percentile_ratio_mid50(self):
        """ The difference between 60% and 40% flux values divided by 
            the difference between 5% and 95% flux values.
            
        """
            
        return self.__flux_percentile_ratio_midXX(25, 75), \
            NonPeriodicFeature.__FLUX_PERC_RAT_MID50_FEAT_NAME
                    
    def flux_percentile_ratio_mid65(self):
        """ The difference between 60% and 40% flux values divided by 
            the difference between 5% and 95% flux values.
            
        """
            
        return self.__flux_percentile_ratio_midXX(17.5, 82.5), \
            NonPeriodicFeature.__FLUX_PERC_RAT_MID65_FEAT_NAME
                    
    def flux_percentile_ratio_mid80(self):
        """ The difference between 60% and 40% flux values divided by 
            the difference between 5% and 95% flux values.
            
        """
            
        return self.__flux_percentile_ratio_midXX(10, 90), \
            NonPeriodicFeature.__FLUX_PERC_RAT_MID80_FEAT_NAME                  