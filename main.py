import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import random
import asyncio

app = FastAPI()

load_dotenv()
origins = os.getenv("ALLOW_ORIGINS", "").split(",")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API pública de Pokemon
POKEMON_API_URL = "https://pokeapi.co/api/v2"

@app.get("/")
async def get_pokemon():
    async with httpx.AsyncClient() as client:

        """
        try:
            response = await client.get(f"{POKEMON_API_URL}/")
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="Error al obtener la data de los Pokemon")
        
        data = response.json()
        n_pks = data.get("count")
        """

        # Documentar error o incongruencia de cantidad de pokemons y cantidad de ids, 
        # Por lo que se utiliza hasta el ID: 1025 verificado manualmente en postman como el último ID encontrado
        # players_pks_ids = random.sample(range(1, n_pks + 1), 6)
        players_pks_ids = random.sample(range(1, 1026), 6)

        # Crear tareas para las solicitudes a la API
        tasks = [fetch_pokemon_data(client, id) for id in players_pks_ids]
        pokemons_data = await asyncio.gather(*tasks)

        # Filtrar Pokémon nulos
        valid_pokemons = [pk for pk in pokemons_data if pk is not None]

        # Comprobar que hay al menos 6 Pokémon válidos
        if len(valid_pokemons) < 6:
            raise HTTPException(status_code=500, detail="No se pudo obtener suficientes Pokémon válidos.")

        p1_pks = valid_pokemons[:3]  # Primeros 3 para el jugador 1
        p2_pks = valid_pokemons[3:6]  # Últimos 3 para el jugador 2

        return {
            "player1_pokemons": p1_pks,
            "player2_pokemons": p2_pks
        }

async def fetch_pokemon_data(client, id):
    try:
        res = await client.get(f"{POKEMON_API_URL}/pokemon/{id}")
        res.raise_for_status()
        data_pk = res.json()

        moves = data_pk.get("moves")

        fetched_moves = []
        for move in moves:
            fetched_moves.append(move.get("move"))

        pk_battle_data = {
            "id": data_pk.get("id"),
            "nombre": data_pk.get("name"),
            "sprite": data_pk.get("sprites", {}).get("front_default"),
            "tipos": data_pk.get("types"),
            "estadisticas": data_pk.get("stats"),
            "ataques": fetched_moves,
        }
        return pk_battle_data
    except httpx.HTTPStatusError as e:
        print(f"Error al obtener el Pokémon {id}: {e.response.status_code}")
        return None  # Retorna None si hay un error

@app.get("/pokemon/move/")
async def get_pokemon_move(url: str):
    async with httpx.AsyncClient() as client:
        move_data = await fetch_pokemon_move(client, url)
        if move_data is None:
            raise HTTPException(status_code=404, detail="Movimiento no encontrado")
        return move_data

async def fetch_pokemon_move(client, url):
    try:
        res = await client.get(url)
        res.raise_for_status()
        data_move = res.json()
        nombres = data_move.get("names")
        nombre_ataque = ""

        for nombre in nombres:
            if nombre.get("language").get("name") == "es":
                nombre_ataque = nombre.get("name")
                break
       
        pk_move_data = {
            "nombre": nombre_ataque,
            "clase": data_move.get("damage_class").get("name")
        }
        return pk_move_data
    except httpx.HTTPStatusError as e:
        print(f"Error al obtener el movimiento de url {url}: {e.response.status_code}")
        return None  # Retorna None si hay un error