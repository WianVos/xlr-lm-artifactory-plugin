## PLACEHOLDER
import xml.etree.ElementTree as ET
class Manifest(object):

    @staticmethod
    def get_deployable_element_inline_file(dName, dType, dXml, dFile):
        deployable =  ET.Element(dType, name="%s" % dName, file="%s" % dFile)
        if dXml:
          addons = ET.fromstring(dXml)
          for addon in addons:
            deployable.append(addon)
        return deployable

    @staticmethod
    def get_deployable_element_url(dName, dType, dXml, dUrl):

        #create the base Element
        deployable =  ET.Element(dType, name="%s" % dName)

        # create and add in the url bit
        fileUrlElement = ET.Element("fileUrl")
        fileUrlElement.text = dUrl
        deployable.append(fileUrlElement)

        #tag on the rest of the stuffels
        #biatch
        if dXml:
          addons = ET.fromstring(dXml)
          for addon in addons:
            deployable.append(addon)
        return deployable

    @staticmethod
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