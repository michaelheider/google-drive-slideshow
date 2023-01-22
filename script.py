#!/usr/bin/python3

import os
import random
from dotenv import load_dotenv

from customTypes import *
from fileSystem import FileSystem


class Main:
    __env: env
    __fileSystem: FileSystem

    class __DirectoryEmptyException(Exception):
        pass

    def __readEnv(self) -> None:
        load_dotenv()
        env = {
            'DRIVE_ID': os.getenv('DRIVE_ID'),
            'ROOT_FOLDER_ID': os.getenv('ROOT_FOLDER_ID'),
            'CREDENTIALS_FILE': os.getenv('CREDENTIALS_FILE'),
            'TOKEN_FILE': os.getenv('TOKEN_FILE', 'token.json'),
            'CACHE_RETENTION': int(os.getenv('CACHE_RETENTION', 30)),
            'CACHE_FILE': os.getenv('CACHE_FILE', 'cache.json'),
        }
        if env['DRIVE_ID'] and env['ROOT_FOLDER_ID'] and env['CREDENTIALS_FILE']:
            self.__env = env
        else:
            raise ValueError(
                'Environment variables are invalid. Check your `.env`.')

    def __chooseRandomFileRec(self, folder: Folder) -> tuple[File, str]:
        hasFiles = folder['nrFiles'] > 0
        n = folder['nrFolders']
        if hasFiles > 0:
            n += 1
        if n == 0:
            raise self.__DirectoryEmptyException(
                "Directory '{0}' is empty.".format(folder['id']))
        rFolder = random.randint(0, n-1)
        if hasFiles and rFolder == n-1:
            # pick file from current folder
            rFile = random.randint(0, folder['nrFiles']-1)
            file: File = self.__fileSystem.filterNodes(
                folder['nodes'], False, True)[rFile]
            return file, file['name']
        else:
            # descend one layer
            nextNode = self.__fileSystem.filterNodes(
                folder['nodes'], True, False)[rFolder]
            nextFolder = self.__fileSystem.getFolder(nextNode['id'])
            file, path = self.__chooseRandomFileRec(nextFolder)
            return file, nextFolder['name'] + "/" + path

    def __chooseRandomFileFirstLevel(self) -> tuple[File, str]:
        topLevelFolder = self.__fileSystem.getFolder(
            self.__env['ROOT_FOLDER_ID'])
        nrFolders = topLevelFolder['nrFolders']
        topLevelFolders = self.__fileSystem.filterNodes(
            topLevelFolder['nodes'], True, False)
        r = random.randint(0, nrFolders-1)
        nextFolder = self.__fileSystem.getFolder(topLevelFolders[r]['id'])
        file, path = self.__chooseRandomFileRec(nextFolder)
        return file, nextFolder['name'] + "/" + path

    def __chooseRandomPicture(self) -> tuple[File, str]:
        """
        Choose a random picture.
        Retry in case of errors.
        """

        ###########################################################################################
        ###########################################################################################
        ###########################################################################################
        # TODO
        # make sure the file is an image (else rejection sampling)
        # download the file
        # display the file
        # find a way to still display the file while we are downloading the next one in the background

        errors = 0
        while errors < 3:
            try:
                return self.__chooseRandomFileFirstLevel()
            except self.__DirectoryEmptyException:
                # try again, rejection sampling
                print("Hit empty directory. Retry.")
                errors += 1
        raise RuntimeError("Choosing a random picture failed too many times.")

    def run(self) -> None:
        file, path = self.__chooseRandomPicture()
        print(path)

    def __init__(self) -> None:
        self.__readEnv()
        self.__fileSystem = FileSystem(self.__env)

        # sanity check
        # topLevelFolder = self.__fileSystem.getFolder(self.__env['ROOT_FOLDER_ID'])
        # print("sanity check Google Drive API")
        # print("top level name:      '{0}'".format(topLevelFolder['name']))
        # print("top level subfolders: {0:>3}".format(
        #     topLevelFolder['nrFolders']))
        # print("top level files:      {0:>3}".format(topLevelFolder['nrFiles']))


if __name__ == '__main__':
    instance = Main()
    instance.run()
