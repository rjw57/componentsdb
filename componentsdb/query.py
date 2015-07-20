from componentsdb.model import (
    Component, UserComponentPermission, User
)

def user_components(user, permission):
    return Component.query.join(UserComponentPermission).\
        filter(UserComponentPermission.user==user).\
        filter(UserComponentPermission.permission==permission)
