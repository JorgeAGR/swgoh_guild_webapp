from dataclasses import dataclass, field
from typing import Self, Any
import requests
import pandas as pd
import os
import abc
import json
from google.cloud import storage

@dataclass
class FileManager(abc.ABC):
    host: str

    def _save_guild_and_member_data(self, guild_data_request: dict[str, Any], member_data_list: list[dict]) -> str:
            basename = f"{guild_data_request['profile']['id']}_latest_request.json"
            guild_data_request['member'] = member_data_list
            with open(basename, 'w') as file:
                json.dump(guild_data_request, file)
            return basename
    
    @abc.abstractmethod
    def write_latest_data(self, consolidated_data: dict[str, Any]) -> int:
        return


@dataclass
class GoogleCloudFileManager(FileManager):
    bucket_name: str
    '''
    host = project_name for this manager
    '''

    def __post_init__(self):
        self.project = self.host
        client = storage.Client(project=self.project)
        self.bucket = client.bucket(self.bucket_name)
        return

    def write_latest_data(self, guild_data_request: dict[str, Any], member_data_list: list[dict]) -> int:
        filename = self._save_guild_and_member_data(guild_data_request, member_data_list)
        blob = self.bucket.blob(filename)
        blob.upload_from_filename(filename, content_type='json')
        return requests.Response.ok