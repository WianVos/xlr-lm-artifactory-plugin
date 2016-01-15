import os ,sys, time, ast,datetime
import string
import random

from string import Template

from overtherepy import SshConnectionOptions, OverthereHost, OverthereHostSession

class DarBuildServer(object):
    def __init__(self, server):

        self.sshOpts = SshConnectionOptions(server['host'], username=server['username'],privateKeyFile=server['key_file'],password=server['password'],port=server['port'] )

        self.host = OverthereHost(self.sshOpts)
        self.session = OverthereHostSession(self.host)
        self.zipBinary = server['pathToZipExecutable']
        self.workingDirectory = server['workingDirectory']
        self.create_directory(self.workingDirectory)
        workDir = self.session.remote_file(self.workingDirectory)
        self.session.get_conn().setWorkingDirectory(workDir)

    def __del__(self):
        self.destroy_work_directory()
        self.session.close_conn()

    def closeConnection(self):
        self.session.close_conn()

    @staticmethod

    def createServer(server):
        return DarBuildServer(server)
    #

    def init_dar(self, appName, appVersion):
        workspace_root = self.create_dar_directory(appName, appVersion)
        manifest_filename = "%s/deployit-manifest.xml" % workspace_root
        self.write_dar_manifest(appName, appVersion, workspace_root)

    def delete_workspace(self, appName, appVersion):
        dirName = "%s/%s" % (appVersion, appName)

        response = self.execute_command("/bin/rm -rf %s" %(dirName))
        response = self.execute_command("/bin/rm -rf %s" %(appVersion))



    def import_ear(self, appName, appVersion, deployable, url):
        self.download_file_into_dar(appName, appVersion,deployable, str(url))

    def create_dar_directory(self, appName, appVersion):
        dirName = "%s/%s" % (appVersion, appName)

        # check if the directory exists .. if it does we should go do something else.
        # might want to do a better locking mechanism
        if self.dir_exists(dirName):
          print "unable to create dar directory: %s/%s/%s" % (self.workingDirectory, appVersion, appName)
          raise Exception('unable to create Dar Package Directory')
        else:
          self.create_directory(dirName)

        return dirName


    def download_file_into_dar(self, appName, appVersion, deployable, url):
        #filename = url.split('/')[-1]
        filename = os.path.basename(url)
        outfile = "%s/%s/%s/%s" % (appVersion, appName,deployable, filename)
        dirName =  "%s/%s/%s" % (appVersion, appName,deployable)
        if self.dir_exists(dirName):
          print "output dir already exists: %s" % (dirName)
        else:
          self.create_directory(dirName)

        self.execute_command("/usr/bin/curl --retry 5 --retry-delay 2 -k -L -o %s %s" % (outfile, url))

    def read_manifest(self, appName, appVersion):
        file_name = "%s/%s/%s/deployit-manifest.xml" % (self.workingDirectory, appVersion, appName)
        return self.session.read_file(file_name, encoding="UTF-8")


    def write_manifest(self, appName, appVersion, content):

        file_name = "%s/%s/deployit-manifest.xml" % (appVersion, appName)
        self.write_to_file(file_name, content)

    def create_directory(self, dirName):
        self.execute_command("/bin/mkdir -p %s" % (dirName))

    def create_file(self, fileName, content=None):
        if content:
         self.write_to_file(fileName, str(content))
        else:
         self.execute_command("/bin/touch %s" % (fileName))


    def write_to_file(self, fileName, content):
        remoteFile = self.session.remote_file("%s/%s" % (self.workingDirectory, fileName))
        self.session.copy_text_to_file(str(content), remoteFile)

    def dir_exists(self, dirName):
        command = "[ -d %s ]" % (dirName)
        response = self.session.execute(command, check_success=False, suppress_streaming_output=False)

        if response.rc == 0 :
          return True
        else:
          return False


    def execute_command(self, command):
        print "executing command: %s " % (command)
        response = self.session.execute(command, check_success=False, suppress_streaming_output=False)


        if response.rc != 0:
          print response.stderr
          print response.stdout
          print "unable to execute command %s" % (command)
          raise Exception('unable to execute command ')
        else:
          print "Response:", str(response.stdout)
          print "Errors:", str(response.stderr)

       # self.switch_working_directory()
        return response


    def write_dar_manifest(self, appName, appVersion, workspace_root):
       filename = "./%s/deployit-manifest.xml" % (workspace_root)
       file_content = self.basic_dar_manifest_template().substitute(appVersion=appVersion, appName=appName)
       self.create_file(filename, file_content)

    def basic_dar_manifest_template(self):
       xml_template  = '<?xml version=\"1.0\" encoding=\"UTF-8\"?> \n'
       xml_template += ' <udm.DeploymentPackage version=\"$appVersion\" application=\"$appName\"> \n'
       xml_template += '   <orchestrator /> \n'
       xml_template += '   <deployables/> \n'
       xml_template += ' </udm.DeploymentPackage> \n'
       return Template(xml_template)

    def package_dar(self, appName, appVersion):
        command = "set -x \n"
        command += "if [ -f %s_%s.dar ] \n"
        command += " then rm -rf %s_%s.dar \n"
        command += "fi \n"
        command += "cd %s/%s \n" % (appVersion, appName)
        command += "/usr/bin/zip -r %s/%s_%s.dar *" % (self.workingDirectory, appName.replace('/','_'), appVersion.replace('.','_'))
        self.execute_multiline_command(command)


    def remove_dar(self, appName, appVersion):
        command = "set -x \n"
        command += "cd %s \n" % self.workingDirectory
        command += "if [ -f %s_%s.dar ] \n" % (appName.replace('/','_'), appVersion.replace('.','_'))
        command += " then rm -rf %s_%s.dar \n" % (appName.replace('/','_'), appVersion.replace('.','_'))
        command += " fi \n"
        self.execute_multiline_command(command)

    def write_exec_script(self, commands, script):
        self.session.upload_text_content_to_work_dir(self, commands, script, executable=False)

    def execute_multiline_command(self, command):

        tmp_filename = self.filename_generator()
        self.write_to_file(tmp_filename, command)
        self.execute_command("chmod +x %s" % (tmp_filename))
        self.execute_command("./%s" % (tmp_filename))


    def filename_generator(self, size=9, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def upload_dar_package(self, appName, appVersion, xldeployServer):
        dar_file_name = "%s_%s.dar" % (appName.replace('/','_'), appVersion.replace('.','_'))
        command = "/usr/bin/curl -k -u %s:%s -X POST -H \"content-type:multipart/form-data\" %s/package/upload/%s -F fileData=@./%s " % (xldeployServer['username'], xldeployServer['password'], xldeployServer['url'], dar_file_name, dar_file_name)
        self.execute_command(command)

        #TODO: Check for success
        #check for success
        #query the repo for the just uploaded application package
        #command = "/usr/bin/curl -k -u %s:%s %s/repository/query?type=udm.DeploymentPackage" % (xldeployServer['username'], xldeployServer['password'],  xldeployServer['url'])
        #response = self.execute_command(command)
        #str_xml = ''.join(response.stdout)
        #xml = ET.fromstring(str_xml)
        #found = False
        #for ci in xml:
        #  if "%s/%s" % (appName, appVersion) in ci.attrib['ref']:
        #    found = True
        #if found is False:
        #  raise Exception('dar package did not upload succesfully')
