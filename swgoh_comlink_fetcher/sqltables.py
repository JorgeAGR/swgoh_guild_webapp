from dataclasses import dataclass, field
import abc
import os
import datetime
from typing import Self, Any
from google.cloud import bigquery

@dataclass
class Raid:
    id: str
    duration: int # in days


@dataclass
class RaidSQLTable(abc.ABC):
    raid: Raid
    table_location: str
    url: str

    @property
    def schema(self) -> dict[str, type]:
        return {'PlayerID': str, 'Allycode': int, 'Name': str, 'Score': int, 'EndDate': datetime.date}

    # @abc.abstractproperty
    # def url(self) -> str:
    #     return
    
    # @abc.abstractproperty
    # def table_location(self) -> str:
    #     return

    @abc.abstractmethod
    def query(self, query: str) -> None:
        return
    
    @property
    def latest_raid_date_query(self) -> str:
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
        return query

    @property
    def latest_raid_date(self) -> datetime.datetime:
        return datetime.date.fromisoformat(self.query(self.latest_raid_date_query))

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
    
    def query(self, query: str) -> None:
        return self.client.query(query, location=self.location)
    
    def write(self, rows: list[dict]) -> None:
        return
    

if __name__ == '__main__':
    raid = Raid('krayt_results', 3)
    sqltable = RaidGoogleBigQueryTable(raid, 'swgoh-guild-webapp.raid_results', 'swgoh-guild-webapp.raid_results', 'swgoh-guild-webapp', 'us-central1')
    print(0)