#!/usr/bin/python
import xml.etree.ElementTree as ET
import os, sys
import shutil

validate_log = open("validate.log", "w")
validate_log.write("log Opened for writing\n")

#The set of attributes to be enforced.
#this can be adjusted as deisred.
attributeNames = ['ENVIRONMENT', 'APPLICATION', 'LOB', 'REGION', 'AIT', 'APPGROUP']

def main():
        writeLog("doing Startup tasks...")
        startValidation()
        writeLog("done with Startup tasks.")

        writeLog("doing runTests.")
        runTests()
        writeLog("done running tests.")

        writeLog("doing wrapup tasks...")
        endValidation()
        writeLog("done with wrapup tasks.")

        return 0     #success

#formats the xml wrapper for an issue.
def issue(s, p, m):
        string = "<issue><severity>" +s+ "</severity><path>" +p+ "</path><message>" +m+ "</message></issue>"
        writeLog(string)
        return string

#function called at start, for any setup, etc.
def startValidation():
        global xmldoc

        print "<validation><issues>"

        #test if os environment variable for _SETUP is set.
        try:
                writeLog("trying to read environment Variable.")
                temp = os.environ['_SETUP']
                writeLog("value of os environment variable is " + temp)
        except:
                #environment variable doesn't exist.
                writeLog("using cached xmlFile for testing.")
                xmldoc = ET.parse("/export/home/gclandorf/geneos/psTemplate/gateway/gateways/gabrielGW64/xmlToValidateAgainst.xml")
                writeLog("File found and parsed sucessfully...")
        else:
                writeLog("using file from Gateway." )
                xmldoc = ET.parse(os.environ['_SETUP'])

                #check the sourcefile.
                sourceFile = os.environ['_SETUP']
                writeLog("The xml file used for parsing is " + sourceFile)
                writeLog("A copy has been stashed in the local file xmlToValidateAgainst.xml")
                #a local file has been kept.
                shutil.copyfile(sourceFile, "./xmlToValidateAgainst.xml")

#function called at end, for any cleanup, etc.
def endValidation():
        print "</issues></validation>"

#function that runs a series of tests on the xml. custom tests can be defined and should be put in here.
def runTests():
        #@TODO - this should really be fed a list of functions of tests to run on all MEs and/or ME Folders.
        #Or maybe it should be kept specific to Attribute testing the way it is, as that makes sense on MEFolders && MEs.
        writeLog("made it into runTests")


        checkManagedEntitiesAttributes()


        writeLog("completed Running tests")

#puts a message in the logfile.
def writeLog(message):
        validate_log.write(message+"\n")

def checkManagedEntitiesAttributes():
        writeLog("made it into processManagedEntities")
        mainManagedEntitiesSection = xmldoc.find("./managedEntities")
        writeLog("foundMainSection")

        path= "/gateway/managedEntities"

        # iterate over children - which are either MEGroups or MEs proper.
        managedEntityID=1
        managedEntityGroupID=1
        for child in mainManagedEntitiesSection:
                writeLog("checking another child")
                if child.tag == "managedEntityGroup":
                        writeLog("It's a folder")
                        writeLog("found a Managed Entity Group - MEGroupID is " + str(managedEntityGroupID))
                        #child is a managedEntityGroup / Folder

                        #append this childNodes info onto its parents path to create its xpath
                        childPath = ('%s/%s[%i]' % (path, child.tag, managedEntityGroupID))

                        checkMENodeForAttributes(child, childPath)
                        managedEntityGroupID+=1
                elif child.tag == "managedEntity" :
                        writeLog("It's an ME")
                        writeLog("found a Managed Entity - MEID is " + str(managedEntityID))
                        # child is a plain ManagedEntity

                        childPath = ('%s/%s[%i]' % (path, child.tag, managedEntityID))

                        processME(child, childPath)
                        managedEntityID+=1

