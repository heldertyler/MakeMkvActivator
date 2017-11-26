from bs4 import BeautifulSoup
import requests
import logging
import os

if os.name == 'nt':
    import winreg

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='makemkvactivation.log',  filemode='a')

#Get the installed MakeMkv activation key
def get_current_key():
    if os.name == 'posix':
        if '/Users/' + os.getlogin() + '/Library/MakeMKV/settings.conf':
            with open ('/Users/' + os.getlogin() + '/Library/MakeMKV/settings.conf', 'r') as file:
                lines = file.readlines()
                return lines[4].split('"')[1]
        else:
            return None

    elif os.name == 'nt':
        global registry_location
        registry_location = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\MakeMkv', 0, winreg.KEY_ALL_ACCESS)
        return winreg.QueryValueEx(registry_location, 'app_key')[0]

current_key = get_current_key()

if current_key == None and os.name == 'posix':
    print('MakeMkv settings.conf not create yet, Please open MakeMkv.app, close the applicaiton, and run this script again.')

#Get Current MakeMkv Key and Activate Software
raw_html = requests.get('https://www.makemkv.com/forum2/viewtopic.php?f=5&t=1053')

if raw_html.status_code == 200:
    web_page = BeautifulSoup(raw_html.text, 'html.parser')
    makemkv_findkey = web_page.find(class_='codecontent')
    key = str(makemkv_findkey.text.split('>')[0])

    if key is not None and key != current_key:
        if os.name == 'posix':
            open('/Users/' + os.getlogin() + '/Library/MakeMKV/settings.confnew', 'a')
            with open('/Users/' + os.getlogin() + '/Library/MakeMKV/settings.conf', 'r') as currentConfig, open('/Users/' + os.getlogin() + '/Library/MakeMKV/settings.confnew', 'w') as newConfig:
                for line in currentConfig:
                    if line.startswith('app_Key'):
                        newConfig.write(line.replace(line.split('"')[1], akey))
                    else:
                        newConfig.write(line)
                    
            os.remove('/Users/' + os.getlogin() + '/Library/MakeMKV/settings.conf')
            os.rename('/Users/' + os.getlogin() + '/Library/MakeMKV/settings.confnew', '/Users/' + os.getlogin() + '/Library/MakeMKV/settings.conf')

        elif os.name == 'nt':
            winreg.SetValueEx(registry_location, 'app_key', 0, winreg.REG_SZ, key)
            registry_location.Close()
        print('The current activation key is: ' + key + '. Installed key has been updated as it was out of date.')
        logging.info('The current activation key is: ' + key + '. Installed key has been updated as it was out of date.')

    elif key is not None and key == current_key:
        print('The current activation key is: ' + key + '. This key is already installed.')
        logging.info('The current activation key is: ' + key + '. This key is already installed.')
        
    else:
        print('The activation key is currently being updated. Please check back later.')
        logging.info('The activation key is currently being updated. Please check back later.')
        
else:
    print('The web page is currently down. Please check back later. ERROR CODE: ' + str(raw_html.status_code))
    logging.error('The web page is currently down. Please check back later. ERROR CODE: ' + str(raw_html.status_code))

raw_html.close()
