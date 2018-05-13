#! /usr/bin/env python
# encoding: utf-8

import os


class Sphinx(object):

    def __init__(self, virtualenv, prompt):
        """
        :param runner: A command.run function.
        """
        self.virtualenv = virtualenv
        self.prompt = prompt

    def build(self, source_path, output_path, cwd):

        assert os.path.isdir(source_path)
        assert os.path.isdir(cwd)

        # Running sphinx-build will fail if the repository does
        # not have working docs for the given branch, tag etc.
        docs_path = self.find_configuration(source_path=source_path)

        # Create the environment (with sphinx installed etc)
        env = self.create_environment(docs_path=docs_path, cwd=cwd)

        if not os.path.isdir(output_path):
            os.makedirs(output_path)

        command = ['sphinx-build', '-b', 'html', docs_path, output_path]
        self.runner(command=command, cwd=cwd, env=env)

    def create_environment(self, docs_path, cwd):

        # Check if there is a requirements.txt file in the docs_path
        # if so we install it
        requirements_path = os.path.join(docs_path, 'requirements.txt')

        if os.path.isfile(requirements_path):

            with open(requirements_path, 'r') as requirements_file:
                requirements = requirements_file.read()

            name = self.environment_name(requirements=requirements)
            env = self.virtualenv.create(name=name)

            self.runner('python -m pip install -r {}'.format(
                requirements_path), cwd=cwd, env=env)

        else:

            name = self.environment_name(requirements='sphinx')
            env = self.virtualenv.create(name=name)

            self.runner('python -m pip install sphinx', cwd=cwd, env=env)

        return env

    def environment_name(self, requirements):

        # The Python executable
        python = sys.executable
        python_hash = hashlib.sha1(
            python.encode('utf-8')).hexdigest()[:6]

        # The requirements
        requirements_hash = hashlib.sha1(
            requirements.encode('utf-8')).hexdigest()[:6]

        name = 'sphinx-virtualenv-' + requirements_hash + '-' + python_hash

        return name

    def find_configuration(self, source_path):
        """ Find the Sphinx conf.py file.

        :return: The directory containing the Sphinx conf.py file
        """

        for root, _, filenames in os.walk(source_path):
            if 'conf.py' in filenames:
                return root

        raise run_error.RunError("No conf.py")
