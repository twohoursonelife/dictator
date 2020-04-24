import configparser
import os.path


def check_config():
    if os.path.isfile('dictator/utility/config.ini'):
        return('Using existing config.', check_player_log())
    else:
        config = configparser.ConfigParser()
        config['Settings'] = {'Bot_token': 'token',
                              'Bot_prefix': '-',
                              'DB_host': 'localhost',
                              'DB_db': 'database',
                              'DB_user': 'username',
                              'DB_pass': 'password',
                              'bot_id': '658883039761399859',
                              'verify_channel_id': '660359992410636288',
                              'log_channel_id': '660359992410636288',
                              'stats_channel_id': '687671123604930607',
                              'bot_channel_id': '604287242529407006',
                              'general_channel_id': '423293333864054837'}
        with open('dictator/utility/config.ini', 'w') as config_file:
            config.write(config_file)
        return('Config file does not exist. Creating with default values.')
    
def check_player_log():
    if os.path.isfile('dictator/utility/player-log.txt'):
        return('Using existing player-log.')
    else:
        with open('dictator/utility/player-log.txt', 'w') as f:
            f.write('Start player log\n')

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
