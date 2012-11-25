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

import sys
import csv
import csvdata
from sklearn.ensemble import RandomForestClassifier

class ClassifyCSV(object):
    """ Encapsulates the functionality to classify stars using the parameters
        stored in a CSV file.
    
    """
    def __init__(self, filename_, stars_set_min_cardinal_, training_set_percent_, 
                  number_of_trees_):
        """ Initiation of ClassifyCSV objects. Only for variable initialization.
        
        """           
        
        # Create objects to store metadata of CSV file and the data of the file.
        self.__meta = csvdata.MetaData()
        self.__ds = csvdata.CSVDataSet(self.__meta)  
        
        # Name of the file with the confusion matrix generated.
        self.__outfilename = "conf_matrix.csv"
        
        # Name of the csv file.
        self.__filename = filename_
        # Minimum number of instances in a class to be used for training.
        self.__stars_set_min_cardinal = stars_set_min_cardinal_
        # Percentage of instances of each class to be used for training.
        self.__training_set_percent = training_set_percent_
        # Number of decision trees to use for classifying.
        self.__number_of_trees = number_of_trees_  
        
    def print_meta_info(self, meta, n, row):
        """ Print info about the metadata of CSV file.
        
        """
        
        # Print info for all columns of CSV file.
        for n in range(meta.len()):
            info = meta.get_col_info(n)
            print "%s, Value=%s" % (info, row[n])
        
        # Return the number of columns.
        return n
    
    def print_classes_info(self, ds, n, row, current_class, class_count, \
                           class_column_number, number_of_rows):
        """ Print information about classes and number of instances in each one.
        
        """
        
        # For all the rows (read previously from CSV file).
        for n in range(number_of_rows):
            # Get current row.
            row = ds.get_row(n)
            
            # If this class is differente of previous class.
            if current_class != row[class_column_number]:
                # Print information for previous class.
                if current_class != "":
                    print "Class: %s, number of instances:%d" % \
                    (current_class, class_count)
                # Update class name.
                current_class = row[class_column_number]
                # Initialize counter for the new class.
                class_count = 1
            else:
                # Increment counter of classes instances.
                class_count += 1
        
        # Print information of last class.
        if current_class != "":
            print "Class: %s, number of instances:%d" % (current_class, class_count)
            
        # Return the number of rows.
        return n
    
    def get_rows_only_with_params(self, ds, param_range, rows_indexes, rows_set, \
                             actual_class_name, classnames_set):
        """ Return the rows received but only with the columns that contains data. 
        
        """
    
        # For all the rows related to data in this row set.
        for ti in rows_indexes:
            
            # Get the row.
            row = ds.get_row(ti)
            
            param_row = []
            
            # Copy only the columns of the row related to data parameters
            for i in range(param_range[0], param_range[1]):
                param_row.append(row[i])
    
            # Add the row of parameters.
            rows_set.append(param_row)
            # Add the class name.
            classnames_set.append(actual_class_name)
            
    def get_numerical_classes_set(self, classnames_training_set, unique_classes_name_set):
        """ Return a set of numbers to identify the class of each data in the
            training set. The goal is getting an numerical identification for 
            each class. This number is given to the classifier in place of the 
            class name. So, the classifier identifies each class with
            the number given here. 
        
        """
        
        # The list for the numerical identifications of the classes.
        numerical_classes_set = []
        
        # Get a numeric identification for each class.
        for actual_class_name in classnames_training_set:
            try:
                # The number is the index that the class name has in the
                # set that contains all the names of the classes just once.
                index = unique_classes_name_set.index(actual_class_name)
                
                numerical_classes_set.append(index)
            except:
                print "Error searching for %s in %s" % \
                    (actual_class_name, unique_classes_name_set)
        
        return numerical_classes_set        
            
    def get_unique_classes(self, classes_names):
        """ Receives the complete set of names for all the stars and
            return a list that contains each class name just once.
        
        """
        
        # Set that will contain the names of the classese just once.
        unique_classes_names = []
        
        # For all the classes names.
        for c in classes_names:
            try:
                # Check if the class name is already in the set of
                # unique class names.
                unique_classes_names.index(c)
            except ValueError:
                # It is not in the set, so add to it.
                unique_classes_names.append(c)
        
        return unique_classes_names
    
    def generate_confusion_matrix(self, eval_set_class_names, 
                                  classes_prediction,unique_classes_name_set,
                                  total_instances, perc_pred_success):
        """ Generate the confusion matrix with the results of the prediction.
        
        """
        
        header_row = ['']
        header_row.extend(unique_classes_name_set)
        classes_rows = []  
        
        number_of_classes_evaluated = len(unique_classes_name_set)
        
        # Initiate rows of data.
        for n in range(number_of_classes_evaluated):
            new_row = []
            new_row.append(unique_classes_name_set[n])
            new_row.extend([0] * number_of_classes_evaluated) 
            classes_rows.append(new_row) 
    
        # Count each prediction in each cell of the confusion matrix. 
        for i in range(len(eval_set_class_names)):
            index_class_evaluated = \
                unique_classes_name_set.index(eval_set_class_names[i])
                
            prediction = classes_prediction[i]
            index_class_predicted = int(prediction[0])
    
            row = classes_rows[index_class_predicted]
            
            # First column is the name of the class, the index must be incremented.
            row[index_class_evaluated + 1] += 1
    
        # Print confusion matrix to standard output.
