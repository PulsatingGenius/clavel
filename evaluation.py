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
This module evaluates the results of a prediction over a set of stars
whose class is known.

"""  

import csv

class Evaluation(object):           
    
    def __init__(self, predicted_classes_, evaluation_classes_, star_classes_, outfilename_suffix_):
        """ Initializes variables and evaluates the prediction. """
        
        self.__predicted_classes = predicted_classes_
        self.__star_classes = star_classes_
        self.__outfilename = "conf_matrix_" + outfilename_suffix_ + ".csv"
        
        self.__evaluation_classes = evaluation_classes_
        
    def generate_confusion_matrix(self):
        """ Generate the confusion matrix with the results of the prediction. 
            Column corresponds to actual classes, and rows to predicted classes.  
        
        """
        
        # Get the names of the classes.
        unique_classes_name_set = self.__star_classes.unique_classes_names        
              
        # Fill the matrix with the prediction results.
        header_row = ['']
        header_row.extend(unique_classes_name_set)
        # Matrix for the rows, the first column of each row will be 
        # the name of the class.
        classes_rows = []  
        
        number_of_classes_evaluated = len(unique_classes_name_set)
        
        # Initiate rows of data.
        for i in range(number_of_classes_evaluated):
            new_row = []
            # First column is the name of the class predicted.
            new_row.append(unique_classes_name_set[i])
            # Rest of columns are the number of predictions.
            new_row.extend([0] * number_of_classes_evaluated) 
            classes_rows.append(new_row) 
    
        # Initiate row with the number of total predictions for each class.
        total_instances = ["TOT"]
        total_instances.extend([0] * number_of_classes_evaluated)  
    
        # Count each prediction in each cell of the confusion matrix. 
        for i in range(len(self.__evaluation_classes)):    
            # Get the index for the class evaluated.
            class_col_index = self.__evaluation_classes[i]
            # Get the index for the class predicted, 
            # retrieved as float so convert it to int to be used as a list index.
            class_row_index = int(self.__predicted_classes[i])
            
            # Get the row of the class predicted.
            row = classes_rows[class_row_index]
            
            # Increment the count for the class predicted, the first
            # cell is for the name of the class.
            row[class_col_index + 1] += 1
            
            # Add it to the total of the class evaluated.
            total_instances[class_col_index + 1] += 1
        
        # Set the name of last the row. 
        perc_pred_success = ["(CC)"]
            
        # Calculate the percentage of match for each class evaluated.   
        for i in range(number_of_classes_evaluated):            
            # Get the row of the predicted class.
            row = classes_rows[i]
            
            # Add one to the index for the class predicted as the first
            # cell of the row is used for the name of the class and data
            # begins from second cell.          
            predict_success = int(row[i + 1]) * 100.0 / total_instances[i + 1]
                
            perc_pred_success.append("%2.f" % predict_success)              
          
        # Write the confusion matrix to a CSV file.
        with open(self.__outfilename, 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"')
            writer.writerow(header_row)      
                
            for r in classes_rows:
                writer.writerow(r)
            
            writer.writerow(total_instances)
            writer.writerow(perc_pred_success)          