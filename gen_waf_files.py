'''

###
# WARNING: This will overwrite your <project>.waf_files with a generated one. Save a backup. Use at your own risk.
###

Usage
1. Place this file in your lumberyard\dev folder. It should be alongside lmbr_waf.bat, lmbr_waf.sh, etc.
2. run: autogen_project_waf.py <name_of_gem_case_sensitive>

Description: This script looks in the engine_root for for the gem, literally using the gem name to locate the folder. It is case sensitive.
This script will scan the Gem/Code for Includes and Source, and generates (and overwrites) a new .waf_files.

You'll want to run lmbr_waf configure after this.

e.g.:
gen_waf_files.py MySampleProject && lmbr_waf configure

'''
import os
from os import walk
import json
import sys


def find_engine_root():
    fallback_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

    if not os.path.isfile('engine.json'):
        return fallback_dir

    with open("engine.json") as handle:
        engine_data = json.load(handle)
        if "ExternalEngiePath" in engine_data:
            return engine_data["ExternalEnginePath"]

    return fallback_dir


class WafGenerator:
    ENGINE_DIR = ""
    GEM_NAME = ""

    tree = {
        "none": {
            "Source": [],
        },
        "auto": {
            "Source": [],
        },
    }

    def __init__(self, gem_name, engine_dir):
        self.GEM_NAME = gem_name
        self.ENGINE_DIR = engine_dir

    def GetDict(self):
        return self.tree

    def GetJsonOutput(self):
        return json.dumps(self.tree, indent=4, sort_keys=True)

    def Write(self):
        with open(self.__get_waf_path(), 'w') as handle:
            handle.write(self.GetJsonOutput())

    def Generate(self):
        proj_dir = self.__get_gem_code_path()
        for (dirpath, dirnames, filenames) in walk(proj_dir):
            # clean up the path
            t_dirpath = dirpath.replace(proj_dir, '').replace("\\","/")[1:]

            if "Source" not in t_dirpath and "Include" not in t_dirpath:
                continue

            for filename in filenames:
                # precompiled files go in the none section
                # do other files go there?
                if '_precompiled' in filename:
                    if t_dirpath not in self.tree['none']:  # Create the "Category" in our tree, if needed
                        self.tree['none'][t_dirpath] = []

                    self.tree['none'][t_dirpath].append("{}/{}".format(t_dirpath, filename))
                    continue

                # only made it here if not a precompiled header/source
                if t_dirpath not in self.tree['auto']:  # Create the "category" in our tree, if needed
                    self.tree['auto'][t_dirpath] = []

                self.tree['auto'][t_dirpath].append("{}/{}".format(t_dirpath, filename))

    def __get_gem_code_path(self):
        return os.path.join(self.ENGINE_DIR, self.GEM_NAME, "Gem", "Code")

    def __get_waf_path(self):
        return os.path.join(self.__get_gem_code_path(), "{}.waf_files".format(self.GEM_NAME.lower()))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Specify a project to generate. See the comment in the script to understand usage.")
        quit()

    waf_generator = WafGenerator(sys.argv[1], find_engine_root())
    waf_generator.Generate()

    # Print the output
    #print(waf_generator.GetJsonOutput())

    # Write the waf file
    waf_generator.Write()
    