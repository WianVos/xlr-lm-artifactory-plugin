[![Build Status](https://travis-ci.org/WianVos/xlr-lm-artifactory-plugin.svg?branch=master)](https://travis-ci.org/WianVos/xlr-lm-artifactory-plugin)

# Xlrelease Artifactory Plugin

This plugin allows for the further integration of Artifactory into an XL-Release/Xl-Deploy infrastructure.

## Overview
This plugin is capable of building an xldeploy dar file (deployment archive file) from components pulled from Jfrog Artifactory and uploading that dar file to a specified xl-deploy instances.
It does this by combining several steps in a xl-release phase while making use of an external "build" server slave host.

## TODO
- document and clean code
- figure out build and test

## Use case
For a certain client there was a string need to build a dar file out of deployable artifact files which are stored in artifactory and so called config (xl-deploy ci's which do not contain any actual tangeble artifacts)
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
- pathToZipExecutable: path to the Zip binary


### "lm.DarBuildServer" extends="xlrelease.Configuration">
        <property name="serverName" label="Name" kind="string" description="Unique name describing this RTC Client Server" />
        <property name="host" label="host" kind="string" />
        <property name="port" default="22" label="port" kind="string" />
        <property name="username" label="Username" kind="string" />
        <property name="password" label="Password" kind="string" password="true" required="false" />
        <property name="key_file" label="private keyfile" kind="string" required="false" default="none"/>
        <property name="workingDirectory" label="Filesystem Workspace" kind="string" />
        <property name="pathToZipExecutable" label="path to the Zip binary" kind="string" default="/usr/bin/zip" hidden="true"/>
    </type>

    <type type="lm.createDarPackage" description="create an initial Dar package on the Dar Buildserver" extends="xlrelease.PythonScript">
        <property name="iconLocation" default="lm/liberty-mutual-logo.png" hidden="true" />
        <property name="taskColor" hidden="true" default="#7A1F99" />
        <property name="darBuildServer" category="input" label="Dar BuildServer to use" referenced-type="lm.DarBuildServer" kind="ci" />
        <property name="appName" default="${appName}" category="input" label="Application Name" kind="string" required="true"/>
        <property name="appVersion" default="${appVersion}" category="input" label="Application Version" kind="string" required="true"/>
        <property name="scriptLocation" default="lm/createDarPackage.py" hidden="true" />
    </type>

    <type type="lm.uploadDarPackage" description="upload a dar package to and xlDeploy server" extends="lm.createDarPackage">
        <property name="scriptLocation" default="lm/uploadDarPackage.py" hidden="true" />
        <property name="xldeployServer" category="input" label="xldeploy server" referenced-type="xldeploy.Server" kind="ci"/>
    </type>

    <!-- Artifactory Integration -->

    <type type="lm.addDeployablesFromArtifactoryRepo" description="get all deployables from artifactory repo" extends="lm.createDarPackage">
       <property name="artifactoryServer" category="input" label="Artifactory Server to use" referenced-type="artifactory.Server" kind="ci" />
       <property name="artifactRepository" label="artifactory repository" category="input" kind="string" default="xlrelease" required="true" />
       <property name="artifactTypes" label="artifact types to include plus their xld type" category="input" kind="string" default="war:wlp.EnterpriseApplicationSpec,ear:wlp.EnterpriseApplicationSpec" required="true" />
       <property name="artifactSearchString" label="specific filename search" category="input" kind="string" required="false" default="none" />
       <property name="linkOnly" label="inlcude by link" category="input" kind="boolean" default="true" required="true" />
       <property name="scriptLocation" default="lm/addDeployablesFromArtifactoryRepo.py" hidden="true" />
    </type>

    <type type="lm.addPlainCI" description="add a ci without and artifact" extends="lm.createDarPackage">
        <property name="deployableName" category="input" label="Deployable Name" kind="string" required="true"/>
        <property name="deployableType" category="input" label="Deployable Type" kind="string" required="true"/>
        <property name="deployableUrl" category="input" label="Url to download the Deployable from" kind="string" required="false"/>
        <property name="deployableXml" category="input" size="large" label="Deployable Type Aditional XML" kind="string" required="false"/>
        <property name="scriptLocation" default="lm/addPlainCI.py" hidden="true" />
    </type>


    <type type="lm.mergeConfigDeployables" description="merge deployables configuration into the dar package" extends="lm.createDarPackage">
        <property name="scriptLocation" default="lm/mergeConfigDeployables.py" hidden="true" />
        <property name="configDeployables" category="input" label="Deployables configuration xml" kind="string" size="large" hidden="false" required="true" />
    </type>

    <type type="lm.mergeConfigDeployablesArtifactory" description="merge deployables configuration into the dar package from Artifactory" extends="lm.createDarPackage">
        <property name="scriptLocation" default="lm/mergeConfigDeployablesArtifactory.py" hidden="true" />
        <property name="artifactoryServer" category="input" label="Artifactory Server to use" referenced-type="artifactory.Server" kind="ci" />
        <property name="artifactRepository" label="artifactory repository" category="input" kind="string" default="xlrelease" required="true" />
        <property name="configFileName" label="filename to pull from artifactory" category="input" kind="string" default="app_config.xml" required="true" />
    </type>


    <type type="lm.cleanDarPackageWorkspace" description="clean up the Dar workspace" extends="lm.createDarPackage">
        <property name="scriptLocation" default="lm/cleanDarWorkspace.py" hidden="true" />
    </type>
    <type type="lm.addEarFromArtifactory" description="download an earfile from artifactory and add it to a Dar package" extends="lm.createDarPackage">
        <property name="deployableName" category="input" label="Deployable Name" kind="string" required="true"/>
        <property name="deployableType" category="input" label="Deployable Type" kind="string" required="true"/>
        <property name="deployableUrl" category="input" label="Url to download the Deployable from" kind="string" required="true"/>
        <property name="deployableXml" category="input" size="large" label="Deployable Type Aditional XML" kind="string" required="false"/>
        <property name="scriptLocation" default="lm/addEarFromArtifactory.py" hidden="true" />
    </type>

    <type type="lm.addArtifactByHttp" description="download an artifact an add it into a dar package" extends="lm.addEarFromArtifactory">
        <property name="scriptLocation" default="lm/addArtifactByHttp.py" hidden="true" />
    </type>


</synthetic>

