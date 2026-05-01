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
# CLASE POKEMON
# ==========================================
class Pokemon:
    def __init__(self, data):
        self.id = data.get("id")
        self.name = data.get("name", "")
        self.tipo1 = data.get("tipo1") or ""
        self.tipo2 = data.get("tipo2")
        tipo_unico = data.get("tipo")
        if not self.tipo2 and tipo_unico:
            partes = [t.strip() for t in tipo_unico.split("/") if t.strip()]
            self.tipo1 = partes[0] if partes else self.tipo1
            self.tipo2 = partes[1] if len(partes) > 1 else None
        if self.tipo2 in ("null", "", None):
            self.tipo2 = None

        # Atributos Base
        self.max_hp = data.get("hp", data.get("stats", {}).get("hp", 0))
        self.current_hp = data.get("current_hp", self.max_hp)
        self.attack = data.get("atk", data.get("stats", {}).get("atk", 0))
        self.defense = data.get("def", data.get("stats", {}).get("def", 0))
        self.spat = data.get("spat", data.get("stats", {}).get("spat", 0))
        self.spdf = data.get("spdf", data.get("stats", {}).get("spdf", 0))
        self.speed = data.get("spe", data.get("stats", {}).get("spe", 0))
        self.gender = data.get("gender", "macho")
        self.state = data.get("state")
        self.position = data.get("position")
        
        # Stats mutables (pueden cambiar durante el combate)
        self.current_attack = self.attack
        self.current_defense = self.defense
        self.current_spat = self.spat
        self.current_spdf = self.spdf
        self.current_speed = self.speed
        
        # URLs de imágenes para Tkinter
        self.img_mini = data.get("img_mini", "")
        self.img_large_gif = data.get("img_large_gif", "")
        self.img_back = data.get("img_back", "")
        # Seleccionar aleatoriamente hasta 4 movimientos
        self.movimientos = self._seleccionar_movimientos(data.get("moves", []))
        
    def _seleccionar_movimientos(self, moves_data):
        if not moves_data:
            return []
        cantidad = min(4, len(moves_data))
        seleccionados = random.sample(moves_data, cantidad)
        movimientos = []
        for m in seleccionados:
            movimientos.append(Movimiento(
                m.get("name", ""),
                m.get("power", 0),
                m.get("accuracy", 100),
                m.get("type", "Normal"),
                m.get("category", "physical"),
            ))
        return movimientos

    def recibir_dano(self, cantidad):
        self.current_hp -= cantidad
        if self.current_hp < 0:
            self.current_hp = 0

    def esta_debilitado(self):
        return self.current_hp <= 0

    # NUEVO: Función vital para la barra de vida gráfica (HUD)
    def obtener_porcentaje_hp(self):
        return (self.current_hp / self.max_hp) * 100

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