## Processes an ME Folder,
# @Args: MEFolder - the xmlNode of the MEGroup to be worked on
#        Path - the GSE Error compliant XPath to the parentNode of MEFolder
def checkMENodeForAttributes(MENode, path):
        writeLog("Checking MEFolder")
        #check if attributes are good on this one folder or managedEntity.
        #other Attribute Tests should be added here.

        checkHasAttributes(MENode, path)
        checkAttributesMatchStandards(MENode, path)

        #other Attribute Tests should be added here.

        # iterate over children - which are either MEGroups or MEs proper.
        managedEntityID=1
        managedEntityGroupID=1
        for child in MENode:
                if child.tag == "managedEntityGroup":
                        writeLog("found a Managed Entity Group - MEGroupID is " + str(managedEntityGroupID))
                        #child is a managedEntityGroup / Folder

                        #append this childNodes info onto its parents path to create its xpath
                        childPath = ('%s/%s[%i]' % (path, child.tag, managedEntityGroupID))

                        #recursive call to deal with subfolder.
                        checkMENodeForAttributes(child, childPath)
                        managedEntityGroupID+=1
                elif child.tag == "managedEntity" :
                        writeLog("found a Managed Entity - MEID is " + str(managedEntityID))
                        # child is a plain ManagedEntity

                        childPath = ('%s/%s[%i]' % (path, child.tag, managedEntityID))

                        processME(child, childPath)
                        managedEntityID+=1

def processME(MENode, path):
        #check if attributes are good.
        #other Attribute Tests should be added here.
        checkHasAttributes(MENode, path)
        checkAttributesMatchStandards(MENode, path)

def checkHasAttributes(MENode, path):
        attribute = MENode.findall("./attribute")

        if not attribute:
                print issue("Warning", path, "ManagedEntity or ManagedEntity Group without attribute specified.")

def findAttributes(MENode):
        attributeList = []
        for child in MENode:
                if child.tag == 'attribute' :
                        attributeList.append(child)
        return attributeList

def checkAttributesMatchStandards(MENode, path):

        writeLog("now checking attributes against standards.")
        #attributes = MENode.findall("./attribute")
        #@BUG!!! This will find nested sub-children attributes, rather than letting the children handle their own.
        # -- should instead loop over children and only check immediate child attributes.
        # -- this matters because it leads to bad xpaths for ME children.
        attributes = findAttributes(MENode)
        for attribute in attributes:
                attributeName = attribute.get('name')
                attributeValue = attribute.text
                writeLog("Found an attribute: " + attributeName)
                writeLog("checking attribute...")
                checkAttribute(attributeName, attributeNames, path)
                writeLog("checked attribute sucessfully.")

def checkAttribute(attribute, AttributeList, path):
        if attribute in AttributeList :
                #then there's no issue, do no further checks
                return
        writeLog("running checkAttribute, checking Against list.")
        closestMatch = checkAttributeSimilarToStandardAttribute(attribute, AttributeList)
        writeLog("Found Closest Matching attribute.")
        if closestMatch != None:
                writeLog("Found an issue, it's close to a standard, Error!")
                print issue("Error", path, "Attribute '" + attribute + "' is similar to an attribute in the standardized set: '" + closestMatch + "', please conform to the standard.")
        else:
                writeLog("didn't recognize it, only warning.")
                print issue("Warning", path, "Attribute " + attribute + " doesn't match any standard attribute.")
        return

def checkAttributeSimilarToStandardAttribute(attribute, attributeList):
        writeLog("Checking against list... for closest match capitolized and non...")
        (dist, attributeMatched) = closestMatch(attribute, attributeList)
        writeLog("distances calculated..")

        if dist < 2 :
                return attributeMatched
        else:
                return None

def closestMatch(attribute, stringList):
        attributeMatched=""
        minDistance = None
        attributeLowered = attribute.lower()
        for string2 in stringList:
                if attributeLowered == string2.lower() :
                        return (0, string2)
                distance = customHammingDistance(attributeLowered, string2.lower())
                if minDistance == None or distance < minDistance:
                        minDistance=distance
                        attributeMatched=string2
        return (minDistance, attributeMatched)


def customHammingDistance(string1, string2):
        distance = 0
        index=0
        for char in string1:
                try:
                        char2 = string2[index]
                except:
                        #out of bounds, string 2 shorter than string 1
                        distance+=1
                else:
                        if char != string2[index]:
                                distance+=1
                index+=1
        return distance

if __name__ == '__main__':
        status = main()

        sys.exit(status)
