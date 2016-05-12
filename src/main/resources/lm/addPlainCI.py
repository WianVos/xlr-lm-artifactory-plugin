import requests,re, os, sys
import xml.etree.ElementTree as ET
from xml.dom import minidom
from lm.DarBuildServer import DarBuildServer


default_encoding = "utf-8"
re_space = re.compile('>\n\s+([^<>\s].*?)\n\s+</', re.DOTALL)



def check_available(url):

    retries = 10
    nr_tries = 0


    while True:
        # increment trie counter
        nr_tries += 1
        Base.info("trying to see if %s is a valid artifact to use. Try nr: %i" % (url, nr_tries))


        # try to fetch a response
        response = requests.head(url, verify=False)

        # if the status code is above 299 (which usually means that we have a problem) retry
        if response.status_code > 299:

            # if the number of retries exceeds 10 fail hard .. cuz that is how we roll
            if nr_tries > retries:
              Base.fatal('Unable to retrieve artifact from url after %i retries' % retries )
              response.raise_for_status()
            # warn the user
            Base.warning("unable to retrieve head for url %s" %  url)

            # it is good form to back off a failing remote system a bit .. every retry we are gonna wait 5 seconds longer . Coffee time !!!!
            sleeptime = 5 * int(nr_tries)

            Base.warning("timing out for: %i seconds" % sleeptime)

            # sleep dammit .. i need it ..
            time.sleep(sleeptime)
        else:
            Base.info("check for artifact from %s : succesfull" % url)
            Base.info( str(response.text))
            return str(response.text)



    r = requests.head(url, verify=False)
    r.raise_for_status()

    return True

def well_formed_xml(xml_string):
    """
    checks xml_string for the presence of <list></list> tags and adds them if not present
    """

    if str(xml_string).startswith('<list>'):
        return str(xml_string)
    else:
        return """<list> \n
            %s
            </list> \n
            """ % str(xml_string)



def formatXml(elem):
    """
    Formats xml in to a nice looking string
    :param elem:  elementree object
    :return: string
    """
    not_pretty_xml = ET.tostring(elem, default_encoding)
    document = minidom.parseString(not_pretty_xml)
    nearly_pretty_xml = document.toprettyxml(indent="  ")
    pretty_xml = re_space.sub('>\g<1></', nearly_pretty_xml)
    final_xml = "".join([s for s in pretty_xml.strip().splitlines(True) if s.strip()])
    return final_xml


def get_deployable_element_inline_file(dName, dType, dXml, dFile):
    deployable =  ET.Element(dType, name="%s" % dName, file="%s/%s" %(dName, dFile))
    if dXml:
      addons = ET.fromstring(dXml)
      for addon in addons:
        deployable.append(addon)
    return deployable

def get_deployable_element_url(dName, dType, dXml, dUrl):

    #create the base Element
    deployable =  ET.Element(dType, name="%s" % dName)

    # create and add in the url bit
    fileUriElement = ET.Element("fileUri")
    fileUriElement.text = dUrl
    deployable.append(fileUriElement)
    #tag on the rest of the stuffels
    #biatch
    print "adding additional xml to element %s" % dName
    if dXml:
      addons = ET.fromstring(dXml)
      for addon in addons:
        deployable.append(addon)
    return deployable

def merge_new_deployable_with_manifest(manifest, deployable=None, orchestrator=None):
    """
    :param manifest: a xmltree object of a valid dar package manifest
    :param deployables: additional deployable
    :param orchestrators: additional orchestrators
    :return: xmltree manifest
    """
    for child in manifest:
       if child.tag == "deployables":
            if deployable != None:
                child.append(deployable)
       if child.tag == "orchestrators":
            if orchestrator != None:
                child.append()

    return manifest

def get_additional_xml_from_url(url):
    """
    download additional xml for a ci for an external url
    :param url: url to obtain the xml from
    :return:
    """
    print "downloading xml from %s" % url
    error = 300
    output = requests.get(url)

    if ( output.status_code < error ) :
        print "Download from %s : succesfull" % url
        print str(output.text)
        return str(output.text)
    else:
        print 'unable to download xml'
        return False



additional_xml = None

if deployableXml and deployableXmlUrl:
    print "deployableXml and deployableXmlUrl are both set. deployableXmlUrl takes precedence"

if deployableXmlUrl:
    additional_xml = get_additional_xml_from_url(deployableXmlUrl)
elif deployableXml:
    additional_xml = deployableXml

additional_xml = well_formed_xml(additional_xml)

server = DarBuildServer.createServer(darBuildServer)

# do the xml bit
manifest = server.read_manifest(appName, appVersion)

#translate the string in to an element tree
manifest_root = ET.fromstring(manifest)

# check if the stuff where about to add actually exists
if checkArtifactAvailability:
   if check_available(deployableUrl):
       print "artifact exists, moving on"
   else:
       print "artifact does not exist, existing"
       sys.exit(2)

# encode the deployable element
if linkOnly:
    deployable_element = get_deployable_element_url(deployableName, deployableType, additional_xml, deployableUrl)
else:
    server.import_ear(appName, appVersion, deployableName, deployableUrl)
    deployable_element = get_deployable_element_inline_file(deployableName, deployableType, additional_xml, os.path.basename(deployableUrl))

# merge the manifest with the deployable
updated_manifest = merge_new_deployable_with_manifest(manifest_root,deployable=deployable_element)

# format the xml to look pretty
# and transform it back into a string
updatedXml = formatXml(updated_manifest)

# print the result to the log
print "manifest xml:"
print updatedXml

# write the damm thing to the manifest file on the workspace
server.write_manifest(appName, appVersion, updatedXml)

server.closeConnection()