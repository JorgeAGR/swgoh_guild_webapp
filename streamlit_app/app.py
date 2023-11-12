import streamlit as st
import json
import requests
from src.app_utils import *
from src.raid import Raid
import pandas as pd

@st.cache_data(show_spinner=False, ttl=24*60*60)
def get_raid_data(fetcher_url: str, guild_id: str, raid_id: str, interval_days: int) -> pd.DataFrame:
    response = requests.get(f'{fetcher_url}/raid/{guild_id}?raid_id={raid_id}&interval_days={interval_days}')
    df_dict = json.loads(response.content)
    return Raid(pd.DataFrame(df_dict))


def app_startup() -> None:
    st.set_page_config(layout="wide")
    start_vars = {
        # 'allycode': '000000000',
        'guild_id': 'dYXen85NS3SCrdllQ4lAEg',
        'swgoh_comlinK_fetcher_url': 'https://swgoh-comlink-fetcher-4hzooxs5za-uc.a.run.app',
        'raid': 'kraytdragon',
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


def draw_guild_roster_view() -> None:
    st.header(f'Viewing roster for {st.session_state.guild_id}')
    summary_df = st.session_state.raid_data._raw_df.groupby('EndDate').sum().reset_index()
    st.line_chart(summary_df, x='EndDate', y='Score')
    return st.dataframe(data=st.session_state.raid_data.df,
                        hide_index=True,
                        column_config={
                            'Score': st.column_config.LineChartColumn(
                                'Score History',
                                width='medium'
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