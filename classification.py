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
This module contains a class that receives a star from a LEMON database
and performs the prediction of the variability class of that star.

"""

import lombscargle
import periodicfeature
import nonperiodicfeature
import modelserial
from starfeatures import StarsFeatures

class Classifier(object):
    
    def __init__(self, models_files_, filters_names_, classes_names_):
        """ Stores the arguments received. """
        
        self.__models_files = models_files_
    
        self.__filters_names = filters_names_
        
        self.__classes_names = classes_names_
    
    def predict(self, star, clf_model):
        """ This function receives a star and a classifier model the
            prediction of the variability class of the star.
            
        """
                    
        # Properties for the Lomb Scargle method.
        lsprop = lombscargle.LSProperties()   
        ls = lombscargle.LombScargle(lsprop) 
        
        unix_times = []
        mags = []
        
        # Get all the measurements of the star ligth curve.
        for i in range(star.__len__):
            unix_times.append(star.time(i))
            mags.append(star.amg(i))
        
        # Calculate the periodgram.
        pgram, nmags, ntimes = ls.calculate_periodgram_from_curve(unix_times, mags)
        # Calculate periodic features of stars.
        perfeat = periodicfeature.PeriodicFeature(pgram, lsprop)
        # Calculate no periodic features of stars.
        noperfeat = nonperiodicfeature.NonPeriodicFeature(nmags, ntimes)
        
        # Store all the features of this star in a list.
        features, features_names = StarsFeatures.save_feature(perfeat, noperfeat)  
                   
        # Predict class.
        predicted_class = clf_model.predict(features)

        # Class name.
        scm = modelserial.StarClassNames()
        scm.read()     
        
        return scm.class_name(int(predicted_class))   