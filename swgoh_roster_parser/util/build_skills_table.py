from dataclasses import dataclass
from typing import Any, Self
import pandas as pd


def check_rare_material_tier(tiers_list: list[dict], flag_key: str) -> int:
    # Using 0-based index, which the character data uses
    for i, tier in enumerate(tiers_list):
        if tier[flag_key] == True:
            return i
    return -1


def check_zeta_tier(tiers_list: list[dict]) -> int:
    return check_rare_material_tier(tiers_list, 'isZetaTier')


def check_omicron_tier(tiers_list: list[dict]) -> int:
    return check_rare_material_tier(tiers_list, 'isOmicronTier')


def parse_skill_dict(skill_dict: dict[str, Any]) -> tuple[str, int, int]:
    skill_id = skill_dict['id']
    omicron_tier = check_omicron_tier(skill_dict['tier'])
    zeta_tier = check_zeta_tier(skill_dict['tier'])
    return skill_id, omicron_tier, zeta_tier


def create_skills_dataframe(skills_list: list[dict]) -> pd.DataFrame:
    skill_id_list = []
    skill_omicron_tiers = []
    skill_zeta_tiers = []
    for skill in skills_list:
        skill_id, omicron_tier, zeta_tier = parse_skill_dict(skill)
        if (omicron_tier != -1) or (zeta_tier != -1):
            skill_id_list.append(skill_id)
            skill_omicron_tiers.append(omicron_tier)
            skill_zeta_tiers.append(zeta_tier)
    return pd.DataFrame(data={'ID': skill_id_list, 'Omicron Tier': skill_omicron_tiers, 'Zeta Tier': skill_zeta_tiers}).set_index('ID')


if __name__ == '__main__':
    import requests

    comlink_host = 'https://swgoh-comlink-4hzooxs5za-uc.a.run.app'
    payload = {'payload': {'version': '0.33.9:l0BFemZbSAifxVZGWQslhQ',
                           'includePveUnits': False,
                           'requestSegment': 1},
                'enums': False}
    data = requests.post(f'{comlink_host}/data', json=payload).json()
    skills_list = data['skill']