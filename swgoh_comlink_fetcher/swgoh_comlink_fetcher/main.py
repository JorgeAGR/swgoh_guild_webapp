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

'''
TO DOs:
- Include fetching and saving 'lastActivity' per player.
-- To convert to UTC timestamp:
    return['lastActivity']/1000
    so to datetime:
    datetime.datetime.fromtimestamp(return['lastActivity']/1000)
test allycode: 795921637
'''


def request_comlink_guild_data(comlink_host: str, guild_id: str) -> tuple[dict, dict]:
    comlink_fetcher = SwgohCommlinkFetcher(comlink_host)
    guild_data_request = comlink_fetcher.get_guild_data(guild_id)
    member_data_list = comlink_fetcher.get_member_data(guild_data_request)
    return guild_data_request, member_data_list


def update_raid_data(bq_raid_dataset: str, project_name: str, location: str, 
                     guild_data_request: dict[str, Any], member_data_list: list[dict]) -> None:
    raid = Raid.build_from_guild_request(guild_data_request)
    bq_table = RaidBigQueryTable(raid, bq_raid_dataset, project_name, location)
    latest_raid_date = bq_table.latest_raid_date()
    if raid.raid_end_date > latest_raid_date:
        scores_rows = raid.raid_result_df(guild_data_request, member_data_list).to_dict(orient='records')
        errors = bq_table.write(scores_rows)
    return


def save_comlink_guild_data(project_name: str, bucket_name: str,
                            guild_data_request: dict[str, Any], member_data_list: list[dict]) -> None:
    filestorage = GoogleCloudFileManager(project_name, bucket_name)
    filestorage.write_latest_data(guild_data_request, member_data_list)
    return


app = FastAPI()


# split this up. a fetch is only interacting with the Comlink
# a forward/proxy_fetch requests to comlink and then send to someone else in their stead 
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