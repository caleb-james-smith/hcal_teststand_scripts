####################################################################
# Type: SCRIPT                                                     #
#                                                                  #
# Description: Perform n cycles where a cycle is the following:    #
# * Write 00...001 to the Bridge scratch register.                 #
# * Read back the value of the Bridge scratch register.            #
# * Check that they're the same. Report an error if they aren't    #
# * Repeat for 00...010 through 10...000 (32 read-writes total).   #
####################################################################

from hcal_teststand import *
from hcal_teststand.hcal_teststand import *
import sys
from optparse import OptionParser

# CLASSES:
# /CLASSES

# FUNCTIONS:
# /FUNCTIONS

# MAIN:
if __name__ == "__main__":
	# Arguments:
	crate = 1		# Crate number to run the test over
	slot = 2		# Slot number to run the test over
	parser = OptionParser()
	parser.add_option("-n", "--ncycles", dest="ncycles",
		default=1,
		help="The number of cycles you want to run over (default is 1)", metavar="INT")
	parser.add_option("-v", "--verbose", dest="verbose",
		default=False,
		help="Turn on verbose mode (default is off)", metavar="BOOL")
	parser.add_option("-t", "--teststand", dest="ts",
		default="904",
		help="The name of the teststand you want to use (default is 904)", metavar="STR")
	(options, args) = parser.parse_args()
	name = options.ts
	n = int(options.ncycles)
	v = False
	if options.verbose:
		if options.verbose.lower() == "true" or options.verbose  == "1":
			v = True
	
	# Set up:
	ts = teststand(name)		# Initialize a teststand object. This object stores the teststand configuration and has a number of useful methods.
	print ">> Running BER test on teststand {0}.".format(name)
	print ">> Processing {0} cycle(s) ...".format(n)
	
	# Cycle n times:
	n_cycles = 0
	n_errors = 0
	errors = []
	for j in range(n):
		# Do a cycle:
		if v: print "==== Cycle {0} ============================================".format(j + 1)
		for i in range(1, 33):
			# Construct test string:
			b = "0" * (32 - i)
			b += "1"
			b += "0" * (i - 1)
			if v: print "Binary string to write: {0}".format(b)
		
			# Convert test string to hex:
			h_write = "{0:#010x}".format(int(b, 2))
			if v: print "Hex string to write: {0}".format(h_write)
		
			# Write, then read:
			script = [
				"put HF{0}-{1}-B_SCRATCH {2}".format(crate, slot, h_write),
				"get HF{0}-{1}-B_SCRATCH".format(crate, slot)
			]
			output = ngccm.send_commands_parsed(ts.ngccm_port, script)["output"]
			h_read = "{0:#010x}".format(int(output[1]["result"], 16))
			for cmd in output:
				if v: print "<< Command: {0} -> {1}".format(cmd["cmd"], cmd["result"])
			if v: print "Hex string read: {0}".format(h_read)
		
			# Check for error:
			if h_write != h_read:
				n_errors += 1
				errors.append([h_write, h_read])
				if v: print "ERROR: The read value of {0} didn't match the written value of {1}.".format(h_read, h_write)
			
			if v: print ""
		n_cycles += 1
	
	# Print summary:
	print "===== SUMMARY ====="
	print "Total number of cycles: {0}".format(n_cycles)
	print "! Number of mismatch errors: {0}".format(n_errors)
	if n_errors:
		print "! Below is some information about these errors:"
		for i in range(len(errors)):
			print "{0}: string written = {1}, string read = {2}".format(i + 1, errors[i][0], errors[i][1])
# /MAIN