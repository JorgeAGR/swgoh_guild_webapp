from dataclasses import dataclass, field
from typing import Self, Any
import http
import pandas as pd
import os
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
import datetime
from swgoh_comlink_fetcher.fetcher import SwgohCommlinkFetcher
from swgoh_comlink_fetcher.filestorage import GoogleCloudFileManager
from swgoh_comlink_fetcher.sqltables import RaidBigQueryTable, Raid


app = FastAPI()


@app.post('/comlink/{guild_id}')
def fetch_latest_guild_data(guild_id: str) -> Response:
    comlink_host = os.environ['COMLINK_URL']
    bq_raid_dataset = os.environ['BQ_RAID_DATASET']
    bucket_name = os.environ['BUCKET_NAME']
    project_name = os.environ['PROJECT_NAME']
    location = os.environ['LOCATION']

    guild_data_request, member_data_list = request_comlink_guild_data(comlink_host, guild_id)

    update_raid_data(bq_raid_dataset, project_name, location, guild_data_request, member_data_list)

    save_comlink_guild_data(project_name, bucket_name, guild_data_request, member_data_list)
    return JSONResponse(content={'message': f'Latest data for {guild_id} fetched.'})


@app.get('/raid/{guild_id}') # modify this wil multiple arguments
def get_raid_results(guild_id: str, raid_id: str='kraytdragon', interval_days: int=30) -> dict[str, dict]:
    bq_raid_dataset = os.environ['BQ_RAID_DATASET']
    project_name = os.environ['PROJECT_NAME']
    location = os.environ['LOCATION']

    raid = Raid.build_dummy_raid(raid_id)
    bq_table = RaidBigQueryTable(raid, bq_raid_dataset, project_name, location)
    raid_results = bq_table.raid_results(interval_days)

    return raid_results.to_dict()


if __name__ == '__main__':
    import yaml
    
    with open('config/environ_vars.yaml', 'r') as file:
        environ_vars = yaml.safe_load(file)
    for var in environ_vars:
        os.environ[var] = str(environ_vars[var])

    # response = get_raid_results(os.environ['GUILD_ID'], os.environ['RAID_ID'])
    response = fetch_latest_guild_data(os.environ['GUILD_ID'])
    print(0)