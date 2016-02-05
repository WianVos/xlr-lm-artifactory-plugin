#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
import com.xhaus.jyson.JysonCodec as json
from com.xebialabs.deployit.plugin.api.reflect import Type
import requests
import com.xebialabs.xlrelease.api.XLReleaseServiceHolder as XLReleaseServiceHolder
import com.xebialabs.deployit.repository.SearchParameters as SearchParameters
import com.xebialabs.deployit.plugin.api.reflect.Type as Type

__type_step_dict = {"cis":        "lm.addPlainCI",
                    "config" :    "lm.mergeConfigDeployables"}

__release = getCurrentRelease()

def find_ci_id(name, type):
    sp = SearchParameters()
    sp.setType(Type.valueOf(type))

    for p in XLReleaseServiceHolder.getRepositoryService().listEntities(sp):
        if str(p.getTitle()) == name:
           return p




def createSimpleTask(phaseId, taskTypeValue, title, propertyMap):
    """
    adds a custom task to a phase in the release
    :param phaseId: id of the phase
    :param taskTypeValue: type of task to add
    :param title: title of the task
    :param propertyMap: properties to add to the task
    :return:
    """
    print propertyMap

    parenttaskType = Type.valueOf("xlrelease.CustomScriptTask")

    parentTask = parenttaskType.descriptor.newInstance("nonamerequired")
    parentTask.setTitle(title)

    childTaskType = Type.valueOf(taskTypeValue)
    childTask = childTaskType.descriptor.newInstance("nonamerequired")
    for item in propertyMap:
        if childTask.hasProperty(item):
            childTask.setProperty(item,propertyMap[item])
        else:
            print "dropped property: %s on %s because: not applicable" % (item, taskTypeValue)
    parentTask.setPythonScript(childTask)

    taskApi.addTask(str(phaseId),parentTask)



def get_target_phase(targetPhase):
    """
    search the release for the targetPhase by string name
    for some stupid reason we can't address it by its name ..

    :param targetPhase:string
    :return:phaseId
    """
    phaseList = phaseApi.searchPhasesByTitle(targetPhase,release.id)
    if len(phaseList) == 1:
        return phaseList[0]
    else:
        print "Requested phase: %s not found. Create it in the template first" % targetPhase
        sys.exit(2)
        #should be replaced by some logic to create the phase


def load_profile(profile):
    """
    returns a dict .. if input is json it will return ad dict .. if dict it will return the dict
    :param profile:
    :return:
    """

    if type(profile) is dict:
        return profile
    else:
       return json.loads(profile)

def download_json_profile(url):
    print "downloading json from %s" % url
    error = 300
    output = requests.get(url)

    if ( output.status_code < error ) :
        print "Download from %s : succesfull" % url
        print str(output.text)
        return str(output.text)
    else:
        print 'unable to download json'
        return False


def handle_profile(profile, targetPhase):
    """
    parse the loaded profile and add a task for each item in it
    :param profile: json or dict
    :param targetPhase: phase to add the steps to
    :return:
    """

    loaded_profile = load_profile(profile)
    phaseId = get_target_phase(targetPhase)
    title_nr = 0

    for type, data in loaded_profile.items():

        if __type_step_dict.has_key(type):
            taskTypeValue = __type_step_dict[type]
        else:
            taskTypeValue = type

        for data_item in data:
            final_data_items = dict(data_item.items() + __default_data_items.items())
            title_nr += 1

            createSimpleTask(phaseId, taskTypeValue, "dar_build_task_%s_%i" % (type, title_nr), final_data_items )


#setting global variables

__dar_build_server = find_ci_id(darBuildServer['title'], 'lm.DarBuildServer')
__xldeploy_server  = find_ci_id(xldeployServer['title'], 'xldeploy.Server')

__default_data_items = {"appName" : appName,
                        "appVersion" : appVersion,
                        "darBuildServer" : __dar_build_server,
                        "xldeployServer" : __xldeploy_server}

# pre build steps to execute
# one should always
__pre_build_steps = {"lm.createDarPackage" : [{"appName" : appName, "appVersion" : appVersion, "darBuildServer" : __dar_build_server , "xldeployServer" : __xldeploy_server }]}
__post_build_steps = {"lm.uploadDarPackage" :[{"appName" : appName, "appVersion" : appVersion, "darBuildServer" : __dar_build_server , "xldeployServer" : __xldeploy_server}]}
__cleanup_build_steps = {"lm.cleanDarPackageWorkspace": [{"appName" : appName, "appVersion" : appVersion, "darBuildServer" : __dar_build_server , "xldeployServer" : __xldeploy_server}]}






# both inputJson and inputJsonUrl cannot be None .
# we need input


if inputJson == None and inputJsonUrl == None:
    print "both inputJson and inputJsonUrl are empty: this can not be . existing step"
    sys.exit(2)

# inputJsonUrl takes precedence over inputJson ..
# BECAUSE I SAY SO ....Biatch
# Just checking if anyone ever really reads this ;-)

if inputJson:
    inputJson = inputJson.replace('\n','').replace('\t', '').replace('\r', '')
if inputJsonUrl:
    if inputJsonUrl.startswith('http'):
        inputJson = download_json_profile(inputJsonUrl)

handle_profile(__pre_build_steps, phaseName)
handle_profile(inputJson, phaseName)
handle_profile(__post_build_steps, phaseName)
handle_profile(__cleanup_build_steps, phaseName)
