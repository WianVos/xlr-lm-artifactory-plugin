#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
import com.xhaus.jyson.JysonCodec as json
from com.xebialabs.deployit.plugin.api.reflect import Type
import requests, re
import com.xebialabs.xlrelease.api.XLReleaseServiceHolder as XLReleaseServiceHolder
import com.xebialabs.deployit.repository.SearchParameters as SearchParameters
import com.xebialabs.deployit.plugin.api.reflect.Type as Type

__type_step_dict = {"cis":        "lm.addPlainCI",
                    "config" :    "lm.mergeConfigDeployables"}

__release = getCurrentRelease()

__type_title_dict = {'lm.addPlainCI' :              {'prefix'       : 'add',
                                                    'data_fields'   : ['deployableType', 'deployableName'],
                                                    'postfix'       : 'to deployment package'},
                     'lm.mergeConfigDeployables' :  {'prefix'       : 'adding',
                                                    'postfix'       : 'config xml to package'},
                     'lm.uploadDarPackage' :        {'prefix'       : 'uploading dar to',
                                                    'datafields'    : ['xldeployServer']},
                     'lm.createDarPackage' :        {'prefix'       : 'create workspace on',
                                                     'data_fields'  : ['darBuildServer']}
                    }

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
    #print propertyMap

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
    output = requests.get(url, verify=False)

    if ( output.status_code < error ) :
        print "Download from %s : succesfull" % url
        print str(output.text)
        return str(output.text)
    else:
        print 'unable to download json'
        return False

# def resolve_variables_in_profile(dict):
#     """
#     resolve the variables
#     :return:
#     """
#     variable_start_regex = re.compile('^\$\{', re.IGNORECASE)
#     variables = getCurrentRelease().getVariableValues()
#
#     # loop over the profile dict and check if there are variables in any values..
#     # variables are not allowed in keys
#     for key, value in dict.items():
#         if type(value) == dict:
#             return resolve_variables_in_profile(value)
#         if type(value) == str:
#             if re.match(variable_start_regex, value) != None:
#                 for vk, vv in variables.items():
#                     if vk in value:
#                         value.replace(vk, vv)
#                         dict[key] = value
#     return dict

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

            title = get_title("dar_build_task_%s_%i" % (type, title_nr), taskTypeValue, data)

            createSimpleTask(phaseId, taskTypeValue, title, final_data_items )


def get_title(title, citype, data):

    print "GATHERING TITLE for %s" % citype

    if __type_title_dict.has_key(citype):
        print __type_title_dict[citype]

        new_title = []
        for x in ['prefix', 'data_fields', 'postfix']:
            try:
                out = __type_title_dict[citype][x]

                if type(out) == list:
                    for e in out:
                        try:
                            new_title.append(data[0][e])
                        except KeyError:
                            print 'unable to retrieve %s from step data' % e
                else:
                    new_title.append(out)
            except KeyError:
                print 'no data defined for field %s' % x



        return " ".join(new_title)
    else:
        return title

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
