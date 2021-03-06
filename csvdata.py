#! /usr/bin/env python

# Copyright (c) 2012 Felipe Gallego. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
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
This module reads and writes features and star information from CSV files.
"""       

import os
import sys
import fnmatch
import csv
import logging

class CsvUtil(object):
    CLASS = 'CLASS'
    PARAM = 'PAR'
    ID = 'ID'
    PREDICTION = 'PREDICTION'
    PRED_PROBA = 'PROBABILITY'         
    FILE_EXT = '.csv'

class ColumnDef(object):
    """ It keeps the information related to a column. """    
    
    def __init__(self, colnumber_, colname_):    
        """ Initiation of ColumnDef objects. Only for variable assignment. 
        
            colnumber_ - Number related to the position of the column.
            colname_ - Name of the column.
        """
        
        self.__colnumber = colnumber_     
        self.__colname = colname_  
        self.__number_of_instances = 0        
        
    @property
    def colnumber(self):
        return self.__colnumber  
    
    @property
    def colname(self):
        return self.__colname       
    
    @colname.setter
    def colname(self, colname_):
        self.__colname = str(colname_)  

    def is_id(self):       
        return self.__colname == CsvUtil.ID
        
    def is_class(self):
        return self.__colname == CsvUtil.CLASS  
        
    def __str__(self):        
        return "Col=%s, Name=%s" % \
            (self.__colnumber, self.__colname)            
    
class MetaData(object):    
    """ It keeps information related to the columns of a table. """
    
    def __init__(self):            
        self.__coldef = []
            
    def process_cols(self, row):
        """ Process the row received as information related to the columns.
        
            row - A row whose elements are processed as column names.
        
        """
           
        n = 0
         
        # For each element in the row adds a new column definition.
        for c in row:    
            self.__coldef.append(ColumnDef(n, c))
            n += 1
            
    def get_col_info(self, n):
        """ Returns the information of the column at position n. 
        
            n - Number of the column whose information is returned.
        
        """        
        
        if n >= len(self.__coldef):
            raise IndexError("There is not a column number %d" % n)
        else:
            return self.__coldef[n]
        
    def get_id_col(self):
        """ Get the number of the column that contains the id of the star. """
        
        n = -1
        i = 0
        
        # Look for a column with the name that corresponds to the name of the
        # id column.
        while (i < len(self.__coldef)) and (n == -1):       
            if self.__coldef[i].is_id():
                n = i 
                
            i += 1
                
        if n == -1:
            raise ValueError("There is not a column with the star identification.")
        else:
            return n          
        
    def get_col_of_class(self):
        """ Get the number of the column that contains the class of the star. """
                
        n = -1
        i = 0
        
        # Look for a column with the name that corresponds to the name of the 
        # class column.        
        while (i < len(self.__coldef)) and (n == -1):
            if self.__coldef[i].is_class():
                n = i 
                
            i += 1
                
        if n == -1:
            raise ValueError("There is not a column with CLASS type.")
        else:
            return n        
        
    def get_range_of_params(self):
        """ Get the range of columns that contains parameters.
            It is assumed that all the columns containing parameters are 
            contiguous, otherwise it is not possible to calculate a range.
        
        """
        
        par_range = []
        
        range_init_found = False
        
        last_column = 0
        
        # Calculate the range looking for the first column that is not
        # the id nor the class, and add the following columns until the
        # end, the id column or the class column is reached. 
        for c in self.__coldef:
            if not c.is_id() and not c.is_class():
                if not range_init_found:
                    range_init_found = True
                    par_range.append(c.colnumber)
                else:
                    last_column = c.colnumber
                
        if range_init_found:
            par_range.append(last_column)
            
        return par_range
            
    def len(self):
        return len(self.__coldef)  
            
    def __str__(self):        
        return "Size=%d" % len(self.__coldef)
    
class FeaturesFile(object):
    """ Read and write features to CSV files. """
        
    def write_header(self, csv_file, features_names):
        """ Write to file the header with the name of the columns.
        
            csv_file - csv file used to write the header.
            features_names - The names of the features to include in the header.
             
        """
        
        header = [CsvUtil.ID, CsvUtil.CLASS]
        
        header.extend(features_names)
        
        csv_file.writerow(header)        
        
    def write_rows(self, csv_file, star_classes, features):
        """ Write to file the features of the stars.
        
            csv_file - csv file used to write the header.
            star_classes - StarClasses object, it contains all the information
                related to the stars.             
            features - Features to write in the csv file.        
         
        """
        
        # For the features of each star.
        for i in range(len(features)):
            
            # If the star is enabled (data for this star is ok).
            if star_classes.is_enabled(i):
            
                # Creates the row to write using the information and features of
                # current star.
                row = [star_classes.star_identifier(i)] + \
                    [star_classes.class_name(i)] + \
                    features[i]
                    
                # Writes the row to disk.
                csv_file.writerow(row)    
                
    def get_file_name(self, filter_name, filename):
        """ Returns the name of the csv file constructed from the file name 
            received and the name of the filter whose features are to be
            saved in this file.
            
            filter_name - Name of the filter to add as suffix to the file name.
            filename - Prefix of the file name.
            
        """
        return filename + '_' + filter_name + CsvUtil.FILE_EXT     
    
    def write_features(self, filename, star_classes, features_names): 
        """ 
        
            filename - Name of the file to write the features.
            star_classes - StarClasses object, it contains all the information
                related to the stars.
            features_names - Names of the features to write.
        """
        
        # For each filter writes the features of its stars to a different file.        
        for i in range(len(star_classes.filters_names)):
            
            # Get the name of the filter.
            filter_name = star_classes.filter_name(i)
            
            # Get the features of the star.
            features = star_classes.get_filter_features(i)       
        
            current_filename = self.get_file_name(filter_name, filename)
            
            with open(current_filename, 'wb') as csvfile:
                
                logging.info("Writing features to file: " + current_filename)
                
                csv_file = csv.writer(csvfile, delimiter=',', quotechar='"')   
                     
                self.write_header(csv_file, features_names)
                self.write_rows(csv_file, star_classes, features) 
            
    def get_filters_names_from_filename(self, filename):
        """ Extracts the filter name from a filename that should corresponds
            to a features file that incorporates the filter name using the
            format: name_filter.ext
            The filter name is intended to be between the last '_' and last '.'.
            
            filename - File name to use.
            
        """
        
        files_names = []
        filters_names = []
        
        file_name_pattern = filename + '*' + CsvUtil.FILE_EXT
            
        logging.info('Searching features file with pattern %s.', file_name_pattern)        
        
        for file_found in os.listdir('.'):
            
            if fnmatch.fnmatch(file_found, file_name_pattern):
                
                files_names.append(file_found)
                
                logging.info("Found features file: " + file_found)                
                
                underscore_rpar = file_found.rpartition('_')                
                dot_rpar = file_found.rpartition('.')
                
                # If the characters that mark off the filter name are found.
                if ( len(underscore_rpar[0]) > 0 and \
                     len(underscore_rpar[1]) > 0 and \
                     len(dot_rpar[0]) > 0 and \
                     len(dot_rpar[1]) > 0 ):
                
                    filtername = file_found[len(underscore_rpar[0]) + \
                                       len(underscore_rpar[1]) : \
                                       len(dot_rpar[0]) + \
                                       len(dot_rpar[1]) - 1]
                        
                    filters_names.append(filtername)
        
        if len(files_names) > 0:               
            logging.info('Found the following features files for filters %s' % files_names)
        else:
            logging.info("Features files not found.")                       
                              
        return files_names, filters_names                
            
    def read_features(self, filename, meta, star_classes):
        """ Read information of stars from one or more CVS files.
            The information contains identification, class, and features of stars.
            It could exists several files, one per filter, so a file related to
            each filter is used. The names of the files are constructed from the 
            file name received and the filter name.
            
            filename - Name of the file to read.
            meta - Information of the columns contained in the file.
            star_classes - StarClasses object, it contains all the information
                related to the stars.
        
        """
        
        # Indicates if the information about the stars has already been saved.    
        star_info_saved = False   
        
        # Get the actual name of files. These name must follow a pattern that uses
        # the file name received and must include a suffix for the name of the filter.
        files_names, filters_names = self.get_filters_names_from_filename(filename)     
        
        # Check if some file name has been found.
        if len(files_names) > 0:
            logging.info("Filter names: %s" % filters_names)        
        
            # The variables store the number of the columns that contains the data
            # of the stars related to their identification, class, and features.
            id_col = 0
            class_col = 0
            param_range_col = []   
            
            # To save the information related to class identifiers and classes.
            star_ids = []
            star_classes_names = []     
            
            # An index for each filter (file) being processed.
            filter_index = 0     
                      
            # For each filter read the features from its file.
            for filename, afilter in zip(files_names, filters_names):
                
                logging.info('Opening features file %s for filter %s' % (filename, afilter))
                
                # Adds a new filter for the set of stars.
                star_classes.add_filter_name(afilter)
    
                # Read csv file.
                with open(filename, 'rb') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
                    try:
                        n = 0
                        for row in reader:
                            # First row is columns names.
                            if n == 0:
                                logging.info('Processing row of columns names.')
                                
                                meta.process_cols(row)
                                
                                # if the star information has not been saved, 
                                # (it only happens when processing the first file).                              
                                if not star_info_saved :
                                    # After processing the row with the type of each column,
                                    # get the column corresponding to the star identifier and class.
                                    id_col = meta.get_id_col()
                                    
                                    class_col = meta.get_col_of_class()
                                    
                                    # Get the range of columns that contains the features.
                                    param_range_col = meta.get_range_of_params()  
                                    
                                    if len(param_range_col) < 2:
                                        sys.exit('Error establishing range of columns for features, in %f at line %d' % (filename, reader.line_num))
                                                            
                            # Rest of rows is star information (identifier and class)
                            # and their features, save them.
                            else:               
                                # if the star information has not been saved, 
                                # (it only happens when processing the first file).     
                                if not star_info_saved :
                                    star_ids.append(row[id_col])
                                    star_classes_names.append(row[class_col])
                                                                   
                                # Get from current row only the features of the star.
                                star_features_in_current_filter = \
                                    row[param_range_col[0]:param_range_col[1]+1]
                                
                                # Add the features of current star in the appropriate filter..
                                star_classes.add_feature(filter_index, 
                                                                star_features_in_current_filter)
                                            
                            n += 1
                    except csv.Error as p:
                        logging.info('Error reading file %s, line %d: %s' % (filename, reader.line_num, p)) 
                        sys.exit('Error reading file %s, line %d: %s' % (filename, reader.line_num, p))                                                     
                        
                logging.info("Read %d rows from file '%s'" % (n, filename)) 
                        
                filter_index += 1  
                
                # if the star information has not been saved, 
                # (it only happens when processing the first file). 
                if not star_info_saved :
                    star_classes.set_star_id_and_classes(star_ids, star_classes_names)
                    
                    star_info_saved = True  
                
        return star_info_saved            