import threading
import PCANBasic as pcan
import sys
import time
import os

import secure_can as seccan
        
class can_thread(threading.Thread):
    """ Implementation of serial running in a thread.
    This will run a thread when the start method is called
    
    Inheriets the threading class.
    """
    def __init__(self, rxcallback):
        threading.Thread.__init__(self)
        self.__quit = False
        self.__canbus = pcan.PCAN_USBBUS1
        self.__caniface = pcan.PCANBasic()
        self.__connected = False
        self.__rxcallback = rxcallback

    #disconnects from pcan
    def disconnect(self):
        self.__caniface.Uninitialize(self.__canbus)

    #connects to pcan in listen only mode
    def connect(self, listenonly = True):
        self.__caniface.Uninitialize(self.__canbus)
        if listenonly:
			self.__caniface.SetValue(self.__canbus, pcan.PCAN_LISTEN_ONLY, pcan.PCAN_PARAMETER_ON)
			
        result = self.__caniface.Initialize(self.__canbus, pcan.PCAN_BAUD_250K, pcan.PCAN_USB)
        if result == pcan.PCAN_ERROR_OK:
            print "Connected great" 
            self.__connected = True
        else:
            print "Connection did not work " + str(hex(result)) 
        return self.__connected

    #writes data over can bus with ext_id or base_id address
    def write(self, address, data):
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

        try:
            for x in range(0, len(data)):
                msg.DATA[x] = data[x] 
            print "Sending ID = " + str(hex(msg.ID)) 
            print "Length = " + str(msg.LEN)
            for x in range(0, msg.LEN):
                sys.stdout.write(str(hex(msg.DATA[x])) + " ")
            self.__caniface.Write(self.__canbus, msg) 
        except:
            print "Unexpected error:", sys.exc_info()[0]            
        pass
		
    def quit(self):
        self.__quit = True
    def run(self):
        while not self.__quit:
            ret = self.__caniface.Read(self.__canbus)
            if ret[0] == pcan.PCAN_ERROR_OK:
                self.__rxcallback(ret[1].ID, list(ret[1].DATA)[0:ret[1].LEN] )
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
