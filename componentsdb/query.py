"""
Canned queries on the database

"""

from componentsdb.model import Collection, UserCollectionPermission

def user_collections(user, permission):
    # pylint: disable=no-member
    return Collection.query.join(UserCollectionPermission).\
        filter(UserCollectionPermission.user == user).\
        filter(UserCollectionPermission.permission == permission)
