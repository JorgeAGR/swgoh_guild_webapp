from dataclasses import dataclass, field
import abc
import os
import datetime
import pandas as pd
from typing import Self, Any
from google.cloud import bigquery


@dataclass
class Raid:
    id: str
    duration: int # in days
    raid_end_date: datetime.date

    @classmethod
    def build_from_guild_request(cls, guild_data_request: dict[str, Any]) -> Self:
        raid_id = guild_data_request['recentRaidResult'][0]['raidId']
        duration = round(int(guild_data_request['recentRaidResult'][0]['duration'])/(60*60*24)) # converted to days
        raid_end_date = datetime.date.fromtimestamp(int(guild_data_request['recentRaidResult'][0]['endTime']))
        return cls(raid_id, duration, raid_end_date)
    
    @staticmethod
    def raid_result_df(guild_data_request: dict[str, Any], member_data_list: list[dict],
                       rename_mapping: dict[str, str] = {'playerId': 'PlayerID', 'memberProgress': 'Score', 'allyCode': 'Allycode', 'name': 'Name'}) -> pd.DataFrame:
        scores_df = pd.DataFrame(guild_data_request['recentRaidResult'][0]['raidMember'])
        allycode_df = pd.DataFrame({'playerId': [member['playerId'] for member in member_data_list],
                                    'allyCode': [member['allyCode'] for member in member_data_list],
                                    'name': [member['name'] for member in member_data_list]})
        scores_df = scores_df.join(allycode_df.set_index('playerId'), on='playerId').drop(['memberRank', 'memberAttempt'], axis=1).rename(rename_mapping, axis=1)
        scores_df['EndDate'] = datetime.date.fromtimestamp(int(guild_data_request['recentRaidResult'][0]['endTime'])).isoformat()
        return scores_df


@dataclass
class RaidSQLTable(abc.ABC):
    raid: Raid
    table_location: str
    url: str

    @property
    def schema(self) -> dict[str, type]:
        return {'PlayerID': str, 'Allycode': int, 'Name': str, 'Score': int, 'EndDate': datetime.date}

    @abc.abstractmethod
    def query(self, query: str) -> None:
        return
    
    def latest_raid_date(self) -> pd.DataFrame:
        query = f'''
        SELECT
        DISTINCT(EndDate)
        FROM
        `{self.table_location}.{self.raid.id}` t
        WHERE DATE(EndDate) IN
        (
        SELECT 
            MAX(DATE(EndDate)) AS max_partition
        FROM `{self.table_location}.{self.raid.id}`
        WHERE DATE(EndDate) >= DATE_SUB(CURRENT_DATE(), INTERVAL {self.raid.duration} DAY)
        )
        AND DATE(EndDate) >= DATE_SUB(CURRENT_DATE(), INTERVAL {self.raid.duration} DAY)
        '''
        return self.query(query)
    
    def latest_raid_results(self) -> pd.DataFrame:
        query = f'''
        SELECT
        *
        FROM
        `{self.table_location}.{self.raid.id}` t
        WHERE DATE(EndDate) IN
        (
        SELECT 
            MAX(DATE(EndDate)) AS max_partition
        FROM `{self.table_location}.{self.raid.id}`
        WHERE DATE(EndDate) >= DATE_SUB(CURRENT_DATE(), INTERVAL {self.raid.duration} DAY)
        )
        AND DATE(EndDate) >= DATE_SUB(CURRENT_DATE(), INTERVAL {self.raid.duration} DAY)
        '''
        return self.query(query)

    @abc.abstractmethod
    def write(self, rows: list[dict]) -> None:
        return
    

@dataclass
class RaidGoogleBigQueryTable(RaidSQLTable):
    project: str
    location: str
    
    def __post_init__(self):
        self.client = bigquery.Client(self.project)
        return
    
    def query(self, query: str) -> pd.DataFrame:
        return self.client.query(query, location=self.location).result().to_dataframe()
    
    def write(self, rows: list[dict]) -> None:
        return self.client.insert_rows_json(f'{self.table_location}.{self.raid.id}', rows)
    

if __name__ == '__main__':
    raid = Raid('krayt_results', 3)
    sqltable = RaidGoogleBigQueryTable(raid, 'swgoh-guild-webapp.raid_results', 'swgoh-guild-webapp.raid_results', 'swgoh-guild-webapp', 'us-central1')
    print(0)