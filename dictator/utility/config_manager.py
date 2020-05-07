import configparser
import os.path


def check_config():
    if os.path.isfile('dictator/utility/config.ini'):
        return('Using existing config.')
    else:
        config = configparser.ConfigParser()
        config['Settings'] = {'Bot_token': 'token',
                              'Bot_prefix': '-',
                              'DB_host': 'localhost',
                              'DB_db': 'database',
                              'DB_user': 'username',
                              'DB_pass': 'password',
                              'bot_id': '658883039761399859',
                              'verify_channel_id': '656484598779215872',
                              'log_channel_id': '620375198251745282',
                              'stats_channel_id': '423293333864054837',
                              'bot_channel_id': '604287242529407006',
                              'general_channel_id': '423293333864054837',
                              'suggestion_channel_id': '703244428172853318'}
        with open('dictator/utility/config.ini', 'w') as config_file:
            config.write(config_file)
        return('Config file does not exist. Creating with default values.')

def read(setting):
    config = configparser.ConfigParser()
    config.read('dictator/utility/config.ini')
    return(config['Settings'][setting])


def db_config():
    db_config = {'host': str(read('DB_host')),
                 'database': str(read('DB_db')),
                 'user': str(read('DB_user')),
                 'password': str(read('DB_pass'))}
    return(db_config)
