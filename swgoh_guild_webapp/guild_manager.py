from dataclasses import dataclass, field
from typing import Self, Any
import requests
import pandas as pd
import datetime
import os
from swgoh_commlink_fetcher import SwgohCommlinkFetcher
from entities import Guild, Player, CharacterRoster, Character
from raid import RaidResults

'''
Need to add player data caching
'''

@dataclass
class GuildManager:
    fetcher: SwgohCommlinkFetcher
    guild_id: str
    out_path: os.PathLike
    refresh_hours: int = 6
    '''
    refresh_hours : hours after the latest data request is considered stale
    '''

    def __post_init__(self):
        self.latest_guild_request_time = datetime.datetime.fromtimestamp(0)
        self.request_latest_guild_data()
        self.guild = self.build_guild()
        self.latest_raid = self.build_raid()

    def _request_guild_data(self) -> tuple[dict, datetime.datetime]:
        guild_request = self.fetcher.get_guild_data(self.guild_id)
        guild_request_time = datetime.datetime.now()
        return guild_request, guild_request_time
    
    def request_latest_guild_data(self) -> None:
        if (datetime.datetime.now() - self.latest_guild_request_time).seconds > 60*60*self.refresh_hours:
            self.latest_guild_request, self.latest_guild_request_time = self._request_guild_data()
        return

    def build_guild(self) -> Guild:
        self.request_latest_guild_data()
        members = [Player.build_player(self.fetcher.get_player_data(member['playerId'], 'playerId'), member['galacticPower']) for member in self.latest_guild_request['member']]
        return Guild.build_guild(self.latest_guild_request, members)
    
    def build_raid(self) -> RaidResults:
        self.request_latest_guild_data()
        raid = RaidResults.build_results(self.latest_guild_request)
        return raid

    
if __name__ == '__main__':
    guild_id = 'dYXen85NS3SCrdllQ4lAEg'
    fetcher = SwgohCommlinkFetcher()
    manager = GuildManager(fetcher, guild_id, '/mnt/d/data/swgoh/guilds')