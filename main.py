import socket
import argparse
import sys

import os
import xml.etree.ElementTree as ET
import vdf

from copy import deepcopy
from tabulate import tabulate


def saveNewServerInfoToSteamFile(serverName, ipAddress, queryPort, steamServerListPath):
    completeAddress = ipAddress + ":" + str(queryPort)
    # load and parse steam vdf server list
    d = vdf.load(open(steamServerListPath))
    d1 = deepcopy(d)
    maxIndex = -1
    for key, _ in d['Filters']['favorites'].items():
        if int(key) > maxIndex:
            maxIndex = int(key)

    # create new server in vdf dict
    d1['Filters']['favorites'][str(maxIndex + 1)] = {'name': serverName, 'address': completeAddress, 'LastPlayed': '0',
                                                    'appid': '0', 'accountid': '0'}
    vdf.dump(d1, open(steamServerListPath, 'w'), pretty=True)


def updateServer(updateServerList, steamServerListPath):
    print('Start updating servers')
    d = vdf.load(open(steamServerListPath))
    d1 = deepcopy(d)
    for key, value in d['Filters']['favorites'].items():
        for server in updateServerList:
            if value['name'] == server[0]:
                d1['Filters']['favorites'][key] = {'name': server[0],
                                                  'address': socket.gethostbyname(server[1]) + ':' + str(server[2]),
                                                  'LastPlayed': '0', 'appid': '0', 'accountid': '0'}

    # save updated servers to steam server list file
    vdf.dump(d1, open(steamServerListPath, 'w'), pretty=True)


def deleteServerFromSteamFile(serverName, steamServerListPath):
    print('Start deleting servers')
    d = vdf.load(open(steamServerListPath))
    serverFound = False
    for key, value in d['Filters']['favorites'].items():
        if value['name'] == serverName:
            deleteKey = key
            serverFound = True
            break

    if serverFound:
        # only delete item if server found else continue fixing up server indexing
        d['Filters']['favorites'].pop(key)

    d1 = deepcopy(d)
    # fix up server indexing if necessary
    keyIndex = 0
    # clear up server list
    d1['Filters']['favorites'].clear()
    for key in d['Filters']['favorites'].keys():
        keyIndex += 1
        d1['Filters']['favorites'][keyIndex] = d['Filters']['favorites'][key]

    # save updated servers to steam server list file
    vdf.dump(d1, open(steamServerListPath, 'w'), pretty=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--update", help="only update servers and shutdown after", action="store_true")
    parser.add_argument("-r", "--reset", help="resets/deletes config file and create a new blank", action="store_true")
    parser.add_argument("configPath", help="path of the config file")
    args = parser.parse_args()

    print("Welcome to SteamNonStaticIPUpdater")

    if args.reset:
        # reset config file
        os.remove(args.configPath)

    if os.path.exists(args.configPath):
        # load
        print("load config file")
        configFile = open(args.configPath, "r")

        # load cfg xml
        tree = ET.parse(configFile)
        root = tree.getroot()

        for elem in root:
            if elem.tag == 'steamPaths':
                # find server list path
                steamServerFilePath = elem.find('ServerListPath').text

        configFile.close()
    else:
        # create cfg xml
        configFile = open(args.configPath, "w")

        print("wait for steam server file path")
        steamServerFilePath = input()
        steamServerFilePath += "\\serverbrowser_hist.vdf"

        config = ET.Element('config')
        steamPaths = ET.SubElement(config, 'steamPaths')
        ServerFilePath = ET.SubElement(steamPaths, 'ServerListPath')
        ServerFilePath.text = steamServerFilePath

        a = ET.tostring(config, encoding="unicode")
        configFile.write(a)

        print("new config file created with %s as server file path" % steamServerFilePath)

        configFile.close()

    #print(steamServerFilePath)

    configFile = open(args.configPath, "r")
    # parse cfg xml file
    tree = ET.parse(args.configPath)
    root = tree.getroot()

    if args.update:
        # only update

        # update all server from cfg file in steam server list
        print('Read config file and find all server')
        updateServerList = []
        for elem in root:
            if elem.tag == 'Server':
                updateServerList.append((elem.get('name'), elem.get('hostname'), int(elem.get('queryPort'))))

        print('Found %s servers to update' % len(updateServerList))
        updateServer(updateServerList, steamServerFilePath)
        print('Finished updating Servers')

        sys.exit(0)

    while True:
        print("Input Command")
        newUserInput = input()
        if newUserInput=='create':
            # add new server to update list
            print('Server Name')
            serverName = input()
            print('Hostname')
            hostname = input()
            print('QueryPort')
            queryPort = int(input())

            # add new server to cfg xml
            element = ET.SubElement(root, 'Server', {'name':serverName, 'hostname':hostname, 'queryPort':str(queryPort)})

            # save new server to cfg xml
            tree.write(args.configPath)

            # save new server to steam server list
            saveNewServerInfoToSteamFile(serverName, socket.gethostbyname(hostname), queryPort, steamServerFilePath)

        elif newUserInput == 'delete':
            print('Server Name')
            serverName = input()

            print('Do you really want to delete Server %s [y/n]' % serverName)
            answer = input()
            if answer != 'y':
                continue

            print('Start deleting server from cfg xml file')
            # delete server from cfg xml
            for elem in root:
                if elem.tag == 'Server' and elem.get('name') == serverName:
                    root.remove(elem)
                    break

            # save new server to cfg xml
            tree.write(args.configPath)

            print('Start deleting server from steam server list file')
            # delete server from steam server list
            deleteServerFromSteamFile(serverName, steamServerFilePath)

            print('Server %s removed' % serverName)

        elif newUserInput == 'list':
            serverCount = 0
            serverList = []
            for elem in root:
                if elem.tag == 'Server':
                    serverCount += 1
                    serverList.append([serverCount, elem.get('name'), elem.get('hostname'), elem.get('queryPort')])

            print("\n"+tabulate(serverList, headers=['Server Nr', 'Server name', 'hostname', 'QueryPort'],
                  tablefmt='orgtbl')+"\n")

        elif newUserInput == 'update':
            # update all server from cfg file in steam server list
            print('Read config file and find all server')
            updateServerList = []
            for elem in root:
                if elem.tag == 'Server':
                    updateServerList.append((elem.get('name'), elem.get('hostname'), int(elem.get('queryPort'))))

            print('Found %s servers to update' % len(updateServerList))
            updateServer(updateServerList, steamServerFilePath)
            print('Finished updating Servers')

        elif newUserInput == 'exit':
            # terminate updater
            break

    configFile.close()

    print('Bye Bye from SteamNonStaticIPUpdater')
