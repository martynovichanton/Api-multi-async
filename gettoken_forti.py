from getpass import getpass
import requests
import gc
import json
from Crypto import Crypto
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import asyncio
import aiohttp

device_ip = "10.1.1.1"

async def token(user, password):
    # session = aiohttp.ClientSession()
    async with aiohttp.ClientSession() as session:
        crypto = Crypto()
        url = f"https://" + device_ip + "/jsonrpc"
        payload = crypto.encrypt_random_key(json.dumps({
            "method": "exec",
            "params": [{
                "url": "/sys/login/user",
                "data": {"user":user,"passwd":password}
            }],
        }))
        headers = {
                    'Content-Type':"application/json",
                    'cache-control':"no-cache"
        }

        response = await session.request('post', url, data=crypto.decrypt_random_key(payload), headers=headers)
        print(await response.json())
        return {"token": (await response.json())["session"]}

async def main():
    main_crypto = Crypto()
    user = main_crypto.encrypt_random_key(getpass("User"))
    password = main_crypto.encrypt_random_key(getpass("Password"))
    print(await token(main_crypto.decrypt_random_key(user), main_crypto.decrypt_random_key(password)))

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())