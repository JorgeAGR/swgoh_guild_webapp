import streamlit as st

from streamlit_app.app_utils import *
from swgoh_guild_webapp.entities import Guild


def draw_guild_roster_view() -> None:
    st.header(f'Viewing roster for {st.session_state.guild_manager.guild.name}')
    st.data_editor(data=st.session_state.guild_manager.guild.data,
                   disabled=['Allycode', 'Name', 'GP'],
                   hide_index=True,
                   use_container_width=True)
    return

if __name__ == '__main__':
    app_startup()
    add_sidebar()

    guild = draw_guild_roster_view()

    # central = st.empty()
    # with central.container():
    #     if st.session_state.allycode != '000000000':
    #         guild = draw_guild_view()
    #     else:
    #         st.write('Welcome! Enter your allycode to search for guild.')

    #if allycode_input_button:
    #    with central.container():
    #        guild = draw_guild_view(int(allycode_input_box), fetcher)