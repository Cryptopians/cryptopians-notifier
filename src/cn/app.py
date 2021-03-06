import sys
import time

import ccxt

from cn import settings
from cn.core import store
from cn.utils.logging import getLogger
from cn.utils.module import import_string

logger = getLogger(__name__)


def run():
    initialized = store.initialize_store()
    if not initialized:
        logger.warning("Couldn't initialize store from remote")
    while True:
        for exchange in ccxt.exchanges:
            if exchange in settings.BLACKLISTED_EXCHANGES:
                continue
            klass = import_string('ccxt.%s' % exchange)
            client = klass()
            if client.has.get('publicAPI'):
                try:
                    markets = client.load_markets()
                    store.process_markets(client, markets)
                except:
                    err = sys.exc_info()[0]
                    msg = "Couldn't fetch data from '%s': %s" % (client.name, err)
                    logger.warning(msg)
        logger.info("Successfully verified data from %d exchanges" % len(ccxt.exchanges))
        store.update_store()
        time.sleep(int(settings.CN_INTERVAL))
