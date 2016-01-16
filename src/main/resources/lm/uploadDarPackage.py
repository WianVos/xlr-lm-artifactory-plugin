from lm.DarBuildServer import DarBuildServer


server = DarBuildServer.createServer(darBuildServer)

server.package_dar(appName, appVersion)

server.upload_dar_package(appName, appVersion, xldeployServer)

server.remove_dar(appName, appVersion)

server.closeConnection()