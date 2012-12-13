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
This module get the training and evaluation sets from a set of data given
the minimum number of instances in each class to be considered for training
using the percentage of instances chosen for the training set.

"""   

import random

class TrainEvalSet(object):    
    """ Get a random training and evaluation sets from a set of data instances. 
        
    """   
    
    def __init__(self, classifarg_, star_classes_):
        """ Initializes all the data related to training and evaluations
            sets for the instances received.
            
        """
        
        # Names of classes.        
        self.__training_classes = []
        # Indexes related to star_class to the stars of each class.    
        self.__classes_indexes = []   
        # Indexes to use for training in each class.
        self.__sets_of_training_indexes_for_classes = []
        # Indexes to use for evaluation in each class.
        self.__sets_of_evaluation_indexes_for_classes = []  
        # Minimum number of instances in a class to be considered for training.
        self.__min_cardinal = classifarg_.stars_set_min_cardinal
        # Percentage of instances to be used in each class for training.
        self.__training_set_percent = classifarg_.training_set_percent
        # Data for all the classes and their indexes.
        self.__star_classes = star_classes_
        
    def get_number_of_classes(self):
        return len(self.__num_of_instances_of_class)           
        
    def __str__(self):
        return "Number of classes: %d, Minimum cardinal: %d, training_set_percent: %d" % \
            (len(self.__num_of_instances_of_class), self.__min_cardinal, self.__training_set_percent)
            
    def get_indexes_for_class(self, class_name):
        """ For a given class get the indexes of its instances.
            These indexes correspond to self.__star_classes. 
        
        """
        
        instances_of_class = []
        
        all_classes = self.__star_classes.classes
        
        for i in range(len(all_classes)):
            # If current star corresponds to this class and it is enabled,
            # add it to the set of this class.
            if ( all_classes[i] == class_name ) and \
                ( self.__star_classes.enabled[i] == True ):
                instances_of_class.append(i)
        
        return instances_of_class
            
    def determine_classes_to_use_for_training(self):
        """ Determine the classes to be used for training depending on the
            number of instances available for each class. Count the number of
            instances of each class and if its number of elements is bigger 
            than minimum cardinal the class is selected for training, 
            otherwise the class and all of its instances are discarded for
            training.
            
        """
        
        # Initialize variables to account for all the classes and 
        # the number of its instances.
        unique_classes = [self.__star_classes.classes[0]]
        number_of_instances_by_class = [0]
        
        # Count the number of instances for each class that will be considered
        # for training.
        for i in range(len(self.__star_classes.classes)):
            # Check if the star is enabled, otherwise is ignored.
            if self.__star_classes.enabled[i] == True:
                # The instances are not ordered, so search for the class.
                try:
                    class_name = self.__star_classes.classes[i]
                    
                    # Check if any instance of this class has been found before.
                    current_class_index = unique_classes.index(class_name)
                    # Count for it.
                    number_of_instances_by_class[current_class_index] += 1
                except ValueError:
                    # This is the first instance of this class, add its name.
                    unique_classes.append(class_name)
                    # Count it as a new element.
                    number_of_instances_by_class.append(1)
            else:
                print "Instance at index %d ignored for training" % i
           
        # Check the number of instances found for each class and determine
        # if it has enough elements for training (a number of instances
        # bigger than the minimum cardinal).
        for i in range(len(unique_classes)):                            
            if number_of_instances_by_class[i] >= self.__min_cardinal:
                # Save the class name.
                self.__training_classes.append(unique_classes[i])
                # Save the instances of this class.
                instances = self.get_indexes_for_class(unique_classes[i])
                self.__classes_indexes.append(instances)
                
                print "Class %s used for training, %d elements, %s." \
                    % ( unique_classes[i], len(instances), instances)
            else:
                print "Class %s ignored for training, not enough elements." \
                    % unique_classes[i]

    def calculate_training_and_evaluation_sets(self):
        """ Calculate the sets of indexes of each class to be used for
            training and evaluation. A a random calculation determines
            the indexes to be used for for training and evaluation.
            These indexes are related to the position of the star in 
            star_class.
        
        """
        
        # Determine the classes and the instances to use for training.
        self.determine_classes_to_use_for_training()    
        
        # Inspect the classes of all the rows and get the training set for each.
        for instances in self.__classes_indexes:
            # Initialize sets for the training and evaluation indexes of 
            # current class.
            training_indexes = []
            evaluation_indexes = []            
            
            # Number of instances of current class.
            number_of_instances = len(instances)
            
            # Calculate the number of instances of current class for training.
            number_of_instances_for_training = \
                int(number_of_instances * self.__training_set_percent / 100)
            
            # Get a random sample of indexes of this class to be used for training. 
            training_indexes = random.sample(xrange(number_of_instances), \
                                               number_of_instances_for_training)
            
            # Check if there is any instance to use for evaluation,
            # this run could use a set only for training.
            if number_of_instances - number_of_instances_for_training > 0: 
                # Evaluation indexes are those from current class not used 
                # for training.
                for i in range(number_of_instances):
                    try:
                        # Try if it has been selected for training.
                        training_indexes.index(i)
                    except ValueError:
                        # This element in not in the training set,
                        # add it to the evaluation set.
                        evaluation_indexes.append(i)  
                
            self.__sets_of_training_indexes_for_classes.append(training_indexes)
            self.__sets_of_evaluation_indexes_for_classes.append(evaluation_indexes)
            
    def __get_indexes(self, sets_of_indexes): 
        """ Returns the whole set of identifiers related to the set of indexes received 
            and the numerical identifiers for each class.
        
        """   
        
        instances = []
        class_identifiers = []
        
        # All the classes.
        for class_index in range(len(self.__training_classes)):
            # Get the set of indexes for current class.
            index_set = sets_of_indexes[class_index]
            instances_set = self.__classes_indexes[class_index]
            
            "Clase %s numero de instancias %d" % (self.__star_classes.classes[class_index], len(index_set))
            
            for i in index_set:
                instances.append(instances_set[i])
                class_identifiers.append(class_index) 
                
        return instances, class_identifiers        
            
    def training_indexes(self):
        """ Returns the whole set of identifiers used for training and 
            the numerical identifiers for each class.
            
        """
        
        return self.__get_indexes(self.__sets_of_training_indexes_for_classes)
        
        
    def evaluation_indexes(self):
        """ Returns the whole set of identifiers used for evaluation and 
            the numerical identifiers for each class.
            
        """     
        
        return self.__get_indexes(self.__sets_of_evaluation_indexes_for_classes)   
                    