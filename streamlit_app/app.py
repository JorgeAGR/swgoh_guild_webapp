import streamlit as st
import json
import requests
from src.app_utils import *
from src.raid import Raid
import pandas as pd
import numpy as np

@st.cache_data(show_spinner=False, ttl=24*60*60)
def get_raid_data(fetcher_url: str, guild_id: str, raid_id: str, interval_days: int) -> pd.DataFrame:
    response = requests.get(f'{fetcher_url}/raid/{guild_id}?raid_id={raid_id}&interval_days={interval_days}')
    df_dict = json.loads(response.content)
    return Raid(raid_id, pd.DataFrame(df_dict))


def app_startup() -> None:
    st.set_page_config(layout="wide")
    start_vars = {
        # 'allycode': '000000000',
        'guild_id': 'dYXen85NS3SCrdllQ4lAEg',
        'guild_name': 'Ascendant Knights',
        'swgoh_comlinK_fetcher_url': 'https://swgoh-comlink-fetcher-4hzooxs5za-uc.a.run.app',
        'raid': 'speederbike',
        'raid_interval': 30, # days
        'out_path': '/mnt/d/data/swgoh/guilds',
        'op_unit_slack': 3, # this var is to denote the "danger zone" for unit availability vs planetary op need
        'op_fig_char_max': 12, # max num of chars allowed in ops figures
        'rote_data_path': '../data/rote_data', # relative path to rote data for main app
        'rote_data_path_pages': '../../data/rote_data', # relative path to rote data for app pages
    }
    for var in start_vars:
        if var not in st.session_state:
            st.session_state[var] = start_vars[var]
    with st.spinner('Fetching guild data. This may take a bit...'):
        # st.session_state.guild_manager = init_guild(st.session_state.guild_id, st.session_state.out_path)
        st.session_state.raid_data = get_raid_data(st.session_state['swgoh_comlinK_fetcher_url'],
                                                   st.session_state['guild_id'],
                                                   st.session_state['raid'],
                                                   st.session_state['raid_interval'])
    return


def to_expected_percent(scores: list[float], average_score: float, buckets: int=5) -> list[float]:
    intervals_dict = {average_score/buckets*bucket: 1/buckets*bucket for bucket in range(buckets+1)}
    nearest_score_bucket = [np.abs(np.asarray(list(intervals_dict.keys()))-score).argmin() for score in scores]
    score_percent = [intervals_dict[list(intervals_dict.keys())[bucket_id]] for bucket_id in nearest_score_bucket]
    return score_percent


def to_max_percent(scores: list[float], buckets: int=4) -> list[float]:
    return to_expected_percent(scores, max(scores), buckets)


def format_allycode(allycode: int) -> str:
    allycode = str(allycode)
    new_allycode = ''
    for i, integer in enumerate(allycode):
        new_allycode += integer
        if i%3 == 2:
            new_allycode += '-'
    new_allycode = new_allycode[:-1]
    return new_allycode


def draw_guild_roster_view() -> None:
    st.header(f'Viewing raid performance for {st.session_state.guild_name}')
    latest_score = st.session_state.raid_data.summary_df.iloc[-1].Score
    try:
        previous_score = st.session_state.raid_data.summary_df.iloc[-2].Score
    except:
        previous_score = 0
    st.metric('Most recent score', f'{latest_score:,}', f'{int(latest_score-previous_score):,}')
    reward_avg_score = st.session_state.raid_data.current_reward/len(st.session_state.raid_data.df)
    st.line_chart(st.session_state.raid_data.summary_df, x='EndDate', y='Score', color=(219, 58, 58))
    modified_df = st.session_state.raid_data.df.copy()
    #modified_df.loc[:,'Score'] = modified_df.Score.apply(lambda x: [round(i/1e6,1) for i in x])
    modified_df.loc[:,'Expected Score'] = modified_df.Score.apply(to_expected_percent, args=(reward_avg_score, 5))
    modified_df.loc[:,'Max Score'] = modified_df.Score.apply(to_max_percent, args=(4,))
    modified_df.loc[:,'Allycode'] = modified_df.Allycode.map(format_allycode)
    print(modified_df)
    return st.dataframe(data=modified_df,
                        hide_index=True,
                        column_config={
                            'Score': st.column_config.LineChartColumn(
                                'Score History',
                                width='medium',
                                help='History of scores in Millions of points'
                            ),
                            'EndDate': None,
                            'Expected Score': st.column_config.LineChartColumn(
                                'Expected Score % History',
                                width='medium',
                                y_min=0, y_max=1,
                                help='Freeloader Detection: This represents scores as a % from the average player score required to achieve the current reward chest.'
                            ),
                            'Max Score': st.column_config.LineChartColumn(
                                'Max Score % History',
                                width='medium',
                                y_min=0, y_max=1,
                                help="Consistency Measurement: This represents scores as a % of the player's maximum score achieved."
                            )
                        },
                        use_container_width=True,
                        height=(len(st.session_state.raid_data.df) + 1) * 35 + 3)


if __name__ == '__main__':
    app_startup()
    add_sidebar()

    raid = draw_guild_roster_view()

    # central = st.empty()
    # with central.container():
    #     if st.session_state.allycode != '000000000':
    #         guild = draw_guild_view()
    #     else:
    #         st.write('Welcome! Enter your allycode to search for guild.')

    #if allycode_input_button:
    #    with central.container():
    #        guild = draw_guild_view(int(allycode_input_box), fetcher)