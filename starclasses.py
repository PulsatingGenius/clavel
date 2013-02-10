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
This module read from a file the classes corresponding to a list of stars 
to be used for training and/or evaluation purposes.

"""

import csv
import sys
import csvdata
import logging
import database

class StarClasses(object):
    
    def get_unique_classes(self):
        """ Takes the complete set of names for all the stars and
            return a list that contains each class name just once.
            
        """
        
        # For all the classes names.
        for c in self.__stars_classes_names:
            try:
                # Check if the class name is already in the set of
                # unique class names.
                self.__unique_classes_names.index(c)
            except ValueError:
                # It is not in the set, so add to it.
                self.__unique_classes_names.append(c)    
    
    def retrieve_stars_classes_from_file(self, csv_filename):
        """ Read from a CSV file the list of star whose variability type is known.
            These stars are used to train and/or evaluate the classifier.
            
        """        
        
        logging.info('Reading data to identify the stars from file %s.' % csv_filename)
        
        # Read csv file with stars identifiers and their classes.
        with open(csv_filename, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            try:
                # For each row in csv file.
                for row in reader:
                    # Add the first element of the row as the star id.
                    self.__stars_identifiers.append(int(row[0]))
                    # Add the second element of the row as the star type.
                    self.__stars_classes_names.append(row[1])
                    # By default, the use of the star is enabled.
                    self.__enabled.append(True)
                    # By default, the training is not selected for training.
                    self.__for_training.append(False)
                    # By default, the training is not selected for evaluation.
                    self.__for_evaluation.append(False)                    
            except csv.Error as p:
                sys.exit('file %s, line %d: %s' % (csv_filename, reader.line_num, p))  
                
        self.get_unique_classes()       
        
        logging.info('%d stars identifiers has been read from file.' % \
                     len(self.__stars_identifiers))    
        
    def retrieve_stars_classes_from_database(self, database_file_name): 
        """ Retrieve the identification of stars from a LEMON database. """   
        
        logging.info('Reading identifiers of stars from a LEMON database: %s' % \
                     database_file_name)
        
        # Create database in LEMON format.
        db = database.LEMONdB(database_file_name)   
        
        self.__stars_identifiers = db.star_ids   
        
        logging.info('%d stars identifiers read from LEMON database' % \
                      len(self.__stars_identifiers))
        
    def get_star_info_cols(self, header_row):
        """ Examines the metadata and header rows to locate the columns that
            contains the information related to identification and class 
            of the stars. 
            
        """

        star_id_col = -1
        class_name_col = -1
        
        for i in range(len(header_row)):
            if header_row[i] == csvdata.CsvUtil.ID:
                star_id_col = i
            elif header_row[i] == csvdata.CsvUtil.CLASS:
                class_name_col = i
                    
        if star_id_col < 0 or class_name_col < 0:
            raise ValueError("Columns for identification '%d' and class '%d' of the star not found in features file" % \
                             (star_id_col, class_name_col))        
        
        return star_id_col, class_name_col
        
    def retrieve_stars_classes_from_features_file(self, features_file_name):
        """ Retrieve the identification of stars from a features file 
            generated previously. 
            
        """
        
        logging.info("Reading data to identify the stars from features file with suffix '%s'." % features_file_name)
        
        n_rows = 0
        header_row = []
        class_name_col = 0
        star_id_col = 0
             
        # Search for files
        features_file = csvdata.FeaturesFile()    
        
        files_names, filters_names = \
            features_file.get_filters_names_from_filename(features_file_name)                        
            
        if len(files_names) > 0:
            logging.info("Reading star information from first features file found: '%s', filter '%s'." % \
                         (files_names[0], filters_names[0]))
                
            # Read csv file with stars identifiers and their classes.
            with open(files_names[0], 'rb') as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='"')
                try:
                    # For each row in csv file.
                    for row in reader:
                        if n_rows == 0:
                            header_row = row
                            
                            # Get the number of the columns that contains the information
                            # of the star identification and star class.
                            star_id_col, class_name_col = self.get_star_info_cols(header_row)                        
                        else:                    
                            # Add the first element of the row as the star id.
                            self.__stars_identifiers.append(row[star_id_col])
                            # Add the second element of the row as the star type.
                            self.__stars_classes_names.append(row[class_name_col])
                            # By default, the use of the star is enabled.
                            self.__enabled.append(True)
                            # By default, the training is not selected for training.
                            self.__for_training.append(False)
                            # By default, the training is not selected for evaluation.
                            self.__for_evaluation.append(False) 
                            
                        n_rows += 1                   
                except csv.Error as p:
                    sys.exit('file %s, line %d: %s' % (features_file_name, reader.line_num, p))  
                except ValueError as e:
                    sys.exit('file %s, line %d: %s' % (features_file_name, reader.line_num, e)) 
                    
            self.get_unique_classes()       
            
            logging.info('%d stars identifiers has been read from file.' % \
                         len(self.__stars_identifiers))             
    
    def __init__(self):
        """ Initializes variables and from the file indicated
            read star identifiers and their class names. 
            
        """
        
        # Identifiers of the stars.
        self.__stars_identifiers = []
        # Class name of the stars.
        self.__stars_classes_names = []
        # Set that will contain the names of all classes just once.
        self.__unique_classes_names = []           
        # If there is any problem reading the data of a star, 
        # it could be disabled and the star shouldn't be used.
        self.__enabled = []
        # Filters available in source data.        
        self.__filters_names = []        
        # Container for all the features of the stars in all the filters_names available.
        self.__features_all_filters = []
        # Indicates if the star is used for training.
        self.__for_training = []
        # Indicates if the star is used for evaluation.
        self.__for_evaluation = []             
    
    @property
    def classes(self):
        return self.__stars_classes_names   
    
    @property
    def stars_identifiers(self):
        return self.__stars_identifiers

    def star_identifier(self, index):
        return self.__stars_identifiers[index]
    
    def class_name(self, index):
        return self.__stars_classes_names[index]

    def is_enabled(self, index):
        return self.__enabled[index]
    
    def disable(self, index):
        self.__enabled[index] = False
    
    @property
    def number_of_stars(self):
        return len(self.__stars_identifiers)    
    
    @property
    def unique_classes_names(self):
        return self.__unique_classes_names
    
    def filter_name(self, nfilter):
        return str(self.__filters_names[nfilter])
    
    def add_filter_name(self, a_filter):
        """ Saves the filter and adds a new list 
            to save the features of the stars in this filter.  
            
        """
            
        self.__filters_names.append(a_filter)
        self.__features_all_filters.append([])
        
    @property
    def filters_names(self):        
        return self.__filters_names
    
    @property
    def number_of_filters(self):
        return len(self.__features_all_filters)    
        
    def get_class_id(self, class_name):
        """ For a class name return an numerical identifier.
            This numerical identifier corresponds to the position
            that the class name has in the list of unique class name.
         
        """
        return self.__unique_classes_names.index(class_name)        
    
    def get_class_number_from_id(self, iden):
        """ For a star identifier return the class number. """
        
        try:
            # Search the index for the identifier.
            index = self.__stars_identifiers[iden]
            # Get the name of its class.
            class_name = self.__stars_classes_names[index]
            # Search the index for this class name.
            class_number = self.get_class_id(class_name)
        except ValueError:
            # This should not occur.
            logging.error("iden %d index %d class_name %s" % (iden, index, class_name))
            raise   
            
        return class_number 

    def get_class_numbers_from_ids(self, stars_ids):
        """ For the stars identifiers received returns the class's number. """
         
        class_numbers = [] 
         
        for i in stars_ids:
            class_numbers.append(self.get_class_number_from_id(i))
                
        return class_numbers
    
    def get_instance_id(self, index):
        """ For a given index return the value of that instance. """
        
        return self.__stars_identifiers[index]    
    
    def get_class_number_from_index(self, index):
        """ For a given index return the value of that instance. """
        
        return self.__stars_classes_names[index]
    
    def disable_star(self, star_id):
        """ Disable the star whose identifier is indicated. """
        
        logging.warning("Disabling star %d ..." % star_id)
        try:
            # Get the index for the star identifier.
            index = self.__stars_identifiers.index(star_id)
            
            self.disable(index)
            
            logging.warning("... at index %d" % index)
        except ValueError:
            pass
        
    def get_filter_features(self, nfilter):
        return self.__features_all_filters[nfilter]        

    def get_features_by_filter_name(self, afilter):
        
        features = []
        
        logging.info('Searching features for filter %s' % afilter)
        
        for i in range(len(self.__filters_names)):
            if self.__filters_names[i] == afilter:
                features = self.__features_all_filters[i]
                logging.info("Found %d features for filter %s" % \
                             (len(features), afilter))
                break
            
        if len(features) == 0:
            logging.error('Not found features for filter %s' % afilter)
            
        return features 
        
    def add_feature(self, filter_index, star_features):
        """ Adds the features of only a star in the filter indicated. """
         
        self.__features_all_filters[filter_index].append(star_features)         
        
    def feature(self, filter_index, feature_index):
        """ Returns the features of the star indicated by
            the index of the filter and the index of the star.
                        
        """
        features = self.__features_all_filters[filter_index]
        
        return features[feature_index]
    
    def set_star_id_and_classes(self, star_ids, star_classes):
        """ Sets the star identifiers and classes with values received. """
        
        self.__stars_identifiers = star_ids

        self.__stars_classes_names = star_classes
        
        # In this case all the stars are enabled.
        self.__enabled = [True] * len(star_classes)

        # Get the list that contains the names of the classes just once.        
        self.get_unique_classes()
        