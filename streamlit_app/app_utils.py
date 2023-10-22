import streamlit as st
import os
from swgoh_guild_webapp.swgoh_commlink_fetcher import SwgohCommlinkFetcher
from swgoh_guild_webapp.entities import Guild
from swgoh_guild_webapp.guild_manager import GuildManager, GuildLocalFileManager


@st.cache_data(show_spinner=False)
def init_guild(guild_id: str, out_path: os.PathLike) -> Guild:
    fetcher = SwgohCommlinkFetcher()
    file_manager = GuildLocalFileManager(guild_id, '/mnt/d/data/swgoh/guilds', archive=True)
    manager = GuildManager(fetcher, guild_id, file_manager, refresh_hours=24)
    return manager


def app_startup() -> None:
    st.set_page_config(layout="wide")
    start_vars = {
        # 'allycode': '000000000',
        'guild_id': 'dYXen85NS3SCrdllQ4lAEg',
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
        st.session_state.guild_manager = init_guild(st.session_state.guild_id, st.session_state.out_path)
    return


def add_sidebar() -> None:
    with st.sidebar:
        st.title('Ascendant Knights Guild Tool')
        # with st.form(key='allycode_form'):
        #     last_allycode = None
        #     if st.session_state.allycode != '000000000':
        #         last_allycode = st.session_state.allycode
        #     allycode_input_box = st.text_input('Allycode', key='allycode')
        #     allycode_input_button = st.form_submit_button('Enter')
    return


def add_logo() -> None:
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(https://media.discordapp.net/attachments/1043780117824012448/1141821400055812126/Photoleap_17_08_2023_02_45_14_h0mMS.jpg);
                background-repeat: no-repeat;
                padding-top: 120px;
                background-position: 20px 20px;
                wdith: 120px;
                height: 120px;
            }
            [data-testid="stSidebarNav"]::before {
                content: "ATA Guild Management";
                margin-left: 20px;
                margin-top: 20px;
                font-size: 30px;
                position: relative;
                top: 100px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    return