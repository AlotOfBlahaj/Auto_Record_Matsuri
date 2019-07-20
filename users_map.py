def user_map(user):
    """
    建立用户频道与用户名对应
    :param user: str
    :return: str
    """
    natsuiromatsuri_tuple = ('UCQ0UDLQCjY0rmuxCDE38FGg', 'natsuiromatsuri', '3264432')
    uruharushia_tuple = ('UCl_gCybOJRIgOXw6Qb4qJzQ',)
    USERS_DICT = {natsuiromatsuri_tuple: 'natsuiromatsuri',
                  uruharushia_tuple: 'uruharushia'}
    ALL_USER_TUPLE = (natsuiromatsuri_tuple, uruharushia_tuple)
    for u in ALL_USER_TUPLE:
        if user in u:
            return USERS_DICT[u]
