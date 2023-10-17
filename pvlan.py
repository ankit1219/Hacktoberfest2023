########################################################################################################################
#
#TOPOLOGY :
# 				  ____________       
#  				 |            |   
# 				 |            |     
#                |            |
#  				 | Heavenly-2 |    
#                |  		  |
#  				 |            |     
# 				 |____________|     

# 
#Steps which is followed For this:-
# Step 1:- Configured to the Switch(Heavenly-2)
# Step 2:- Create the monitor sessions in the box.
# Step 3:- Create source vlans on monistor session
# step 4:- verify getting Error message as " " and not causing any cores on the switch.
########################################################################################################################
from ats import tcl
from ats import aetest
from ats.log.utils import banner
import time
import logging
import os
import sys
import re
import pdb
import json
import pprint
import socket
import struct
import inspect
#########################################
# pyATS imports
from pyats.topology import loader
#from pyats import aetest
#from ats.async import pcall
from pyats.async_ import pcall
from pyats.async_ import Pcall
#from unicon.eal.dialogs import Statement, Dialog
#from unicon.eal.expect import Spawn, TimeoutError
#import nxos.lib.nxos.util as util
#import ctsPortRoutines
#import pexpect
#import nxos.lib.common.topo as topo
##########################################
from ats import aetest
from ats.log.utils import banner
from ats.datastructures.logic import Not, And, Or
from ats.easypy import run
from ats.log.utils import banner
import parsergen
from unicon.eal.expect import Spawn
from unicon.eal.dialogs import Statement, Dialog
from unicon.eal.expect import Spawn, TimeoutError
from genie.conf import Genie
import pdb
import sys
import json
import os
########################################

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
global uut1           
global uut1_intf1, uut1_intf2



class ForkedPdb(pdb.Pdb):
    '''A Pdb subclass that may be used
    from a forked multiprocessing child1
    '''
    def interaction(self, *args, **kwargs):
        _stdin = sys.stdin
        try:
            sys.stdin = open('/dev/stdin')
            pdb.Pdb.interaction(self, *args, **kwargs)
        finally:
            sys.stdin = _stdin



################################################################################
####                       COMMON SETUP SECTION                             ####
################################################################################
class common_setup(aetest.CommonSetup):
    @aetest.subsection
    def qos_topo_parse(self,testscript,testbed,R1):
        global uut1
        global uut1_intf1, uut1_intf2

        global uut_m

        global custom
        custom = testbed.custom

        uut1=testbed.devices[R1]
        uut_list=[uut1]

        router_list = [R1]

    @aetest.subsection
    def connect_to_devices(self,testscript,testbed,R1):
        global uut1

        #connect to n7k devices
        #uut1_mgmt = uut1.connect(alt_start='alt')
        #ForkedPdb().set_trace()
        log.info("Connecting to Device:%s"%uut1.name)
        try:
            uut1.connect()
            log.info("Connection to %s Successful..."%uut1.name)
        except Exception as e:
            log.info("Connection to %s Unsuccessful "\
                      "Exiting error:%s"%(uut1.name,e))
            self.failed(goto=['exit'])


################################################################################
###                          TESTCASE BLOCK                                  ###
################################################################################

###############################################################################################
# Test case 1 :
###############################################################################################

class Sys_monitor_ses_CSCwf19968(aetest.Testcase):

    "Verifying source vlan limit in Monitor session"

    @aetest.test
    def tc01_test(self):
        ##################################################################

        log.info(banner("Collecting internal build version"))
        cmd = "sh version internal build-identifier"
        output = uut1.execute(cmd)
        
        log.info(banner("Create monitor session"))
        cmd = """monitor session 11
                 source vlan 2-3967
              """
        output = uut1.configure(cmd, timeout=2400)
        op=uut1.configure("sh cores")
        lines = op.split("\n")
        if len(lines) >= 3:
            extracted_value = lines[2].strip()
            print(extracted_value)
        else:
            print("Invalid input")
        match = re.search("ERROR: Number of source vlans exceeds maximum.",output)
        if match :
            log.info(banner("output is throwing an ERROR :Number of source vlans exceeds maximum. 0 vlans are already applied, please change the config to only include 32 additional vlans, which is expected."))
            self.passed("Testcase is Passed")
        else :	
            log.error("Failed")
            cmd1="""sh cores"""
            output=uut1.configure(cmd1)
            match = re.search("vsh.bin",output)
            if match :
                log.info(banner("Testcase is Failed"))
            else :
                log.info(banner("chrash not seen, re-configure source vlan again"))
                output = uut1.configure(cmd, Timeout=2400)
                output=uut1.configure(cmd1)
                match = re.search("vsh.bin",output)
                if match :
                    log.info(banner("Testcase is Failed, core seen log a bug."))
                    self.failed(goto=['common_cleanup'])
            self.failed(goto=['common_cleanup'])
            
            
        
        
################################################################################
####                       COMMON CLEANUP SECTION                           ####
################################################################################
class common_cleanup(aetest.CommonCleanup):
#ForkedPdb().set_trace()
    @aetest.subsection
    def remove_configuration(self):

        ##############################################################
        # clean up the session, release the ports reserved and cleanup the dbfile
        ##############################################################


        log.info('remove monitor session in {0}'.format(uut1))
        cmd = """ no monitor session 11 """
        uut1.configure(cmd)
        
if __name__ == '__main__': # pragma: no cover
    import argparse
    from ats import topology
    parser = argparse.ArgumentParser(description='standalone parser')
    parser.add_argument('--testbed', dest='testbed', type=topology.loader.load)
    parser.add_argument('--R1', dest='R1', type=str)
    parser.add_argument('--mode',dest = 'mode',type = str)
    args = parser.parse_known_args()[0]
    aetest.main(testbed=args.testbed,
                R1_name=args.R1,
                mode = args.mode,
                pdb = True)
