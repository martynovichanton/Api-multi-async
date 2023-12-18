import os
import sys
import paramiko
import time
from getpass import getpass
from datetime import datetime
import json
from Crypto import Crypto
import time
import gc
# import urllib3
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import asyncio
import aiohttp
import random

class F5():
    def __init__(self, ip, port, token):
        self.session = aiohttp.ClientSession()
        self.crypto = Crypto()
        self.ip = ip
        self.port = port
        self.sleepTimeCommand = 0.1
        #self.token = self.crypto.encrypt_random_key(token)
        self.headers = self.crypto.encrypt_random_key(json.dumps({
                    'Content-Type':"application/json",
                    'X-F5-Auth-Token':token,
                    'cache-control':"no-cache",
                }))

    async def runCommand(self, command):
        await asyncio.sleep(random.uniform(0,5))
        method = command.split('---')[0]
        #url = "https://" + self.ip + ":" + str(self.port) + command.split('---')[1]
        url = f"https://{self.ip}:{str(self.port)}{command.split('---')[1]}"
        payload = command.split('---')[2]

        response = await self.session.request(method, url, data=payload, headers=json.loads(self.crypto.decrypt_random_key(self.headers)))
        return await response.json()
        
    async def closeSession(self):
        await self.session.close()


    

