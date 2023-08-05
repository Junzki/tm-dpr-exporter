# -*- coding:utf-8 -*-
import argparse
from .app import App

parser = argparse.ArgumentParser(description='DPR Exporter')
parser.add_argument('--config', '-c', type=str, help='Config file',
                    default='config.yaml')

app = App()


if __name__ == '__main__':
    args, argv = parser.parse_known_args()
    app.configure(args.config)
    app.setup()

    app.run()
