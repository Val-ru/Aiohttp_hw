
from db import Session, User, Advertisement
import json
from aiohttp import web
from sqlalchemy.exc import IntegrityError
from db import init_orm, close_orm, Session, User
from sqlalchemy.ext.asyncio import AsyncSession
from bcrypt import hashpw, gensalt
from pydantic import BaseModel, ValidationError


def hash_password(password: str) -> str:
    password = password.encode()
    password = hashpw(password, gensalt())
    password = password.decode()
    return password

app = web.Application()


async def orm_contex(app: web.Application):
    print("START")
    await init_orm()
    yield
    await close_orm()
    print("FINISH")


@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response

app.cleanup_ctx.append(orm_contex)
app.middlewares.append(session_middleware)

def get_error(err_cls: type[web.HTTPConflict | web.HTTPNotFound], err_msg):
    err_msg = json.dumps({"error": err_msg})
    return err_cls(text=err_msg, content_type="application/json")


class AdvertisementCreate(BaseModel):
    header: str
    description: str
    owner: str


class AdvertisementView(web.View):

    @property
    def session(self) -> AsyncSession:
        return self.request.session

    @property
    def adv_id(self) -> int:
        return int(self.request.match_info["advertisements_id"])

    async def get_advertisement_by_id(self):

        adv_id = int(self.request.match_info["advertisements_id"])
        advertisement = await self.session.get(Advertisement, adv_id)
        if advertisement is None:
            raise get_error(web.HTTPNotFound, "Advertisement not found")
        return advertisement


    async def add_advertisement(self, advertisement: Advertisement):

        self.session.add(advertisement)
        try:
            await self.session.commit()
        except IntegrityError:
            raise get_error(web.HTTPConflict, "advertisement already exists")


    async def get(self):

        advertisement = await self.get_advertisement_by_id()
        return web.json_response(advertisement.dict)


    async def post(self):
        try:
            json_data = await self.request.json()
            data = AdvertisementCreate(**json_data)
            user_id = 1

            advertisement = Advertisement(
                header=data.header,
                description=data.description,
                owner=data.owner,
                user_id=user_id
            )
            await self.add_advertisement(advertisement)
            return web.json_response(advertisement.id_dict(), status=201)
        except ValidationError as e:
            return web.json_response({"errors": e.errors()}, status=400)


    async def patch(self):
        json_data = await self.request.json()

        advertisement = await self.get_advertisement_by_id()

        if "header" in json_data:
            advertisement.header = json_data["header"]
        if "description" in json_data:
            advertisement.description = json_data["description"]
        if "owner" in json_data:
            advertisement.owner = json_data["owner"]

        await self.session.add(advertisement)
        await self.session.commit()

        return web.json_response(advertisement.id_dict)


    async def delete(self):

        advertisement = await self.get_advertisement_by_id()
        await self.session.delete(advertisement)
        await self.session.commit()
        return web.json_response({"status": "Deleted successfully"})

app.add_routes(
    [
        web.post("/adv_list", AdvertisementView),
        web.get(r"/adv_list/{adv_id:\d+}", AdvertisementView),
        web.patch(r"/adv_list/{adv_id:\d+}", AdvertisementView),
        web.delete(r"/adv_list/{adv_id:\d+}", AdvertisementView)
    ]
)


class UserView(web.View):

    @property
    def session(self) -> AsyncSession:
        return self.request.session

    @property
    def user_id(self) -> int:
        return int(self.request.match_info["user_id"])

    async def get_user_by_id(self):
        user_id = int(self.request.match_info["user_id"])
        user = await self.session.get(User, user_id)
        if user is None:
            raise get_error(web.HTTPNotFound, "User not found")
        return user


    async def add_user(self, user: User):
        self.session.add(user)
        try:
            await self.session.commit()
        except IntegrityError:
            raise get_error(web.HTTPConflict, "user already exists")


    async def get(self):
        user = await self.get_user_by_id()
        return web.json_response(user.dict)


    async def post(self):
        json_data = await self.request.json()
        user = User(name=json_data["name"], password=hash_password(json_data["password"]))
        await self.add_user(user)
        return web.json_response(user.id_dict)


    async def patch(self):
        json_data = await self.request.json()
        user = await self.get_user_by_id()

        if "name" in json_data:
            user.name = json_data["name"]
        if "password" in json_data:
            user.password = hash_password(json_data["password"])

        await self.add_user(user)
        return web.json_response(user.id_dict)


    async def delete(self):
            user = await self.get_user_by_id()
            await self.session.delete(user)
            await self.session.commit()
            return web.json_response({"status": "deleted"})


app.add_routes(
    [
        web.post("/users", UserView),
        web.get(r"/users/{user_id:\d+}", UserView),
        web.patch(r"/users/{user_id:\d+}", UserView),
        web.delete(r"/users/{user_id:\d+}", UserView)
    ]
)

# app.add_url_rule("/register")
#
# app.add_url_rule("/login")

web.run_app(app)