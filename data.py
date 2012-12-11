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
This module represents a data.
"""       

import random

class ColumnDef(object):
    """ It keeps the information related to a column. """
    
    __meta = "META"
    __class = "CLASS"
    __param = "PAR"
    
    def __init__(self, colnumber_, type_):    
        """ Initiation of ColumnDef objects. Only for variable assignment. """
        
        self.__colnumber = colnumber_     
        self.__type = type_
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
        self.__colname = colname_  
        
    def is_class(self):
        return self.__type == self.__class
    
    def is_param(self):
        return self.__type == self.__param    
        
    def __str__(self):        
        return "Col=%s, Name=%s, Type=%s" % \
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
        
    def get_range_of_params(self):
        """ Get the range of columns that contains parameters. """
        par_range = []
        
        range_init_found = False
        
        for c in self.__coldef:
            if c.is_param():
                if not range_init_found:
                    range_init_found = True
                    par_range.append(c.colnumber)
            elif range_init_found:
                par_range.append(c.colnumber)
        
        return par_range
    
    def len(self):
        return len(self.__coldef)
    
    def get_col_of_class(self):
        n = -1
        i = 0
        while (i < len(self.__coldef)) and (n == -1):
            if self.__coldef[i].is_class():
                n = i 
                
            i += 1
                
        if n == -1:
            raise ValueError("There is not a column with CLASS type")
        else:
            return n
            
    def __str__(self):        
        return "Size=%d" % len(self.__coldef)
    
class DataSet(object):    
    """ It keeps rows of data. """
    
    def __init__(self, meta_):
        """ . """
        
        self.__meta = meta_
        self.__ds = []
        
    def add_row(self, row):
        new_row = []

        for n in range(len(row)):
            elem = row[n].strip()
            
            if (type(elem) == int) or (type(elem) == float):
                new_row.append(float(elem))
            else:
                new_row.append(elem)
                
        self.__ds.append(new_row)
            
    def get_row(self, n):
        if ( n >= len(self.__ds) ):
            raise IndexError("There is not a row %d" % n)
        else:        
            return self.__ds[n]
        
    def get_number_of_rows(self):
            return len(self.__ds)
        
    def print_meta_col(self, n):
        if ( n >= len(self.__ds) ):
            raise IndexError("There is not a column number %d" % n)
        else:
            str_meta = ""
            
            for n in range(self.__meta.len()):
                str_meta += " | %s" % self.__meta.get_col_info(n).colname
            
            print str_meta
                
            print self.__ds[n]
            
    def __str(self):
        return "Meta is %d and dataset lenght is %d" % \
            (self.__meta.len(), len(self.__ds))
         
class TrainingData(object):    
    """ . """

    def choose_training_and_evaluation_sets(self, instances_range):
        """ Define two sets of indexes from the range received to be used 
            as training and evaluation elements. """
        
        training_indexes = []
        evaluation_indexes = []
        
        minr = instances_range[0]
        maxr = instances_range[-1]
        
        # Check if the range contains enough elements for training.
        if ( maxr - minr ) > self.__min_cardinal:
            # Get the number of instances for the training set.
            number_of_samples_for_training = \
                int(((maxr - minr) * self.__training_set_percent / 100))
            
            # Get a random number of samples from the range received.
            training_indexes = random.sample(range(minr, maxr),  \
                                               number_of_samples_for_training)
            
            # Search in the range for indexes not selected for training.
            for i in range(minr, maxr):
                try:
                    training_indexes.index(i)
                except ValueError:
                    # This element in not in the training set,
                    # add it to the evaluation set.
                    evaluation_indexes.append(i)
            
        return training_indexes, evaluation_indexes     
    
    def calculate_training_data_for_class(self, current_class, start_index, end_index):
        """ . """
        
        # Add the class to the set of classes.
        self.__classes.append(current_class)
        
        # Add the number of instances for this class to the appropriate set.
        self.__num_of_instances_of_class.append(end_index - start_index)
        
        # Add the range for this class to the set of ranges.
        self.__ranges_for_classes.append(range(start_index, end_index))
        
        # Get the sets of training and evaluation sets for this class.
        training_indexes, evaluation_indexes = \
            self.choose_training_and_evaluation_sets(range(start_index, end_index))
            
#        if len(training_indexes) > 0:
#            print "%s: training:%d, eval:%d, total:%d" % \
#                (current_class, len(training_indexes), len(evaluation_indexes), end_index - start_index)
          
        # Add these sets to the appropriate sets.  
        self.__training_indexes_for_classes.append(training_indexes)       
        self.__evaluation_indexes_for_classes.append(evaluation_indexes)
    
    def __init__(self, min_cardinal_, training_set_percent_, dataset_, meta_):
        """ . """
        
        self.__num_of_instances_of_class = []        
        self.__classes = []    
        self.__ranges_for_classes = []   
        self.__training_indexes_for_classes = []
        self.__evaluation_indexes_for_classes = []  
        self.__min_cardinal = min_cardinal_
        self.__training_set_percent = training_set_percent_
        
        # Initialize training options.        
        number_of_data_rows = dataset_.get_number_of_rows()
        class_column_number = meta_.get_col_of_class()
        
        current_class_name = ""   
        start_index = 0 
               
        # Inspect the classes of all the rows and get the training set for each.
        for row_index in range(number_of_data_rows):
            row = dataset_.get_row(row_index)
            
            # Check if class of current row is not equal to previous row.
            if current_class_name != row[class_column_number]:
                
                # Check if it is the first row.
                if row_index <> 0:
                    # Current row is for a different class than previous row.
                    # Calculate training options for previous class.
                    self.calculate_training_data_for_class(current_class_name, start_index, row_index)
          
                    # Update minimum index of the new class.
                    start_index = row_index
                           
                # Save the new class name.
                current_class_name = row[class_column_number]
            
        if current_class_name <> "":
            # Last class, save the options for this class.
            self.calculate_training_data_for_class(current_class_name, start_index, row_index + 1)           
        
    def get_number_of_classes(self):
        return len(self.__num_of_instances_of_class)
        
    def get_training_data(self, class_number):
        """ . """
        
        return (self.__num_of_instances_of_class[class_number], 
                self.__classes[class_number],    
                self.__ranges_for_classes[class_number],   
                self.__training_indexes_for_classes[class_number])
        
    def get_evaluation_instances(self):
        """ . """
        
        return (self.__classes,   
                self.__evaluation_indexes_for_classes)        
        
    def shuffle_training_instances(self):
        """ . """
        
        self.__training_indexes_for_classes = []
        self.__evaluation_indexes_for_classes = []
        
        for ir in self.__ranges_for_classes:
            training_instances, evaluation_instances = \
                self.__training_indexes_for_classes.append(self.get_training_instances(ir))
            
            self.__training_indexes_for_classes.append(training_instances)       
            self.__evaluation_indexes_for_classes.append(evaluation_instances)            
        
    def __str__(self):
        return "Number of classes: %d, Minimum cardinal: %d, training_set_percent: %d" % \
            (len(self.__num_of_instances_of_class), self.__min_cardinal, self.__training_set_percent)        