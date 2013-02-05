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

import logging
import csvdata
import database
import lombscargle
import periodicfeature
import nonperiodicfeature    

class StarsFeatures(object):
    
    def __init__(self, star_classes_):
        """ Initializes variables. """    
        
        # Create objects to store metadata of CSV file and the data of the file.
        self.META = csvdata.MetaData()     
        
        self.__star_classes = star_classes_
        
    @staticmethod
    def save_feature(perfeat, noperfeat):
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
        
    def calculate_features(self, filename):
        """ Calculate features of the stars. Read the light curves from
            database, calculate periodic and no periodic features and store
            all the features in a data structure that is accessed using
            an index corresponding to the order the star has been stored
            in star_classes.
            
        """       
        
        logging.info('Opening LEMON db %s.' % filename)
        
        # Create database in LEMON format.
        db = database.LEMONdB(filename)
        
        # Retrieve the information of filters created.
        filters = db.pfilters                 
        
        # For each filter add an empty list to contain the features
        # of all the stars in that filter.
        for a_filter in filters:           
            # Adds a new filter for the set of stars.
            self.__star_classes.add_filter_name(str(a_filter))
        
        logging.info('Ready to read and calculate features using %d light curves from a LEMON db for filters %s.' % \
                     (self.__star_classes.number_of_stars, self.__star_classes.filters_names) )    
        
        # Properties for the Lomb Scargle method.
        lsprop = lombscargle.LSProperties()  
        ls = lombscargle.LombScargle(lsprop)
        
        # Percentage of calculation completed.
        perc_completed = 0
        
        # For all the stars in the database.
        for star_index in range(self.__star_classes.number_of_stars):           
            # For all the filters of current star.
            for filter_index in range(len(filters)):
                # Get the filter.
                pfilter = filters[filter_index]

                # Get the curve of the current star in the current filter.
                star_id = self.__star_classes.get_instance_id(star_index)

                curve = db.get_light_curve(star_id, pfilter)
                # Get the object that will calculate the periodgram of the curve
                # (not normalized).
                try:
                    # Calculate the periodgram.
                    pgram, nmags, ntimes = ls.calculate_periodgram(pfilter, curve)

                    # Calculate periodic features of stars.
                    perfeat = periodicfeature.PeriodicFeature(pgram, lsprop)

                    # Calculate no periodic features of stars.
                    noperfeat = nonperiodicfeature.NonPeriodicFeature(nmags, ntimes)

                    # Store all the features of this star in a list.
                    star_features_in_current_filter = StarsFeatures.save_feature(perfeat, noperfeat)
      
                    # Add the features calculated in the appropriate filter
                    # data structure.
                    self.__star_classes.add_feature(filter_index, star_features_in_current_filter)
                except TypeError:
                    logging.error("Error reading from DB star with identifier %d for filter %s" % (star_id, pfilter))
                    
                    self.__star_classes.disable_star(star_id)
                    
                    # Save fake feature for this star. Necessary to avoid an 
                    # error accessing with a sequential index to a non 
                    # existing feature. This feature wouldn't be accessed as 
                    # this has been disabled.
                    self.__star_classes.add_feature(filter_index, [])
                    
            # Only to print a progress message of the calculation each 10% of advance.
            perc = star_index * 100 / self.__star_classes.number_of_stars 
            perc_module = perc % 10                    
            if perc >= 10 and perc_module == 0 and perc != perc_completed :
                logging.info('Calculating features for stars:%3.f%% done.', perc)
                perc_completed = perc
                     
        logging.info('Finished the calculation of features from LEMON db.')
                    
    def write_features(self, filename):
        """ Write to file the features calculated. """
        
        logging.info('Writing features to file %s.' % filename)
        
        features_file = csvdata.FeaturesFile()    
        
        features_file.write_features(filename, self.__star_classes)   
        
    def read_features(self, filename):
        """ Read the features from one or more files with the file name given
            and a suffix indicating the filter name.
            
        """
        
        logging.info('Reading features from file %s.' % filename)
        
        features_file = csvdata.FeaturesFile() 
     
        return features_file.read_features(filename, \
                                           self.META, self.__star_classes)
            
    def retrieve_features(self, classifarg):
        """ Returns the features of the stars.
            If a file containing the features is given, the features are read
            from this file. Otherwise the features are calculated from the
            light curves stores in the LEMON database.
            
        """
        logging.info('Getting the features of stars.')
        
        # If a database file has been given.
        if classifarg.database_file_provided:
            logging.info('Calculating star features from the light curves of LEMON database %s.' %
                         classifarg.database_file_name)
            
            # Calculate the features from the light curves of a LEMON db.
            self.calculate_features(classifarg.database_file_name)        
        
            # If a features file has been given.
            if classifarg.features_file_provided:
                # Write the features to file.
                self.write_features(classifarg.features_file_name)
        
        elif classifarg.features_file_provided:            
            # Try to read the features from a file.
            if self.read_features(classifarg.features_file_name) == False:
                
                logging.info("Star features couldn't be read from file")
        else:
            logging.info('No source has been specified to retrieve the star data.')