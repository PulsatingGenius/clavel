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
This module stores the features of a set of stars.

"""

import database
import lsproperties
import lombscargle
import periodicfeature
import nonperiodicfeature

class StarsFeatures(object):
    
    def __init__(self):
        """ Initializes variables. """

        # Container for all the features of the stars in all the filters available.
        self.__features_all_filters = []
        
    @property
    def number_of_filters(self):
        return len(self.__features_all_filters)
        
    def get_filter_features(self, nfilter):
        return self.__features_all_filters[nfilter]
        
    def save_feature(self, perfeat, noperfeat):
        """ Save the star features with all the features. """
            
        feature = []
        
        # Three frequencies are used.
        for n in range(3):
            # Append frequency attribute.
            feature.append(perfeat.get_fund_freq(n))
            # Append amplitude attribute.
            feature.append(perfeat.get_amplitude(n))
            # Append amplitude of three first harmonics.
            feature.extend(perfeat.get_amplitude_firsts_harm(n))
            
        # Append frequencies offset
        feature.append(perfeat.freq_y_offset())
            
        # Add difference of amplitudes        
        feature.append(noperfeat.amplitude_dif())
                        
        # Add percentage of values beyond 1 standard deviation.
        feature.append(noperfeat.beyond1st())
                        
        # Add linear trend.
        feature.append(noperfeat.linear_trend())
        
        # Add maximum slope.
        feature.append(noperfeat.max_slope())
        
        # Add median_absolute_deviation.
        feature.append(noperfeat.median_absolute_deviation())
        
        # Add percentage of values beyond 20% of median.
        feature.append(noperfeat.median_buffer_range_percentage())
        
        # Add percentage o consecutive values with positive slope.
        feature.append(noperfeat.pair_slope_trend())
        
        # Add percentage of biggest difference between maximum and minimum magnitude. 
        feature.append(noperfeat.percent_amplitude())
        
        # Add differences of magnitudes between percentile 5 and 95.
        feature.append(noperfeat.percent_difference_flux_percentile())
        
        # Add skew.
        feature.append(noperfeat.skew())
        
        # Add Kurtosis.
        feature.append(noperfeat.kurtosis())
        
        # Add standard deviation.
        feature.append(noperfeat.std())
        
        # Add flux ratio at percentile 20.
        feature.append(noperfeat.flux_percentile_ratio_mid20())
        
        # Add flux ratio at percentile 35.
        feature.append(noperfeat.flux_percentile_ratio_mid35())
        
        # Add flux ratio at percentile 50.
        feature.append(noperfeat.flux_percentile_ratio_mid50())
        
        # Add flux ratio at percentile 65.
        feature.append(noperfeat.flux_percentile_ratio_mid65())
        
        # Add flux ratio at percentile 80.
        feature.append(noperfeat.flux_percentile_ratio_mid80())    
            
        return feature          
        
    def calculate_features(self, filename, stars_classes):
        """ Calculate features of the stars. Read the light curves from
            database, calculate periodic and no periodic features and store
            all the features in a data structure that is accessed using
            an index corresponding to the order the star has been stored
            in star_classes.
            
        """       
        
        # Create database in LEMON format.
        db = database.LEMONdB(filename)
        
        # Properties for the Lomb Scargle method.
        lsprop = lsproperties.LSProperties()        
        
        # For each filter add an empty list to contain the features
        # of all the stars in that filter.
        for a_filter in db.pfilters:
            self.__features_all_filters.append([])
            
            # Save the name of the filter in order.
            stars_classes.add_filter_name(str(a_filter))
        
        # For all the stars in the database.
        for star_id in stars_classes.ids:           
            # For all the filters of current star.
            for filter_index in range(len(db.pfilters)):
                # Get the filter.
                pfilter = db.pfilters[filter_index]
                # Get the curve of the current star in the current filter.
                curve = db.get_light_curve(star_id, pfilter)
                # Get the object that will calculate the periodgram of the curve
                # (not normalized).
                try:
                    ls = lombscargle.LombScargle(star_id, pfilter, curve, lsprop)
                    # Calculate the periodgram.
                    pgram, nmags, ntimes = ls.calculate_periodgram()
                    # Calculate periodic features of stars.
                    perfeat = periodicfeature.PeriodicFeature(pgram, lsprop)
                    # Calculate no periodic features of stars.
                    noperfeat = nonperiodicfeature.NonPeriodicFeature(nmags, ntimes)
                    
                    # Store all the features of this star in a list.
                    star_features_in_current_filter = self.save_feature(perfeat, noperfeat)
                                    
                    # Add the features calculated in the appropriate filter
                    # data structure.
                    self.__features_all_filters[filter_index].append(star_features_in_current_filter) 
                except TypeError:
                    print "Error reading from DB star with identifier %d for filter %s" % (star_id, pfilter)
                    
                    stars_classes.disable_star(star_id)
                    
                    # Save fake feature for this star. Necessary to avoid an 
                    # error accessing with a sequential index to a non 
                    # existing feature. This feature wouldn't be accessed as 
                    # this has been disabled.
                    self.__features_all_filters[filter_index].append([])                    