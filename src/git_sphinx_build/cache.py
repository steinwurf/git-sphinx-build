import json
import os


class Cache:

    def __init__(self, cache_path, unique_name):
        """ Create a new RunResult object
        """
        self.cache_path = cache_path
        self.unique_name = unique_name

        self.filename = unique_name + '.json'
        self.filepath = os.path.join(self.cache_path, self.filename)

        if os.path.isfile(self.filepath):

            with open(self.filepath, 'r') as json_file:
                self.cache = json.load(json_file)
        else:
            self.cache = {}

    def __del__(self):

        with open(self.filepath, 'w') as json_file:
            self.cache = json.store(json_file, self.cache)

    def match(self, sha1):

        if sha1 in self.cache:
            path = self.cache[sha1]

            return os.path.isdir(path)

        return False

    def update(self, sha1, path):

        assert os.path.isdir(path)

        self.cache[sha1] = path