#        print header_row
#            
#        print total_instances
#        print perc_pred_success 
          
        # Write the confusion matrix to a CSV file.
        with open(self.__outfilename, 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"')
            writer.writerow(header_row)      
                
            for r in classes_rows:
                writer.writerow(r)
            
            writer.writerow(total_instances)
            writer.writerow(perc_pred_success)          
        
    def evaluate_prediction(self, clf, evaluation_set, eval_set_class_names, unique_classes_name_set):
        """ Applies the classifier to the evaluation set, getting the class
            prediction for each instance of the evalution set.
        
        """
        
        eval_instances_by_class = [0] * len(unique_classes_name_set)
        prediction_results = [0] * len(unique_classes_name_set)
        
        # To save predictions for each instance.
        predicted_classes = []
        
        # For each instance in the evaluation set. 
        for i in range(len(eval_set_class_names)):
            # Predict class for current instance.
            predicted_class = clf.predict(evaluation_set[i])
            # Save prediction.
            predicted_classes.append(predicted_class) 
             
            # Index for the class predicted. First element of the list.
            predicted_class_index = int(predicted_class[0])     
            # Get name for the class predicted.        
            class_predicted_name = unique_classes_name_set[predicted_class_index]  
            
            # Get actual class name for current instance.
            actual_class_name = eval_set_class_names[i]          
            # Get index for the actual class.
            actual_class_index = unique_classes_name_set.index(actual_class_name)
            # Count this instance in the appropriate class.
            eval_instances_by_class[actual_class_index] += 1    
            
            # Count the prediction if successful.    
            if actual_class_name == class_predicted_name:
                prediction_results[predicted_class_index] += 1
            
        total_prediction_ok = 0
        total_instances_eval = 0   
        
        total_instances = ["TOT"]
        perc_pred_success = ["(CC)"]
            
        # Print results.    
        for i in range(len(unique_classes_name_set)):
            
            predict_success = 0.0
            
            if eval_instances_by_class[i] <> 0:
                predict_success = (prediction_results[i] * 100) / eval_instances_by_class[i]
                # Add prediction for this class to total.
                total_prediction_ok += prediction_results[i]
                total_instances_eval += eval_instances_by_class[i]
                
            total_instances.append(eval_instances_by_class[i])
            perc_pred_success.append("%2.f" % predict_success)
        
        self.generate_confusion_matrix(eval_set_class_names, predicted_classes, unique_classes_name_set, total_instances, perc_pred_success)     

    def open_csv_file(self):
        """ Read a CSV file and save the data as metadata and data rows.
        
        """
                
        # Read csv file.
        with open(self.__filename, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            try:
                n = 0
                for row in reader:
                    # First row is metadata, save it as metadata.
                    if n == 0:
                        self.__meta.process_meta(row)
                    # Second row is column information, save it as column info.
                    elif n == 1:
                        self.__meta.process_cols(row)
                    # Rest of rows is data, save.
                    else:
                        self.__ds.add_row(row)
                                    
                    n += 1
            except csv.Error as p:
                sys.exit('file %s, line %d: %s' % (self.__filename, reader.line_num, p))      
            
    def classify(self):   
        """ Classify data of the CSV file.
         
        """   
        
        # Open CSV file.
        self.open_csv_file()
                 
        # Set the training options.
        tdata = csvdata.TrainingData(self.__stars_set_min_cardinal, 
                                  self.__training_set_percent, 
                                  self.__ds, 
                                  self.__meta)
        
        # Get evaluation set, set of parameters and set of classes name.
        training_set = []
        classnames_training_set = []
        
        param_range = self.__meta.get_range_of_params()
        
        for n in range(tdata.get_number_of_classes()):
            num_of_instances, actual_class_name, indexes_range, training_indexes = \
                tdata.get_training_data(n)
                
            if len(training_indexes) > 0:
                self.get_rows_only_with_params(self.__ds, param_range, training_indexes, \
                                          training_set, actual_class_name, classnames_training_set)
        
        # Get evaluation set, set of parameters and set of classes name.
        evaluation_set = []
        eval_set_class_names = []
        
        classes, evaluation_indexes = tdata.get_evaluation_instances()
        
        for n in range(len(classes)):
            self.get_rows_only_with_params(self.__ds, param_range, evaluation_indexes[n], \
                                      evaluation_set, classes[n], eval_set_class_names)
    
        # Get lists to show resume of results.
        unique_classes_name_set = self.get_unique_classes(classnames_training_set)
    
        numerical_classes_set = self.get_numerical_classes_set(classnames_training_set, unique_classes_name_set)
    
        # Classify.
        clf = RandomForestClassifier(self.__number_of_trees)
        clf = clf.fit(training_set, numerical_classes_set)
        
        self.evaluate_prediction(clf, evaluation_set, eval_set_class_names, unique_classes_name_set)    
    