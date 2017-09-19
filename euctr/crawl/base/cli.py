# -*- coding: utf-8 -*-
import sys
import dataset
import logging
import importlib
from . import config
from . import helpers
logger = logging.getLogger(__name__)


# Module API

def cli(argv):
    # Prepare conf dict
    conf = helpers.get_variables(config, str.isupper)

    # Prepare conn dict
    conn = {
        'warehouse': dataset.connect(config.WAREHOUSE_URL),
    }

    # Get and call collector
    collect = importlib.import_module('collectors.%s' % argv[1]).collect
    collect(conf, conn, *argv[2:])


if __name__ == '__main__':
    cli(sys.argv)
