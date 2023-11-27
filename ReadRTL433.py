#-----------------------------------------------------------------------------
#   FILE:   ReadRTL433.py
#   AUTHOR: Sean Wilson
#   DATE:   11/26/2003
#
#   COPYRIGHT (C) 2023  PVE, Inc.
#
#   This module reads a JSON output file from rtl_433 and parses out the last
#   entries for a given set of device IDs, filling in a dictionary collection
#   of telemetry entries.
#
#   The module will also trim the output file to only include the last entries
#   of these devices, to keep the output file from growing too large.
#-----------------------------------------------------------------------------
import json

class RTL433Reader:
    
    #-----------------------------------------------------
    #   Function to initialize the object.
    #
    #   Inputs:
    #       - szPath        path to rtl_433 output file
    #       - bTrim         flag to trim the output file
    #-----------------------------------------------------
    def __init__(self, szPath, bTrim):
        self.path = szPath
        self.trim = bTrim

        # define telemetry dictionary 
        self.telemetry = {
            "temp"  : "",
            "humid" : "",
            "wind"  : ""
        }


    #-----------------------------------------------------
    #   Function to get telemetry from the rtl_433 output
    #   file.
    #
    #   Returns:
    #       dictionary object containing telemetry
    #-----------------------------------------------------
    def GetDevices(self):
        file = open("DeviceList.json", "r")
        oContents = json.loads(file.read())
        file.close()

        return list(oContents["devices"])


    #-----------------------------------------------------
    #   Function to get telemetry from the rtl_433 output
    #   file.
    #
    #   Returns:
    #       dictionary object containing telemetry
    #-----------------------------------------------------
    def GetTelemetry(self):
        bDone = False

        # get list of devices to search for
        aoSearchDevices = {}
        aoDevices = self.GetDevices()
        for oDevice in aoDevices:
            aoSearchDevices[oDevice["id"]] = oDevice
        print ("- checking", len(aoSearchDevices), "devices")

        # read output file entries
        oOutFile = open(self.path, "r")
        aoEntries = oOutFile.readlines()
        oOutFile.close()
        print ("- read", len(aoEntries), "entries")

        iIndex = len(aoEntries) - 1  # start at end of file
        while (not bDone): 
            if (len(aoSearchDevices) > 0):
                # we still have devices to find
                oEntry = json.loads(aoEntries[iIndex])
                print("- entry:", oEntry)
                if (oEntry["id"] in aoSearchDevices):
                    # valid device entry, so process it
                    oModel = aoSearchDevices[oEntry["id"]]
                    for oItem in oModel["telemetry"]:
                        self.telemetry[oItem["newfield"]] = oEntry[oItem["logfield"]]

                    # remove device, so we don't process any more entries for it
                    del aoSearchDevices[oEntry["id"]]

                # decrement the index line, stopping if we're at the beginning
                iIndex -= 1
                if (iIndex <= 0):
                    bDone = True

            else:
                # no more devices-- we're done!
                bDone = True

        # trim file, as necessary
        if (self.trim):
            self.TrimFile(iIndex, aoEntries)

        return self.telemetry


    #-----------------------------------------------------
    #   Function to trim the rtl_433 output file to the 
    #   last device line read.
    #
    #   Inputs:
    #       - iIndex    index of last read item
    #       - aoEntries collection of output entries
    #
    #   Returns:
    #       dictionary object containing telemetry
    #-----------------------------------------------------
    def TrimFile(self, iIndex, aoEntries):
        
        oFile = open(self.path, "w")

        oRange = range(iIndex, len(aoEntries))
        print("- length:", len(aoEntries))
        print("- Index:", iIndex)
        print("- range:", oRange)

        for iCounter in oRange:
            oFile.write(aoEntries[iCounter])

        oFile.close
