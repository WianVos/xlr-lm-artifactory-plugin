# Liberty Mutual Artifactory/Rational Team Concert Plugin

This plugin allows for the integration of both Artifactory and Rational Team Concert in accordance with a use case brought forward by Liberty Mutual.

## Overview
This plugin is capable of building an xldeploy dar file (deployment archive file) from components pulled from several sources and uploading that dar file to a specified xl-deploy instances.
It does this by combining several steps in a xl-release phase while making use of an external "build" server.

## TODO
- fix username password keyfile issue
- make the create darpackage emmit it's settings so that the rest of the jobs wil automaticly pick up the correct settings
- document and clean code

## Use case
Liberty Mutual (the client) has the need to build a dar file out of ear files which are stored in artifactory and so called config (xl-deploy ci's which do not contain any actual tangeble artifacts)
Te rationale behind this is that they want to store the config in a version control system exported from a xl-deploy instance while the ear files are build and delivered by jenkins to Artifactory.

## Components

### xldeploy.server
this is a configuration.HttpConnection derivative that holds the connection parameters to the xl-deploy instance that will receive the finished dar package

### lm.DarBuildServer
This configuration item represents a remote system used as "build" server.

parameters:
- serverName: name of the server
- host: host address of the server
- username: user wich will login and execute the build process
- password: coresponding password to the user
- workingDirectory: base directory to use for file operations

### lm.RTCClientServer
This configuration item represents a remote system with installed rtc client software (lscm)
parameters:
- Name: name of the server
- host: host address
- username: username of the login user
- password: password of the login user
- File System Workspace Base: temporary filesystem on the machine to use for file operations
- Path to the RTC Client software: path to the lscm executable.

### lm.RTCConfigRepo
Represents a RTC Repository stream/component thingamajig
parameters:
- Name: name of the rtc repo (internal use)
- host: address of the rtc server
- username: rtc user
- password: rtc password
- RTC repository url: url to the rtc repo
- RTC workspace name: name of the workspace in RTC
- Stream: name of the stream in RTC
- RTC Component name: name of the component in RTC
- RTC workitem nr: Workitem to use with rtc







    <type type="lm.getConfigXmlFromRTC" extends="xlrelease.PythonScript">
        <property name="taskColor" hidden="true" default="#68B768" />
        <property name="configRTCServer" category="input" label="Target RTC Client Server" referenced-type="lm.RTCClientServer" kind="ci" />
        <property name="configRTCRepo" category="input" label="Target RTC Repo" referenced-type="lm.RTCConfigRepo" kind="ci" />
        <property name="scriptLocation" default="lm/getApplicationPackageConfigRTC.py" hidden="true" />
        <property name="config_xml" category="output" />
    </type>

<!-- Dar Builder -->
     <type type="lm.DarBuildServer" extends="xlrelease.Configuration">
        <property name="serverName" label="Name" kind="string" description="Unique name describing this RTC Client Server" />
        <property name="host" label="host" kind="string" />
        <property name="username" label="Username" kind="string" />
        <property name="password" label="Password" kind="string" password="true" />
        <property name="workingDirectory" label="Filesystem Workspace" kind="string" />
        <property name="pathToZipExecutable" label="path to the Zip binary" kind="string" default="/usr/bin/zip" hidden="true"/>
    </type>

    <type type="lm.addEarFromArtifactory" description="download an earfile from artifactory and add it to a Dar package" extends="xlrelease.PythonScript">
        <property name="iconLocation" default="lm/liberty-mutual-logo.png" hidden="true" />
        <property name="taskColor" hidden="true" default="#7A1F99" />
        <property name="darBuildServer" category="input" label="Dar BuildServer to use" referenced-type="lm.DarBuildServer" kind="ci" />
        <property name="appName" category="input" label="Application Name" kind="string" required="true"/>
        <property name="appVersion" category="input" label="Application Version" kind="string" required="true"/>
        <property name="deployableName" category="input" label="Deployable Name" kind="string" required="true"/>
        <property name="deployableType" category="input" label="Deployable Type" kind="string" required="true"/>
        <property name="deployableUrl" category="input" label="Url to download the Deployable from" kind="string" required="true"/>
        <property name="deployableXml" category="input" size="large" label="Deployable Type Aditional XML" kind="string" required="false"/>
        <property name="scriptLocation" default="lm/addEarFromArtifactory.py" hidden="true" />
    </type>

    <type type="lm.createDarPackage" description="create an initial Dar package on the Dar Buildserver" extends="xlrelease.PythonScript">
        <property name="taskColor" hidden="true" default="#7A1F99" />
        <property name="darBuildServer" category="input" label="Dar BuildServer to use" referenced-type="lm.DarBuildServer" kind="ci" />
        <property name="appName" category="input" label="Application Name" kind="string" required="true"/>
        <property name="appVersion" category="input" label="Application Version" kind="string" required="true"/>
        <property name="scriptLocation" default="lm/createDarPackage.py" hidden="true" />
    </type>

    <type type="lm.uploadDarPackage" description="upload a dar package to and xlDeploy server" extends="lm.createDarPackage">
        <property name="scriptLocation" default="lm/uploadDarPackage.py" hidden="true" />
        <property name="xldeployServer" category="input" label="xldeploy server" referenced-type="xldeploy.Server" kind="ci"/>
    </type>

    <type type="lm.mergeConfigDeployables" description="merge deployables configuration into the dar package" extends="lm.createDarPackage">
        <property name="scriptLocation" default="lm/mergeConfigDeployables.py" hidden="true" />
        <property name="configDeployables" category="input" label="Deployables configuration xml" kind="string" size="large" hidden="false" required="true" />
    </type>

    <type type="lm.mergeConfigDeployablesRTC" description="merge deployables configuration into the dar package from RTC" extends="lm.createDarPackage">
        <property name="scriptLocation" default="lm/mergeConfigDeployablesRTC.py" hidden="true" />
        <property name="configRTCServer" category="input" label="Target RTC Client Server" referenced-type="lm.RTCClientServer" kind="ci" />
        <property name="configRTCRepo" category="input" label="Target RTC Repo" referenced-type="lm.RTCConfigRepo" kind="ci" />
    </type>

    <type type="lm.cleanDarPackageWorkspace" description="clean up the Dar workspace" extends="lm.createDarPackage">
        <property name="scriptLocation" default="lm/cleanDarWorkspace.py" hidden="true" />
    </type>

</synthetic>


# xlr-lm-artifactory-plugin
# xlr-lm-artifactory-plugin
