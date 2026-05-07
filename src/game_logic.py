import json
import random
import math

# ==========================================
# CLASE MOVIMIENTO
# ==========================================
class Movimiento:
    def __init__(self, name, power, accuracy, move_type, category="physical"):
        self.name = name
        self.power = power
        self.accuracy = accuracy
        self.type = move_type
        self.category = category.lower() if isinstance(category, str) else "physical"

# ==========================================
# CLASE COMBATE Y FÓRMULA DE DAÑO
# ==========================================
class Combate:
    def __init__(self, equipo1, equipo2, factor_k=0.1):
        self.equipo1 = equipo1
        self.equipo2 = equipo2
        self.k = factor_k
        self.turno_actual = 1
        
        self.pokemon_actual1 = self.equipo1[0]
        self.pokemon_actual2 = self.equipo2[0]

    def juego_terminado(self):
        vivos_j1 = sum(1 for p in self.equipo1 if not p.esta_debilitado())
        vivos_j2 = sum(1 for p in self.equipo2 if not p.esta_debilitado())
        
        if vivos_j1 == 0:
            return 2 
        elif vivos_j2 == 0:
            return 1 
        return 0 

    def calcular_dano(self, atacante, defensor, movimiento):
        if movimiento.power == 0:
            return 0

        if movimiento.category == "special":
            ataque = atacante.current_spat
            defensa = defensor.current_spdf or 1
        else:
            ataque = atacante.current_attack
            defensa = defensor.current_defense or 1

        termino1 = (ataque / defensa) * movimiento.power
        termino2 = defensor.current_speed * self.k
        damage = termino1 - termino2
        return max(1, math.floor(damage))

    def aplicar_accion(self, jugador, accion):
        """Ejecuta una acción directamente (usado cuando la IA debe forzar un cambio)"""
        tipo, indice = accion
        if tipo == "CAMBIAR":
            if jugador == 1:
                self.pokemon_actual1 = self.equipo1[indice]
            else:
                self.pokemon_actual2 = self.equipo2[indice]

    # MEJORADO: Ahora devuelve un "registro" (log) para que Tkinter lo muestre en la caja de diálogo
    def resolver_turno(self, accion1, accion2):
        tipo1, idx1 = accion1
        tipo2, idx2 = accion2
        
        log_turno = [] # Aquí guardaremos los mensajes para la UI
        log_turno.append(f"--- TURNO {self.turno_actual} ---")

        # 1. FASE DE CAMBIOS
        if tipo1 == "CAMBIAR":
            viejo = self.pokemon_actual1.name
            self.pokemon_actual1 = self.equipo1[idx1]
            log_turno.append(f"Jugador 1 retira a {viejo} y envía a {self.pokemon_actual1.name}!")
            
        if tipo2 == "CAMBIAR":
            viejo = self.pokemon_actual2.name
            self.pokemon_actual2 = self.equipo2[idx2]
            log_turno.append(f"El rival retira a {viejo} y envía a {self.pokemon_actual2.name}!")

        # 2. FASE DE ATAQUE
        primero, segundo = 1, 2
        act1, act2 = accion1, accion2
        poke_primero, poke_segundo = self.pokemon_actual1, self.pokemon_actual2

        if self.pokemon_actual2.speed > self.pokemon_actual1.speed:
            primero, segundo = 2, 1
            act1, act2 = accion2, accion1
            poke_primero, poke_segundo = self.pokemon_actual2, self.pokemon_actual1

        # Ataque del primero
        if act1[0] == "ATACAR" and not poke_primero.esta_debilitado():
            mov = poke_primero.movimientos[act1[1]]
            log_turno.append(f"¡{poke_primero.name} usó {mov.name}!")
            dano = self.calcular_dano(poke_primero, poke_segundo, mov)
            poke_segundo.recibir_dano(dano)
            log_turno.append(f"El ataque hizo {dano} de daño.")
            
            if poke_segundo.esta_debilitado():
                log_turno.append(f"¡{poke_segundo.name} se ha debilitado!")

        # Ataque del segundo
        if act2[0] == "ATACAR" and not poke_segundo.esta_debilitado():
            mov = poke_segundo.movimientos[act2[1]]
            log_turno.append(f"¡{poke_segundo.name} usó {mov.name}!")
            dano = self.calcular_dano(poke_segundo, poke_primero, mov)
            poke_primero.recibir_dano(dano)
            log_turno.append(f"El ataque hizo {dano} de daño.")
            
            if poke_primero.esta_debilitado():
                log_turno.append(f"¡{poke_primero.name} se ha debilitado!")
            
        self.turno_actual += 1
        return log_turno # Retornamos la lista de eventos para la Interfaz Gráfica

# ==========================================
# FUNCIONES UTILITARIAS
# ==========================================
def cargar_equipo_desde_json(ruta_json, ids_equipo):
    with open(ruta_json, "r", encoding="utf-8") as f:
        todos_pokemons = json.load(f)
        
    equipo = []
    for pid in ids_equipo:
        data = next((p for p in todos_pokemons if p["id"] == pid), None)
        if data:
            equipo.append(Pokemon(data))
    return equipo


def cargar_equipos_desde_json(ruta_json):
    with open(ruta_json, "r", encoding="utf-8") as f:
        datos = json.load(f)

    equipo_jugador = [Pokemon(p) for p in datos.get("team_jugador", [])]
    equipo_ia = [Pokemon(p) for p in datos.get("team_ia", [])]
    return equipo_jugador, equipo_ia


def guardar_equipos_en_json(ruta_json, equipo_jugador, equipo_ia):
    def pokemon_a_dict(poke):
        return {
            "id": poke.id,
            "name": poke.name,
            "tipo1": poke.tipo1,
            "tipo2": poke.tipo2,
            "hp": poke.max_hp,
            "atk": poke.attack,
            "def": poke.defense,
            "spat": poke.spat,
            "spdf": poke.spdf,
            "spe": poke.speed,
            "current_hp": poke.current_hp,
            "current_attack": poke.current_attack,
            "current_defense": poke.current_defense,
            "current_spat": poke.current_spat,
            "current_spdf": poke.current_spdf,
            "current_speed": poke.current_speed,
            "gender": poke.gender,
            "state": poke.state,
            "position": poke.position,
            "img_mini": poke.img_mini,
            "img_large_gif": poke.img_large_gif,
            "img_back": poke.img_back,
            "moves": [
                {
                    "name": m.name,
                    "power": m.power,
                    "accuracy": m.accuracy,
                    "type": m.type,
                    "category": m.category,
                }
                for m in poke.movimientos
            ],
        }

    equipos = {
        "team_jugador": [pokemon_a_dict(p) for p in equipo_jugador],
        "team_ia": [pokemon_a_dict(p) for p in equipo_ia],
    }

    try:
        with open(ruta_json, "w", encoding="utf-8") as f:
            json.dump(equipos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error guardando equipos.json: {e}")