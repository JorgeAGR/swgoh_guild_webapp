import os
from typing import Any
import pandas_gbq

def get_bq_latest_raid(request: dict[str, Any]) -> dict[str, dict]:
    query = f'''
    SELECT
        PlayerID,
        Allycode,
        Name,
        Score
        FROM
        `{os.environ['PROJECT']}.{os.environ['DATASET']}.{os.environ['TABLE']}` t
        WHERE DATE(EndDate) IN 
        (
        SELECT 
            MAX(DATE(EndDate)) AS max_partition
        FROM `{os.environ['PROJECT']}.{os.environ['DATASET']}.{os.environ['TABLE']}`
        WHERE DATE(EndDate) >= DATE_SUB(CURRENT_DATE(), INTERVAL {os.environ['RAID_DAYS_CYCLE']} DAY)
        )
    AND DATE(EndDate) >= DATE_SUB(CURRENT_DATE(), INTERVAL {os.environ['RAID_DAYS_CYCLE']} DAY)
    '''
    df = pandas_gbq.read_gbq(query, project_id=os.environ['PROJECT'])
    return df.to_json()