import sys, time, ast


from java.lang import String
from java.util import Arrays

import lm.DarBuildServer
reload(lm.DarBuildServer)

from lm.DarBuildServer import DarBuildServer
server = DarBuildServer.createServer(darBuildServer)

server.init_dar(appName, appVersion)

server.closeConnection()