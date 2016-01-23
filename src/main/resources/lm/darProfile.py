#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
import com.xhaus.jyson.JysonCodec as json
from com.xebialabs.deployit.plugin.api.reflect import Type

__type_step_dict = {"cis":        "lm.addPlainCI",
                    "config" :    "lm.mergeConfigDeployables"}

__release = getCurrentRelease()

__default_data_items = {"appName" : appName,
                        "appVersion" : appVersion,
                        "darBuildServer" : darBuildServer,
                        "xldeployServer" : xldeployServer}

# pre build steps to execute
# one should always
__pre_build_steps = {"lm.createDarPackage" : [{"appName" : appName, "appVersion" : appVersion, "darBuildServer" : darBuildServer, "xldeployServer" : xldeployServer}]}
__post_build_steps = {"lm.uploadDarPackage" :[{"appName" : appName, "appVersion" : appVersion, "darBuildServer" : darBuildServer, "xldeployServer" : xldeployServer}]}
__cleanup_build_steps = {"lm.cleanDarPackageWorkspace": [{"appName" : appName, "appVersion" : appVersion, "darBuildServer" : darBuildServer, "xldeployServer" : xldeployServer}]}




def createSimpleTask(phaseId, taskTypeValue, title, propertyMap):
    """
    adds a custom task to a phase in the release
    :param phaseId: id of the phase
    :param taskTypeValue: type of task to add
    :param title: title of the task
    :param propertyMap: properties to add to the task
    :return:
    """
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
        return False
        #should be replaced by some logic to create the phase


def load_profile(profile):
    """
    returns a dict .. if input is json it will return ad dict .. if dict it will return the dict
    :param profile:
    :return:
    """

    if type(profile) == dict:
        return profile
    else:
       return json.loads(profile)

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

            createSimpleTask(phaseId, taskTypeValue, "dar_build_task_%i" % (title_nr), final_data_items )



handle_profile(__pre_build_steps, phaseName)
handle_profile(inputJson, phaseName)
handle_profile(__post_build_steps, phaseName)
handle_profile(__cleanup_build_steps, phaseName)
