import streamlit as st
import os
import yaml
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from swgoh_guild_webapp.entities import Guild
from swgoh_guild_webapp.tb_rote import Planet, Operation
from app_utils import *


def style_quantity(row, props='') -> list[str]:
    diff = row['owner'] - row['quantity']
    if (diff < 0) or (diff == np.nan):
        props = 'background-color:FireBrick;'
    elif (diff > st.session_state.op_unit_slack):
        props = 'background-color:DarkGreen;'
    else:
        props = 'color:black;background-color:Gold;'
    return [props for i in range(len(row))]
    

def guild_op_status_df(operation: Operation, guild: Guild) -> pd.DataFrame:
    op_status_df = operation.data.set_index('charid')
    allowed_query = f"(combat_type == 'character' and relic >= {operation.relic_req}) or (combat_type == 'ship' and rarity == 7)"
    have_df = guild.data.query(allowed_query).groupby('charid').count()['owner']
    names_df = guild.data[['charid', 'name']].drop_duplicates().set_index('charid')
    op_status_df = op_status_df.join(have_df).join(names_df).fillna(0).astype({'owner': int})[['name', 'quantity', 'owner',]].set_index('name')

    # aesthetics code for nicer presentation
    # df = op_status_df.style.hide().apply(style_quantity, axis=1).apply_index(style_quantity, axis=0)#.relabel_index(['Need', 'Available'], axis=1)
    # df = df.rename(columns={'name': 'Name', 'quantity': 'Need', 'owner': 'Available'})
    return op_status_df


def create_names_array(op_status_df: pd.DataFrame) -> list[str]:
    names_array = []
    for i in range(len(op_status_df)):
        for j in range(op_status_df.iloc[i]['quantity']):
            names_array.append(str(op_status_df.index[i]))
    return names_array


def warp_name_text(name: str) -> list[str]:
    name_chunks = name.split(' ')
    name_pairs = len(name_chunks) // 2
    new_name = []
    for pair in np.arange(np.floor(name_pairs), dtype=int):
        if (len(name_chunks[2*pair]) + len(name_chunks[2*pair+1])) <= st.session_state.op_fig_char_max:
            new_name.append(name_chunks[2*pair] + ' ' + name_chunks[2*pair+1])
        else:
                new_name.append(name_chunks[2*pair])
                new_name.append(name_chunks[2*pair+1])
    if (name_pairs * 2) < len(name_chunks):
        new_name.append(name_chunks[-1])
    return new_name


def make_op_figure(op_status_df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10,10))
    ax.set_axis_off()
    unit_rows = 3
    unit_cols = 5
    for r in range(unit_rows-1):
        ax.axhline((r+1)/unit_rows, color='black')
    for c in range(unit_cols-1):
        ax.axvline((c+1)/unit_cols, color='black')
    names_array = create_names_array(op_status_df)
    for r in np.arange(unit_rows):
        for c in np.arange(unit_cols):
            name = names_array[unit_rows*r+c]
            new_name = warp_name_text(name)
            for n, name in enumerate(new_name):
                # remember that y is drawn from top down
                ax.text((c+0)/unit_cols, (0.5-n*0.1-r+2)/unit_rows, name,
                        fontsize=15)
    return fig


def compile_planets() -> list[Planet]:
    planets = {}
    planets_path = os.path.join(__file__.rstrip(os.path.basename(__file__)), st.session_state.rote_data_path_pages)
    planet_yamls = os.listdir(planets_path)
    for planet_yaml in planet_yamls:
        planet = Planet.build_from_yaml(os.path.join(planets_path, planet_yaml))
        planets[f'{planet.sector}{planet.alignment}'] = planet
    planet_argsort = np.argsort(list(planets.keys()))
    return list(np.asarray(list(planets.values()))[planet_argsort])


def main_view() -> None:
    planets = compile_planets()

    tabs = st.tabs([planet.name for planet in planets])
    for p, tab in enumerate(tabs):
        with tab:
            opscol, cmcol = st.columns([3, 1])
            with opscol:
                operations = [[planets[p].operations[i] for i in range(3)],
                              [planets[p].operations[i] for i in range(3, 6)]]
                with st.container():
                    for i, ops_row in enumerate(operations):
                        ops_cols = st.columns([1, 1, 1])
                        for j, op in enumerate(ops_row):
                            op_status_df = guild_op_status_df(op, st.session_state.guild)
                            with ops_cols[j]:
                                fig = make_op_figure(op_status_df)
                                st.caption(f'Operation {2*i+j+1}')
                                st.pyplot(fig)
            with cmcol:
                st.write(planets[p].combat_missions)
    return

    '''
    tabs = st.tabs([planet.name for planet in planets])
    for i, tab in enumerate(tabs):
        with tab:
            opscol, cmcol = st.columns([3, 1])
            with opscol:
                for i, op in enumerate(planets[i].operations):
                    fig, ax = plt.subplots(figsize=(2,2))
                    ax.set_axis_off()
                    rows = 3
                    cols = 5
                    for r in range(rows-1):
                        ax.axhline((r+1)/rows)
                    for c in range(cols-1):
                        ax.axvline((c+1)/cols)
                    st.pyplot(fig)
                    with st.expander(label=f'Operation {i+1}'):
                        need_df = guild_op_status_df(op, st.session_state.guild)
                        st.dataframe(need_df)
            with cmcol:
                st.write(planets[i].combat_missions)
    '''

if __name__ == '__main__':
    app_startup()
    add_sidebar()

    central = st.empty()
    with central.container():
        if st.session_state.allycode != '000000000':
            main_view()
        else:
            st.write('Welcome! Enter your allycode to search for guild.')