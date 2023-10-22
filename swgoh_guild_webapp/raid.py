from dataclasses import dataclass, field
from typing import Self, Any
import requests
import pandas as pd
import datetime
from swgoh_guild_webapp.entities import Guild
import os


CURRENT_RAIDS = {'kraytdragon': 'Krayt Dragon',}
NAME_MAP = {'playerId': 'PlayerID', 'memberProgress': 'Score'}
TYPE_MAP = {'playerId': str, 'memberProgress': int}

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
    def clean_data(data: dict[str, list]) -> dict[str, list]:
        return data

    @staticmethod
    def build_scores_df(data: dict[str, list] or list[dict]) -> pd.DataFrame:
        scores_df = pd.DataFrame(data)
        scores_df = scores_df.drop([col for col in scores_df.columns if col not in TYPE_MAP.keys()], axis=1)
        scores_df = scores_df.astype(TYPE_MAP).rename(NAME_MAP, axis=1).sort_values(by='Score', ascending=False).set_index('PlayerID')
        return scores_df

    @classmethod
    def build_results(cls, guild_request_raid_result: dict) -> Self:
        raid_id = guild_request_raid_result['raidId']
        total_points = guild_request_raid_result['guildRewardScore']
        end_date = datetime.datetime.fromtimestamp(int(guild_request_raid_result['endTime']))
        scores_df = cls.build_scores_df(guild_request_raid_result['raidMember'])
        return cls(raid_id, total_points, end_date, scores_df)
    

@dataclass
class GuildRaidResults:
    guild: Guild
    raid_results: RaidResults

    def __post_init__(self):
        self.scores_df = self.build_scores_dataframe(self.guild, self.raid_results)

    @staticmethod
    def build_scores_dataframe(guild: Guild, raid_results: RaidResults) -> pd.DataFrame:
        df = guild.data.join(raid_results.scores_df, on='PlayerID').sort_values('Score', ascending=False)
        df = df.drop('GP', axis=1)
        df['EndDate'] = str(raid_results.end_date.date())
        return df

if __name__ == '__main__':
    from swgoh_commlink_fetcher import SwgohCommlinkFetcher
    guild_id = 'dYXen85NS3SCrdllQ4lAEg'
    fetcher = SwgohCommlinkFetcher()
    guild_data = fetcher.get_guild_data(guild_id)
    guild = Guild.build_guild(guild_data, members=[])
    raid = RaidResults.build_results(guild_data['recentRaidResult'][0])
    guild_raid = GuildRaidResults(guild, raid)
    print(1)