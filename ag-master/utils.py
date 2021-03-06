from functools import wraps

from common.course_config import is_admin, is_admin_token
from common.oauth_client import get_user, is_staff, login

BUCKET = "ag-master.buckets.cs61a.org"

SUBM_ENDPOINT = "/api/v3/backups"
SCORE_ENDPOINT = "/api/v3/score/"


def admin_only(func):
    @wraps(func)
    def wrapped(*args, access_token=None, course="cs61a", **kwargs):
        token_good = access_token and is_admin_token(
            access_token=access_token, course=course
        )
        cookie_good = is_staff(course=course) and is_admin(
            email=get_user()["email"], course=course
        )
        if token_good or cookie_good:
            try:
                return func(*args, **kwargs, course=course)
            except PermissionError:
                pass
        if access_token:
            raise PermissionError
        else:
            return login()

    return wrapped


def super_admin_only(func):
    @wraps(func)
    @admin_only
    def wrapped(*args, course, **kwargs):
        if course != "cs61a":
            raise PermissionError
        return func(*args, **kwargs)

    return wrapped
