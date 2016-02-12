# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from datetime import datetime
import re

from sqlalchemy.orm.exc import NoResultFound

from darts.models import Player, Session


class PlayerPipeline(object):

    def process_item(self, item, spider):

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
            db_player = self.session.query(Player).filter(
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

    def open_spider(self, spider):
        self.session = Session()

    def close_spider(self, spider):
        self.session.close()
