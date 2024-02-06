from dataclasses import dataclass, field
import pandas as pd
import abc
import numpy as np


@dataclass
class Raid:
    raid_id: str
    _raw_df: pd.DataFrame

    def __post_init__(self) -> None:
        self.df = self._build_streamlit_df(self._raw_df)
        self.summary_df = self._build_summary_df(self._raw_df)
        return
    
    @staticmethod
    def _raids_rewards_thresholds() -> dict[str, tuple]:
        return {
            'kraytdragon': (10e6, 17e6, 25e6, 90e6, 130e6, 265e6, 416e6, 520e6),
            'speederbike': (16e6, 23.2e6, 36e6, 108e6, 125.6e6, 144e6, 208e6, 424e6),
        }
    
    @staticmethod
    def _build_summary_df(raw_df: pd.DataFrame) -> pd.DataFrame:
        return raw_df.groupby('EndDate').sum().reset_index()
    
    @property
    def rewards_thresholds(self) -> tuple[float]:
        return self._raids_rewards_thresholds()[self.raid_id]
    
    @property
    def current_reward(self) -> float:
        latest_total_points = self.summary_df.iloc[-1].Score
        rewards = np.asarray(self.rewards_thresholds)
        return rewards[rewards <= latest_total_points][-1]

    @staticmethod
    def _build_streamlit_df(raw_df: pd.DataFrame) -> pd.DataFrame:
        latest_date = raw_df.sort_values(by='EndDate', ascending=False).EndDate.iloc[0]
        latest_scores = raw_df.query(f"EndDate == '{latest_date}'").set_index('PlayerID')
        df = latest_scores[['Allycode', 'Name']]
        print(raw_df)
        df.loc[:,'Latest Score'] = latest_scores['Score'].values
        df = df.join(raw_df[raw_df.Allycode.isin(df.Allycode)].sort_values(by='EndDate').groupby('Allycode')['Score'].apply(list), on='Allycode')
        df = df.join(raw_df[raw_df.Allycode.isin(df.Allycode)].sort_values(by='EndDate').groupby('Allycode')['EndDate'].apply(list), on='Allycode')
        return df