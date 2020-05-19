from user_scraper.models import UserData
import base64

from .tasks import ScraperExecutor
from .user_service import UserService
from .models import User,UserData


async def get_user_data(host_and_port, username, passwd) -> UserData:
    user_service = UserService(host_and_port, username, passwd)
    async with user_service as user_service:
        user = await user_service.get_user_info()
        executor = ScraperExecutor(user_service)

        following, followers = await executor.get_follow_data(user.id)
        return UserData(name=user.name, following=following, followers=followers)


