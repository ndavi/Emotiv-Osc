import asyncio
from lib.cortex import Cortex
import json
from pythonosc import osc_message_builder
from pythonosc import udp_client

oscMessages = {}

async def do_stuff(cortex):
    # await cortex.inspectApi()
    print("** Create OSC Client **")
    client = udp_client.SimpleUDPClient("127.0.0.1", 55555)
    print("** USER LOGIN **")
    await cortex.get_user_login()
    print("** GET CORTEX INFO **")
    await cortex.get_cortex_info()
    print("** HAS ACCESS RIGHT **")
    await cortex.has_access_right()
    print("** REQUEST ACCESS **")
    await cortex.request_access()
    print("** AUTHORIZE **")
    await cortex.authorize(debit=2)
    print("** GET LICENSE INFO **")
    await cortex.get_license_info()
    print("** QUERY HEADSETS **")
    await cortex.query_headsets()
    if len(cortex.headsets) > 0:
        print("** CREATE SESSION **")
        await cortex.create_session(activate=True,
                                    headset_id=cortex.headsets[0])
        print("** SUBSCRIBE **")
        dataColumns = await cortex.subscribe(['mot', 'fac', 'met'])
        for val in dataColumns['result']['success']:
            oscMessages[val['streamName']] = []
            for col in val['cols']:
                oscMessages[val['streamName']].append("/" + val['streamName'] + "/" + col)
        while True:
            values = json.loads(await cortex.get_data())
            key = list(values.keys())[0]
            currentOscMessages = oscMessages[key]
            i = 0
            for currentOscMessage in currentOscMessages:
                client.send_message(currentOscMessage, values[key][i])
                i = i + 1

        await cortex.close_session()


def test():
    cortex = Cortex('./cortex_creds')
    asyncio.run(do_stuff(cortex))
    cortex.close()


if __name__ == '__main__':
    test()
