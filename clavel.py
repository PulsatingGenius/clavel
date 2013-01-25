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
This module predicts the type of variability for stars.
The variability is predicted from the light curves of the stars. This
program calculates several features from these light curves that are
processed by means of machine learning techniques. 
The stars are retrieved from a database generated by LEMON 
(https://github.com/vterron/lemon/). 

"""

import sys
import logging
import csv
import csvdata
import classifargs
import modelserial
import starclasses
import starfeatures
import trainevalsets
import evaluation
from sklearn.ensemble import RandomForestClassifier

def init_log(classifarg):
    """ Initializes the log for the application. """
    
    # Initially this software is intended to be used in unix systems.
    log_file = '/dev/null'
    
    if classifarg.log_file_provided:
        log_file = classifarg.log_file_name
    
    logging.basicConfig(filename=log_file, format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)
    
def error_exit(msg): 
    """ Print a message to log and exists with the same message. """
    
    logging.error(msg)
    sys.exit(msg)

def train_for_evaluation(classifarg, star_classes, tr_ev_sets, nfilter):
    """ Performs the training with the set of features and classes received. """
    
    # Get the indexes of the training instances and 
    # the corresponding classes identifier.
    training_indexes, training_classes = tr_ev_sets.training_indexes()
    
    # Creates the training set of features from the set of all the features and
    # the set of indexes to use for training.
    features_of_training_set = []
    
    features = star_classes.get_filter_features(nfilter)
     
    for i in training_indexes:
        try:                        
            features_of_training_set.append(features[i])
        except IndexError:
            error_exit('Error collecting the set of features for training.')
            
    # The classification model.
    clf = None
    
    # The model has not been read from file, so generate the classifier.
    if clf == None:  
        filter_name = star_classes.filter_name(nfilter)        
        
        logging.info('Creating Random Forest classifier for filter %s.' % filter_name)      
        clf = RandomForestClassifier(classifarg.number_of_trees)
        
        # Train the classifier using the training set and 
        # the numerical identifiers for the classes.
        clf = clf.fit(features_of_training_set, training_classes)
        
        # If a model file has been provided, write the model generated to file.
        if classifarg.model_file_provided():  
            cm = modelserial.ClassifModel()                            
            cm.save_model(clf, classifarg.model_file_name, filter_name) 
                
    return clf

def predict_for_evaluation(clf, evaluation_indexes, features):
    """ Performs the prediction with the set of features and classes received. 
        Returns the numeric identifiers of each predicted class.
    
    """      
    
    # To save the predictions for each instance.
    predicted_classes = []
    
    # For each instance in the evaluation set. 
    for index in evaluation_indexes:
        # Predict class for current instance.
        predicted_class = clf.predict(features[index])
        # Save prediction.
        predicted_classes.append(predicted_class[0])
        
    return predicted_classes
        
def retrieve_stars_features(classifarg):
    """ Read the stars information and loads it into the structures used.
        The information is read from the source indicated by the program
        arguments.
    
    """
    
    logging.info('Getting stars features.')
    
    # Get the stars whose classes are known.
    star_classes = starclasses.StarClasses()  
    
    if classifarg.stars_id_file_provided:
        star_classes.retrieve_stars_classes_from_file(classifarg.stars_id_file_name)
    elif classifarg.database_file_provided:
        star_classes.retrieve_stars_classes_from_database(classifarg.database_file_name)
    elif classifarg.features_file_provided:
        star_classes.retrieve_stars_classes_from_features_file(classifarg.features_file_name)               
    else:
        error_exit("It hasn't been specified an origin for the stars identification.")
    
    # Calculate the features of the stars whose identifiers are
    # indicated and return all the features in a data structure.
    # It is done at first to detect any problem with data reading or
    # feature calculations, so the star can be discarded.
    stars_features = starfeatures.StarsFeatures(star_classes)
    stars_features.retrieve_features(classifarg)
    
    return star_classes

def evaluate_classifier(classifarg):
    """ Performs the training for a set of stars and the prediction of the class 
        for another set of stars in order to evaluate the success of the
        classification performed. 
        
    """       
    
    logging.info('Reading stars information.')
    
    # Read stars information. 
    star_classes = retrieve_stars_features(classifarg)    
    
    # Calculates the training and evaluation sets.
    tr_ev_sets = trainevalsets.TrainEvalSet(classifarg, star_classes)    
    tr_ev_sets.calculate_training_and_evaluation_sets()

    # Train and evaluate for all the filters.
    for nfilter in range(star_classes.number_of_filters):
        # Perform training
        clf = train_for_evaluation(classifarg, star_classes, tr_ev_sets, nfilter)
        
        evaluation_indexes, evaluation_classes = tr_ev_sets.evaluation_indexes()
        
        # Predict.
        predicted_classes = predict_for_evaluation(clf, evaluation_indexes, 
                                    star_classes.get_filter_features(nfilter)) 
        
        # Evaluate prediction.
        evaluat = evaluation.Evaluation(predicted_classes, 
                                        evaluation_classes,
                                        star_classes,
                                        star_classes.filter_name(nfilter))
        
        evaluat.generate_confusion_matrix()   

def only_training(classifarg):
    """ Performs only training with the data received.
        Read the star list to use for training and generates 
        the classification model. 
     
    """
    
    if classifarg.model_file_provided():
        logging.info('Reading stars information.')
        
        # Read stars information. 
        star_classes = retrieve_stars_features(classifarg)        
        
        # Establish the training set.
        tr_ev_sets = trainevalsets.TrainEvalSet(classifarg, star_classes)
        tr_ev_sets.set_all_stars_for_training()
        
        # Train for all the filters.
        for nfilter in range(star_classes.number_of_filters):
            train_for_evaluation(classifarg, star_classes, tr_ev_sets, nfilter)
    else:
        error_exit('For training a file name to save the model must be provided.')
        
        
def write_prediction_to_file(afilter, star_classes, predicted_classes, classifarg):
    """ Writes to a file the prediction of a given filter. """        
    
    prediction_file_name = classifarg.prediction_file + '_' + afilter + csvdata.CsvUtil.FILE_EXT   
    
    with open(prediction_file_name, 'wb') as csvfile:
        logging.info("Writing prediction for filter %s to file: %s" % (afilter, prediction_file_name))
                
        csv_file = csv.writer(csvfile, delimiter=',', quotechar='"')  
        
        # Write header.
        row = [csvdata.CsvUtil.ID, csvdata.CsvUtil.PREDICTION]
        csv_file.writerow(row)
        
        # Write rows.
        stars_identifiers = star_classes.stars_identifiers
                
        for star_id, predict in zip(stars_identifiers, predicted_classes):
            
            row = [star_id, star_classes.class_name(int(predict))] 
            csv_file.writerow(row)      
     
def predict_stars_classes(clf, filters_names, star_classes, classifarg):
    """  Predict star classes using the model and the stars received. """    
    
    for classifier, afilter in zip(clf, filters_names):
        logging.info('Predicting class for stars using filter %s', afilter)
        
        features = star_classes.get_features_by_filter_name(afilter)
        
        # Predict class for current instance.
        predicted_classes = classifier.predict(features)
        
        write_prediction_to_file(afilter, star_classes, predicted_classes, classifarg)  
        
        # Write confusion matrix.
        evaluat = evaluation.Evaluation(predicted_classes,
                                        range(len(star_classes.unique_classes_names)), 
                                        star_classes,
                                        afilter)
        
        evaluat.generate_confusion_matrix()
        
def only_prediction(classifarg):
    """ Performs only the prediction of the class for a set of stars.
        To accomplish this task the stars and the classifier model must be read.
        
    """

    # If a model file has been provided, read it from file.
    if classifarg.model_file_provided():        
        # Try to read the model file, it couldn't exist.
        cm = modelserial.ClassifModel()            
        
        clf, filters_names = cm.read_model(classifarg.model_file_name)  
        
        if clf <> None:
            # Retrieve the information of stars to predict.
            star_classes = retrieve_stars_features(classifarg)
            
            predict_stars_classes(clf, filters_names, star_classes, classifarg)
        else:
            error_exit("The classification model can't be read, prediction cann't be done.")          
    else:
        error_exit("A file with a classification model hasn't been provided, prediction cann't be done.")

def main(): 
    """ Main function. Process program arguments and determine if the stars
    to process are going to be retrieved from a LEMON database or any other
    source. The only argument necessary is the first one, related to the
    name of the file. """
    
    # Create object to process program arguments.
    ca = classifargs.ClassifierArguments()
    
    # Process program arguments.
    ca.parse()     
    
    init_log(ca)
    
    logging.info('----- Clavel started ---------------------------------------')
    
    # Check that all the program arguments received are coherent.
    if ca.check_arguments_set():
    
        # Performs the action indicated by the programs arguments.
        if ca.is_training:
            logging.info("Let's go training!")        
            only_training(ca)
                           
        elif ca.is_prediction:
            logging.info("Let's go prediction!")
            only_prediction(ca)        
            
        elif ca.is_evaluation:
            logging.info("Let's go evaluation!")        
            evaluate_classifier(ca)   

        logging.info('Clavel finished.')      
        
    else:
        error_exit("Program arguments aren't valid")      

# Run 'main' function as __main__.
if __name__ == "__main__":
    main()