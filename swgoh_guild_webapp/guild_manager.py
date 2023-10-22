from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Self, Any
import requests
import pandas as pd
import datetime
import os
import json
from swgoh_guild_webapp.swgoh_commlink_fetcher import SwgohCommlinkFetcher
from swgoh_guild_webapp.entities import Guild, Player, CharacterRoster, Character
from swgoh_guild_webapp.raid import RaidResults, GuildRaidResults

'''
Need to add player data caching
'''
@dataclass
class GuildFileManager(ABC):
    guild_id: str

    @abstractmethod
    def read_latest_request(self, name: str) -> dict[str, Any] or None:
        return
    
    @abstractmethod
    def write_latest_request(self, request: dict[str, Any], name: str, time: datetime.datetime) -> None:
        return
    
    @abstractmethod
    def when_latest_request(self, name: str) -> datetime.datetime:
        return


@dataclass
class GuildLocalFileManager(GuildFileManager):
    guild_id: str
    out_dir: os.PathLike
    archive: bool = True
    '''
    archive : bool
        If True, will save the current latest data requests into an archive directory.
    '''

    def __post_init__(self) -> None:
        os.makedirs(self.guild_dir, exist_ok=True)
        os.makedirs(self.latest_dir, exist_ok=True)
        os.makedirs(self.archive_dir, exist_ok=True)
        return
    
    @property
    def guild_dir(self) -> os.PathLike:
        return os.path.join(self.out_dir, self.guild_id)
    
    @property
    def latest_dir(self) -> os.PathLike:
        return os.path.join(self.guild_dir, 'latest')
    
    @property
    def archive_dir(self) -> os.PathLike:
        return os.path.join(self.guild_dir, 'archive')

    def _save_df(self, df: pd.DataFrame, name: str, dir: os.PathLike) -> None:
        file_path = os.path.join(dir, name)
        df.to_csv(file_path, index=False)
        return

    def _read_request_json(self, file_path: os.PathLike) -> dict[str, Any]:
        with open(file_path, 'r') as file:
            request = json.load(file)
        return request

    def _write_request_json(self, request: dict[str, Any], file_path: os.PathLike) -> None:
        with open(file_path, 'w') as file:
            file.write(json.dumps(request, indent=4))
        return
    
    def when_latest_request(self, name: str) -> datetime.datetime or None:
        latest_files = os.listdir(self.latest_dir)
        latest_files.sort(key=lambda x: name in x, reverse=True)
        file_timestamp = None
        if len(latest_files) > 0 and (name in latest_files[0]): # this is to handle the no file case
            file_timestamp = int(latest_files[0].split('_')[-1])
        return datetime.datetime.fromtimestamp(file_timestamp)
    
    def _build_latest_request_file_name(self, name: str) -> str:
        latest_date = self.when_latest_request(name)
        latest_name = None
        if latest_date is not None:
            latest_name = f'{name}_{int(latest_date.timestamp())}'
        return latest_name
    
    def read_latest_request(self, name: str) -> dict[str, Any] or None:
        latest_name = self._build_latest_request_file_name(name)
        if latest_name is not None:
            return self._read_request_json(os.path.join(self.latest_dir, latest_name))
        else:
            return None
    
    def _archive_latest_request(self, name: str) -> None:
        latest_name = self._build_latest_request_file_name(name)
        if latest_name is not None:
            latest_path = os.path.join(self.latest_dir, latest_name)
            latest_request = self._read_request_json(latest_path)

            archive_name_dir = os.path.join(self.archive_dir, name)
            os.makedirs(archive_name_dir, exist_ok=True)
            self._write_request_json(latest_request, os.path.join(archive_name_dir, latest_name))
            os.remove(latest_path)
        return

    def write_latest_request(self, request: dict[str, Any], name: str, time: datetime.datetime) -> None:
        self._archive_latest_request(name)
        latest_path = os.path.join(self.latest_dir, f'{name}_{round(time.timestamp())}')
        self._write_request_json(request, latest_path)
        return


@dataclass
class GuildManager:
    fetcher: SwgohCommlinkFetcher
    guild_id: str
    file_manager: GuildFileManager
    refresh_hours: int = 24
    '''
    refresh_hours : hours after the latest data request is considered stale
    '''

    def __post_init__(self) -> None:
        self.get_latest_data()
        self.guild = self.build_guild()
        self.latest_raid = self.build_raid()

    @property
    def valid_requests(self):
        return ['guild_request', 'raid_result', 'members_request']

    def latest_request_time(self, name: str):
        latest_date = self.file_manager.when_latest_request(name)
        if latest_date is None:
            return datetime.datetime.fromtimestamp(0)
        else:
            return latest_date

    def _request_guild_data(self) -> dict[str, Any]:
        guild_request = self.fetcher.get_guild_data(self.guild_id)
        return guild_request
    
    def _request_member_data(self) -> dict[str, dict]:
        members_requests = {member['playerId']: self.fetcher.get_player_data(member['playerId'], 'playerId') for member in self._latest_guild_request['member']}
        return members_requests
    
    def get_latest_guild_data(self) -> dict[str, Any]:
        current_time = datetime.datetime.now()
        if (current_time - self.latest_request_time('guild_request')).total_seconds() > 60*60*self.refresh_hours:
            latest_guild_request = self._request_guild_data()
            self.file_manager.write_latest_request(latest_guild_request, 'guild_request', current_time)
        return self.file_manager.read_latest_request('guild_request')
    
    def get_latest_member_data(self) -> list[dict]:
        current_time = datetime.datetime.now()
        if (current_time - self.latest_request_time('members_request')).total_seconds() > 60*60*self.refresh_hours:
            latest_members_request = self._request_member_data()
            self.file_manager.write_latest_request(latest_members_request, 'members_request', current_time)
        return self.file_manager.read_latest_request('members_request')
    
    def get_latest_raid_data(self) -> dict[str, Any]:
        latest_raid_result = self.file_manager.read_latest_request('raid_result')
        if (latest_raid_result is None) or (latest_raid_result['endTime'] != self._latest_guild_request['recentRaidResult'][0]['endTime']):
            latest_raid_result = self._latest_guild_request['recentRaidResult'][0]
            self.file_manager.write_latest_request(latest_raid_result, 'raid_result', self.latest_request_time('guild_request'))
        return self.file_manager.read_latest_request('raid_result')
    
    def get_latest_data(self) -> None:
        self._latest_guild_request = self.get_latest_guild_data()
        self._latest_raid_result = self.get_latest_raid_data()
        self._latest_member_request = self.get_latest_member_data()
        return

    def build_guild(self) -> Guild:
        members = [Player.build_player(self._latest_member_request[member['playerId']], member['galacticPower']) for member in self._latest_guild_request['member']]
        return Guild.build_guild(self._latest_guild_request, members)
    
    def build_raid(self) -> RaidResults:
        raid_results = RaidResults.build_results(self._latest_raid_result)
        return GuildRaidResults(self.guild, raid_results)
    

class GuildTags:
    guild: Guild

    def __post_init__(self):
        
        return
    
if __name__ == '__main__':
    guild_id = 'dYXen85NS3SCrdllQ4lAEg'
    fetcher = SwgohCommlinkFetcher()
    file_manager = GuildLocalFileManager(guild_id, '/mnt/d/data/swgoh/guilds')
    manager = GuildManager(fetcher, guild_id, file_manager, refresh_hours=6)
    manager.latest_raid.scores_df.to_csv('raid_scores.csv')
    print(0)