#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
import time
import sys


import xml.parsers.expat
import xml.etree.ElementTree as ET


from lm.DarBuildServer import DarBuildServer
from rtc.RTCWorkspace import RTCWorkspace



# functions
def format_additional_xml(xml):
  deployables =  ET.Element('deployables')
  for child in xml:
    try:
      child.attrib['name'] = child.attrib.pop('id')
    except KeyError:
      pass

    deployables.append(child)

  return deployables

workspace = RTCWorkspace.createRTCWorkspace(configRTCRepo, configRTCServer)
server = DarBuildServer.createServer(darBuildServer)

config_xml = workspace.read_file("config.xml")

#get the xml from the existing manifest in the workspace
output = server.read_manifest(appName, appVersion)
root = ET.fromstring(output)

additional_deployables = ET.fromstring(config_xml)
#get the additionals ready for adding into the existing xml
for child in root:
  if child.tag == "deployables":
    for new_child in format_additional_xml(additional_deployables):
     child.append(new_child)

updatedXml = ET.tostring(root,encoding="us-ascii")

server.write_manifest(appName, appVersion, updatedXml)

server.closeConnection()