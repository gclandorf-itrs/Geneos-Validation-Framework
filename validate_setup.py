#!/usr/bin/python

#validate-setup
# ./validate-setup.py testSection testToUse setupFile [testPerNode]
import sys
import os
import validate_tests as vt
import validate_main as vm

def listSections():
    print("The list of section names for testing are:")
    for section in vt.tag_values:
	    print "%s\t" % section

def helpStatement():
    print("Error with script arguments. Expected arguments are:")
    print("[1]:Section To Test\n" +
        "[2]:Test Name \n[3]:Gateway Setup File \n" +
        "[4]: Run Test Per Node (Optional)")
    print("Ex: ./validate-setup.py managedEntity " +
        "attributesOnME ../stuff/gateway.setup.xml True")


testSection = ''
testToUse = ''
setupFile = '/export/home/dsobiepan/opt/gateway/gateways/david_test_gw/gateway.setup.xml'
testPerNode = False
    
numArgs = len(sys.argv)
if(numArgs < 4):
    helpStatement()
    sys.exit()

#print str(sys.argv[1])
if(not str(sys.argv[1]) in vt.tag_values):
    print "Not a valid test Section."
    listSections()
    sys.exit()
testSection = str(sys.argv[1])
if(not str(sys.argv[2]) in vt.test_dict):
    print "Not an existing test. Was it added to validate_tests?"
    print "The full list of current tests include:"
    vm.testCheck()
    sys.exit()
testToUse = str(sys.argv[2])
if(not os.path.exists(str(sys.argv[3]))):
    print "Cannot find gateway setup file at %s" % str(sys.argv[3])
    sys.exit()
setupFile = str(sys.argv[3])
if(sys.argv[4]):
    if str(sys.argv[4]).lower() == 'true':
        print "Note: Using the node base iterator for tests."
        testPerNode = True
vm.kickoff(testSection, testToUse, setupFile, testPerNode)
#vm.main()

		