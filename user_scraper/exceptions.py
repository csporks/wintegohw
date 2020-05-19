class UserRepoError(Exception):
    pass

class LoginError(UserRepoError):
    pass

class ScrapeError(Exception):
    pass