import os
import sys
import paramiko
import time
from getpass import getpass
from datetime import datetime
import json
from Crypto import Crypto
import time
# import urllib3
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from F5 import F5
from Forti import Forti
import asyncio
# import aiohttp

async def iterate(RUN_ASYNC=False):
    mainDir = sys.argv[1]
    print(f"[*] {mainDir}")
    mainCrypto = Crypto()
    port = 443

    f5Token = mainCrypto.encrypt_random_key(getpass("Enter f5 token"))
    fortiToken = mainCrypto.encrypt_random_key(getpass("Enter forti token"))
    
    now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    outputDir = "output" + "-" + now
    if not os.path.exists(f"{mainDir}/{outputDir}"):
        os.mkdir(f"{mainDir}/{outputDir}")
    
    logFile = open(f"{mainDir}/{outputDir}/log.txt", "w")
    logFile.write(f"[*] {mainDir}" + "\n")

    for dir in os.listdir(f"{mainDir}/api"):
        print(f"[*] {dir}")
        logFile.write(f"[*] {dir}" + "\n")
        
        commandsFile = open(f"{mainDir}/api/{dir}/commands.txt", 'r')
        devicesFile = open(f"{mainDir}/api/{dir}/devices.txt", 'r')
        commands = commandsFile.read().splitlines()
        devices = devicesFile.read().splitlines()
        commandsFile.close()
        devicesFile.close()

        print(f"[*] Devices: {devices}")
        print(f"[*] Commands to run: {commands}")
        logFile.write(f"[*] Devices: {devices}" + "\n")
        logFile.write(f"[*] Commands to run: {commands}" + "\n")


        if dir == 'f5' or dir == 'f501' or dir == 'f502':  
            token = f5Token

        if dir == 'forti' or dir == 'forti01' or dir == 'forti02': 
            token = fortiToken
            

        for device in devices:
            outFilePerDevice = open(f"{mainDir}/{outputDir}/{device}.txt", "w")
            print (f"[*] {device}")
            logFile.write(f"[*] {device}" + "\n")

            if dir == 'f5' or dir == 'f501' or dir == 'f502':
                api = F5(device, port, mainCrypto.decrypt_random_key(token))

            if dir == 'forti' or dir == 'forti01' or dir == 'forti02': 
                api = Forti(device, port, mainCrypto.decrypt_random_key(token))
            
            if RUN_ASYNC:
                tasks = []
                for command in commands:
                    # time.sleep(api.sleepTimeCommand)
                    task = asyncio.ensure_future(api.runCommand(command))
                    tasks.append(task)
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                for r in responses:
                    out = r
                    print(json.dumps(out))
                    outFilePerDevice.write(json.dumps(out) + "\n")
            else:
                for command in commands:
                    time.sleep(api.sleepTimeCommand)
                    out = await api.runCommand(command)
                    print(json.dumps(out))
                    outFilePerDevice.write(json.dumps(out) + "\n")

            await api.closeSession()
            outFilePerDevice.close()  
            
    print("\n[*] DONE!\n")
    logFile.write("\n[*] DONE!\n")
    logFile.close()

async def main():
    if len(sys.argv) == 2:
        await iterate()
    else:
        print("Run api_multi.py <folder name>")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())