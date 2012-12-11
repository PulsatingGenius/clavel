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

import classifargs
import classifycsv
from sklearn.ensemble import RandomForestClassifier   

if __name__ == "__main__":
    
    # Process program arguments
    args = classifargs.ClassifierArguments()
    
    args.process_program_args()
    
    # Print program arguments.
    print "Input CSV file: %s" % args.filename
    print "Classification Parameters:"
    print "-Minimum number of instances in class to be classified: %d" % args.stars_set_min_cardinal
    print "-Percentage of instances to be used for training: %d%%" % args.training_set_percent    
    print "-Number of decision trees used to classify: %d" % args.number_of_trees
    
    # Read CSV file with data.
    classif_csv = classifycsv.ClassifyCSV(args.filename, args.stars_set_min_cardinal, 
                             args.training_set_percent, args.number_of_trees)    
    
    # Classify CSV data.
    classif_csv.classify() 
    