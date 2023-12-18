from getpass import getpass
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
        url = "https://" + device_ip + "/mgmt/shared/authn/login"
        crypto = Crypto()
        payload = crypto.encrypt_random_key("{\n    \"username\":" + user + ",\n    \"password\":" + password + ",\n    \"loginProviderName\": \"tmos\"\n}")
        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache",
            }
        response = await session.request('post', url, data=crypto.decrypt_random_key(payload), headers=headers)
        if response.status != 200:
            return {"Error":await response.text()}
        token = crypto.encrypt_random_key((await response.json())['token']['token'])
        del response
        gc.collect()


        url = "https://" + device_ip + "/mgmt/shared/authz/tokens"
        payload = ""
        headers = crypto.encrypt_random_key(json.dumps({
            'X-F5-Auth-Token': crypto.decrypt_random_key(token),
            'cache-control': "no-cache"
        }))
        response = await session.request('get', url, data=payload, headers=json.loads(crypto.decrypt_random_key(headers)))
        if response.status != 200:
            return {"Error":await response.text()}
        del response
        gc.collect()


        url = "https://" + device_ip + "/mgmt/shared/authz/tokens/" + crypto.decrypt_random_key(token)
        payload = "{\n    \"timeout\":\"3600\"\n}"
        headers = crypto.encrypt_random_key(json.dumps({
            'Content-Type': "application/json",
            'X-F5-Auth-Token': crypto.decrypt_random_key(token),
            'cache-control': "no-cache"
        }))
        response = await session.request('patch', url, data=payload, headers=json.loads(crypto.decrypt_random_key(headers)))
        if response.status != 200:
            return {"Error":await response.text()}
        token = crypto.encrypt_random_key((await response.json())['token'])  
        timeout = (await response.json())['timeout']
        del response
        gc.collect()
        await session.close()
        return {"token":crypto.decrypt_random_key(token), "timeout":timeout}

async def main():
    main_crypto = Crypto()
    user = main_crypto.encrypt_random_key(getpass("User"))
    password = main_crypto.encrypt_random_key(getpass("Password"))
    print(await token(main_crypto.decrypt_random_key(user), main_crypto.decrypt_random_key(password)))

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())