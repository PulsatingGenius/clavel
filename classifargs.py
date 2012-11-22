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
This module process the arguments received by the classifier, check
for number and correctness, and provides these arguments to other modules. 

"""

import sys

class ClassifierArguments(object):
    
    def __init__(self):
        """ Initiation of ClassifierArguments objects. 
            Only for variable initialization. """   
        
        # Limits for some values of arguments.
        # Maximun valur for the percentage of instances of each class to be 
        # used for training.
        self.__max_percent = 99
        # Maximun number of decision trees to use for classifying.
        self.__max_trees = 200          
                
        # Name of the database of light curves.
        self.__filename = ""
        # Minimum number of instances in a class to be used for training.
        self.__stars_set_min_cardinal = 15
        # Percentage of instances of each class to be used for training.
        self.__training_set_percent = 65
        # Number of decision trees to use for classifying.
        self.__number_of_trees = 60  
        
        # Value for no error return value.
        self.__no_error_value = 0
        
        # Value for error return value.
        self.__error_value = -1        
        
    @property 
    def filename(self):
        return self.__filename
    
    @property 
    def stars_set_min_cardinal(self):
        return self.__stars_set_min_cardinal
    
    @property 
    def training_set_percent(self):
        return self.__training_set_percent
    
    @property 
    def number_of_trees(self):
        return self.__number_of_trees    
    
    @property 
    def no_error_value(self):
        return self.__no_error_value
    
    @property 
    def error_value(self):
        return self.__error_value        
    
    def print_usage(self, program_name):
        print "------------------------------------------------------------------------------------------"
        print "Usage:"
        print "%s name [min] [perc] [trees] \n%s \n%s \n%s%d. \n%s%d." % \
            (program_name, \
            "- name - Name of the file with the data.", \
            "- min - Optional, minimum number of instances in class to be classified.", \
            "- perc - Optional, percentage of instances to be used for training, 1-", \
            self.__max_percent,
            "- trees - Optional, number of decision trees used to classify, <", \
            self.__max_trees) 
        print "------------------------------------------------------------------------------------------"   
    
    def process_filename_arg(self, value, program_name):
        return_value = self.__no_error_value    
        
        try:
            self.__filename = value
        except ValueError:
            self.print_usage(program_name)
            return_value = self.error_value
            
        return return_value
    
    def process_minset_arg(self, value, program_name):
        return_value = self.no_error_value  
            
        try:
            n = int(value)
            if n > 0:
                self.__stars_set_min_cardinal = n
            else:
                print "Error: 'Minimum number of stars in set' argument should be between 1 and 99."
                return_value = self.error_value            
        except ValueError:
            self.print_usage(program_name)
            return_value = self.error_value        
            
        return return_value
    
    def process_trainpercent_arg(self, value, program_name):
        return_value = self.no_error_value  
            
        try:
            n = int(value)
            if n <= self.__max_percent:
                self.__training_set_percent = n
            else:
                print "Error: 'Training percent' argument should be smaller than 200."
                return_value = self.error_value            
        except ValueError:
            self.print_usage(program_name)
            return_value = self.error_value
            
        return return_value
    
    def process_numoftrees_arg(self, value, program_name):
        return_value = self.no_error_value    
        
        try:
            n = int(value)
            if n < self.__max_trees:
                self.__number_of_trees = n
            else:
                print "Error: 'Number of trees' argument should be smaller than 200."
                return_value = self.error_value            
        except ValueError:
            self.print_usage(program_name)
            return_value = self.error_value         
            
        return return_value
    
    def process_program_args(self):
        
        return_value = self.no_error_value
        
        num_of_arguments = len(sys.argv)
        
        program_name = sys.argv[0]
    
        # Not enough arguments or user asking for help.
        if (num_of_arguments < 2) or (sys.argv[1] == "?"):
            self.print_usage(sys.argv[0])  
            
            return_value = self.error_value
        elif num_of_arguments > 1 :
            return_value = self.process_filename_arg(sys.argv[1], program_name)
            if (return_value <> self.error_value ) and ( num_of_arguments > 2 ):
                return_value = self.process_minset_arg(sys.argv[2], program_name)     
            if (return_value <> self.error_value ) and ( num_of_arguments > 3 ):
                return_value = self.process_trainpercent_arg(sys.argv[3], program_name)           
            if (return_value <> self.error_value ) and ( num_of_arguments > 4 ):
                return_value = self.process_numoftrees_arg(sys.argv[4], program_name) 
            if (return_value <> self.error_value ) and ( num_of_arguments > 5 ):
                print "Too much arguments for classifier, received %d, only 5 are necessary" % \
                    len(sys.argv)
                            
        return return_value
    
    def input_file_is_cvs(self):
        is_cvs = True
        
        try:
            self.__filename.index(".csv")
        except ValueError:
            is_cvs = False
            
        return is_cvs 