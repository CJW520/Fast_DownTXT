Conn = {
    "connections": {"default": "mysql://root:root@192.168.139.131:3306/book"},
    # 'connections': {
    #     'default': {
    #         'engine': 'tortoise.backends.mysql',  # 'tortoise.backends.mysql',
    #         'credentials': {
    #             'host': '192.168.139.131',
    #             'port': '3306',
    #             'user': 'root',
    #             'password': 'root',
    #             'database': 'book',
    #             'minsize': 1,
    #             'maxsize': 5,
    #             'charset': 'utf8mb4',
    #             "echo": True
    #         }
    #     }
    # },
    'apps': {
        'models': {
            'models': ['models','blueprints.models', 'aerich.models'],
            'default_connection': 'default'
        }
    },
    'use_tz': False,
    'timezone': 'Asia/Shanghai'
}

def ToJsonList(lists):
    return [models.to_json() for models in lists]
