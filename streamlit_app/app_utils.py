import streamlit as st
from swgoh_guild_webapp.swgoh_commlink_fetcher import SwgohCommlinkFetcher
from swgoh_guild_webapp.entities import Guild


@st.cache_data(show_spinner=False)
def init_guild(allycode: int, username: str, password: str) -> Guild:
    fetcher = SwgohCommlinkFetcher(username, 
                                   password)
    guild_dict = fetcher.get_guild(allycode)
    guild = Guild.build_guild(guild_dict)
    return guild


def app_startup() -> None:
    st.set_page_config(layout="wide")
    start_vars = {
        'allycode': '000000000',
        'op_unit_slack': 3, # this var is to denote the "danger zone" for unit availability vs planetary op need
        'op_fig_char_max': 12, # max num of chars allowed in ops figures
        'rote_data_path': '../data/rote_data', # relative path to rote data for main app
        'rote_data_path_pages': '../../data/rote_data', # relative path to rote data for app pages
    }
    for var in start_vars:
        if var not in st.session_state:
            st.session_state[var] = start_vars[var]
    if st.session_state.allycode != '000000000':
        with st.spinner('Fetching guild data. This may take a bit...'):
            st.session_state.guild = init_guild(int(st.session_state.allycode),
                                                st.session_state.fetcher_username,
                                                st.session_state.fetcher_password)
    return


def add_logo() -> None:
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(https://media.discordapp.net/attachments/319317817226952715/1083890657556447263/image.png);
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


def add_sidebar() -> None:
    with st.sidebar:
        st.title('ATA Guild Viewer')
        with st.form(key='allycode_form'):
            last_allycode = None
            if st.session_state.allycode != '000000000':
                last_allycode = st.session_state.allycode
            allycode_input_box = st.text_input('Allycode', key='allycode')
            allycode_input_button = st.form_submit_button('Enter')
    return