from dataclasses import dataclass
from typing import Dict, List

@dataclass
class User:
    id: str
    name: str

@dataclass
class UserData:
    name: str
    followers: List[str]
    following: List[str]