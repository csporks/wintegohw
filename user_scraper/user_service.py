from typing import List
import aiohttp
import logging
import base64

from user_scraper.models import User
from .exceptions import UserRepoError, LoginError


logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, host, user, passwd):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.session = None
        self.host = host
        self.url = f"http://{host}/api"
        self.cookie = None
    async def __aenter__(self):
        try:
            session = aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True))
            self.session = await session.__aenter__()
            payload = {"username": self.user, "password": self.passwd}
            url = f"{self.url}/login"
            async with self.session.post(url, json=payload) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise LoginError(f"An error has occured while trying to login user{text}")
                token = resp.cookies.get("token")
                self.cookie = f"token={token}"
        except aiohttp.ClientError as e:
            raise LoginError(f"Couldn't connect to user server due to {str(e)}")
        return self


    async def _get_followers_range(self, user_id, index, is_self):
        headers = {"Cookie": self.cookie}
        user_id = "me" if is_self else user_id
        f_url = f"{self.url}/user/{user_id}/followers?skip={index}"
        try:
            async with self.session.get(f_url, headers=headers) as resp:
                data = await resp.json()
                followers = []
                for follower in data["followers"]:
                    first_name =follower["firstName"] 
                    last_name = follower["lastName"]
                    name = f"{first_name} {last_name}"
                    followers.append(name=name, id=follower["id"])
                return followers, bool(data["more"])
        except aiohttp.ClientError as e:
            raise UserRepoError(e)
        
    async def get_followers(self, user_id, is_self) -> List[User]:
        followers = []
        index = 0
        end = False
        while(not end):
            res = await self._get_followers_range(user_id, 10, is_self)
            followers.append(res[0])
            end = not res[1]
            index += 10
            
        return followers

    def _extract_user_info(self, text) -> User:
        decoded = base64.b64decode(text).decode("unicode_escape")
        decoded = decoded.split("\n")[1].strip()
        s_f_name = "\u0012"
        s_l_name = "\u001a"
        first_name =decoded[decoded.index(s_f_name) + 2: decoded.index(s_l_name)] 
        last_name = decoded[decoded.index(s_l_name) + 2: decoded.index(" ")]
        id = decoded[:decoded.index(s_f_name)]
        return User(name=f"{first_name} {last_name}", id=id)

    async def get_user_info(self) -> User:
        headers = {"Cookie": self.cookie}
        f_url = f"{self.url}/user/me"
        async with self.session.get(f_url, headers=headers) as resp:
            text = await resp.text()
            return self._extract_user_info(text)
            



    async def __aexit__(self, exc_type, exc_value, traceback):
        try:
            await self.session.__aexit__(exc_type, exc_value, traceback)
        except aiohttp.ClientError as e: 
            logger.error(f"Couldn't close session ${e}")
