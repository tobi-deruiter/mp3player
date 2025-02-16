from dotenv import load_dotenv
import subprocess as sp
import select
import sys
import os

class BTCTRL:
    POWER_ON = "bluetoothctl power on"
    AGENT_ON = "bluetoothctl agent on"

    SCAN_ON = "bluetoothctl scan on"
    SCAN_OFF = "bluetoothctl scan off"
    
    DEVICES = "bluetoothctl devices"

    asoundrc_template = "pcm.%s {\n\ttype plug\n\tslave.pcm {\n\t\ttype bluealsa\n\t\tdevice \"%s\"\n\t\tprofile \"a2dp\"\n\t}\n\thint {\n\t\tshow on\n\t\tdescription \"%s\"\n\t}\n}\n\npcm.!default {\n\ttype plug\n\tslave.pcm \"%s\"\n}"

    def __init__(self):
        load_dotenv()
        self.__procs = {
            "scan": None,
            "pair": None,
            "connect": None,
            "devices": None
        }
        self.devices = {}
        for stdout_line in self.execute_and_read("devices", BTCTRL.DEVICES):
            if (device_info:=self.valid_device(stdout_line, 2)) != None:
                self.devices[len(self.devices)] = device_info

    def valid_device(self, stdout_line:str, maxsplit:int):
        info = stdout_line.split(" ", maxsplit=maxsplit)
        MAC_address = info[maxsplit-1]
        device_name = info[maxsplit].rstrip('\n')
        if MAC_address.split(":") != device_name.split("-") and [MAC_address, device_name] not in self.devices.values():
            return [MAC_address, device_name]
        return None

    def get_input(self):
        input_ready, _, _ = select.select([sys.stdin], [], [], 0)
        if input_ready:
            return sys.stdin.readline().rstrip('\n')
        return None

    def execute_and_read(self, proc:str, cmd:str):
        self.__procs[proc] = sp.Popen(cmd.split(" "), stdout=sp.PIPE, universal_newlines=True)
        for stdout_line in iter(self.__procs[proc].stdout.readline, ""):
            yield stdout_line

        self.__procs[proc].stdout.close()
        return_code = self.__procs[proc].wait()
        if return_code:
            print("Command:", cmd, "failed. Please try again.")
        
    def scan(self):
        for stdout_line in self.execute_and_read("scan", BTCTRL.SCAN_ON):
            if "NEW" in stdout_line:
                if (device_info:=self.valid_device(stdout_line, 3)) != None:
                    print(device_info[0], device_info[1])
                    self.devices[len(self.devices)] = device_info

            if self.get_input() == "stop":
                break
                
    def create_asoundrc(self, d_num:int):
        MAC_Address = self.devices[d_num][0]
        device_name = self.devices[d_num][1]
        pcm = device_name.lower().replace(" ", "")
        home_dir = os.getenv("HOME_DIR")
        with open(f"{home_dir}/.asoundrc", "w") as asoundrc:
            asoundrc.write(BTCTRL.asoundrc_template % (pcm, MAC_Address, device_name, pcm))
    
    def connect(self, d_num:int):
        MAC_address = self.devices[d_num][0]
        for stdout_line in self.execute_and_read("connect", f"bluetoothctl pair {MAC_address}"):
            if "Pairing successful" in stdout_line:
                print(stdout_line, end="")

        for stdout_line in self.execute_and_read("connect", f"bluetoothctl trust {MAC_address}"):
            if "trust successful" in stdout_line:
                print(stdout_line, end="")

        self.create_asoundrc(d_num)
        
        for stdout_line in self.execute_and_read("connect", f"bluetoothctl connect {MAC_address}"):
            if "Connection successful" in stdout_line:
                print(stdout_line, end="")


if __name__ == "__main__":
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