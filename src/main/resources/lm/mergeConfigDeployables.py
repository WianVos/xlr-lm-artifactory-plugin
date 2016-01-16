import xml.etree.ElementTree as ET



from lm.DarBuildServer import DarBuildServer

server = DarBuildServer.createServer(darBuildServer)

# functions
def format_additional_xml(xml):
  deployables =  ET.Element('deployables')
  for child in xml:
    try:
      child.attrib['name'] = child.attrib.pop('id')
    except KeyError:
      pass

    deployables.append(child)

  print deployables

  return deployables
    
    


def get_deployable_element(dName, dType, dXml, fileName):

    deployable =  ET.Element(dType, name="%s" % dName, file="%s/%s" %(dName, fileName))
    if dXml:
      addons = ET.fromstring(dXml)
      for addon in addons:
        deployable.append(addon)
    return deployable








#get the xml from the existing manifest in the workspace
output = server.read_manifest(appName, appVersion)
root = ET.fromstring(output)

# get the additional deployables in a root type element (xml needs to be in <list></list> format
additional_deployables = ET.fromstring(configDeployables)
#get the additionals ready for adding into the existing xml



for child in root:
  if child.tag == "deployables":
    for new_child in format_additional_xml(additional_deployables):
     child.append(new_child)
     print child.tag, child.attrib

updatedXml = ET.tostring(root,encoding="us-ascii")

server.write_manifest(appName, appVersion, updatedXml)
