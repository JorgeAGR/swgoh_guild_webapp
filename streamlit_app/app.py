import streamlit as st

from streamlit_app.app_utils import *
from swgoh_guild_webapp.entities import Guild


def draw_guild_roster_view() -> None:
    st.header(f'Viewing roster for {st.session_state.guild_id}')
    summary_df = st.session_state.raid_data._raw_df.groupby('EndDate').sum().reset_index()
    st.line_chart(summary_df, x='EndDate', y='Score')
    return st.dataframe(data=st.session_state.raid_data.df,
                        hide_index=True,
                        column_config={
                            'Score History': st.column_config.LineChartColumn(
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