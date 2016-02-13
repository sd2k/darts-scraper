# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from datetime import datetime
import re

from sqlalchemy.orm.exc import NoResultFound

from darts import items
from darts.models import Event, Match, MatchResult, Player, Session, Tournament


class ItemToDBPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, items.Player):
            self.process_player(item, spider)
        elif isinstance(item, items.Tournament):
            self.process_tournament(item, spider)
        elif isinstance(item, items.Event):
            self.process_event(item, spider)
        elif isinstance(item, items.Match):
            self.process_match(item, spider)
        elif isinstance(item, items.MatchResult):
            self.process_match_result(item, spider)

    def process_player(self, item, spider):

        if item.get('dob'):
            item['dob'] = datetime.strptime(
                item['dob'], '%d/%m/%Y'
            ).date()

        if item.get('career_earnings'):
            item['career_earnings'] = float(
                re.sub('\\D', '', item['career_earnings'])
            )
        if item.get('pdc_ranking'):
            item['pdc_ranking'] = int(item['pdc_ranking'])
        if item.get('red_dragon_ranking'):
            item['red_dragon_ranking'] = int(item['red_dragon_ranking'])
        if item.get('ddb_ranking'):
            item['ddb_ranking'] = int(item['ddb_ranking'])
        if item.get('ddb_popularity'):
            item['ddb_popularity'] = int(item['ddb_popularity'])
        if item.get('career_9_darters'):
            item['career_9_darters'] = int(item['career_9_darters'])

        player = Player(**item)

        try:
            self.session.query(Player).filter(
                Player.id == player.id
            ).one()
            spider.logger.info('Updating player %s', player.name)
            self.session.query(Player).filter(
                Player.id == player.id).update(item)
            self.session.commit()
        except NoResultFound:
            spider.logger.info('Adding player %s', player.name)
            self.session.add(player)
            self.session.commit()
        except:
            spider.logger.debug(
                'Error adding or updating player %s', player.name
            )
            self.session.rollback()
            raise

        return item

    def process_tournament(self, item, spider):

        tournament = Tournament(**item)

        try:
            spider.logger.info('Adding tournament %s', tournament.name)
            self.session.add(tournament)
            self.session.commit()
        except:
            spider.logger.debug(
                'Error adding tournament %s', tournament.name
            )
            self.session.rollback()
            raise

        return item

    def process_event(self, item, spider):

        if item['year']:
            item['year'] = int(item['year'])
        if item['prize_fund']:
            item['prize_fund'] = int(re.sub(r'\\D', '', item['prize_fund']))

        event = Event(**item)

        try:
            spider.logger.info('Adding event %s', event.name)
            self.session.add(event)
            self.session.commit()
        except:
            spider.logger.debug(
                'Error adding event %s', event.name
            )
            self.session.rollback()
            raise

        return item

    def process_match(self, item, spider):

        if item['date']:
            item['date'] = datetime.strptime(
                item['date'], '%d/%m/%Y'
            ).date()

        match = Match(**item)

        try:
            spider.logger.info('Adding match %s', match.name)
            self.session.add(match)
            self.session.commit()
        except:
            spider.logger.debug(
                'Error adding match %s', match.name
            )
            self.session.rollback()
            raise

    def process_match_result(self, item, spider):

        item['player_id'] = int(item['player_id'])
        item['match_id'] = int(item['match_id'])
        if item['score']:
            item['score'] = int(item['score'])
        if item['average']:
            item['average'] = float(item['average'])
        if item['high_checkout']:
            item['high_checkout'] = int(item['high_checkout'])
        if item['checkout_info']:
            item['checkout_percent'] = float(
                re.sub(
                    r'.* (\d)+\.(\d+)\%.*',
                    '0.' + r'\1' + r'\2',
                    item['checkout_info']
                )
            )
            item['checkout_chances'] = int(
                re.sub(
                    r'.+\(\d+/(\d+)\).+',
                    r'\1',
                    item['checkout_info']
                )
            )

        match_result = MatchResult(**item)

        try:
            spider.logger.info('Adding match_result %s', match_result.name)
            self.session.add(match_result)
            self.session.commit()
        except:
            spider.logger.debug(
                'Error adding match_result %s', match_result.name
            )
            self.session.rollback()
            raise

    def open_spider(self, spider):
        self.session = Session()

    def close_spider(self, spider):
        self.session.close()
