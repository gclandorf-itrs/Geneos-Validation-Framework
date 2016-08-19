#!/usr/bin/python
import xml.etree.ElementTree as ET
import os, sys
import shutil
import validation_tests

validation_tests.init()
validate_log = open("validate.log", "w")
validate_log.write("log Opened for writing\n")

tag_values = {
    'include': ("includes", 1),
    'probe': ("probes", 1),
    'managedEntity': ("managedEntities", 1), 
    'type': ("types", 1),
    'sampler': ("samplers", 1),
    'samplerInclude': ("samplerIncludes", 1),
    'action': ("actions", 1),
    'effect': ("effects", 1),
    'command': ("commands", 1),
    'scheduledCommand': ("scheduledCommands", 1), #no groups, fits name schm
    'rule': ("rules", 1), 
    'alert': ("alerting", 0),
    'activeTime': ("activeTimes", 1),
    'timeSeries': ("dataSets", 1),
    'hotStandby': ("hotStandby", 0),
    'databaseLogging': ("databaseLogging", 0),
    'tickerEventLogger': ("tickerEventLogger", 0),
    'authentication': ("authentication", 0),
    'environment': ("environments", 1),
    'auditOutput': ("auditOutputs", 1), #no groups but has plural/nonplurals
    'knowledgeBase': ("knowledgeBase", 0),
    'persistence': ("persistence", 0),
    'staticVariables': ("staticVars", 0),
    'expressReport': ("expressReports", 0),
    'selfAnnouncingProbe': ("selfAnnouncingProbes", 0),
    'exportedData': ("exportedData", 0),
    'importedData': ("importedData", 0),
    'publishing': ("publishing", 0),
    'operatingEnvironment': ("operatingEnvironment", 0),
    }

	
def main():
        global gatewaysetup, testsToUse
        #gwfile = "/export/home/dsobiepan/opt/gateway/"
        #gwfile = gwfile + "gateways/david_test_gw/gateway.setup.xml"
        gwfile = "gateway.setup01.xml"
        gatewaysetup = ET.parse(gwfile)
        sectionToTest = "managedEntity";
        testsToUse = "processME";
        testCheck()
        parser(sectionToTest)
        return 0

""" parser        
    Traversal of a Section's groups and individual nodes.
    Uses XPath and numeric count for iteration through the tree.
    Goes item through item based off order from the gateway setup.
"""        
def parser(sectionType):
        SectionTree = gatewaysetup.find("./" +  tag_values[sectionType][0])
        path = "/gateway/" + sectionType
        #print "path: " + path 
        if tag_values[sectionType][1]:
            print "Value is tag_values[sectionType][1], going to traverse"
            traverseSection(SectionTree, path, sectionType)
        else :
            print "Not a group based section."
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
    #print "This is where tests go"
    tests = testsToUse.split(";");
    for test in tests:
        if callable(validation_tests.test_dict[test]):
            validation_tests.test_dict[test](node, nodePath);
        else:
           print "No test called " + test + " located."
    return
""" testCheck
	Debug function that outputs all available test functions.
"""    
def testCheck():
    for x in validation_tests.test_dict:
        print x
        print ( callable(validation_tests.test_dict[x]))

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

if __name__ == '__main__':
        status = main()

        sys.exit(status)
