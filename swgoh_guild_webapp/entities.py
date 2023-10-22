from dataclasses import dataclass, field
from typing import Self, Any
import pandas as pd

@dataclass
class Character:
    charid: str
    name: str
    relic: int
    rarity: int
    gp: int
    combat_type: str

    @property
    def combat_type(self) -> str:
        return self._combat_type

    @combat_type.setter
    def combat_type(self, value: str) -> None:
        if str(value).lower() in ('character', 'ship'):
            self._combat_type = value.lower()
        else:
            print(f'{self.name} type not recognized! Setting to character by default.')
            self._combat_type = 'character'
        return

    @classmethod
    def build_char(cls, char_dict: dict[str, str or int]) -> Self:
        return cls(**char_dict)

    def to_list(self):
        return [self.charid, self.name, self.relic, self.rarity, self.gp, self.combat_type]


@dataclass
class CharacterRoster:
    roster_dict: dict[str, Character] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # self.data = self._build_df(self.roster_dict)
        return
    
    @staticmethod
    def _build_df(roster_dict: dict[str, Character]) -> pd.DataFrame:
        col_names = Character.__dataclass_fields__.keys()
        df = pd.DataFrame({col: [] for col in col_names})
        for char in roster_dict.values():
            df.loc[len(df), :] = char.to_list()
        df = df.astype({col: Character.__dataclass_fields__[col].type for col in col_names})
        return df

    def add_unit(self, charid: str, name: str, relic: int, rarity: int, gp: int, combat_type: str) -> None:
        self.roster_dict[charid] = Character(charid, name, relic, rarity, gp, combat_type)
        return

    @classmethod
    def build_roster(cls, raw_roster_dict: dict[str, str or int]) -> Self:
        roster_dict = {}
        for charid, char_dict in raw_roster_dict.items():
            roster_dict[charid] = Character.build_char(char_dict)
        return cls(roster_dict)

    def __getitem__(self, key):
        return self.roster_dict[key]


@dataclass
class Player:
    player_id: str
    allycode: int
    name: str
    gp: int
    roster: CharacterRoster

    def __post_init__(self) -> None:
        #self.data = self._build_df(self.name, self.allycode, self.roster)
        return

    @staticmethod
    def _build_df(name: str, allycode: int, roster: CharacterRoster) -> pd.DataFrame:
        df = roster.data
        df.loc[:, 'owner'] = name
        df.loc[:,'allycode'] = allycode
        return df

    @classmethod
    def build_player(cls, player_request: dict[str, Any], gp: int) -> Self:
        player_id = player_request['playerId']
        allycode = int(player_request['allyCode'])
        name = player_request['name']
        return cls(player_id, allycode, name, gp, CharacterRoster([]))


@dataclass
class Guild:
    guild_id: str
    name: str
    guild_gp: int
    members: list[Player]

    def __post_init__(self) -> None:
        self.data = self._build_df(self.members)
        return

    @staticmethod
    def _build_df(members: list[Player]) -> pd.DataFrame:
        data = {'PlayerID': [member.player_id for member in members],
                'Allycode': [member.allycode for member in members],
                'Name': [member.name for member in members],
                'GP': [member.gp for member in members]}
        type_mapper = {'PlayerID': str, 'Allycode': str, 'Name': str, 'GP': int}
        df = pd.DataFrame(data).astype(type_mapper).sort_values(by='GP', ascending=False).set_index('PlayerID')
        return df

    @classmethod
    def build_guild(cls, guild_request: dict[str, Any], members: list[Player]):
        guild_id = guild_request['profile']['id']
        name = guild_request['profile']['name']
        guild_gp = guild_request['profile']['guildGalacticPower']
        return cls(guild_id, name, guild_gp, members)


if __name__ == '__main__':
    from swgoh_commlink_fetcher import SwgohCommlinkFetcher
    guild_id = 'dYXen85NS3SCrdllQ4lAEg'
    fetcher = SwgohCommlinkFetcher()
    guild_request = fetcher.get_guild_data(guild_id)
    guild = Guild.build_guild(guild_request, members=[])