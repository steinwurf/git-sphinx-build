#! /usr/bin/env python
# encoding: utf-8

import os


class BuildInfo(object):
    """ Stores information about a specific build.

    Information is added by different steps in the build process in a
    write once fashion. Such that we avoid accidental overwrites.

    """

    valid_keys = {
        "config_file": "filename of the Sphinx configuration \
            file as a string",
        "config_dir": "The directory containing the config_file \
            as a string",
        "config_file_path": "The full path to the config_file \
            as a string",
        "sphinx_env": "Dict like os.environ, but where the PATH and PYTHONPATH \
            variables have been modified to contains the necessary tools \
            for building the docs.",
        "slug": "Human readable name for a specific version of the docs",
        "repository_path": "Path to the repsository",
        "source_path": "Path to the documentation sources",
        "output_path": "Path to the output",
        "type": "The type of build"
    }

    def __init__(self):
        # Because we override __setattr__ we have to call the
        # __setattr__ in the base to avoid recursion
        object.__setattr__(self, 'info', {})

    def __getattr__(self, attribute):
        """ Return the value corresponding to the attribute.
        :param attribute: The name of the attribute to return as a string.
        :return: The attribute value, if the attribute does not exist
            return None
        """
        self._check_key(attribute=attribute)

        if attribute in self.info:
            return self.info[attribute]
        else:
            raise AttributeError("No key {} in BuildInfo".format(attribute))

    def __setattr__(self, attribute, value):
        """ Sets a dependency attribute.
        :param attribute: The name of the attribute as a string
        :param value: The value of the attribute
        """
        self._check_key(attribute=attribute)

        if attribute in self.info:
            raise AttributeError("Attribute {} read-only.".format(attribute))
        else:
            self.info[attribute] = value

    def __contains__(self, attribute):
        """ Checks if the attribute is available.
        :return: True if the attribute is available otherwise False
        """
        self._check_key(attribute=attribute)

        return (attribute in self.info)

    def _check_key(self, attribute):
        if attribute not in BuildInfo.valid_keys.keys():
            raise AttributeError("Invalid attribute key {} valid {}".format(
                attribute, BuildInfo.valid_keys.keys()))
