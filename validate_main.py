#!/usr/bin/python
import xml.etree.ElementTree as ET
import os, sys
import shutil
import validate_tests as vt

vt.init()
validate_log = open("validate.log", "w")
validate_log.write("log Opened for writing\n")
""" kickoff
    the main function of this file.
	Uses parameters passed from validate_setup
	and assigns values to global vars while
	opening and parsing the gateway setup xml file.
	
"""
def kickoff(sectionToTest, inputtedTest, setupFile, testPerNode):
        global gatewaysetup, testToUse
        testToUse = inputtedTest
        gatewaysetup = ET.parse(setupFile)
        parser(sectionToTest, testPerNode)
        print "Test complete."
        sys.exit()

""" parser        
    Traversal of a Section's groups and individual nodes.
    Uses XPath and numeric count for iteration through the tree.
    Goes item through item based off order from the gateway setup.
"""        
def parser(sectionType, testPerNode):
        SectionTree = gatewaysetup.find("./" +  vt.tag_values[sectionType][0])
        path = "/gateway/" + sectionType
        #print "path: " + path 
        if vt.tag_values[sectionType][1] & testPerNode:
            print "Performing test via generic traverseSection iterator"
            traverseSection(SectionTree, path, sectionType)
        else:
            print "Performing test without generic iterator"
            runTestOnNode(SectionTree, path)
        return

""" traverseSection        
    Traversal of a Section's groups and individual nodes.
    Uses XPath and numeric count for iteration through the tree.
    Goes item through item based off order from the gateway setup.
"""
def traverseSection(SectionTree, path, sectionType):
        itemID=1
        GroupID=1
        #print "On path: " + path
        for node in SectionTree:
            #print "node tag is : " + node.tag
            if node.tag == sectionType + "Group":
                print ("traverseSection - " + node.tag + 
				    " on " + sectionType +
				    " Group #" + str(GroupID))
                nodePath = ('%s/%s[%i]' % (path, node.tag, GroupID))
                runTestOnNode(node, nodePath)
                traverseSection(node, nodePath, sectionType)
                GroupID+=1
            elif node.tag == sectionType:
                print ("traverseSection - " + node.tag +
				    " on " + sectionType +
				    " #" + str(itemID))
                nodePath = ('%s/%s[%i]' % (path, node.tag, itemID))
                runTestOnNode(node, nodePath)
                itemID+=1
        return

""" runTestOnNode
	Runs the globally define test function(s) on the current node.
	Test functions are ; delimited and a check is made to ensure
	the functions are callable.
"""		
def runTestOnNode(node, nodePath):
    if callable(vt.test_dict[testToUse]):
        vt.test_dict[testToUse](node, nodePath)
    else:
        print "No test called " + testToUse + " located."
        print "How did this get through so far in the script??"
    return
""" testCheck
	Debug function that outputs all available test functions.
"""    
def testCheck():
    for x in vt.test_dict:
        print x
        #print ( callable(vt.test_dict[x]))

""" startValidation
    Original start function, which would use a cache and environment variable
	system for loading the gateway setup file. Currently unused.
"""
def startValidation():
        global xmldoc
        print "<validation>\n\t<issues>"
        #test if os environment variable for _SETUP is set.
        try:
                writeLog("trying to read environment Variable.")
                temp = os.environ['_SETUP']
                writeLog("value of os environment variable is " + temp)
        except:
                #environment variable doesn't exist.
                writeLog("using cached xmlFile for testing.")
                xmldoc = ET.parse("/export/home/dsobiepan/scripts/py/0.xml")
                writeLog("File found and parsed sucessfully...")
        else:
                writeLog("using file from Gateway." )
                xmldoc = ET.parse(os.environ['_SETUP'])

                #check the sourcefile.
                sourceFile = os.environ['_SETUP']
                writeLog("The xml file used for parsing is " + sourceFile)
                #a local file has been kept.
                shutil.copyfile(sourceFile, "./xmlToValidateAgainst.xml")

#function called at end, for any cleanup, etc.
def endValidation():
        print "\t</issues>\n</validation>"

""" runTests
    function that runs a series of tests on the xml. 
    Custom tests can be defined and should be put in here.
"""
def runTests():
        #@TODO - this should really be fed a list of 
		#functions of tests to run on all MEs and/or ME Folders.
        #Or maybe it should be kept specific to 
		#Attribute testing the way it is, as that makes sense on MEFolders && MEs.
        writeLog("made it into runTests")
        mainManagedEntitiesSection = xmldoc.find("./managedEntities")
        path = "/gateway/managedEntities"
        checkMENodeAttrs(mainManagedEntitiesSection, path)
        writeLog("completed Running tests")
