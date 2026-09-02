import argparse

from pystro.config import Config, load_json
from pystro.api import get_engine_master

def main():
    parser = argparse.ArgumentParser(description='Retrieve the master engine from the Maestro API')
    parser.add_argument('-e', '--environment', help='The environment to use from the configuration file', default='test')
    args = parser.parse_args()

    config = Config.from_json(environment=args.environment)
    master_engine = get_engine_master(config)
    if master_engine:
        print(f"Master engine: {master_engine}")
    else:
        print("Could not find master engine.")

            

if __name__ == "__main__":
    main()