from dataclasses import dataclass
from typing import Any, Self
from abc import abstractmethod, abstractstaticmethod
from mod import Mod
import pandas as pd
import os


@dataclass
class SkillMaterialsTable:
    df: pd.DataFrame

    @classmethod
    def build_from_csv(cls, file_path: os.PathLike) -> Self:
        return cls(pd.read_csv(file_path, index_col='ID'))

    @staticmethod
    def _check_ability_material(skill_df: pd.DataFrame, skill_id: str, tier: int, material_col: str) -> bool:
        if skill_id not in skill_df.index:
            return False
        elif tier == skill_df.loc[skill_id, material_col]:
            return True
        else:
            return False
        
    def check_omicron(self, skill_id: str, tier: int) -> bool:
        return self._check_ability_material(self.df, skill_id, tier, 'Omicron Tier')
    
    def check_zeta(self, skill_id: str, tier: int) -> bool:
        return self._check_ability_material(self.df, skill_id, tier, 'Zeta Tier')


@dataclass
class Character:
    defid: str
    name: str
    rarity: int
    level: int
    gear: int
    relic: int
    mods: list[Mod]
    omicrons: int
    zetas: int

    @staticmethod
    def count_rare_abilities(skills_list: list[dict], skills_table: SkillMaterialsTable) -> int:
        omicrons = 0
        zetas = 0
        for skill in skills_list:
            omicrons += skills_table.check_omicron(skill['id'], skill['tier'])
            zetas += skills_table.check_zeta(skill['id'], skill['tier'])
        return omicrons, zetas

    @classmethod
    def build_from_json(cls, character_dict: dict[str, Any], skills_table: SkillMaterialsTable) -> Self:
        defid = character_dict['definitionId']
        name = defid.split(':')[0]
        rarity = character_dict['currentRarity']
        level = character_dict['currentLevel']
        gear = character_dict['currentTier']
        relic = character_dict['relic']
        if relic is not None:
            relic = relic['currentTier'] - 2
        else:
            relic = 0
        mods = [Mod.build_from_json(mod) for mod in character_dict['equippedStatMod']]
        omicrons, zetas = cls.count_rare_abilities(character_dict['skill'], skills_table)
        return cls(defid, name, rarity, level, gear, relic, mods, omicrons, zetas)
    

if __name__ == '__main__':
    import json
    
    with open('/mnt/c/Users/jorge/OneDrive/Documents/Projects/swgoh_guild_webapp/player.json', 'r') as file:
        player_dict = json.load(file)

    hyoda_dict = player_dict['rosterUnit'][1]
    skills_table = SkillMaterialsTable.build_from_csv('/mnt/c/Users/jorge/OneDrive/Documents/Projects/swgoh_guild_webapp/swgoh_roster_parser/util/skills_zeta_omi.csv')
    hyoda = Character.build_from_json(hyoda_dict, skills_table)
    print(hyoda)