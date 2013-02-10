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
import logging

class ClassifierArguments(object):
    """ Encapsulates the processing of program arguments, the file name with
        the data of stars and the some parameters for the classifying process.
        
    """
    
    def __init__(self, stars_set_min_cardinal_ = 15, training_set_percent_ = 65, 
                 number_of_trees_ = 100):
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
        
        # Initiate arguments of the parser.
        self.__parser = argparse.ArgumentParser()
        
        self.__parser.add_argument('-t', dest='t', action='store_true', 
                                   help='Training mode')
        
        self.__parser.add_argument('-p', metavar='suffix for the file names of predicted stars', dest='p', 
                                   help='Prediction mode')
        
        self.__parser.add_argument('-e', dest='e', action='store_true', 
                                   help='Evaluation mode')
        
        self.__parser.add_argument('-c', metavar='cardinal', type=int, default ='25', dest='c', 
                                   help='Minimum number of stars of a type to consider the type for training')
        
        self.__parser.add_argument('-g', metavar='percentage', type=int, default ='75', dest='g', 
                                   help='Percentage of instances used for training')
        
        self.__parser.add_argument('-r', metavar='trees', type=int, default ='50', dest='r', 
                                   help='Number of trees used in classification')

        self.__parser.add_argument('-s', metavar='Stars identifiers file name', dest='s', 
                                   help='File that contains the stars identifiers')
        
        self.__parser.add_argument('-d', metavar='LEMON database file name', dest='d', 
                                   help='File that contains the LEMON database')        
        
        self.__parser.add_argument('-f', metavar='suffix for the file names of the features', dest='f', \
                                   help='File with the star features, if it exists the features are read from this file, instead of calculating. If the file does no exist, the features calculated are stored in the file')
        
        self.__parser.add_argument('-m', metavar='model file name', dest='m', 
                                   help='File to save the classification model')
        
        self.__parser.add_argument('-l', metavar='log file name', dest='l', 
                                   help='File to save the log messages')        
        
        self.__args = None    
        
    @property    
    def is_training(self):        
        return self.__args.t
    
    @property
    def is_prediction(self):
        return self.__args.p <> None
    
    @property
    def is_evaluation(self):
        return self.__args.e
        
    def parse(self):
        
        self.__args = self.__parser.parse_args()
            
        if self.__args.c <> None:
            self.__stars_set_min_cardinal = self.__args.c
            
        if self.__args.g <> None:
            self.__training_set_percent = self.__args.g
            
        if self.__args.r <> None:
            self.__number_of_trees = self.__args.r 
            
    @property
    def datafile_and_stars_file_provided(self):
        return self.stars_id_file_provided and self.database_file_provided
            
    def check_arguments_set(self):
        """ Checks if the set of arguments received is coherent, i.e.,
            arguments aren't contradictory or anything is missing.
            
        """
        logging.info('Checking the coherence of program arguments received.')
        arguments_ok = True
          
        # Check that only a function mode is specified.
        if ( self.is_training and (self.is_prediction or self.is_evaluation )) or \
            ( self.is_prediction and ( self.is_evaluation or self.is_training )) or \
            ( self.is_evaluation and ( self.is_prediction or self.is_training )):
            logging.error("Only one function mode is allowed, training or prediction or evaluation.")
            arguments_ok = False
          
        # Check arguments for training mode.
        if self.is_training:
            if ( not self.datafile_and_stars_file_provided ) and \
                 not self.features_file_provided :
                logging.error("In training mode a features file or the pair database + stars identifiers file must be provided.")
                arguments_ok = False
                
        # Check arguments for predicting mode.
        if self.is_prediction:
            if ( not self.datafile_and_stars_file_provided ) and \
                 not self.features_file_provided :
                logging.error("In predicting mode a pair of files for database and stars identifiers must be provided.")
                arguments_ok = False  
                
        # Check arguments for evaluation mode.
        if self.is_evaluation:
            if ( not self.datafile_and_stars_file_provided ) and \
                 not self.features_file_provided :
                logging.error("In evaluation mode a features file or the pair database + stars identifiers file must be provided.")
                arguments_ok = False
          
        return arguments_ok
    
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
    def prediction_file(self):
        return self.__args.p
    
    @property
    def database_file_provided(self):
        return self.__args.d <> None
    
    @property
    def database_file_name(self):
        return self.__args.d
    
    @property
    def features_file_provided(self):
        return self.__args.f <> None
    
    @property
    def features_file_name(self):
        return self.__args.f
    
    def model_file_provided(self): 
        return self.__args.m <> None      
    
    @property
    def model_file_name(self):
        return self.__args.m
    
    def log_file_provided(self): 
        return self.__args.l <> None     
    
    @property
    def log_file_name(self):
        return self.__args.l           
    
    @property
    def stars_id_file_provided(self): 
        return self.__args.s <> None     
    
    @property
    def stars_id_file_name(self):
        return self.__args.s     