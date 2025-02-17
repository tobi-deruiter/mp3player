from dotenv import load_dotenv
import subprocess as sp
import select
import sys
import os

"""
Class to control bluetooth connections on the raspberry pi.
"""
class BTCTRL:
    # commands used for execute and execute_and_read
    POWER_ON = "bluetoothctl power on"
    AGENT_ON = "bluetoothctl agent on"
    SCAN_ON = "bluetoothctl scan on"
    SCAN_OFF = "bluetoothctl scan off"
    DEVICES = "bluetoothctl devices"
    PAIR = "bluetoothctl pair %s"
    TRUST = "bluetoothctl trust %s"
    UNTRUST = "bluetoothctl untrust %s"
    CONNECT = "bluetoothctl connect %s"
    DISCONNECT = "bluetoothctl disconnect %s"
    REMOVE = "bluetoothctl remove %s"

    # process names used for __procs
    P_SCAN = "scan"
    P_CONN = "connect"
    P_DEVI = "devices"

    # .asoundrc template
    asoundrc_template = "pcm.%s {\n\ttype plug\n\tslave.pcm {\n\t\ttype bluealsa\n\t\tdevice \"%s\"\n\t\tprofile \"a2dp\"\n\t}\n\thint {\n\t\tshow on\n\t\tdescription \"%s\"\n\t}\n}\n\npcm.!default {\n\ttype plug\n\tslave.pcm \"%s\"\n}"

    """
    Initialize the BTCTL class by loading the .env file (used to ge the home directory), making the __procs dictionary,
        making an empty dictionary for devices, and filling in the devices dictionary by getting the trusted devices
    """
    def __init__(self):
        load_dotenv()
        self.__procs = {
            "scan": None,
            "connect": None,
            "devices": None
        }
        self.devices = {}
        for stdout_line in self.execute_and_read(BTCTRL.P_DEVI, BTCTRL.DEVICES):
            if (device_info:=self.valid_device(stdout_line, 2)) != None:
                self.devices[len(self.devices)] = device_info

    """
    Check if a device is a valid one. It is considered valid if it is not already in the devices dictionary
        and if the device name is not the same as the MAC address

    args:
        stdout_line: string given by execute_and_read()
        maxsplit: integer to decide how many times the stdout_line should be split
            and is used to find the MAC address and device name
    """
    def valid_device(self, stdout_line:str, maxsplit:int):
        info = stdout_line.split(" ", maxsplit=maxsplit)
        MAC_address = info[maxsplit-1]
        device_name = info[maxsplit].rstrip('\n')
        if MAC_address.split(":") != device_name.split("-") and [MAC_address, device_name] not in self.devices.values():
            return [MAC_address, device_name]
        return None

    """
    Get input without halting code. This is used to stop the output of scan()
    """
    def get_input(self):
        input_ready, _, _ = select.select([sys.stdin], [], [], 0)
        if input_ready:
            return sys.stdin.readline().rstrip('\n')
        return None
    
    """
    Execute a given command with a given process name.

    args:
        proc: process name (P_SCAN, P_CONN, P_DEVI) used for private variable __proc
        cmd: command to be executed
    """
    def execute(self, proc:str, cmd:str):
        self.__procs[proc] = sp.Popen(cmd.split(" "), stdout=sp.PIPE, universal_newlines=True)
        self.__procs[proc].stdout.close()
        return self.__procs[proc].wait()

    """
    Execute a given command with a given process name and return all command outputs

    args:
        proc: process name (P_SCAN, P_CONN, P_DEVI) used for private variable __proc
        cmd: command to be executed

    returns:
        stdout_line: every line outputted from the given command, returned as they come with yield
    """
    def execute_and_read(self, proc:str, cmd:str):
        self.__procs[proc] = sp.Popen(cmd.split(" "), stdout=sp.PIPE, universal_newlines=True)
        for stdout_line in iter(self.__procs[proc].stdout.readline, ""):
            yield stdout_line

        self.__procs[proc].stdout.close()
        return_code = self.__procs[proc].wait()
        if return_code:
            print("Command:", cmd, "failed. Please try again.")
        
    """
    Begin scanning for new devices to connect to and add valid devices to self.devices.
    """
    def scan(self):
        for stdout_line in self.execute_and_read(BTCTRL.P_SCAN, BTCTRL.SCAN_ON):
            if "NEW" in stdout_line:
                if (device_info:=self.valid_device(stdout_line, 3)) != None:
                    print(device_info[0], device_info[1])
                    self.devices[len(self.devices)] = device_info

            if self.get_input() == "stop":
                break

    def stop_scan(self):
        if self.__procs[BTCTRL.P_SCAN].poll() is None:
            self.__procs[BTCTRL.P_SCAN].kill()
            print("Scanning stopped")
                
    """
    Create .asoundrc file in home directory. This will allow for audio to be played through
        the bluetooth connection

    args:
        d_num: integer corresponding to index in self.devices
    """
    def create_asoundrc(self, d_num:int):
        MAC_Address = self.devices[d_num][0]
        device_name = self.devices[d_num][1]
        pcm_name = device_name.lower().replace(" ", "")
        home_dir = os.getenv("HOME_DIR")
        with open(f"{home_dir}/.asoundrc", "w") as asoundrc:
            asoundrc.write(BTCTRL.asoundrc_template % (pcm_name, MAC_Address, device_name, pcm_name))
    
    """
    Bluetooth connect to given device number.

    args:
        d_num: integer corresponding to index in self.devices
    """
    def connect(self, d_num:int):
        MAC_address = self.devices[d_num][0]
        if self.execute(BTCTRL.P_CONN, BTCTRL.PAIR % MAC_address): print("Pair failed.")       # pair to device
        if self.execute(BTCTRL.P_CONN, BTCTRL.TRUST % MAC_address): print("Trust failed.")     # trust device for automatic reconnection
        self.create_asoundrc(d_num)     # create .asoundrc file so audio can be played through bluetooth connection
        if self.execute(BTCTRL.P_CONN, BTCTRL.CONNECT % MAC_address): print("Connect Failed")  # connect to device
        self.stop_scan()                # stop scanning for devices

    """
    Bluetooth disconnect from given device number.

    args:
        d_num: integer corresponding to index in self.devices
    """
    def disconnect(self, d_num:int):
        MAC_address = self.devices[d_num][0]
        if self.execute(BTCTRL.P_CONN, BTCTRL.DISCONNECT % MAC_address): print("Disconnect failed.")    # disconnect from device

    """
    Forget bluetooth connection to given device number.

    args:
        d_num: integer corresponding to index in self.devices
    """
    def forget(self, d_num:int):
        MAC_address = self.devices[d_num][0]
        if self.execute(BTCTRL.P_CONN, BTCTRL.UNTRUST % MAC_address): print("Untrust failed.")    # untrust device
        if self.execute(BTCTRL.P_CONN, BTCTRL.REMOVE % MAC_address): print("Remove failed.")    # remove device


def main():
    btctl = BTCTRL()

    while (True):
        print("---Options---")
        print("1: scan for devices")
        print("2: get list of devices")
        print("3: connect to a device")
        print("q: quit")

        opt = input("choose an option: ")
        match opt:
            case "1":
                print("Type 'stop' and enter to stop printing")
                btctl.scan()
            case "2":
                print("devices")
                if len(btctl.devices) < 1:
                    print("No available devices")
                else:
                    for d_num, device_info in btctl.devices.items():
                        print(d_num, ":", device_info[0], device_info[1])
            case "3":
                print("connect")
                if len(btctl.devices) < 1:
                    print("No available devices")
                else:
                    for d_num, device_info in btctl.devices.items():
                        print(d_num, ":", device_info[0], device_info[1])
                    choice = input("choose a device to connect to: ")
                    btctl.connect(int(choice))
            case "q":
                # TODO: cleanup subprocesses
                exit()

# if __name__ == "__main__":
#     main()