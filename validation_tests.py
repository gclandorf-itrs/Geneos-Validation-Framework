#!/usr/bin/python
import xml.etree.ElementTree as ET
import os, sys
import shutil

#The set of attributes to be enforced.
#this can be adjusted as deisred.
attributeNames = ['ENVIRONMENT', 'APPLICATION', 'LOB', 'REGION', 'AIT', 'APPGROUP', 'Location', 'Env']
validate_log = open("validate.log", "w")
validate_log.write("log Opened for writing\n")
#puts a message in the logfile.

""" init
    Defines the hash test_dict , which contains available test functions.
"""
def	init():
    global test_dict
    test_dict = {'processME':processME}
    
""" writeLog 
    Simple message writer to the log file.
"""
def writeLog(message):
    validate_log.write(message+"\n")

""" issue
    Formats the xml wrapper for an issue.
"""
def issue(severity, path, message):
    string = (
        "\t<issue>\n\t\t<severity>\n\t\t\t" + severity +
        "\n\t\t</severity>\n\t\t<path>\n\t\t\t" + path +
        "\n\t\t</path>\n\t\t<message>\n\t\t\t" + message +
        "\n\t\t</message>\n\t</issue>")
    writeLog(string)
    return string

""" processME
    ME Test to check if a node has attributes and if it matches outlined standards.
""" 
def processME(MENode, path):
    hasAttr = checkHasAttributes(MENode, path)
    if hasAttr: 
        checkAttributesMatchStandards(MENode, path)

def checkHasAttributes(MENode, path):
    attribute = MENode.findall("./attribute")
    if not attribute:
        print issue("Warning", path, "ManagedEntity or ManagedEntity Group without attribute specified.")
        return 0
    return 1

def findAttributes(MENode):
    attributeList = []
    for child in MENode:
        if child.tag == 'attribute' :
            attributeList.append(child)
        return attributeList

def checkAttributesMatchStandards(MENode, path):

        writeLog("now checking attributes against standards.")
        #attributes = MENode.findall("./attribute")
        attributes = findAttributes(MENode)
        for attribute in attributes:
                attributeName = attribute.get('name')
                attributeValue = attribute.text
                writeLog("Found attribute: " + attributeName)
                checkAttribute(attributeName, attributeNames, path)
                writeLog("checked attribute sucessfully.")

def checkAttribute(attribute, AttributeList, path):
        if attribute in AttributeList :
                #then there's no issue, do no further checks
                return
        writeLog("running checkAttribute, checking Against list.")
        closestMatch = compareToStdAttr(attribute, AttributeList)
        writeLog("Found Closest Matching attribute.")
        if closestMatch != None:
                writeLog("Found an issue, it's close to a standard, Error!")
                print issue("Error", path, 
                "Attribute '" + attribute + 
                "' is similar to an attribute in the standardized set: '" + 
                closestMatch + "', please conform to the standard.")
        else:
                writeLog("didn't recognize it, only warning.")
                print issue("Warning", path, "Attribute " + attribute + " doesn't match any standard attribute.")
        return

def compareToStdAttr(attribute, attributeList):
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
