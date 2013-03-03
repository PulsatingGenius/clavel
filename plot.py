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
This module calculates the Lomb Scargle periodgram of a light curve
plotting some graphs of the ligth curve and the periodgram.
It is intended to be used from a command line indicating the star to use.

"""

import sys
import database
import lombscargle

def plot_stars(filename, star_identifiers):
    """ . """       
    
    print 'Opening LEMON db %s for stars %s.' % (filename, star_identifiers)
    
    # Create database in LEMON format.
    db = database.LEMONdB(filename)
    
    # Retrieve the information of filters created.
    filters = db.pfilters                 
    
    print 'Ready to read stars from a LEMON db for filters %s.' % str(filters)     
    
    # Properties for the Lomb Scargle method.
    lsprop = lombscargle.LSProperties()  
    ls = lombscargle.LombScargle(lsprop)
    
    # For all the stars in the database.
    for star_id in star_identifiers:           
        # For all the filters of current star.
        for filter_index in range(len(filters)):
            # Get the filter.
            pfilter = filters[filter_index]

            curve = db.get_light_curve(int(star_id), pfilter)
            # Get the object that will calculate the periodgram of the curve
            # (not normalized).
            try:
                # Calculate and plot the periodgram.
                ls.calculate_periodgram(pfilter, curve, True)

            except TypeError:
                print "Error reading from DB star with identifier %s for filter %s" % (star_id, str(pfilter))
                
            break
                 
    print 'Finished the reading of stars from LEMON db.'

def plot():
    
    if len(sys.argv) < 3:
        print "Not enough arguments have been provided -> %s filename stars" % sys.argv[0]
    else:    
        plot_stars(sys.argv[1], sys.argv[2:])    

if __name__ == "__main__":
    plot()