import sys, time, ast, re, os

import xml.etree.ElementTree as ET

from lm.DarBuildServer import DarBuildServer

import party






# get a the buildserver workspace corresponding to the appVersion and appName
server = DarBuildServer.createServer(darBuildServer)

# get the current package manifest
manifest = server.read_manifest(appName, appVersion)

#and translate to an xml root document
manifestRoot = ET.fromstring(manifest)


# query the artifactory repo to see what artifacts we need to get.
artifactory = party.Party()
artifactory.artifactory_url = artifactoryServer['url']
artifactory.username = artifactoryServer['username']
artifactory.password = base64.b64encode(artifactoryServer['password'])


#scan artifactory repo for deployables
def getDeployablesInformation():
    deployables = []
    print  artifactTypes.split(',')
    for x in artifactTypes.split(','):
        x , deployableType = x.split(':')
        result = artifactory.find_by_pattern(".%s" % x, artifactRepository)
        if result:
            for y in result:
                file = {}
                #save the file's link
                link = str(y)
                fileName = str(os.path.basename(y))
                file['name'] = fileName
                file['url'] = link
                file['deployableType'] = str(deployableType)
                print file
                #retrieve the file's xml if any
                #the spec file while be named <filename_type.xlspec>
                specfile = "%s.xlspec" % (fileName.replace(".", "_"))
                specresult = artifactory.find_by_pattern(specfile, specific_repo=artifactRepository, max_depth=4)
                if specresult:
                    file['xml'] = artifactory.query_artifactory(specresult[0]).text
                else:
                    file['xml'] = None
                print file
                deployables.append(dict(file))
    return deployables



def getDeployableElement(dName, dType, dXml, fileName):
    deployable =  ET.Element(dType, name="%s" % dName, file="%s/%s" %(dName, fileName))
    if dXml:
      addons = ET.fromstring(dXml)
      for addon in addons:
        deployable.append(addon)
    return deployable


# figure out all the deployables from aritfactory
deployables = getDeployablesInformation()

# match them to the search pattern
if artifactSearchString:
    x = re.compile(artifactSearchString)
    for d in deployables:
        if x.match(d['name']):
           logger.info("found: %s" % d['name'])
        else:
            deployables.remove(d)



# loop over them and build the manifest xml

if linkOnly is True:
    # loop over them and build the manifest xml
    for d in deployables:
        deployable_xml = getDeployableElement(d['name'], d['deployableType'], d['xml'], d['url'])

        for child in manifestRoot:
            if child.tag == "deployables":
                child.append(deployable_xml)
                print child.tag, child.attrib
else:
    server.import_ear(appName, appVersion, d['name'], d['url'])

    deployable_xml = get_deployable_element(d['name'], d['deployableType'], d['xml'], os.path.basename(d['url']))
    for child in root:
      if child.tag == "deployables":
        child.append(deployable)
        print child.tag, child.attrib


#update the manifest in the workspace
updatedManifestXml = ET.tostring(manifestRoot,encoding="us-ascii")
server.write_manifest(appName, appVersion, updatedManifestXml)

server.closeConnection()
