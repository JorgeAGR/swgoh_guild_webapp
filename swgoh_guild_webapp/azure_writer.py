from dataclasses import dataclass
from typing import Any, Self
import yaml
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey


@dataclass
class AzureWriter:
    host: str
    master_key: str
    database_id: str
    container_id: str

    def __post_init__(self):
        client = cosmos_client.CosmosClient(self.host, {'masterKey': self.master_key}, user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
        try:
            self.db = client.create_database(id=self.database_id)
            print('Database with id \'{0}\' created'.format(self.database_id))

        except exceptions.CosmosResourceExistsError:
            self.db = client.get_database_client(self.database_id)
            print('Database with id \'{0}\' was found'.format(self.database_id))

        # setup container for this sample
        try:
            self.container = self.db.create_container(id=self.container_id, partition_key=PartitionKey(path='/nameKey'))
            print('Container with id \'{0}\' created'.format(self.container_id))

        except exceptions.CosmosResourceExistsError:
            self.container = self.db.get_container_client(self.container_id)
            print('Container with id \'{0}\' was found'.format(self.container_id))
        return
    
    @classmethod
    def build(cls, config_path: str) -> Self:
        with open(config_path) as file:
            config = yaml.safe_load(file)
        return cls(config)
    
    def add_item(self, item_dict: dict[str, Any]) -> None:
        response = self.container.upsert_item(body=item_dict)
        print(f"Added item with nameKey/id {response['nameKey']/{response['id']}}")
        return response


if __name__ == '__main__':
    from swgoh_commlink_fetcher import SwgohCommlinkFetcher


    fetcher = SwgohCommlinkFetcher()
    db_writer = AzureWriter.build('../config/azure_config.yaml')
    for unit_dict in fetcher.get_unit_data():
        db_writer.add_unit(unit_dict)
