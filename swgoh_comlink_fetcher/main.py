from dataclasses import dataclass, field
from typing import Self, Any
import requests
import pandas as pd
import os
from fastapi import FastAPI, APIRouter
from fetcher import SwgohCommlinkFetcher
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
    comlink_fetcher = SwgohCommlinkFetcher()
    guild_data_request = comlink_fetcher.get_guild_data(guild_id)
    return requests.codes.ok

if __name__ == '__main__':
    pass