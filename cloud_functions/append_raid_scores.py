import pandas_gbq
import pandas as pd
from typing import Any
import http

def append_raid_scores(guild_request: dict[str, Any]) -> http.HTTPStatus:
    df = pd.DataFrame(guild_request)
    pandas_gbq.to_gbq(df, table_id, project_id=self.project_id, if_exists='append', table_schema=schema)
    return http.HTTPStatus.OK.value