import sys, time, ast, os

import xml.parsers.expat
import xml.etree.ElementTree as ET

import pprint

from java.lang import String
from java.util import Arrays

from lm.DarBuildServer import DarBuildServer

def get_deployable_element(dName, dType, dXml, dUrl=None):
    if linkOnly:
        deployable =  ET.Element(dType, name="%s" % dName, fileUri="%s" % dUrl)
    else:
        deployable =  ET.Element(dType, name="%s" % dName)

    if dXml:
      addons = ET.fromstring(dXml)
      for addon in addons:
        deployable.append(addon)
    return deployable


server = DarBuildServer.createServer(darBuildServer)

# do the xml bit
output = server.read_manifest(appName, appVersion)

root = ET.fromstring(output)

deployable = get_deployable_element(deployableName, deployableType, deployableXml, deployableUrl)

for child in root:
  if child.tag == "deployables":
    child.append(deployable)
    print child.tag, child.attrib

updatedXml = ET.tostring(root,encoding="us-ascii")

server.write_manifest(appName, appVersion, updatedXml)
