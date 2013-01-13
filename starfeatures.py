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

import os
import csv
import fnmatch
import database
import lsproperties
import lombscargle
import periodicfeature
import nonperiodicfeature

class StarsFeatures(object):
    
    def __init__(self, star_classes_):
        """ Initializes variables. """        
        
        self.__star_classes = star_classes_
        
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
        
    def calculate_features(self, filename):
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
            # Adds a new filter for the set of stars.
            self.__star_classes.add_filter(a_filter)
            
        # Retrieve the information of filters created.
        filters = self.__star_classes.filters
        
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
                    self.__star_classes.add_feature(filter_index, star_features_in_current_filter)
                except TypeError:
                    print "Error reading from DB star with identifier %d for filter %s" % (star_id, pfilter)
                    
                    self.__star_classes.disable_star(star_id)
                    
                    # Save fake feature for this star. Necessary to avoid an 
                    # error accessing with a sequential index to a non 
                    # existing feature. This feature wouldn't be accessed as 
                    # this has been disabled.
                    self.__star_classes.add_feature(filter_index, []) 
        
    def get_file_name(self, filter_name, filename):
        """ Returns the name of the csv file constructed from the file name 
            received and the name of the filter whose features are to be
            saved in this file.
            
        """
 
        position = filename.index('.')
        
        return filename[0:position] + '_' + filter_name + '.csv'

    def write_metaheader(self, csv_file, features):
        """ Write to file a header that contains information about the type of each column. """
        
        features_row = features[0]
        
        metaheader = ['META', 'CLASS']
        
        metaheader.extend(['PAR'] * len(features_row))
        
        csv_file.writerow(metaheader)
        
    def write_header(self, csv_file, features):
        """ Write to file the header with the name of the columns. """
        
        features_row = features[0]
        
        header = ['ID', 'CLASS']
        
        header.extend(['PAR'] * len(features_row))
        
        csv_file.writerow(header)        
        
    def write_rows(self, csv_file, features):
        """ Write to file the features of the stars. """
        
        # For the features of each star.
        for i in range(len(features)):
            
            # If the star is enabled (data for this star is ok).
            if self.__star_classes.is_enabled(i):
            
                # Creates the row to write using the information and features of
                # current star.
                row = [self.__star_classes.star_identifier(i)] + \
                    [self.__star_classes.class_name(i)] + \
                    features[i]
                    
                # Writes the row to disk.
                csv_file.writerow(row)
                    
    def write_features(self, filename):
        """ Write to file the features calculated. """
        
        # For each filter writes its features to a different file.
        for i in range(len(self.__star_classes.filters)):
            current_filename = self.get_file_name(self.__star_classes.filter_name(i), filename)
            
            features = self.__star_classes.get_filter_features(i)
        
            with open(current_filename, 'wb') as csvfile:
                
                print "Writing features to file: " + current_filename
                
                csv_file = csv.writer(csvfile, delimiter=',', quotechar='"')   
                     
                self.write_metaheader(csv_file, features)
                self.write_header(csv_file, features)
                self.write_rows(csv_file, features)       
                
    def get_filters_names_from_filename(self, filename):
        """ Extracts the filter name from a filename that should corresponds
            to a features files that incorporates the filter name using the
            format: name_filter.csv
            The filter name is intended to be between the last '_' and last '.'.
            
        """
        
        filters_names = []
        
        dot_rpar = filename.rpartition('.')
        
        if ( len(dot_rpar[0]) > 0 and len(dot_rpar[1]) > 0):
            final_pos = len(dot_rpar[0]) + len(dot_rpar[1]) - 1
            filename_no_ext = filename[0:final_pos]
        
            for afile in os.listdir('.'):
                if fnmatch.fnmatch(afile, filename_no_ext + '*.csv'):
                    
                    print "Found features file: " + afile                
                    
                    underscore_rpar = afile.rpartition('_')                
                    dot_rpar = afile.rpartition('.')
                    
                    # If the characters that mark off the filter name are found.
                    if ( len(underscore_rpar[0]) > 0 and \
                         len(underscore_rpar[1]) > 0 and \
                         len(dot_rpar[0]) > 0 and \
                         len(dot_rpar[1]) > 0 ):
                    
                        filtername = afile[len(underscore_rpar[0]) + \
                                           len(underscore_rpar[1]) : \
                                           len(dot_rpar[0]) + \
                                           len(dot_rpar[1]) - 1]
                            
                        filters_names.append(filtername)
                              
        return filters_names      
        
    def read_features(self, filename):
        """ Read the features from a file. """
        
        features_read = False 
        
        filters_names = self.get_filters_names_from_filename(filename)
        
        print "Filter names: %s" % filters_names
                                
        return features_read
            
    def get_features(self, classifarg):
        """ Returns the features of the stars.
            If a file containing the features is given the features are read
            from this file. Otherwise the features are calculated from the
            light curves stores in the LEMON database.
            
        """
        
        # If a file of features has been given.
        if classifarg.features_file_is_given:
            # Try to read the features from a file.
            if self.read_features(classifarg.features_file) == False:
                # If the features could not be read from a file, 
                # calculate and write them to the features file given.
                self.calculate_features(classifarg.db_file)
                self.write_features(classifarg.features_file)       
        else:
            # Calculate the features.
            self.calculate_features(classifarg.db_file)
        