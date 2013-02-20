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
This module reads and writes the classification model to a file.
"""

import pickle
import logging
import os
import fnmatch
import csv
import sys

class ClassifModel(object):
    """ Encapsulates the serialization of an object to a file.
        The object corresponds to a classification model.
    
    """
    
    def get_filters_names_from_filename(self, filename):
        """ Extracts the filter name from a filename that should corresponds
            to a model file that incorporates the filter name using the
            format: name_filter.ext
            The filter name is intended to be between the last '_' and last '.'.
            
            filename - File name to process.
            
        """
        
        files_names = []
        filters_names = []
        
        # Get the position of the last dot.
        dot_rpar = filename.rpartition('.')
        
        if ( len(dot_rpar[0]) > 0 and len(dot_rpar[1]) > 0):
            final_pos = len(dot_rpar[0]) + len(dot_rpar[1]) - 1
            filename_no_ext = filename[0:final_pos]
        
            for afile in os.listdir('.'):
                if fnmatch.fnmatch(afile, filename_no_ext + '*.' + dot_rpar[2]):
                    
                    files_names.append(afile)
                    
                    logging.info("Found model file: " + afile)                
                    
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
                        
        logging.info('Found the following model files for filters %s' % files_names)
                              
        return files_names, filters_names
    
    @staticmethod
    def read_model_file(model_file_name):
        """ Read from the file indicated the model as a serialized object.
        
            model_file_name - Name of the file that contains the model to read.
        
        """
                
        clf = None
               
        try:
            pkl_file = open(model_file_name, 'rb')
            
            up = pickle.Unpickler(pkl_file)
            clf = up.load()
            
            pkl_file.close()
        
        except IOError:
            logging.warning("Model file '%s' does not exits" % model_file_name)
        
        except pickle.PickleError:      
            logging.error("Error reading model from file %s" % model_file_name)
            
        return clf                      
    
    def read_model(self, filename):
        """ Read the files for all the models as serialized objects.
            Search for files with a name that matches the file name
            received plus a suffix added to the end of the file name,
            excluding the extension.
            
            filename - Pattern for the files names that contains the models.
        
        """
        
        is_error = False
        
        clf_models = []
        
        logging.info('Reading classification model.')
        
        # Get the actual name of files. These name must follow a pattern that uses
        # the file name received and must include a suffix for the name of the filter.
        files_names, filters_names = self.get_filters_names_from_filename(filename)     
        
        for current_file, current_filter in zip(files_names, filters_names):
            
            logging.info('Reading model for filter %s from file %s.' % \
                         (current_filter, current_file))
            
            model = self.read_model_file(current_file)
            
            if model != None:
                clf_models.append(model)
            else:
                is_error = True
                break
            
        # If there was any error reading the model from file, remove the
        # value of clf_models.
        if is_error:
            clf_models = None
        else:
            logging.info('Classification model(s) read from file(s) is done.')
        
        return clf_models, filters_names
    
    def get_output_file_name(self, filename, filter_name):
        """ Returns the name of the file composed from the file name 
            received and the name of the filter.
            
            filename - Base name to use to compose the file name (name + extension).
            filter_name - Filter name to add to the file name.
            
        """
 
        # Find the position of the dot, where the extension file is supposed to begin.
        position = filename.index('.')
        
        # Return the final file name, composed by the base file name, underscore,
        # the filter name and the extension
        return filename[0:position] + '_' + \
                filter_name + \
                filename[position:len(filename)]     
    
    def save_model(self, clf, filename, filter_name):
        """ Write to a file the classifier model.
        
            clf - Classifier to write.
            filename - Name of the file to use.
            filter_name - Name of the filter for this classifier that will be added to
                the file name as suffix.
        
        """
        
        # The actual file name is composed from the file name
        # and the filter name.
        actual_filename = self.get_output_file_name(filename, filter_name)
        
        logging.info('Saving model to file ' + actual_filename)
        
        try:
            pkl_file = open(actual_filename, 'wb')
            
            # Write classifier object to file.           
            p = pickle.Pickler(pkl_file, protocol = pickle.HIGHEST_PROTOCOL)
            p.dump(clf)
            
            pkl_file.close()
            
            logging.info('File containing model saved')      
        except pickle.PickleError:
            logging.error("Error writing model to file %s" % filename)
            
class StarClassNames(object):
    """ Encapsulates the writing and reading in a file of the list of
        variable stars classes. This list is used for interpreting the
        results of classification, as the result is given as numbers.
        These number corresponds to the ordering of classes in this list
        of variable stars classes.
        
    """
    
    def __init__(self, stars_classes_names_ = None):
        """ Initialization of object variables.
        
            stars_classes_names_ - the list of classes to write to file.
                If no list is provided, the list must be read from a file.
        
        """
        
        
        self.__file_name = "stars_classes.csv"
        self.__stars_classes_names = stars_classes_names_      
        
    def write(self):
        """ Write the stars classes names from a file. """
        
        logging.info("Writing stars classes names from file '%s'." \
                     % self.__file_name)        

        if self.__stars_classes_names != None:
            # Write csv file.
            with open(self.__file_name, 'wb') as csvfile:
                
                logging.info("Writing features to file: " + self.__file_name)
                
                csv_file = csv.writer(csvfile, delimiter=',', quotechar='"')
                
                # Write all the stars classes names to file.
                for cl in self.__stars_classes_names:
                    csv_file.writerow([cl])
        else:
            logging.warning("No stars classes names found, the file has not been written.")
                            
    def read(self):
        """ Read the stars classes names from a file. """
      
        logging.info("Reading stars classes names from file '%s'." \
                     % self.__file_name)
        
        self.__stars_classes_names = []
        
        # Read csv file.
        with open(self.__file_name, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            try:
                for row in reader:
                    self.__stars_classes_names.append(row[0])
            except csv.Error as p:
                logging.error('Error reading file %s, line %d: %s' % \
                              (self.__file_name, reader.line_num, p)) 
              
                sys.exit('Error reading file %s, line %d: %s' % \
                         (self.__file_name, reader.line_num, p))        
                
        logging.info("Stars classes names read are: %s" % self.__stars_classes_names)
        
    def class_name(self, index):
        """ Returns the class name from the list of classes whose position
            in the list matches the index received. """
                
        return self.__stars_classes_names[index]