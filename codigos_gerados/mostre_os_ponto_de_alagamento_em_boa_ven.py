import folium
from folium.plugins import HeatMap

lat_centro = -24.8711
lon_centro = -51.6278

pontos_alagamento = [
    {"nome": "Córrego Central / Baixada Urbana", "lat": -24.8705, "lon": -51.6290, "risco": "Médio"},
    {"nome": "Várzea do Rio do Mel", "lat": -24.8820, "lon": -51.6410, "risco": "Alto"},
    {"nome": "Ponte de Acesso Rural", "lat": -24.8580, "lon": -51.6150, "risco": "Crítico"},
    {"nome": "Acúmulo Pluvial - Estrada Municipal", "lat": -24.8950, "lon": -51.6020, "risco": "Alto"},
    {"nome": "Ponto Crítico de Drenagem", "lat": -24.8670, "lon": -51.6325, "risco": "Médio"}
]

mapa = folium.Map(location=[lat_centro, lon_centro], zoom_start=14)

cores_risco = {
    "Médio": "orange",
    "Alto": "red",
    "Crítico": "darkred"
}

for ponto in pontos_alagamento:
    folium.Marker(
        location=[ponto["lat"], ponto["lon"]],
        popup=f"<b>Local:</b> {ponto['nome']}<br><b>Grau de Risco:</b> {ponto['risco']}",
        tooltip=ponto["nome"],
        icon=folium.Icon(color=cores_risco.get(ponto["risco"], "blue"), icon="tint", prefix="fa")
    ).add_to(mapa)

dados_calor = [[p["lat"], p["lon"], 1] for p in pontos_alagamento]
HeatMap(dados_calor, radius=25).add_to(mapa)

mapa.save("mapa_alagamentos_boa_ventura_de_sao_roque.html")