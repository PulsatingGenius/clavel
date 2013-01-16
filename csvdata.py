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

class CsvUtil(object):
    META = "META"
    CLASS = "CLASS"
    PARAM = "PAR"
    ID = "ID"    
    FILE_EXT = '.csv'

class ColumnDef(object):
    """ It keeps the information related to a column. """    
    
    def __init__(self, colnumber_, type_):    
        """ Initiation of ColumnDef objects. Only for variable assignment. """
        
        self.__colnumber = colnumber_     
        self.__type = str(type_)
        self.__colname = ""  
        self.__number_of_instances = 0        
        
    @property
    def colnumber(self):
        return self.__colnumber
    
    @property
    def type(self):
        return self.__type    
    
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
    
    def is_param(self):
        return self.__type == CsvUtil.PARAM    
        
    def __str__(self):        
        return "Col=%s, Type=%s, Name=%s" % \
            (self.__colnumber, self.__type, self.__colname)            
    
class MetaData(object):    
    """ It keeps metadata of the set of data related to columns. """
    
    def __init__(self):            
        self.__coldef = []     
        
    def process_meta(self, row):
        n = 0
        for c in row:
            self.__coldef.append(ColumnDef(n, c))            
            n += 1
            
    def process_cols(self, row):   
        n = 0 
        for c in row:    
            self.__coldef[n].colname = c
            n += 1
            
    def get_col_info(self, n):
        if n >= len(self.__coldef):
            raise IndexError("There is not a column number %d" % n)
        else:
            return self.__coldef[n]
        
    def get_id_col(self):
        """ Get the number of the column that contains the id of the star. """
        
        n = -1
        i = 0
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
        while (i < len(self.__coldef)) and (n == -1):
            if self.__coldef[i].is_class():
                n = i 
                
            i += 1
                
        if n == -1:
            raise ValueError("There is not a column with CLASS type.")
        else:
            return n        
        
    def get_range_of_params(self):
        """ Get the range of columns that contains parameters. """
        par_range = []
        
        range_init_found = False
        
        last_column = 0
        
        for c in self.__coldef:
            if c.is_param():
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
    
    def write_metaheader(self, csv_file, features):
        """ Write to file a header that contains information about the type of each column. """
                
        features_row = features[0]         
        
        metaheader = [CsvUtil.META, CsvUtil.CLASS]
        
        metaheader.extend([CsvUtil.PARAM] * len(features_row))
        
        csv_file.writerow(metaheader)
        
    def write_header(self, csv_file, features):
        """ Write to file the header with the name of the columns. """

        features_row = features[0]   
        
        header = [CsvUtil.ID, CsvUtil.CLASS]
        
        header.extend([CsvUtil.PARAM] * len(features_row))
        
        csv_file.writerow(header)        
        
    def write_rows(self, csv_file, star_classes, features):
        """ Write to file the features of the stars. """
        
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
            
        """
 
        position = filename.index('.')
        
        return filename[0:position] + '_' + filter_name + CsvUtil.FILE_EXT                
    
    def write_features(self, filename, star_classes): 
        
        # For each filter writes the features of its stars to a different file.        
        for i in range(len(star_classes.filters)):
            
            # Get the name of the filter.
            filter_name = star_classes.filter_name(i)
            
            # Get the features of the star.
            features = star_classes.get_filter_features(i)       
        
            current_filename = self.get_file_name(filter_name, filename)
            
            with open(current_filename, 'wb') as csvfile:
                
                print "Writing features to file: " + current_filename
                
                csv_file = csv.writer(csvfile, delimiter=',', quotechar='"')   
                     
                self.write_metaheader(csv_file, features)
                self.write_header(csv_file, features)
                self.write_rows(csv_file, star_classes, features) 
            
    def get_filters_names_from_filename(self, filename):
        """ Extracts the filter name from a filename that should corresponds
            to a features files that incorporates the filter name using the
            format: name_filter.csv
            The filter name is intended to be between the last '_' and last '.'.
            
        """
        
        files_names = []
        filters_names = []
        
        dot_rpar = filename.rpartition('.')
        
        if ( len(dot_rpar[0]) > 0 and len(dot_rpar[1]) > 0):
            final_pos = len(dot_rpar[0]) + len(dot_rpar[1]) - 1
            filename_no_ext = filename[0:final_pos]
        
            for afile in os.listdir('.'):
                if fnmatch.fnmatch(afile, filename_no_ext + '*' + CsvUtil.FILE_EXT):
                    
                    files_names.append(afile)
                    
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
                              
        return files_names, filters_names                
            
    def read_features(self, filename, meta, star_classes):
        """ Read information of stars from one or more CVS files.
            The information contains identification, class, and features of stars.
            The names of the files are constructed from the file name received
            and
        
        """
        
        # Indicates if the information about the stars has already been saved.    
        star_info_saved = False   
        
        # Get the actual name of files. These name must follow a pattern that uses
        # the file name received and must include a suffix for the name of the filter.
        files_names, filters_names = self.get_filters_names_from_filename(filename)     
        
        # Check if some file name has been found.
        if len(files_names) > 0:
            print "Filter names: %s" % filters_names        
        
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
                
                # Adds a new filter for the set of stars.
                star_classes.add_filter(afilter)
    
                # Read csv file.
                with open(filename, 'rb') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
                    try:
                        n = 0
                        for row in reader:
                            # First row is metadata, save it as metadata.
                            if n == 0:
                                meta.process_meta(row)
                            # Second row is column information, save it as column info.
                            elif n == 1:
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
                        sys.exit('Error reading file %s, line %d: %s' % (filename, reader.line_num, p))                                                     
                        
                filter_index += 1  
                
                # if the star information has not been saved, 
                # (it only happens when processing the first file). 
                if not star_info_saved :
                    star_classes.set_star_id_and_classes(star_ids, star_classes_names)
                    
                    star_info_saved = True  
                
        return star_info_saved            