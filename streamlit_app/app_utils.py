import streamlit as st
import os
import pandas as pd
import json
import requests


# @st.cache_data(show_spinner=False)
# def init_guild(guild_id: str, out_path: os.PathLike) -> Guild:
#     fetcher = SwgohCommlinkFetcher()
#     file_manager = GuildLocalFileManager(guild_id, '/mnt/d/data/swgoh/guilds', archive=True)
#     manager = GuildManager(fetcher, guild_id, file_manager, refresh_hours=24)
#     return manager


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