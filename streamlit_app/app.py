import streamlit as st

from streamlit_app.app_utils import *
from swgoh_guild_webapp.entities import Guild


def draw_guild_view() -> None:
    st.header(f'Viewing roster for {st.session_state.guild.name}')
    st.write(st.session_state.guild.data)
    return

if __name__ == '__main__':
    allycode = 795921637

    app_startup()
    add_sidebar()

    central = st.empty()
    with central.container():
        if st.session_state.allycode != '000000000':
            guild = draw_guild_view()
        else:
            st.write('Welcome! Enter your allycode to search for guild.')

    #if allycode_input_button:
    #    with central.container():
    #        guild = draw_guild_view(int(allycode_input_box), fetcher)