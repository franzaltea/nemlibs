#!/usr/bin/env python
# Started 2017/07/05
# Written By: Nemesis2005
"""
Template for making writing scripts easier
Using nemscript module
"""

##################################################################
# Import Files and initializations
##################################################################
from __future__ import print_function
import getopt
import sys
import time
from nemscript import NemScript
# Or just make a version without syslog then

script_name = 'script_template'

#################################################################
#Functions and classes
#################################################################

def usage():
    print("""
Usage:\n
{0} -b <argument1> -c <argument2> [-d argument3] [--debug]
    -b         some argument (int)
    -c         another argument
    -d         file location for the log (directory only)
    -- debug    run in debug mode. Will not log results and only print it to terminal
    """.format(sys.argv[0]))
    sys.exit(1)
    
class Script_Name(NemScript):

    # Constructor
    def __init__(self, b_arg, file_loc=''):
        NemScript.__init__(self, script_name, create_txt=True, file_loc=file_loc)
        self.b_arg = b_arg

    # Main Script Logic
    def run(self):
        # Measure total time it took to run the script
        start_time = time.time()
        self.log("****** {0} has started. ******".format(script_name))
        self.log("b_arg: {0}".format(self.b_arg))

        # Script logic goes here

        self.log("****** {0} finished. ******".format(script_name))
        self.log("       {0}".format(time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())))
        self.log("       Total Time: {0}".format(round(time.time() - start_time, 2)))

##################################################################
# Main Program
##################################################################
if __name__ == '__main__':
    # Can define variables here
    debug = False
    b_arg = None
    c_arg = None
    d_arg = ''

    
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "b:c:d:", ('debug'))
    except:
        usage()

    for o, a in optlist:
        if o in ('--debug',):
            debug = 1
        elif o == '-b':
            try:
                #Verify the arguments here and pass it to variables
                b_arg = int(a)
            except Exception:
                print("ERROR: Invalid Integer {0}".format(a))
                usage()
        elif o == '-c':
            #Verify the arguments here and pass it to variables
            c_arg = a
        elif o == '-d':
            #Verify the arguments here and pass it to variables
            d_arg = a

    # Check if required arguments are filled
    if not b_arg:
        print("ERROR: b_arg must be provided")
        usage()
        
    # Initialize the script with the required variables
    job = Script_Name(b_arg, file_loc=d_arg)

    # Run the script and if required, add the database
    if debug:
        job.run()
    else:
        job()    
