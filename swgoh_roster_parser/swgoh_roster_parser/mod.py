from dataclasses import dataclass
from typing import Any, Self
from abc import abstractmethod, abstractstaticmethod


class MappedDescriptor:

    @abstractstaticmethod
    def mapping(value: Any) -> Any:
        return
    
    def __set_name__(self, owner, name):
        self._name = '_' + name

    def __get__(self, owner, objtype=None) -> Any:
        return self.mapping(getattr(owner, self._name))
    
    def __set__(self, owner, value) -> None:
        setattr(owner, self._name, value)
        return


class ModStatNameDescriptor(MappedDescriptor):

    @staticmethod
    def mapping(value: int) -> str:
        return {
            '1': 'Health',
            '2': 'Strength',
            '3': 'Agility',
            '4': 'Tactics',
            '5': 'Speed',
            '6': 'Physical Damage',
            '7': 'Special Damage',
            '8': 'Armor',
            '9': 'Resistance',
            '10': 'Armor Penetration',
            '11': 'Resistance Penetration',
            '12': 'Dodge Chance',
            '13': 'Deflection Chance',
            '14': 'Physical Critical Chance',
            '15': 'Special Critical Chance',
            '16': 'Critical Damage %',
            '17': 'Potency %',
            '18': 'Tenacity %',
            '19': 'Dodge %',
            '20': 'Deflection %',
            '21': 'Physical Critical Chance %',
            '22': 'Special Critical Chance %',
            '23': 'Armor %',
            '24': 'Resistance %',
            '25': 'Armor Penetration %',
            '26': 'Resistance Penetration %',
            '27': 'Health Steal %',
            '28': 'Protection',
            '29': 'Protection Ignore %',
            '30': 'Health Regeneration %',
            '31': 'Physical Damage %',
            '32': 'Special Damage %',
            '33': 'Physical Accuracy %',
            '34': 'Special Accuracy %',
            '35': 'Physical Critical Avoidance %',
            '36': 'Special Critical Avoidance %',
            '37': 'Physical Accuracy',
            '38': 'Special Accuracy',
            '39': 'Physical Critical Avoidance',
            '40': 'Special Critical Avoidance',
            '41': 'Offense',
            '42': 'Defense',
            '43': 'Defense Penetration',
            '44': 'Evasion',
            '45': 'Critical Chance',
            '46': 'Accuracy',
            '47': 'Critical Avoidance',
            '48': 'Offense %',
            '49': 'Defense %',
            '50': 'Defense Penetration %',
            '51': 'Evasion %',
            '52': 'Accuracy %',
            '53': 'Critical Chance %',
            '54': 'Critical Avoidance %',
            '55': 'Health %',
            '56': 'Protection %',
            '57': 'Speed %',
            '58': 'Counter Attack %',
            '59': 'Taunt %',
            '60': 'Defense Penetration %',
            '61': 'Mastery %'
            }[str(value)]
    

class ModStatValueDescriptor(MappedDescriptor):

    @staticmethod
    def mapping(value: str) -> float:
        return float(value) / 1e4
        

class ModStatRollsDescriptor(MappedDescriptor):

    @staticmethod
    def mapping(values_list: list[str]) -> list[float]:
        return [float(value) / 1e5 for value in values_list]
    

class ModStatScaledRollsDescriptor(MappedDescriptor):

    @staticmethod
    def mapping(values_list: list[str]) -> list[float]:
        return [float(value)*10-1 for value in values_list]


@dataclass
class ModStat:
    name: ModStatNameDescriptor = ModStatNameDescriptor()
    value: ModStatValueDescriptor = ModStatValueDescriptor()
    rolls: ModStatRollsDescriptor = ModStatRollsDescriptor()
    scaled_rolls: ModStatScaledRollsDescriptor = ModStatScaledRollsDescriptor()


    @classmethod
    def build_from_json(cls, mod_stat_dict: dict[str, Any]) -> Self:
        return cls(mod_stat_dict['stat']['unitStatId'], mod_stat_dict['stat']['statValueDecimal'], mod_stat_dict['unscaledRollValue'], mod_stat_dict['roll'])


class ModSlotDescriptor(MappedDescriptor):

    @staticmethod
    def mapping(value: str) -> str:
        return {
            '1': 'Square',
            '2': 'Arrow',
            '3': 'Diamond',
            '4': 'Triangle',
            '5': 'Circle',
            '6': 'Cross'
        }[value]
    

class ModSetDescriptor(MappedDescriptor):

    @staticmethod
    def mapping(value: str) -> str:
        return {
            '1': 'Health',
            '2': 'Offense',
            '3': 'Defense',
            '4': 'Speed',
            '5': 'Critical Chance',
            '6': 'Critical Damage',
            '7': 'Potency',
            '8': 'Tenacity'
        }[value]
    

class ModRarityDescriptor(MappedDescriptor):

    @staticmethod
    def mapping(value: str) -> int:
        return int(value)


class ModTierDescriptor(MappedDescriptor):

    @staticmethod
    def mapping(value: int) -> str:
        return {
            1: 'E',
            2: 'D',
            3: 'C',
            4: 'B',
            5: 'A',
        }[value]


@dataclass
class Mod:
    primary: ModStat
    secondaries: list[ModStat]
    slot: ModSlotDescriptor = ModSlotDescriptor()
    set: ModSetDescriptor = ModSetDescriptor()
    rarity: ModRarityDescriptor = ModRarityDescriptor()
    tier: ModTierDescriptor = ModTierDescriptor()
    level: int

    @property
    def speed(self):
        if self.primary.name == 'Speed':
            speed = self.primary.value
        else:
            speed = 0
            for secondary in self.secondaries:
                if secondary.name == 'Speed':
                    speed += secondary.value
        return speed

    @classmethod
    def build_from_json(cls, mod_dict: dict[str, Any]) -> Self:
        primary = ModStat.build_from_json(mod_dict['primaryStat'])
        secondaries = [ModStat.build_from_json(secondary) for secondary in mod_dict['secondaryStat']]
        slot = mod_dict['definitionId'][2]
        set = mod_dict['definitionId'][0]
        rarity = mod_dict['definitionId'][1]
        tier = mod_dict['tier']
        level = mod_dict['level']
        return cls(primary, secondaries, slot, set, rarity, tier, level)
    

if __name__ == '__main__':
    import json
    
    with open('/mnt/c/Users/jorge/OneDrive/Documents/Projects/swgoh_guild_webapp/player.json', 'r') as file:
        player_dict = json.load(file)

    hyoda = player_dict['rosterUnit'][1]
    equippedStatMod = hyoda['equippedStatMod']
    mods = []
    for mod in equippedStatMod:
        mods.append(Mod.build_from_json(mod))
    for mod in mods:
        print(mod.speed)
    print(mods[0].set)