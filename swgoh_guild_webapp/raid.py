from dataclasses import dataclass, field
from typing import Self, Any
import requests
import pandas as pd
import datetime
import os


CURRENT_RAIDS = {'kraytdragon': 'Krayt Dragon',}

@dataclass
class RaidResults:
    raid_id: str
    total_points: int
    end_date: datetime.datetime
    scores_df: pd.DataFrame

    @property
    def raid_name(self) -> str:
        if self.raid_id not in CURRENT_RAIDS.keys():
            return self.raid_id
        else:
            return CURRENT_RAIDS[self.raid_id]
        
    @staticmethod
    def build_scores_df(data: dict[str, list] or list[dict]) -> pd.DataFrame:
        type_mapper = {'playerId': str, 'memberProgress': int, 'memberRank': int, 'memberAttempt': int}
        name_mapper = {'playerId': 'Player ID', 'memberProgress': 'Score', 'memberRank': 'Rank', 'memberAttempt': 'Attempt'}
        scores_df = pd.DataFrame(data).astype(type_mapper).rename(name_mapper, axis=1).sort_values(by='Score', ascending=False)
        return scores_df

    @classmethod
    def build_results(cls, guild_request: dict) -> Self:
        results_dict = guild_request['recentRaidResult'][0]
        raid_id = results_dict['raidId']
        total_points = results_dict['guildRewardScore']
        end_date = datetime.datetime.fromtimestamp(int(results_dict['endTime']))
        scores_df = cls.build_scores_df(results_dict['raidMember'])
        return cls(raid_id, total_points, end_date, scores_df)
    
if __name__ == '__main__':
    from swgoh_commlink_fetcher import SwgohCommlinkFetcher
    guild_id = 'dYXen85NS3SCrdllQ4lAEg'
    fetcher = SwgohCommlinkFetcher()
    guild_data = fetcher.get_guild_data(guild_id)
    raid = RaidResults.build_results(guild_data)
