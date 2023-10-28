from dataclasses import dataclass, field
from typing import Self, Any
import requests
import pandas as pd
import os
from fastapi import FastAPI, APIRouter
import datetime
from fetcher import SwgohCommlinkFetcher
import sqltables
# from fastapi.testclient import TestClient


'''
TO DOs:
- Include fetching and saving 'lastActivity' per player.
-- To convert to UTC timestamp:
    return['lastActivity']/1000
    so to datetime:
    datetime.datetime.fromtimestamp(return['lastActivity']/1000)
test allycode: 795921637
'''

app = FastAPI()

# split this up. a fetch is only interacting with the Comlink
# a forward/proxy_fetch requests to comlink and then send to someone else in their stead 
@app.post('/guild/{guild_id}')
def fetch_latest_guild_data(guild_id: str) -> int:
    comlink_host = os.environ['COMLINK_URL']
    bq_raid_dataset = os.environ['BQ_RAID_DATASET']
    bucket_name = os.environ['BUCKET_NAME']
    project_name = os.environ['PROJECT_NAME']
    location = os.environ['LOCATION']

    comlink_fetcher = SwgohCommlinkFetcher(project_name, comlink_host, bucket_name)
    guild_data_request = comlink_fetcher.get_guild_data(guild_id)
    member_data_list = comlink_fetcher.get_member_data(guild_data_request)

    raid = sqltables.Raid.build_from_guild_request(guild_data_request)

    bq_table = sqltables.RaidGoogleBigQueryTable(raid, bq_raid_dataset, bq_raid_dataset, project_name, location)
    latest_raid_date = bq_table.latest_raid_date()
    if len(latest_raid_date) == 0:
        latest_raid_date = datetime.date.fromtimestamp(0)
    else:
        latest_raid_date = latest_raid_date.iloc[0].EndDate

    if raid.raid_end_date > latest_raid_date:
        scores_rows = raid.raid_result_df(guild_data_request, member_data_list).to_dict(orient='records')
        errors = bq_table.write(scores_rows)

    return comlink_fetcher.save_guild_and_member_data(guild_data_request, member_data_list)


if __name__ == '__main__':
    os.environ['COMLINK_URL'] = 'http://localhost:3200'
    os.environ['BQ_RAID_DATASET'] = 'swgoh-guild-webapp.raid_results'
    os.environ['BUCKET_NAME'] = 'swgoh_data'
    os.environ['PROJECT_NAME'] = 'swgoh-guild-webapp'
    os.environ['LOCATION'] = 'us-central1'
    response = fetch_latest_guild_data('dYXen85NS3SCrdllQ4lAEg')
    print(0)