
import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import random

st.set_page_config(
    page_title="Community Connection Lab",
    layout="wide"
)

st.title("Community Connection Lab")
st.write("Simulasi interaktif jaringan pertemanan")

@st.cache_resource
def load_network():
    G = nx.karate_club_graph()
    return G

if "G" not in st.session_state:
    st.session_state.G = load_network().copy()

if "positions" not in st.session_state:
    st.session_state.positions = nx.spring_layout(
        st.session_state.G, seed=7
    )

G = st.session_state.G
pos = st.session_state.positions

col1, col2, col3 = st.columns(3)
col1.metric("Jumlah anggota", G.number_of_nodes())
col2.metric("Jumlah hubungan", G.number_of_edges())
col3.metric(
    "Kelompok terhubung",
    nx.number_connected_components(G)
)

st.subheader("Kontrol jaringan")

anggota = sorted(G.nodes())
a, b = st.columns(2)

with a:
    u = st.selectbox("Anggota A", anggota)

with b:
    v = st.selectbox(
        "Anggota B",
        anggota,
        index=1
    )

c1, c2, c3 = st.columns(3)

with c1:
    if st.button("Tambah hubungan"):
        if u == v:
            st.warning("Pilih dua anggota berbeda.")
        elif G.has_edge(u, v):
            st.warning("Hubungan tersebut sudah ada.")
        else:
            G.add_edge(u, v)
            st.rerun()

with c2:
    if st.button("Hapus hubungan"):
        if G.has_edge(u, v):
            G.remove_edge(u, v)
            st.rerun()
        else:
            st.warning("Hubungan tersebut belum ada.")

with c3:
    if st.button("Reset jaringan"):
        st.session_state.G = load_network().copy()
        st.session_state.positions = nx.spring_layout(
            st.session_state.G, seed=7
        )
        st.rerun()

st.subheader("Visualisasi jaringan")

edges_x, edges_y = [], []

for x, y in G.edges():
    edges_x.extend([pos[x][0], pos[y][0], None])
    edges_y.extend([pos[x][1], pos[y][1], None])

derajat = dict(G.degree())

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=edges_x,
    y=edges_y,
    mode="lines",
    line=dict(width=1, color="#9CA3AF"),
    hoverinfo="none"
))

fig.add_trace(go.Scatter(
    x=[pos[n][0] for n in G.nodes()],
    y=[pos[n][1] for n in G.nodes()],
    mode="markers+text",
    text=[str(n) for n in G.nodes()],
    textposition="middle center",
    marker=dict(
        size=[12 + derajat[n] for n in G.nodes()],
        color=[derajat[n] for n in G.nodes()],
        colorscale="Viridis",
        showscale=True,
        colorbar=dict(title="Hubungan"),
        line=dict(width=1, color="white")
    ),
    hovertemplate=(
        "Anggota %{text}<br>"
        "Jumlah hubungan: %{marker.color}"
        "<extra></extra>"
    )
))

fig.update_layout(
    height=650,
    showlegend=False,
    margin=dict(l=10, r=10, t=20, b=10),
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    plot_bgcolor="white"
)

st.plotly_chart(fig, use_container_width=True)

st.caption(
    "Data awal menggunakan jaringan Karate Club bawaan NetworkX. "
    "Setiap perubahan hanya simulasi."
)
