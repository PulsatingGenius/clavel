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

class ClassifModel(object):
    
    def get_filters_names_from_filename(self, filename):
        """ Extracts the filter name from a filename that should corresponds
            to a model file that incorporates the filter name using the
            format: name_filter.ext
            The filter name is intended to be between the last '_' and last '.'.
            
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
    
    def read_model(self, filename):
        """ Read from the file indicated the model as a serialized object. """
        
        is_error = False
        
        clf = []
        
        logging.info('Reading classification model.')
        
        # Get the actual name of files. These name must follow a pattern that uses
        # the file name received and must include a suffix for the name of the filter.
        files_names, filters_names = self.get_filters_names_from_filename(filename)     
        
        for current_file, current_filter in zip(files_names, filters_names):
            
            logging.info('Reading model for filter %s from file %s.' % \
                         (current_filter, current_file))
                         
            try:
                pkl_file = open(current_file, 'rb')
                
                # Load classifier object from file.
                #clf.append(pickle.load(pkl_file))
                
                up = pickle.Unpickler(pkl_file)
                clf.append(up.load())
                
                pkl_file.close()
            
            except IOError:
                logging.warning("Model file '%s' does not exits" % filename)
                is_error = True
                break
            
            except pickle.PickleError:
                logging.error("Error reading model from file %s" % filename)
                is_error = True
                break
            
        # If there was any error reading the model from file, remove the
        # value of clf.
        if is_error:
            clf = None
        else:
            logging.info('Classification model(s) read from file(s) is done.')
        
        return clf, filters_names
    
    def get_output_file_name(self, filename, filter_name):
        """ Returns the name of the file composed from the file name 
            received and the name of the filter.
            
        """
 
        position = filename.index('.')
        
        return filename[0:position] + '_' + \
                filter_name + \
                filename[position:len(filename)]     
    
    def save_model(self, clf, filename, filter_name):
        """ Write to a file the classifier model. """
        
        # The actual file name is composed from the file name
        # and the filter name.
        actual_filename = self.get_output_file_name(filename, filter_name)
        
        logging.info('Saving model to file ' + actual_filename)
        
        try:
            pkl_file = open(actual_filename, 'wb')
            
            # Write classifier object to file.
            #pickle.dump(clf, pkl_file)
            
            p = pickle.Pickler(pkl_file, protocol=pickle.HIGHEST_PROTOCOL)
            p.dump(clf)
            
            pkl_file.close()
            
            logging.info('File containing model saved')      
        except pickle.PickleError:
            logging.error("Error writing model to file %s" % filename)