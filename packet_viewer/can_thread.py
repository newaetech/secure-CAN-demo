import threading

import sys
import time
import os

if sys.platform.startswith("linux"): #assume rpi
    import can
    #sys.exit() #not ready yet
elif sys.platform.startswith('win'): #assume pcan
    import PCANBasic as pcan
else:
    print "System not supported (x86 win or rpi linux only)"
    sys.exit()
import secure_can as seccan

class pican_wrapper():
    def __init__(self):
    #init and connect in same step?
        self.__canbus = can.interface.Bus(channel = 'can0', bustype = 'socketcan_ctypes')
        self.__connected = False
        pass
    def disconnect(self):
        self.__connected = False
        return 0
        pass
    def connect(self, listenonly = True):
        self.__connected = True
        return 0
    def write(self, addr, data):
        pass
    def read(self):
        if self.__connected == False:
            return [-1, 0]
        ret = self.__canbus.recv()
        if ret != None:
            return [0, ret.arbitration_id, list(ret.data)[0:ret.dlc]]
        else:
            return [-1, 0]

class pcan_wrapper():
    def __init__(self):
        self.__canbus = pcan.PCAN_USBBUS1
        self.__caniface = pcan.PCANBasic() #for now
        self.__connected = False
        
    def disconnect(self):
        self.__caniface.Uninitialize(self.__canbus)
        
    def connect(self, listenonly = True):
        self.__caniface.Uninitialize(self.__canbus)
        if listenonly:
            self.__caniface.SetValue(self.__canbus, pcan.PCAN_LISTEN_ONLY, pcan.PCAN_PARAMETER_ON)
            
        result = self.__caniface.Initialize(self.__canbus, pcan.PCAN_BAUD_250K, pcan.PCAN_USB)
        if result == pcan.PCAN_ERROR_OK:
            self.__connected = True
            return True
        else:
            self.print_err("Connect", result)
            return False

    def print_err(self, errstr, error):
        print errstr + ": " + self.__caniface.GetErrorText(error)[1]
            
    def write(self, addr, data):
        if len(data) > 8:
            return False

        if address > 0x1FFFFFFF:
            return False

        msg = pcan.TPCANMsg()
        msg.ID = address
        msg.LEN = len(data) 
        if address > 0x7FF:
            msg.MSGTYPE = pcan.PCAN_MESSAGE_EXTENDED
        else:
            msg.MSGTYPE = pcan.PCAN_MESSAGE_STANDARD
            
        self.__caniface.Write(self.__canbus, msg)
        
    #[addr, message]
    def read(self):
        packet = self.__caniface.Read(self.__canbus)
        if packet[0] == pcan.PCAN_ERROR_OK:
            return [0, packet[1].ID, list(packet[1].DATA)[0:packet[1].LEN]]
        else:
            return [-1, 0]
    
        
class can_thread(threading.Thread):
    """ Implementation of serial running in a thread.
    This will run a thread when the start method is called
    
    Inheriets the threading class.
    """
    def __init__(self, rxcallback):
        threading.Thread.__init__(self)
        self.__quit = False
        if sys.platform.startswith("linux"): #assume rpi
            self.__can = pican_wrapper()
            #sys.exit() #not ready yet
        elif sys.platform.startswith("win"): #assume pcan
            self.__can = pcan_wrapper()
        self.__connected = False
        self.__rxcallback = rxcallback

    #disconnects from pcan
    def disconnect(self):
        self.__can.disconnect()

    #connects to pcan in listen only mode
    def connect(self, listenonly = True):
        return self.__can.connect(listenonly)

    #writes data over can bus with ext_id or base_id address
    def write(self, address, data):
        write(address, data)
        
    def quit(self):
        self.__quit = True
        
    def run(self):
        while not self.__quit:
            ret = self.__can.read()
            if ret[0] == 0:
                self.__rxcallback(ret[1], ret[2])
        print "Can thread exiting.."
        
    

class test_can():
    """ Implementation of serial running in a thread.
    This will run a thread when the start method is called
    
    Inheriets the threading class.
    """
    helpMenu = {
        "quit       - Quit",
        "send       - send seccan encrypted data",
        "Send       - send unencrypted data",
        "connect    - connect to canbus in listen only mode",
        "Connect    - connect to canbus",
        "disconnect - disconnect from canbus",
        "Help       - This menu"
        } 
    def __init__(self):
        self.__quit = False
        self.__can = can_thread(self.rx_from_can)
        self.__can.start()
        self.__connected = False
        self.__encryption = seccan.secure_can()
        self.__data = [0xDE, 0xAD, 0xBE, 0xEF]
        self.__msgid = 0x2D1
        self.__cnt = 0x0
        
    #prints help menu
    def help(self):
        for msg in self.helpMenu:
            print msg
    
    #method running in other thread
    def rx_from_can(self, address, data):
        id_parts = self.__encryption.get_id_cnt(address)
        decrypt_data = self.__encryption.decrypt(data, id_parts[0], id_parts[1])
        os.write(1, 'RX FROM CAN\n-----------\nID = ' + str(hex(id_parts[0])) + '\nCnt = ' + str(hex(id_parts[1])) + '\n')
#voltage = ((decrypt_data[0][1] << 8) | decrypt_data[0][0]) / 4096.0 * 3.3
        pedal = ((decrypt_data[0][1] << 8) | decrypt_data[0][0]) / 40.95
        #pedal = ((decrypt_data[0][1] << 8) | decrypt_data[0][0]) / 40.96
        os.write(1, 'Pedal % = {}'.format(pedal) + '\nDecrypted = {}\n'.format(decrypt_data[1]))
        pass

    def start(self):
        self.help()
        while 1:
            data = raw_input("Enter Command:")
            if data == 'quit' or data == 'q':
                print 'Quiting now!'
                break;
            #send encrypted data
            elif data == 'send' or data == 's':
                print 'Send now!'
                payload = self.__encryption.encrypt(self.__data, self.__msgid, self.__cnt)
                ext_id = self.__encryption.ext_id(self.__msgid, self.__cnt)
                self.__can.write(ext_id, payload)
                self.__cnt += 1
                
            elif data == 'Send' or data == 'S':
                print 'Send now!'
                self.__can.write(0x1eabcdef, [0x01, 0x02])
            elif data == 'connect' or data == 'c':
                self.__connected = self.__can.connect()
                if self.__connected:
                    print 'Connect success'
                else:
                    print 'Connect Failed'
            elif data == 'Connect' or data == 'C':
                self.__connected = self.__can.connect2()
                if self.__connected:
                    print 'Connect success'
                else:
                    print 'Connect Failed'
            elif data == 'disconnect' or data == 'd':
                if(self.__connected):
                    self.__can.disconnect()
            elif data == 'help' or data == '?':
                self.help()
            else:
                print 'Enter something else!'
        self.__can.quit()
        print ('Exiting!!!')
        time.sleep(1)

#--- Main --------------------------------------------------------------------#

def main():
    '''
    Main entry to the test.
    '''
    test = test_can()
    test.start()

    return
################################################################################
#
if __name__ == "__main__":
    main()
