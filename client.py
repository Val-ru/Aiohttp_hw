import asyncio
from aiohttp import ClientSession

async def main():

    async with ClientSession() as session:

        response = await session.post(
            "http://localhost:8080/users",
            json={"name": "user_10", "password": "1234"},
        )
        print(response.status)
        print(await response.text())


        # response = await session.post(
        #     "http://localhost:8080/advertisements",
        #     json={
        #         "name": "user_10",
        #         "header": "1234",
        #         "description": "Test description",
        #         "owner": "user_10"
        #     },
        # )
        # print(response.status)
        # print(await response.text())


        # response = await session.get("http://localhost:8080/advertisements/1")
        # print(response.status)
        # print(await response.text())


        # response = await session.get("http://localhost:8080/users/1")
        # print(response.status)
        # print(await response.text())


        # response = await session.patch(
        #     "http://localhost:8080/advertisements/1",
        #     json={
        #         "name": "Changed_user_10",
        #         "header": "4321",
        #         "description": "Test_discr",
        #         "owner": "Changed_user_10"
        #     },
        # )
        # print(response.status)
        # print(await response.text())


        # response = await session.patch(
        #     "http://localhost:8080/users/1",
        #     json={"name": "Changed_user_100", "password": "54321"},
        # )
        # print(response.status)
        # print(await response.text())


        # response = await session.delete(
        #     "http://localhost:8080/advertisements/1",
        # )
        # print(response.status)
        # print(await response.text())


        # response = await session.delete(
        #     "http://localhost:8080/users/1",
        # )
        # print(response.status)
        # print(await response.text())