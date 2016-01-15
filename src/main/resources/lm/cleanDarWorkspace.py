import sys, time, ast


from java.lang import String
from java.util import Arrays

from lm.DarBuildServer import DarBuildServer

server = DarBuildServer.createServer(darBuildServer)

response = server.delete_workspace(appName, appVersion)

server.closeConnection()

