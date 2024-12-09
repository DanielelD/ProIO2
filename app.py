from flask import Flask, render_template, request
import folium
import networkx as nx
from geopy.distance import geodesic

app = Flask(__name__)

# Crear el grafo mundial de aeropuertos
grafo = nx.Graph()

aeropuertos = {
    # Aeropuertos actuales
    "La Paz, Bolivia": (-16.512, -68.192),
    "Buenos Aires, Argentina": (-34.607, -58.383),
    "São Paulo, Brasil": (-23.5505, -46.6333),
    "Nueva York, EE.UU.": (40.7128, -74.006),
    "Los Ángeles, EE.UU.": (34.0522, -118.2437),
    "Ciudad de México, México": (19.4326, -99.1332),
    "Toronto, Canadá": (43.65107, -79.347015),
    "Madrid, España": (40.4168, -3.7038),
    "Barcelona, España": (41.3879, 2.16992),
    "París, Francia": (48.8566, 2.3522),
    "Berlín, Alemania": (52.52, 13.405),
    "Londres, Reino Unido": (51.5074, -0.1278),
    "Roma, Italia": (41.9028, 12.4964),
    "Ámsterdam, Países Bajos": (52.3676, 4.9041),
    "Tokio, Japón": (35.6895, 139.6917),
    "Osaka, Japón": (34.6937, 135.5022),
    "Sídney, Australia": (-33.8688, 151.2093),
    "Melbourne, Australia": (-37.8136, 144.9631),
    "El Cairo, Egipto": (30.0444, 31.2357),
    "Johannesburgo, Sudáfrica": (-26.2041, 28.0473),
    "Dubái, Emiratos Árabes Unidos": (25.276987, 55.296249),
    "Delhi, India": (28.6139, 77.209),
    "Moscú, Rusia": (55.7558, 37.6173),
    "Beijing, China": (39.9042, 116.4074),
    "Shanghái, China": (31.2304, 121.4737),
    "Seúl, Corea del Sur": (37.5665, 126.978),
    "Estambul, Turquía": (41.0082, 28.9784),

    # Nuevos aeropuertos de Sudamérica (5)
    "Lima, Perú": (-12.0464, -77.0428),
    "Santiago, Chile": (-33.4489, -70.6693),
    "Bogotá, Colombia": (4.711, -74.0721),
    "Quito, Ecuador": (-0.1807, -78.4678),
    "Montevideo, Uruguay": (-34.9011, -56.1645),

    # Nuevos aeropuertos de Europa (10)
    "Ginebra, Suiza": (46.2381, 6.1419),
    "Zurich, Suiza": (47.378, 8.540),
    "Copenhague, Dinamarca": (55.6761, 12.5683),
    "Bruselas, Bélgica": (50.8503, 4.3517),
    "Estocolmo, Suecia": (59.3293, 18.0686),
    "Lisboa, Portugal": (38.7169, -9.1395),
    "Viena, Austria": (48.2082, 16.3738),
    "Oporto, Portugal": (41.1579, -8.6291),
    "Praga, República Checa": (50.0755, 14.4378),

    # Nuevos aeropuertos de otras regiones (5)
    "Hong Kong, China": (22.3193, 114.1694),
    "Lagos, Nigeria": (6.5244, 3.3792),
    "Doha, Catar": (25.276987, 55.296249),
    "Manila, Filipinas": (14.5995, 120.9842),
}

# Agregar nodos al grafo
for nombre, coords in aeropuertos.items():
    grafo.add_node(nombre, coords=coords)

# Crear rutas (con distancias calculadas)
for origen, coord_origen in aeropuertos.items():
    for destino, coord_destino in aeropuertos.items():
        if origen != destino:
            distancia = geodesic(coord_origen, coord_destino).km
            if distancia <= 10000:  # Conectar solo aeropuertos dentro de 10,000 km
                grafo.add_edge(origen, destino, weight=distancia)

@app.route("/", methods=["GET", "POST"])
def index():
    ruta_mas_corta = []
    distancia_total = 0
    tiempo_vuelo = 0
    mapa_path = None
    ruta_coords = []

    if request.method == "POST":
        origen = request.form.get("origen")
        destino = request.form.get("destino")

        # Calcular la ruta más corta
        ruta_mas_corta = nx.shortest_path(grafo, source=origen, target=destino, weight="weight")
        distancia_total = nx.shortest_path_length(grafo, source=origen, target=destino, weight="weight")

        # Calcular el tiempo de vuelo en horas (asumiendo una velocidad promedio de 800 km/h)
        velocidad_promedio = 800  # km/h
        tiempo_vuelo = distancia_total / velocidad_promedio

        # Crear el mapa interactivo
        coords_origen = grafo.nodes[origen]["coords"]
        mapa = folium.Map(location=coords_origen, zoom_start=2)

        # Agregar nodos (aeropuertos)
        for nodo, data in grafo.nodes(data=True):
            folium.Marker(location=data["coords"], popup=nodo).add_to(mapa)

        # Dibujar todas las rutas
        for u, v, data in grafo.edges(data=True):
            ruta = [grafo.nodes[u]["coords"], grafo.nodes[v]["coords"]]
            folium.PolyLine(ruta, color="blue", weight=1, opacity=0.6).add_to(mapa)

        # Dibujar la ruta más corta
        ruta_coords = [grafo.nodes[nodo]["coords"] for nodo in ruta_mas_corta]
        folium.PolyLine(ruta_coords, color="red", weight=4, opacity=0.8, tooltip="Ruta más corta").add_to(mapa)

        # Guardar el mapa
        mapa_path = "static/mapa_ruta.html"
        mapa.save(mapa_path)

    return render_template("index.html", aeropuertos=list(aeropuertos.keys()), ruta=ruta_mas_corta, distancia=distancia_total, tiempo_vuelo=round(tiempo_vuelo, 4), mapa_path=mapa_path)

if __name__ == "__main__":
    app.run(debug=True)
