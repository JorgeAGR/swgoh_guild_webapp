from dataclasses import dataclass, field
from typing import Self
import pandas as pd
import numpy as np
import yaml

#from base import CharacterRoster, Character


@dataclass
class Operation:
    relic_req: int
    points: float # in Millions of points
    char_reqs: dict[str, int]

    def __post_init__(self):
        self.data = self._build_df(self.char_reqs)
        return

    @staticmethod
    def _build_df(char_reqs: dict[str, int]) -> pd.DataFrame:
        df = pd.DataFrame({'charid': char_reqs.keys(),
                           'quantity': char_reqs.values()})
        return df

@dataclass
class CombatMission:
    relic_req: int
    points: float # in Millions of points
    waves: int = 2
    special_reqs: list[str] = None

    @classmethod
    def build_from_planet(cls, relic_req: int, cm_dict: dict[str, float or list[str]]) -> Self:
        return cls(relic_req, **cm_dict)


@dataclass
class Planet:
    name: str
    relic_req: int
    combat_missions: list[CombatMission]
    operations: list[Operation]
    sector: int
    alignment: str
    star_thresh: list[float] # in Millions of points

    def __post_init__(self) -> None:
        self.data = self._build_df(self.operations)
        return

    @staticmethod
    def _build_df(operations: list[Operation]) -> pd.DataFrame:
        df = operations[-1].data.set_index('charid')
        for i in range(len(operations)-1):
            df = df.join(operations[i].data.set_index('charid'), how='outer', rsuffix=f'{i}')
        df.loc[:,'quantity'] = df.sum(axis=1).astype(int)
        return df['quantity'].reset_index()

    @property
    def alignment(self) -> str:
        return self._alignment

    @alignment.setter
    def alignment(self, value: str) -> None:
        if value.lower() in ('dark', 'light', 'mixed'):
            self._alignment = value.lower()
        else:
            print(f'Alignment for {self.name} value not recognized. Defaulting to "mixed"')
            self._alignment = 'mixed'
        return

    @property
    def star_thresh(self) -> list[float]:
        return self._star_thresh

    @star_thresh.setter
    def star_thresh(self, req_thresh: list[float]) -> None:
        assert len(req_thresh) == 3, f'Number of thresholds for {self.name} stars is different than 3'
        self._star_thresh = req_thresh
        return

    @classmethod
    def build_from_yaml(cls, yaml_path: str) -> Self:
        with open(yaml_path) as file:
            planet_yaml = yaml.safe_load(file)
        relic_req = planet_yaml['relic_req']
        planet_yaml['combat_missions'] = [CombatMission.build_from_planet(relic_req, cm_dict) for cm_dict in planet_yaml['combat_missions']]
        points = planet_yaml['operations']['points']
        planet_yaml['operations'] = [Operation(relic_req, points, char_dict) for char_dict in planet_yaml['operations']['reqs']]
        return cls(**planet_yaml)


if __name__ == '__main__':
    planet = Planet.build_from_yaml('../data/rote_data/corellia.yaml')
    planet.data