from dataclasses import dataclass
from typing import Any, Self
from abc import abstractmethod, abstractstaticmethod
from character import Character, SkillMaterialsTable
from datetime import datetime


class DivisionDescriptor:

    @staticmethod
    def mapping(value: int) -> int:
        return {
            5: 5,
            10: 4,
            15: 3,
            20: 2,
            25: 1
        }[value]
    
    def __set_name__(self, owner, name):
        self._name = '_' + name

    def __get__(self, owner, objtype=None) -> Any:
        return self.mapping(getattr(owner, self._name))
    
    def __set__(self, owner, value) -> None:
        setattr(owner, self._name, value)
        return


@dataclass
class GACRanking:
    skill_rating: int
    league: str
    division: DivisionDescriptor = DivisionDescriptor()

    @classmethod
    def build_from_dict(cls, rating_dict: dict[str, Any]) -> Self:
        skill_rating = rating_dict['playerSkillRating']['skillRating']
        league = rating_dict['playerRankStatus']['leagueId']
        division = rating_dict['playerRankStatus']['divisionId']
        return cls(skill_rating, league, division)


@dataclass
class Player:
    id: str
    allycode: int
    name: str
    level: int
    roster: dict[str, Character] # this likely needs to be a special object or something. since it needs to be sorted by "power" (mix of relic sorting, omis, etc)
    guild_id: str
    guild_name: str
    gac_ranking: GACRanking
    last_activity: datetime

    @classmethod
    def build_from_dict(cls, player_dict: dict[str, Any], skills_table: SkillMaterialsTable):
        player_id = player_dict['playerId']
        allycode = player_dict['allyCode']
        name = player_dict['name']
        level = player_dict['level']
        roster_list = [Character.build_from_json(character_dict, skills_table) for character_dict in player_dict['rosterUnit']]
        roster = {character.name: character for character in roster_list}
        guild_id = player_dict['guildId']
        guild_name = player_dict['guildName']
        gac_ranking = GACRanking.build_from_dict(player_dict['playerRating'])
        last_activity = player_dict['lastActivityTime']
        return cls(player_id, allycode, name, level, roster, guild_id, guild_name, gac_ranking, last_activity)


if __name__ == '__main__':
    import json
    
    with open('/mnt/c/Users/jorge/OneDrive/Documents/Projects/swgoh_guild_webapp/player.json', 'r') as file:
        player_dict = json.load(file)

    skills_table = SkillMaterialsTable.build_from_csv('/mnt/c/Users/jorge/OneDrive/Documents/Projects/swgoh_guild_webapp/swgoh_roster_parser/util/skills_zeta_omi.csv')
    player = Player.build_from_dict(player_dict, skills_table)
    print(player)