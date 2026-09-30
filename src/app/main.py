import logging
import os
import threading
import time

from app_server import start_server
from controller import Controller

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)-11s -%(funcName)-22s- %(levelname)-8s - %(message)-s',
    handlers=[
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


def _auto_refresh_enabled() -> bool:
    return os.getenv('MARKET_AUTO_REFRESH', 'true').lower() in {
        '1',
        'true',
        'yes',
        'on',
    }


def refresh_market_rates_forever() -> None:
    interval = max(60, int(os.getenv('MARKET_REFRESH_SECONDS', '21600')))

    while True:
        controller = Controller()
        try:
            result, _ = controller.sync_market_rates()
            logger.info(
                'Market rates refreshed from %s: %s pairs (as of %s)',
                result['provider'],
                result['updated'],
                result['asOf'],
            )
        except Exception:
            logger.exception('Market-rate refresh failed')
        finally:
            controller.close()

        time.sleep(interval)


def start_market_refresher() -> threading.Thread | None:
    if not _auto_refresh_enabled():
        logger.info('Automatic market-rate refresh is disabled')
        return None

    thread = threading.Thread(
        target=refresh_market_rates_forever,
        name='market-rate-refresher',
        daemon=True,
    )
    thread.start()
    return thread


if __name__ == '__main__':
    start_market_refresher()
    start_server()
