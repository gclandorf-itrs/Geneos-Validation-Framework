# Geneos-Validation-Framework
A library and framework for Validation Hooks-based Gateway config checking.
Useful for performing standards enforcement and other user defined tests upon various sections.

How It Works

The Framework is split into three sections: 
1) The kickoff script validate_setup.py,
2) the driver script validate_main.py,
3) and then library script, validate_tests.py.

validate_setup

The kickoff script validates arguments
and then calls validate_main with the arguments.

Expected arguments are:
1) [String] Section To Test (ex: managedEntity, sampler, rule)
2) [String] The name of the user test function to run.
3) [String] The path of the gateway setup xml file.
4) [Boolean](Optional) whether to use the generic iterator.
	Should be 'True' to enable. Default is False.

validate_setup's checks will ensure that each parameter to be passed
is valid for validate_main.py. This includes ensuring the section inputted
is existing (compared to a dictionary of all sections), checking that
the test function exists, and ensuring the file exists.

validate_main

The driver script consists of generic functions used for
the traversal of the setup xml and calling the user test functions.
The gateway setup file's xml is parsed, and depending on
the section and the user option, the test function runs.

This iterator treats each section item as a node of a tree
and each section group as a tree head. 
If the test per node flag was assigned to true,
the test function would then run on each item.
Otherwise, the test function will execute on the whole section.

validate_tests

The tests script is the library of functions for validations.
All test functions and their helper functions exist in this file,
as will all global, unchanging variables meant for tests.

Some important variables:

tag_values: a dictionary of all sections used in geneos.
Serves as a lookup for section input check, contains the tag
name of the xml section, and a 1/0 to define whether the section
can be used with the generic iterator.
ex: 'managedEntity': ("managedEntities", 1)

validate_log: log for printing output of tests. 
Calling writeLog(string message) will write to the log.

test_dict: This hashmap contains a key-value pair
of the tests that are available to run.

____________________________________________

How to Add Tests To The Framework

All of the additions one would make would be placed in validate_tests.py
Any needed data (similar to attributeNames) should be defined
after the universal value and before functions.

A comment line is placed after some generic helper functions
for user test functions. A test function suite must have at a 
minimum one "main" function with two parameters:
1) XML ElementTree instance of the XML node the test runs on, and
2) The current path to that node.
Helper functions are welcome. It's suggested to group up test
functions together for ease of reading.

Besides adding functions and variables, the final requirement
is to place a key-value pair into test_dict with the name of
your main test function. 
For ease, use the name of the main function for both the key and value.


