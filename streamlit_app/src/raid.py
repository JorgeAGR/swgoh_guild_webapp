from dataclasses import dataclass, field
import pandas as pd


@dataclass
class Raid:
    _raw_df: pd.DataFrame

    def __post_init__(self) -> None:
        self.df = self.to_streamlit(self._raw_df)
        return
    
    @staticmethod
    def to_streamlit(raw_df: pd.DataFrame) -> pd.DataFrame:
        latest_date = raw_df.sort_values(by='EndDate', ascending=False).EndDate.iloc[0]
        latest_scores = raw_df.query(f"EndDate == '{latest_date}'").set_index('PlayerID')
        df = latest_scores[['Allycode', 'Name']]
        df.loc[:,'Latest Score'] = latest_scores['Score'].values
        df = df.join(raw_df[raw_df.Allycode.isin(df.Allycode)].groupby('Allycode')['Score'].apply(list), on='Allycode')
        return df