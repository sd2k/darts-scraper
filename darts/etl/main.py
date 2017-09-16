import logging
import subprocess
import time

import schedule


logging.basicConfig(level=logging.INFO)


def run_player_scraper():
    subprocess.check_call([
        'luigi',
        '--local-scheduler',
        '--module',
        'darts.etl.tasks.scrapers',
        'PlayerScraper',
    ])


def run_event_scraper():
    subprocess.check_call([
        'luigi',
        '--local-scheduler',
        '--module',
        'darts.etl.tasks.scrapers',
        'EventScraper',
    ])


def main():
    schedule.every(2).minutes.do(run_player_scraper)
    schedule.every(2).minutes.do(run_event_scraper)
    run_player_scraper()
    run_event_scraper()
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
