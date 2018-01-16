import json
import os
import requests
import sqlite3
import zipfile
import urllib.request
import time


class BungieApiConfig(object):
    def __init__(self, config_file_uri=None):
        self.__config_file_uri = config_file_uri
        self.__config = {
            'endpoints': dict()
        }

        self.__config_file_uri = os.path.expanduser(config_file_uri)

    def load(self):
        """
        This function loads a json configuration file and applies default values
        in the event the json file has problems loading or being parsed
        """
        if not os.path.isfile(self.__config_file_uri):
            return False

        try:
            with open(self.__config_file_uri, 'r') as jf:
                self.__config = json.load(jf)

                if 'endpoints' not in self.__config:
                    self.__config['endpoints'] = dict()

            return True
        except IOError:
            print('Failed to load file: {}'.format(self.__config_file_uri))
        except ValueError:
            print('Failed to parse file: {}'.format(self.__config_file_uri))

    def save(self):
        """This function simply writes configuration to a file on the local machine"""
        with open(self.__config_file_uri, 'w') as jf:
            json.dump(self.__config, jf)

    def endpoint_get(self, endpoint):
        """This function retrieves an endpoint value, given the key"""
        return self.__config['endpoints'][endpoint]

    def get(self, key):
        """This function retrieves a setting value, given the key"""
        return self.__config[key]


class DestinyManifest(object):  # No inverse pun intended
    def __init__(self, name, path, version):
        self.name = name
        self.path = path
        self.version = version

    def download_and_unpack(self):
        urllib.request.urlretrieve(self.path, 'temp.dat')
        with zipfile.ZipFile('temp.dat', "r") as zip_ref:
            zip_ref.extractall('')

        os.remove('temp.dat')

        temp_name = 'content_{}_{}.sqlite3'.format(self.version, time.strftime("%Y%m%d_%H%M%S"))

        os.rename(self.name, temp_name)
        self.name = temp_name

    def table_extract(self):
        conn = sqlite3.connect(self.name)
        cursor = conn.cursor()

        # Get a collection of all of the tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        for table in tables:
            cursor.execute('SELECT * FROM {};'.format(table[0]))
            rows = cursor.fetchall()
            count = len(rows)

            for i in range(count):
                a = json.loads(rows[i][1])
                print(a)


class BungieApiClient(object):
    def __init__(self, config=None):
        self.__config = config
        self.headers = {'X-API-Key': os.environ['BUNGIE_API_KEY']}
        self.base_uri = self.__config.get('base_uri')

    def manifest_get(self, ):
        request_uri = self.base_uri + self.__config.endpoint_get('manifest')
        request = requests.get(request_uri, headers=self.headers)

        path = self.base_uri + request.json()['Response']['mobileWorldContentPaths']['en']

        manifest = DestinyManifest(
            path[path.find('world_sql_content'):],
            path,
            request.json()['Response']['version']
        )

        return manifest
