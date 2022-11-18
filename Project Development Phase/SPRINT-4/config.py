import mysql.connector


def data_base_connection():
    data_base = mysql.connector.connect(host='127.0.0.1',
                                 user='root',
                                 passwd='mysql@1419',
                                 db='virtualeye',
                                 port=3306)
    return data_base


class Config(object):
    SECRET_KEY = 'you-will-never-guess'
