import os, sys, boto3
import argparse
import subprocess
import yaml


from typing import List, Set


rootdir = os.path.dirname(__file__)
configfile = os.path.join(rootdir, "config/config.yaml")


UnittestFieldName = "Unittests"
UnittestFolderName = "Folder"
UnittestFileList = "Files"


def loadConfig() -> dict:
    config = {}
    with open(configfile, "r") as c:
        config = yaml.load(c)
    if not config:
        raise Exception("Config File Missing")
    return config


def hasUnittests(config: dict) -> bool:
    return UnittestFieldName in config


def hasTestFolder(config: dict) -> bool:
    return hasUnittests(config) \
       and UnittestFolderName in config[UnittestFieldName]


def getTestFolder(config: dict) -> str:
    if hasTestFolder(config):
        return config[UnittestFieldName][UnittestFolderName]
    raise Exception("Config doesn't contain Testfolder path")


def hasTestFiles(config: dict) -> bool:
    return hasUnittests(config) \
       and UnittestFileList in config[UnittestFieldName] \
       and isinstance(config[UnittestFieldName][UnittestFileList], list) \
       and len(config[UnittestFieldName][UnittestFileList]) > 0


def getTestFiles(config: dict) -> Set[str]:
    if not hasTestFiles(config):
        raise Exception("Config hasn't specified any files")
    testfolder = getTestFolder(config)
    testfiles = config[UnittestFieldName][UnittestFileList]
    path = os.path.join(rootdir, testfolder)
    return set(map(lambda x: os.path.join(path, x), testfiles))


def getFolderContent(testfolder: str) -> Set[str]:
    path = os.path.join(rootdir, testfolder)
    files = os.listdir(path)
    files = filter(lambda x: x.endswith(".py"), files)
    files = map(lambda x: os.path.join(path, x), files)
    return set(files)


def checkTestFiles(config: dict, testfolder: str):
    if not hasTestFiles(config):
        raise Exception("No specific Testfield specified in config file")
    allFiles = getFolderContent(testfolder)
    testFiles = getTestFiles(config)
    if len(testFiles) < 1:
        raise Exception("List of Testfiles is empty")
    if not testFiles.issubset(allFiles):
        raise Exception("Files missing: {}".format(testFiles.difference(allFiles)))
    return


def runTest(testfile: str) -> int:
    exec_cmd = " ".join(["python3", testfile])
    try:
        subprocess.check_output(exec_cmd, shell = True)
    except:
        return 1
    return 0

def runTests():
    config = loadConfig()
    if not hasUnittests(config):
        print("No Tests found")
    if not hasTestFolder(config):
        print("No Testfolder found")
    testfolder = getTestFolder(config)
    files = []
    if hasTestFiles(config):
        files = getTestFiles(config)
        checkTestFiles(config, testfolder)
    else:
        files = getFolderContent(testfolder)
    for t in files:
        r = runTest(t)
        if r != 0:
            return 1
        return 0

if __name__ == "__main__":
    runTests()
