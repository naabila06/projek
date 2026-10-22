
import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import math

# =========================
# 1. PENGATURAN HALAMAN
# =========================

st.set_page_config(
    page_title="Community Connection Lab",
    page_icon="🌐",
    layout="wide"
)

st.title("🌐 Community Connection Lab")
st.write(
    "Simulasi interaktif jaringan pertemanan "
    "untuk mempelajari hubungan antaranggota."
)

# =========================
# 2. MEMUAT JARINGAN
# =========================

@st.cache_resource
def load_network():
    return nx.karate_club_graph()

if "G" not in st.session_state:
    st.session_state.G = load_network().copy()

if "positions" not in st.session_state:
    st.session_state.positions = nx.spring_layout(
        st.session_state.G,
        seed=7
    )

G = st.session_state.G
pos = st.session_state.positions

# =========================
# 3. INFORMASI JARINGAN
# =========================

st.subheader("Informasi Jaringan")

col1, col2, col3 = st.columns(3)

col1.metric("Jumlah anggota", G.number_of_nodes())
col2.metric("Jumlah hubungan", G.number_of_edges())
col3.metric(
    "Kelompok terhubung",
    nx.number_connected_components(G)
)

# =========================
# 4. KONTROL HUBUNGAN
# =========================

st.subheader("Kontrol Jaringan")

anggota = sorted(G.nodes())

col_a, col_b = st.columns(2)

with col_a:
    u = st.selectbox(
        "Anggota A",
        anggota,
        key="anggota_a"
    )

with col_b:
    v = st.selectbox(
        "Anggota B",
        anggota,
        index=1,
        key="anggota_b"
    )

col_tambah, col_hapus, col_reset = st.columns(3)

with col_tambah:
    if st.button("➕ Tambah hubungan"):
        if u == v:
            st.warning("Pilih dua anggota yang berbeda.")
        elif G.has_edge(u, v):
            st.warning("Hubungan tersebut sudah ada.")
        else:
            G.add_edge(u, v)
            st.success(
                f"Hubungan anggota {u} dan {v} berhasil ditambahkan."
            )
            st.rerun()

with col_hapus:
    if st.button("➖ Hapus hubungan"):
        if G.has_edge(u, v):
            G.remove_edge(u, v)
            st.success(
                f"Hubungan anggota {u} dan {v} berhasil dihapus."
            )
            st.rerun()
        else:
            st.warning("Hubungan tersebut belum ada.")

with col_reset:
    if st.button("🔄 Reset jaringan"):
        st.session_state.G = load_network().copy()
        st.session_state.positions = nx.spring_layout(
            st.session_state.G,
            seed=7
        )
        st.rerun()

# Perbarui referensi jaringan setelah perubahan
G = st.session_state.G
pos = st.session_state.positions

# =========================
# 5. FUNGSI POSISI ANGGOTA
# =========================

def posisi_anggota(phase):
    hasil = {}

    for n in G.nodes():
        x_awal, y_awal = pos[n]

        # Gerakan kecil agar jaringan tampak hidup
        x_baru = x_awal + 0.035 * math.sin(
            phase + n * 0.7
        )

        y_baru = y_awal + 0.035 * math.cos(
            phase + n * 0.9
        )

        hasil[n] = (x_baru, y_baru)

    return hasil


def koordinat_garis(p):
    x_garis = []
    y_garis = []

    for a, b in G.edges():
        x_garis.extend([
            p[a][0],
            p[b][0],
            None
        ])

        y_garis.extend([
            p[a][1],
            p[b][1],
            None
        ])

    return x_garis, y_garis

# =========================
# 6. MEMBUAT FRAME ANIMASI
# =========================

st.subheader("Visualisasi Jaringan")

jumlah_frame = 40
frames = []

derajat = dict(G.degree())

for i in range(jumlah_frame):
    phase = i * 2 * math.pi / jumlah_frame

    p = posisi_anggota(phase)
    ex, ey = koordinat_garis(p)

    frames.append(
        go.Frame(
            name=str(i),
            data=[
                go.Scatter(
                    x=ex,
                    y=ey
                ),
                go.Scatter(
                    x=[p[n][0] for n in G.nodes()],
                    y=[p[n][1] for n in G.nodes()]
                )
            ],
            traces=[0, 1]
        )
    )

# Posisi awal
p0 = posisi_anggota(0)
ex, ey = koordinat_garis(p0)

fig = go.Figure(
    data=[
        # Garis hubungan antaranggota
        go.Scatter(
            x=ex,
            y=ey,
            mode="lines",
            line=dict(
                width=1,
                color="#9CA3AF"
            ),
            hoverinfo="none"
        ),

        # Titik anggota
        go.Scatter(
            x=[p0[n][0] for n in G.nodes()],
            y=[p0[n][1] for n in G.nodes()],
            mode="markers+text",
            text=[str(n) for n in G.nodes()],
            textposition="middle center",
            marker=dict(
                size=[
                    12 + derajat[n]
                    for n in G.nodes()
                ],
                color=[
                    derajat[n]
                    for n in G.nodes()
                ],
                colorscale="Viridis",
                showscale=True,
                colorbar=dict(
                    title="Hubungan"
                ),
                line=dict(
                    width=1,
                    color="white"
                )
            ),
            hovertemplate=(
                "Anggota %{text}<br>"
                "Jumlah hubungan: %{marker.color}"
                "<extra></extra>"
            )
        )
    ],
    frames=frames
)

# =========================
# 7. TOMBOL ANIMASI
# =========================

fig.update_layout(
    height=700,
    showlegend=False,
    margin=dict(
        l=10,
        r=10,
        t=80,
        b=10
    ),
    xaxis=dict(
        visible=False,
        range=[
            min(x for x, y in pos.values()) - 0.2,
            max(x for x, y in pos.values()) + 0.2
        ]
    ),
    yaxis=dict(
        visible=False,
        range=[
            min(y for x, y in pos.values()) - 0.2,
            max(y for x, y in pos.values()) + 0.2
        ]
    ),
    plot_bgcolor="white",
    updatemenus=[
        dict(
            type="buttons",
            showactive=False,
            x=0.02,
            y=1.12,
            buttons=[
                dict(
                    label="▶ Mulai",
                    method="animate",
                    args=[
                        None,
                        {
                            "frame": {
                                "duration": 80,
                                "redraw": True
                            },
                            "fromcurrent": True,
                            "transition": {
                                "duration": 0
                            }
                        }
                    ]
                ),
                dict(
                    label="⏸ Jeda",
                    method="animate",
                    args=[
                        [None],
                        {
                            "mode": "immediate",
                            "frame": {
                                "duration": 0,
                                "redraw": False
                            },
                            "transition": {
                                "duration": 0
                            }
                        }
                    ]
                )
            ]
        )
    ]
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================
# 8. KETERANGAN
# =========================

st.subheader("Keterangan")

st.write(
    "- Setiap titik mewakili seorang anggota.\n"
    "- Setiap garis mewakili hubungan pertemanan.\n"
    "- Ukuran dan warna titik menunjukkan jumlah hubungan anggota.\n"
    "- Tombol Mulai menjalankan animasi gerakan jaringan.\n"
    "- Tombol Jeda menghentikan animasi sementara.\n"
    "- Tambah dan Hapus hubungan digunakan untuk mengubah jaringan."
)

st.caption(
    "Jaringan awal menggunakan dataset Karate Club bawaan NetworkX. "
    "Perubahan hubungan merupakan simulasi."
)
