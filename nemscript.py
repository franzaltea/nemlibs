#!/usr/bin/env python
# Started 2017/07/05
# Written by Franz Russel Altea
from __future__ import print_function
import time
import sys
import os
import re
import tempfile
# syslog can be used if using unix OS - can add syslog to every logging method
# import syslog


class NemScript:
    """Base class for handling scripts
    """

    __name__ = 'Unnamed job'

    status = {
        'success': "Success",
        'failed': "Failed",
        'dataerror' : "Dataerror",
        'nodata' : "No Data",
        }

    no_data = False

    def __init__(self, jobname=None, create_txt=False, file_loc=''):
        """
        @param jobname: Name of the subclass using NemScript.
        @param create_txt: set to true to save the script result in text file
        @param file_loc: directory where txt file will be saved in
        """
        if jobname:
            self.__name__ = jobname
        self.create_txt = create_txt
        self.file_loc = file_loc
        self.ret = None

    def __str__(self):
        return self.__name__

    def __call__(self, *args):
        """Interface to the job class. This should be called by calling the
        instance of the class."""

        # mark the start of the run
        start_time = time.time()

        # This changes the stdout to a temp file which is eventually
        # written into a txt file. Done this way to make it easy to change how
        # the results are stored. Also makes it easier to seperate the error
        # stderr will contain the failures and stdout will contain everything
        # else
        
        # The current contents are flushed
        sys.stdout.flush()
        sys.stderr.flush()

        # The old file handle is duplicated so it can be restored later on
        oldstdout = os.dup(sys.stdout.fileno())
        oldstderr = os.dup(sys.stderr.fileno())

        # The new tempfile that we are writing to
        stdout = tempfile.TemporaryFile(mode='w+')
        stderr = tempfile.TemporaryFile(mode='w+')

        # This duplicates the file descriptor to the default stdout and
        # default stderr
        os.dup2(stdout.fileno(), 1)
        os.dup2(stderr.fileno(), 2)

        do_exit = False
        try:
            self.run(*args)
        except SystemExit as e:
            # defer the exit until this function is done
            do_exit = True
            self.ret = e
        except:
            import traceback
            s = 'Unhandled exception:\n'
            s += traceback.format_exc()
            self.failure(s)

        end_time = time.time()

        # restore sys.stdout and sys.stderr.
        sys.stdout.flush()
        sys.stderr.flush()
        os.dup2(oldstdout, 1)
        os.dup2(oldstderr, 2)
        os.close(oldstdout)
        os.close(oldstderr)

        # new read stdout and stderr
        stdout.seek(0)
        stderr.seek(0)
        result = stdout.read().strip()
        errors = stderr.read().strip()
        del stdout, stderr

        ere = re.compile('^[ \t]*ERROR.+$', re.MULTILINE)
        errs = re.findall(ere, result)

        ere = re.compile('^[ \t]*WARNING.+$', re.MULTILINE)
        warns = re.findall(ere, result)

        if self.create_txt:
            self.__update_status(start_time, end_time, result, errors, errs, warns)

        if do_exit:
            sys.exit(self.ret)

        return self.ret

    def __update_status(self, start_time, end_time, result=None, errors=None,
                        errs=None, warns=None):
        """Insert information about the job into the text file"""
        # DEBUG - note for future update add a create_txt argument and
        # add different ways of storing the results

        errtext = errors + '\n'.join(errs)
        warntext = '\n'.join(warns)
        if errtext and warntext:
            errtext += '\n'
        errtext += warntext

        # Set status based on errors and whether we have data.
        if len(errors) > 0:
            status = self.status['failed']
        elif len(errs) > 0:
            status = self.status['dataerror']
        elif self.no_data:
            status = self.status['nodata']
        else:
            status = self.status['success']

        # Opens/Creates the file to save to
        # Truncate removes the contents of the file if any
        loc_time_now = time.strftime('%Y_%m_%d_%H_%M_%S')
        file_name = self.file_loc + '{0}_{1}.txt'.format(self.__name__, loc_time_now)
        fd = os.open(file_name, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)

        os.write(fd, 'Status: {0}\n'.format(status))
        os.write(fd, 'Results\n\n')
        os.write(fd, result)
        os.write(fd, '\nTotal running time: {0}\n'.format(round(end_time - start_time, 3)))
        os.write(fd, '\nErrors\n\n')
        os.write(fd, errtext)

        # Close opened file
        os.close(fd)

    def run(self, *args):
        """Do whatever the script does. This is meant to be subclassed
        to do whatever is needed to run the script"""
        self.failure("Job uses default run() method")

    def failure(self, string):
        "Called to indicate a program error"

        print(string, file=sys.stderr)
        print("FAILURE:" + string, file=sys.stdout)
        self.ret = 1

    def error(self, string, new_line=True, spaces=0):
        """Called to indicate a data error requiring immediate resolution."""

        new_line = new_line and "\n" or ""
        space = " " * spaces
        print(string, file=sys.stderr)
        print(new_line + "{0}ERROR:".format(space) + string, file=sys.stdout)
        self.ret = 1

    def warning(self, string, new_line=True, spaces=0):
        """Called to indicate a data error requiring investigation."""

        new_line = new_line and "\n" or ""
        space = " " * spaces
        print(new_line + "{0}WARNING:".format(space) + string, file=sys.stdout)

    def log(self, string, new_line=True, spaces=0):
        """Called to print provided message."""

        new_line = new_line and "\n" or ""
        spaces = " " * spaces
        print(new_line + spaces + string, file=sys.stdout)

    def info(self, string, new_line=True, spaces=0):
        """Called to provide additional notification about the process."""

        new_line = new_line and "\n" or ""
        spaces = " " * spaces
        print(new_line + "{0}INFO:".format(spaces) + string, file=sys.stdout)
