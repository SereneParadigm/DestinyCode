from serene.bungie import *


def main():
    config = BungieApiConfig('Destiny2Api.json')

    if not config.load():
        return 1

    client = BungieApiClient(config)
    manifest = client.manifest_get()
    manifest.download_and_unpack()
    manifest.table_extract()

    return 0


if __name__ == '__main__':
    exit(main())
