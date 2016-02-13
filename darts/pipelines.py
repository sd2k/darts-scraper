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

        if item.get('year'):
            item['year'] = int(item['year'])
        if item.get('prize_fund'):
            item['prize_fund'] = int(re.sub(r'\D', '', item['prize_fund']))

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

        if item.get('date'):
            item['date'] = datetime.strptime(
                re.sub(
                    r'.*([0-9]{2}/[0-9]{2}/[0-9]{4}).*',
                    r'\1',
                    item['date'],
                ),
                '%d/%m/%Y',
            ).date()

        match = Match(**item)

        try:
            spider.logger.info('Adding match %s', match.id)
            self.session.add(match)
            self.session.commit()
        except:
            spider.logger.debug(
                'Error adding match %s', match.id
            )
            self.session.rollback()
            raise

    def process_match_result(self, item, spider):

        newitem = dict(**item)

        newitem['player_id'] = int(newitem['player_id'])
        newitem['match_id'] = int(newitem['match_id'])
        if newitem.get('score'):
            newitem['score'] = int(newitem['score'])
        if newitem.get('average'):
            newitem['average'] = float(newitem['average'])
        if newitem.get('high_checkout'):
            newitem['high_checkout'] = int(newitem['high_checkout'])
        if newitem.get('checkout_info'):
            if re.sub(r'[^a-z0-9().%/]', '', newitem['checkout_info']):
                newitem['checkout_percent'] = float(
                    re.sub(
                        r'.* (\d)+\.(\d+)\%.*',
                        '0.' + r'\1' + r'\2',
                        newitem['checkout_info']
                    )
                )
                newitem['checkout_chances'] = int(
                    re.sub(
                        r'.*\(\d+/(\d+)\).+',
                        r'\1',
                        newitem['checkout_info']
                    )
                )
                del(newitem['checkout_info'])

        match_result = MatchResult(**newitem)

        try:
            spider.logger.info(
                'Adding match_result (player: %s, match: %s',
                match_result.player_id,
                match_result.match_id,
            )
            self.session.add(match_result)
            self.session.commit()
        except:
            spider.logger.debug(
                'Error match_result (player: %s, match: %s',
                match_result.player_id,
                match_result.match_id,
            )
            self.session.rollback()
            raise

    def open_spider(self, spider):
        self.session = Session()

    def close_spider(self, spider):
        self.session.close()
