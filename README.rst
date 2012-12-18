CLAVEL
======

CLAVEL is a python module for LEMON (http://github/vterron/lemon/),
to allow the classification of variable stars.

CLAVEL is distributed with an example that uses data from 
'Supervised classification of variable stars (Debosscher+, 2007)' 
that is available at 
(http://vizier.cfa.harvard.edu/viz-bin/VizieR?-source=J/A+A/475/1159), 
to show an example of classification.

MODULES
=======

* clavel.py - Entry point.
* classifargs.py - Process and store the program arguments that
* lsproperties.py - Stores the parameters to use when calculating the periodgram. 
* nonperiodicfeature.py - Calculates the non periodic features of stars.
* periodicfeature.py - Calculates the periodic features of stars.
* starfeatures.py - Calculates and store the features of stars.
* trainevalsets.py - Selects the subsets of stars used for training and evaluation.
* lombscargle.py - Calculates the periodgram using the Lomb Scargle method.
* starclasses.py - Stores the type and/or features calculated for each star.

INSTALLATION
============

CLAVEL requires Python 2.7.3, numpy, scipy 0.10 o newer, matplotlib 
and scikit-learn (http://scikit-learn.org/stable/).

BASIC USE
=========

This software could be executed using clavel.py. There is help available typing: 
clavel.py -h

Clavel has three function modes that could be selected by means of program arguments,
these modes are: training, prediction and evaluation.

* Training - This mode generates a model to classify stars, 
it uses a collection of stars. The data from stars is retrieved from a LEMON database, 
and the information about the types of the stars is retrieved from a CSV file.
* Prediction - This mode predicts the types for a set of stars using a model created 
previously from a set of stars. 
* Evaluation - This mode evaluates the success of the classifier on a set of stars
whose variability type is known. From this set, the program selects a subset of stars 
for training and a subset of stars for evaluation. The model generated with training is
used to predict the type of the stars of the evaluation set. The comparison between the
predicted type for each star and its actual type allows the evaluation of the classifier. 
