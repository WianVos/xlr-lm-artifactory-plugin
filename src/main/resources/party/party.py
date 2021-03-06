import sys, json, requests, urllib, base64, re, os
from party_config import party_config


class Party:
    def __init__(self, config={}):
        self.files = []

        party_config.update(config)

        # Set instance variables for every value in party_config
        for k, v in party_config.iteritems():
            setattr(self, '%s' % (k,), v)

    def query_artifactory(self, query, query_type='get'):
        """
        Send request to Artifactory API endpoint.
        @param: query - Required. The URL (including endpoint) to send to the Artifactory API
        @param: query_type - Optional. CRUD method. Defaults to 'get'.
        """
        if query_type.lower() == "get":
            response = requests.get(query, auth=(self.username, base64.b64decode(self.password)), headers=self.headers)
        elif query_type.lower() == "put":
            response = requests.put(query, data=query.split('?', 1)[1],
                                    auth=(self.username, base64.b64decode(self.password)), headers=self.headers)
        if query_type.lower() == "post":
            pass

        match = re.search(r'^20.*$', str(response.status_code))
        if not match:
            return None

        return response

    def find_by_properties(self, properties):
        """
        Look up an artifact, or artifacts, in Artifactory by using artifact properties.
        @param: properties - List of properties to use as search criteria.
        """
        query = "%s/%s?%s" % (self.artifactory_url, self.search_prop, urllib.urlencode(properties))
        raw_response = self.query_artifactory(query)
        if raw_response is None:
            return raw_response

        response = json.loads(raw_response.text)

        for item in response['results']:
            for k, v in item.iteritems():
                setattr(self, '%s' % (k,), v)

        if not response['results']:
            return None

        artifact_list = []
        for u in response['results']:
            artifact_list.append(os.path.basename(u['uri']))

        self.files = artifact_list
        setattr(self, 'count', len(artifact_list))

        return "OK"

    def find(self, filename):
        """
        Look up an artifact, or artifacts, in Artifactory by
        its filename.
        @param: filename - Filename of the artifact to search.
        """
        query = "%s/%s?name=%s" % (self.artifactory_url, self.search_name, filename)
        raw_response = self.query_artifactory(query)
        if raw_response is None:
            return raw_response
        response = json.loads(raw_response.text)
        if len(response['results']) < 1:
            return None

        setattr(self, 'name', filename)
        setattr(self, 'url', response)

        return "OK"

    def get_properties(self, filename, properties=None):
        """
        Get an artifact's properties, as defined in the Properties tab in
        Artifactory.
        @param: filename - Filename of artifact of which to get properties.
        @param: properties - Optional. List of properties to help filter results.
        """
        if properties:
            query = "%s?properties=%s" % (filename, ",".join(properties))
        else:
            query = "%s?properties" % filename

        raw_response = self.query_artifactory(query)
        if raw_response is None:
            return raw_response
        response = json.loads(raw_response.text)
        for key, value in response.iteritems():
            setattr(self, '%s' % (key,), value)

        return "OK"

    def set_properties(self, file_url, properties):
        """
        Set properties on an artifact.
        @param: file_url - URL of artifact on which to set properties.
        @param: properties - JSON list of properties to set on the artifact.
        """
        query = "%s?properties=%s" % (file_url, urllib.urlencode(properties).replace('&', '|'))
        response = self.query_artifactory(query, "put")
        if response is None:
            return response

        return "OK"

    def get_repositories(self, repo_type=None):
        """
        Helper method to get repository names. Defaults to all.
        @param: repo_type - type of repository to return (local, remote, virtual)
        """
        # Current Artifactory API doesn't allow multiple types to be
        # selected, so let's allow specifying at least one type.
        repositories = []
        if repo_type is None:
            query = "%s/%s" % (self.artifactory_url, self.search_repos)
        else:
            query = "%s/%s?type=%s" % (self.artifactory_url, self.search_repos, repo_type)

        raw_response = self.query_artifactory(query)
        if raw_response is None:
            return raw_response
        response = json.loads(raw_response.text)

        for line in response:
            for item in line:
                repositories.append(line["key"])

        if repositories:
            return repositories

        return None

    def find_by_pattern(self, filename, specific_repo=None, repo_type=None, max_depth=10):
        """
        Look up an artifact, or artifacts, in Artifactory by
        its partial filename (can use globs).
        @param: filename - Required. Filename or partial filename to search.
        @param: specific_repo - Optional. Name of Artifactory repo to search.
        @param: repo_type - Optional. Values are local|virtual|remote.
        @param: max_depth - Optional. How many directories deep to search. Defaults to 10.
        """

        # Ensure filename is specified
        if not filename:
            errmsg = "No filename specified."
            raise ValueError(errmsg)
            return False

        # Validate specified repo type
        repo_types = ["local", "virtual", "remote", None]
        if repo_type not in repo_types:
            errmsg = "Invalid repo_type '%s' specified (valid types: 'local', 'virtual', 'remote', 'None'.)" % repo_type
            raise ValueError(errmsg)
            return False

        # Add in bookend globs to aid the search, but not if
        # they're already there, cuz Artifactory doesn't like that
        if filename[-1] != "*":
            filename = "%s*" % filename
        if filename[0] != "*":
            filename = "*%s" % filename

        # Create pattern list
        patterns = []
        # Adjust max_depth to determine how many (inclusive) directories deep on the path to search
        for p in range(0, max_depth):
            patterns.append("*/" * p)


        if specific_repo is not None:
            repos = [specific_repo]
        else:
            repos = self.get_repositories(repo_type)

        # Cycle through each pattern in each repo to find the artifact
        results = []
        for repo in repos:
            for pattern in patterns:
                query = "%s/search/pattern?pattern=%s:%s%s" % (self.artifactory_url, repo, pattern, filename)
                raw_response = self.query_artifactory(query)
                if raw_response is None:
                  response = {}
                else:
                  response = json.loads(raw_response.text)
                try:
                    if response['files']:
                        for i in response['files']:
                            results.append("%s/%s" % (response['repoUri'], i))
                except KeyError:
                    pass
        if not results:
            return None

        # Set the class 'files' variable to have the list of found artifacts
        self.files = results
        return results
