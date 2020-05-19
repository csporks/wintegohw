from asyncio import Lock, get_event_loop, Queue
from dataclasses import dataclass
from queue import Empty
from typing import List, Tuple
import logging 
import aiohttp

from .user_service import UserService
from user_scraper.models import User
from .exceptions import UserRepoError, LoginError


logger = logging.getLogger(__name__)

class ScraperRepo:
    def __init__(self):
        self.lock = Lock()
        self.users = dict()
        self.following = set()
        self.followers = []

    async def add_users(self, users: List[User])-> int:
        with self.lock:
            for user in users:
                self.users [user.id] = user
    
    async def add_following(self, user: User):
        with self.lock:
            self.following.add((user.id, user.name))
    
    async def user_processed_before(self, user_id):
        with self.lock:
            return user_id in self.users
    
    def get_following(self):
        return self.following

    def set_followers(self, followers: List[User]):
        self.followers = followers
    
    def get_followers(self):
        return self.followers


class ScraperRepoFactory():
    def get_scraper_repo(self):
        return ScraperRepo()
    


async def _fetch_task(task_queue, task_repo, user_service, user_id, root_user_id):
        try:
            is_self = user_id == root_user_id
            users = await user_service.get_followers(user_id, is_self)
            await task_repo.add_users(users)
            if is_self:
                task_repo.set_followers(users)
            elif any((user for user in users if user.id == root_user_id)):
                await task_repo.add_following(user_id)
            
            for user in users:
                if not task_repo.user_processed_before(user.id):
                    await task_repo.add_user(user)
                    await task_queue.put(user.id)
        except Exception as e:
            await task_queue.put(user_id) # an error has occured put the task in the queue again
        finally:
            task_queue.task_done() 

async def _queue_reader_task(task_queue, task_repo, user_service, root_user_id):
    while(True):
        try:
            user_id = await task_queue.get()
        except Empty as e:
            pass
        else:
            task = _fetch_task(task_queue, task_repo, user_service, user_id, root_user_id)
            get_event_loop().create_task(task)

        
class ScraperExecutor():
    def __init__(self, user_service: UserService, repo_factory=ScraperRepoFactory()):
        self.repo_factory = repo_factory
        self.user_service = user_service

    async def get_follow_data(self, user_id):
        q = Queue()
        task_res_repo = self.repo_factory.get_scraper_repo()
        q_reader = _queue_reader_task(q, task_res_repo, self.user_service, user_id)
        t = get_event_loop().create_task(q_reader)
        await q.put(user_id)
        await q.join()
        t.cancel()
        return ([User(following[0], following[1]) for following in task_res_repo.get_following()],
                task_res_repo.get_followers())
