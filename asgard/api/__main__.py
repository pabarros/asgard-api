import asyncio
from asgard.http.client import http_client


async def main():
    print("main")
    async with http_client.get("https://httpbin.org/ip") as response:
        print(response.status)
        print(await response.json())
        async with http_client.get("https://httpbin.org/headers") as responsse2:
            print(responsse2.status)
            print(await responsse2.text())


asyncio.get_event_loop().run_until_complete(main())
