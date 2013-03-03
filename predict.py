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
This module predicts the class of variability of a star.
It is intended to be used from a command line indicating the star to predict.

"""

import sys
import database
import lombscargle
import modelserial
import periodicfeature
import nonperiodicfeature
import starfeatures

def predict_stars_class(star_features_in_current_filter, pfilter, clf, filters_names, scn):
    """  Predict star classes using the model and the stars received. """    
    
    #print "Predicting for filter %s" % pfilter
    
    for classifier, afilter in zip(clf, filters_names):
        if afilter == pfilter:                        
            try:
                #print "Predict class ..." 
                predicted_class = classifier.predict(star_features_in_current_filter)
                
                #print "Predict probability ..."
                predicted_class_proba = classifier.predict_proba(star_features_in_current_filter)
                
                #print "Prediction: %s" % predicted_class
                
                class_name = scn.class_name(int(predicted_class[0]))
            
                prob = float(predicted_class_proba[0][0]) * 100
            
                print "The predicted class in filter '%s' is '%s' with probability %2.f%%" % (pfilter, class_name, prob)
            except IndexError:
                print "ERROR: The predicted class is out of index."
                
            except Exception as e:
                print "ERROR: %s" % e
            break

def predict_star(database_filename, starsclasses_filename, model_name, star_id):
    """ Predict the class of a star. """       
    
    #print 'Opening LEMON db %s for star %s.' % (database_filename, star_id)
    
    # Create database in LEMON format.
    db = database.LEMONdB(database_filename)
    
    # Retrieve the information of filters created.
    filters = db.pfilters   
    #print "Predicting star '%s' for filters %s" % (star_id, filters)        
    
    #print "Reading star classes."
    scn = modelserial.StarClassNames()
    # Read star classes.
    scn.read()
    
    #print "Reading model."            
    cm = modelserial.ClassifModel()            
    # Read classifier model.
    clf, filters_names = cm.read_model(model_name) 
    
    #print "Read model for filters %s" % filters_names
    
    if clf <> None and len(clf) > 0:                
    
        #print 'Ready to read stars from a LEMON db for filters %s.' % str(filters)     
        
        # Properties for the Lomb Scargle method.
        lsprop = lombscargle.LSProperties()  
        ls = lombscargle.LombScargle(lsprop)
                
        # For all the filters of current star.
        for filter_index in range(len(filters)):
            # Get the filter.
            pfilter = filters[filter_index]
    
            curve = db.get_light_curve(int(star_id), pfilter)
            # Get the object that will calculate the periodgram of the curve
            # (not normalized).
            try:
                print "Calculating features."
                # Calculate and plot the periodgram.
                pgram, nmags, ntimes = ls.calculate_periodgram(pfilter, curve)
                
                # Calculate periodic features of stars.
                perfeat = periodicfeature.PeriodicFeature(pgram, lsprop)
    
                # Calculate no periodic features of stars.
                noperfeat = nonperiodicfeature.NonPeriodicFeature(nmags, ntimes)
    
                # Store all the features of this star in a list.
                star_features_in_current_filter, features_names = \
                    starfeatures.StarsFeatures.save_feature(perfeat, noperfeat)  
                
                predict_stars_class(star_features_in_current_filter, str(pfilter), clf, filters_names, scn)          
    
            except TypeError:
                print "Error reading from DB star with identifier %s for filter %s" % (star_id, str(pfilter))
    else:
        print "ERROR: No classifier has been read."
                 
    #print 'Finished the prediction of star %s.' % star_id
    
def predict():
    
    if len(sys.argv) < 5:
        print "Not enough arguments have been provided -> %s database-file star-classes-file model star-id" % sys.argv[0]
    else:    
        predict_star(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])       

if __name__ == "__main__":
    predict()