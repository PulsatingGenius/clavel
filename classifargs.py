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

import argparse

class ClassifierArguments(object):
    """ Encapsulates the processing of program arguments, the file name with
        the data of stars and the some parameters for the classifying process.
        
    """
    
    def __init__(self, stars_set_min_cardinal_ = 15, training_set_percent_ = 65, 
                 number_of_trees_ = 60):
        """ Initiation of ClassifierArguments objects. 
            Only for variable initialization.
        
        """   
        
        # Limits for some values of arguments.
        # Maximum value for the percentage of instances of each class to be 
        # used for training.
        self.__max_percent = 99
        # Maximum number of decision trees to use for classifying.
        self.__max_trees = 200          
                
        # Name of the database of light curves.
        self.__filename = ""
        # Minimum number of instances in a class to be used for training.
        self.__stars_set_min_cardinal = stars_set_min_cardinal_
        # Percentage of instances of each class to be used for training.
        self.__training_set_percent = training_set_percent_
        # Number of decision trees to use for classifying.
        self.__number_of_trees = number_of_trees_  
        
        # Value for no error return value.
        self.__no_error_value = 0
        
        # Value for error return value.
        self.__error_value = -1
        
        # Initiate program arguments parser.
        self.__parser = argparse.ArgumentParser()
        
        self.__parser.add_argument('-t', metavar=('DB_file_name', 'stars_file_name'), nargs=2, dest='t', help='Only training')
        
        self.__parser.add_argument('-p', metavar=('DB_file_name', 'model_file_name'), nargs=2, dest='p', help='Predict the type of stars with model indicated')
        
        self.__parser.add_argument('-e', metavar=('DB_file_name', 'stars_file_name'), nargs=2, dest='e', help='Evaluate the prediction rate success')
        
        self.__parser.add_argument('-c', metavar='cardinal', type=int, default ='15', dest='c', help='Minimum number of stars of a type to consider the type for training')
        
        self.__parser.add_argument('-g', metavar='percentage', type=int, default ='65', dest='g', help='Percentage of instances used for training')
        
        self.__parser.add_argument('-r', metavar='trees', type=int, default ='50', dest='r', help='Number of tress used in classification')
        
        self.__parser.add_argument('-f', metavar='features_file_name', dest='f', \
                                   help='File with the star features, if it exists the features are read from this file, instead of calculating. If the file does no exist, the features calculated are stored in the file')  
        
        self.__args = None    
        
        self.__db_file = None
        
        self.__stars_file = None   
        
    def assign_files(self, file_list):
        """ Assign the files names received assigning them to the appropriate variable
            depending on order. First is DB and second the stars list. 
            
        """
        
        self.__db_file = file_list[0]
        
        self.__stars_file = file_list[1] 
        
    def is_training(self):        
        return self.__args.t <> None
    
    def is_prediction(self):
        return self.__args.p <> None
    
    def is_evaluation(self):
        return self.__args.e <> None            
        
    def parse(self):
        
        self.__args = self.__parser.parse_args()
        
        if self.is_training():
            self.assign_files(self.__args.t)
            
        elif self.is_prediction():
            self.__db_file = self.__args.p[0]
            
        elif self.is_evaluation():
            self.assign_files(self.__args.e) 
            
        if self.__args.c <> None:
            self.__stars_set_min_cardinal = self.__args.c
            
        if self.__args.g <> None:
            self.__training_set_percent = self.__args.g
            
        if self.__args.r <> None:
            self.__number_of_trees = self.__args.r   
    
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
    def db_file(self):
        return self.__db_file
    
    @property
    def stars_file(self):
        return self.__stars_file
    
    @property
    def features_file_is_given(self):
        return self.__args.f <> None
    
    @property
    def features_file(self):
        return self.__args.f