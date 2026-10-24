import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)
DB_FILE = "km_tracker.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            start_km REAL NOT NULL,
            end_km REAL,
            start_lat REAL,
            start_lng REAL,
            end_lat REAL,
            end_lng REAL,
            status TEXT NOT NULL DEFAULT 'open'
        )
    """)
    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Controle de KM</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        brand: { 50: '#eef2ff', 100: '#e0e7ff', 500: '#6366f1', 600: '#4f46e5', 700: '#4338ca' }
                    }
                }
            }
        }
    </script>
</head>
<body class="bg-slate-50 text-slate-800 min-h-screen">
    <div class="max-w-4xl mx-auto p-4 sm:p-6 lg:p-8">
        <header class="flex justify-between items-center mb-8">
            <div>
                <h1 class="text-2xl sm:text-3xl font-bold text-slate-900 flex items-center gap-3">
                    <i class="fa-solid fa-car-side text-brand-600"></i> KM Tracker
                </h1>
                <p class="text-sm text-slate-500 mt-1">Gestão inteligente de deslocamentos e rotas</p>
            </div>
            <div class="text-right">
                <span class="text-xs font-semibold px-3 py-1 bg-brand-50 text-brand-600 rounded-full border border-brand-100">
                    {{ current_date }}
                </span>
            </div>
        </header>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex items-center justify-between">
                <div>
                    <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">Total Hoje</p>
                    <p class="text-3xl font-extrabold text-slate-900 mt-1">{{ "%.1f"|format(daily_km) }} <span class="text-sm font-medium text-slate-500">km</span></p>
                </div>
                <div class="w-12 h-12 bg-emerald-50 text-emerald-600 rounded-xl flex items-center justify-center text-xl">
                    <i class="fa-solid fa-calendar-day"></i>
                </div>
            </div>
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex items-center justify-between">
                <div>
                    <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">Total no Mês</p>
                    <p class="text-3xl font-extrabold text-slate-900 mt-1">{{ "%.1f"|format(monthly_km) }} <span class="text-sm font-medium text-slate-500">km</span></p>
                </div>
                <div class="w-12 h-12 bg-brand-50 text-brand-600 rounded-xl flex items-center justify-center text-xl">
                    <i class="fa-solid fa-calendar-days"></i>
                </div>
            </div>
        </div>

        <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 mb-8">
            <h2 class="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
                <i class="fa-solid fa-location-dot text-brand-600"></i>
                {% if active_trip %} Finalizar Trajeto em Aberto {% else %} Iniciar Novo Trajeto {% endif %}
            </h2>

            {% if not active_trip %}
            <form action="{{ url_for('start_trip') }}" method="POST" id="start-form">
                <input type="hidden" name="lat" id="start-lat">
                <input type="hidden" name="lng" id="start-lng">
                <div class="flex flex-col sm:flex-row gap-4">
                    <div class="flex-1">
                        <label class="block text-xs font-medium text-slate-500 mb-1">KM Inicial</label>
                        <input type="number" step="0.1" name="start_km" required placeholder="Ex: 45200.5" 
                               class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-slate-800">
                    </div>
                    <div class="flex items-end">
                        <button type="submit" onclick="captureLocation(event, 'start-form', 'start-lat', 'start-lng')"
                                class="w-full sm:w-auto px-6 py-3 bg-brand-600 hover:bg-brand-700 text-white font-medium rounded-xl transition flex items-center justify-center gap-2">
                            <i class="fa-solid fa-play"></i> Iniciar Corrida
                        </button>
                    </div>
                </div>
            </form>
            {% else %}
            <div class="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-4 text-sm text-amber-800 flex justify-between items-center">
                <div>
                    <span class="font-bold">Em andamento:</span> Iniciado em {{ active_trip.start_km }} km.
                </div>
                {% if active_trip.start_lat and active_trip.start_lng %}
                <a href="https://maps.google.com/?q={{ active_trip.start_lat }},{{ active_trip.start_lng }}" target="_blank" class="text-xs text-brand-600 underline font-semibold flex items-center gap-1">
                    <i class="fa-solid fa-map-pin"></i> Ver partida
                </a>
                {% endif %}
            </div>

            <form action="{{ url_for('finish_trip') }}" method="POST" id="finish-form">
                <input type="hidden" name="trip_id" value="{{ active_trip.id }}">
                <input type="hidden" name="lat" id="finish-lat">
                <input type="hidden" name="lng" id="finish-lng">
                <div class="flex flex-col sm:flex-row gap-4">
                    <div class="flex-1">
                        <label class="block text-xs font-medium text-slate-500 mb-1">KM Final (Mínimo: {{ active_trip.start_km }})</label>
                        <input type="number" step="0.1" min="{{ active_trip.start_km }}" name="end_km" required placeholder="Ex: 45245.0" 
                               class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-slate-800">
                    </div>
                    <div class="flex items-end">
                        <button type="submit" onclick="captureLocation(event, 'finish-form', 'finish-lat', 'finish-lng')"
                                class="w-full sm:w-auto px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-xl transition flex items-center justify-center gap-2">
                            <i class="fa-solid fa-flag-checkered"></i> Concluir Trajeto
                        </button>
                    </div>
                </div>
            </form>
            {% endif %}
        </div>

        <div class="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
            <div class="p-6 border-b border-slate-100">
                <h2 class="text-lg font-bold text-slate-900">Histórico Recente</h2>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-slate-50 text-slate-400 text-xs uppercase tracking-wider">
                            <th class="py-3 px-6">Data</th>
                            <th class="py-3 px-6">Inicial</th>
                            <th class="py-3 px-6">Final</th>
                            <th class="py-3 px-6">Distância</th>
                            <th class="py-3 px-6 text-center">Locais</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100 text-sm">
                        {% for trip in trips %}
                        <tr class="hover:bg-slate-50 transition">
                            <td class="py-4 px-6 font-medium text-slate-900">{{ trip.date }}</td>
                            <td class="py-4 px-6 text-slate-600">{{ trip.start_km }} km</td>
                            <td class="py-4 px-6 text-slate-600">{{ trip.end_km if trip.end_km else '-' }} km</td>
                            <td class="py-4 px-6 font-semibold {% if trip.status == 'completed' %}text-emerald-600{% else %}text-amber-500{% endif %}">
                                {% if trip.status == 'completed' %}
                                    +{{ "%.1f"|format(trip.end_km - trip.start_km) }} km
                                {% else %}
                                    Em aberto
                                {% endif %}
                            </td>
                            <td class="py-4 px-6 text-center">
                                <div class="flex items-center justify-center gap-2">
                                    {% if trip.start_lat %}
                                    <a href="https://maps.google.com/?q={{ trip.start_lat }},{{ trip.start_lng }}" target="_blank" title="Origem" class="w-7 h-7 rounded-full bg-slate-100 text-slate-600 hover:bg-brand-50 hover:text-brand-600 flex items-center justify-center">
                                        <i class="fa-solid fa-play text-xs"></i>
                                    </a>
                                    {% endif %}
                                    {% if trip.end_lat %}
                                    <a href="https://maps.google.com/?q={{ trip.end_lat }},{{ trip.end_lng }}" target="_blank" title="Destino" class="w-7 h-7 rounded-full bg-slate-100 text-slate-600 hover:bg-emerald-50 hover:text-emerald-600 flex items-center justify-center">
                                        <i class="fa-solid fa-flag-checkered text-xs"></i>
                                    </a>
                                    {% endif %}
                                    {% if not trip.start_lat and not trip.end_lat %}
                                    <span class="text-xs text-slate-300">-</span>
                                    {% endif %}
                                </div>
                            </td>
                        </tr>
                        {% else %}
                        <tr>
                            <td colspan="5" class="py-8 text-center text-slate-400">Nenhum registro encontrado.</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        function captureLocation(e, formId, latId, lngId) {
            e.preventDefault();
            const form = document.getElementById(formId);
            if (!navigator.geolocation) {
                form.submit();
                return;
            }
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    document.getElementById(latId).value = pos.coords.latitude;
                    document.getElementById(lngId).value = pos.coords.longitude;
                    form.submit();
                },
                (err) => {
                    form.submit();
                },
                { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
            );
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    conn = get_db()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    current_month = datetime.now().strftime("%Y-%m")

    cursor.execute("SELECT SUM(end_km - start_km) FROM trips WHERE date = ? AND status = 'completed'", (today,))
    daily_km = cursor.fetchone()[0] or 0.0

    cursor.execute("SELECT SUM(end_km - start_km) FROM trips WHERE strftime('%Y-%m', date) = ? AND status = 'completed'", (current_month,))
    monthly_km = cursor.fetchone()[0] or 0.0

    cursor.execute("SELECT * FROM trips WHERE status = 'open' ORDER BY id DESC LIMIT 1")
    active_trip = cursor.fetchone()

    cursor.execute("SELECT * FROM trips ORDER BY id DESC LIMIT 15")
    trips = cursor.fetchall()

    conn.close()
    return render_template_string(
        HTML_TEMPLATE,
        daily_km=daily_km,
        monthly_km=monthly_km,
        active_trip=active_trip,
        trips=trips,
        current_date=datetime.now().strftime("%d/%m/%Y")
    )

@app.route("/start", methods=["POST"])
def start_trip():
    start_km = float(request.form.get("start_km"))
    lat = request.form.get("lat") or None
    lng = request.form.get("lng") or None
    today = datetime.now().strftime("%Y-%m-%d")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO trips (date, start_km, start_lat, start_lng, status)
        VALUES (?, ?, ?, ?, 'open')
    """, (today, start_km, lat, lng))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/finish", methods=["POST"])
def finish_trip():
    trip_id = request.form.get("trip_id")
    end_km = float(request.form.get("end_km"))
    lat = request.form.get("lat") or None
    lng = request.form.get("lng") or None

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE trips
        SET end_km = ?, end_lat = ?, end_lng = ?, status = 'completed'
        WHERE id = ? AND status = 'open'
    """, (end_km, lat, lng, trip_id))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)