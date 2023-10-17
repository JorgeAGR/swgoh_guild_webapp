from dataclasses import dataclass, field
from typing import Self, Any
import requests
import pandas as pd
import os

'''
TO DOs:
- Include fetching and saving 'lastActivity' per player.
-- To convert to UTC timestamp:
    return['lastActivity']/1000
    so to datetime:
    datetime.datetime.fromtimestamp(return['lastActivity']/1000)
test allycode: 795921637
'''

@dataclass
class SwgohCommlinkFetcher:
    address: str = 'localhost'
    port: int = 3200

    @property
    def host(self) -> str:
        return f'http://{self.address}:{self.port}'
    
    @property
    def game_version(self) -> str:
        return requests.post(f'{self.host}/metadata').json()['latestGamedataVersion']

    @property
    def unit_data(self):
        return pd.DataFrame(self._fetch_unit_data()['units'])
    
    def get_unit_data(self) -> dict[Any]:
        # currently only need segment 3 for unit data
        payload = {
            "payload": {
                "version": self.game_version,
                "includePveUnits": False,
                "requestSegment": 3
            },
            "enums": False
            }
        return requests.post(f'{self.host}/data', json=payload).json()['units']
    
    # move?
    @staticmethod
    def _parse_relic(relic: dict[str, int] or None) -> int:
        if relic is None:
            return -1
        else:
            return relic['currentTier']-2

    # move?
    @staticmethod
    def _parse_definitionId(definitionId: str) -> str:
        return definitionId.split(':')[0]
    
    # move?
    @staticmethod
    def _parse_combatType(combatType: int) -> str:
        if combatType == 1:
            return 'CHARACTER'
        elif combatType == 2:
            return 'SHIP'
        else:
            return 'N/A'

    # dep?
    @staticmethod
    def _parse_roster_request(rosterUnit: dict[str, any]) -> dict[str, str or int]:
        parsed_roster = {}
        for char_dict in rosterUnit:
            key = SwgohCommlinkFetcher._parse_definitionId(char_dict['definitionId'])
            parsed_roster = {key: {'charid': key,
                                'name': key,
                                'relic': SwgohCommlinkFetcher._parse_relic(char_dict['relic']),
                                'rarity': char_dict['currentRarity'],
                                'gp': 0,
                                'combat_type': char_dict['combatType']} for char_dict in rosterUnit}
        return parsed_roster

    def get_player_data(self, value: int or str, key: str) -> dict[str, Any]:
        '''
        key : 'allyCode' or 'playerId'
        '''
        if key not in ('allyCode', 'playerId'):
            raise 'Invalid key for fetching player data'
        if (key == 'allyCode') and isinstance(value, int):
            value = str(value)
        payload = {
            "payload": {
                key: value,
            },
            "enums": False
            }
        return requests.post(f'{self.host}/player', json=payload).json()
    
    def get_guild_data(self, guild_id: str) -> dict[str, Any]:
        payload = {
            "payload": {
                "guildId": guild_id,
                "includeRecentGuildActivityInfo": True
            },
            "enums": False
            }
        return requests.post(f'{self.host}/guild', json=payload).json()['guild']