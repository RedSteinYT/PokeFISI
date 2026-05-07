import random
import math
import json
import os

from pokemones import (
    TIPOS,
    EFECTIVIDAD_TIPOS,
    obtener_efectividad,
    Movimiento,
    _normalizar_tipo,
)

TIPO_A_INDICE = {tipo: i for i, tipo in enumerate(TIPOS)}

EFECTIVIDAD_TIPOS = {}

from pokemones import obtener_efectividad as _obtener_efectividad_poke

def obtener_efectividad(tipo_ataque, tipo_defensor1, tipo_defensor2=None):
    return _obtener_efectividad_poke(tipo_ataque, tipo_defensor1, tipo_defensor2)


class Movimiento:
    def __init__(self, name, power, accuracy, move_type, category="physical"):
        self.name = name
        self.power = power
        self.accuracy = accuracy
        self.type = move_type
        self.category = category.lower() if isinstance(category, str) else "physical"
    
    def __repr__(self):
        return f"Movimiento({self.name}, pow={self.power}, acc={self.accuracy}, tipo={self.type})"


class PokemonCombate:
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
        
        self.current_attack = self.attack
        self.current_defense = self.defense
        self.current_spat = self.spat
        self.current_spdf = self.spdf
        self.current_speed = self.speed
        
        self.img_mini = data.get("img_mini", "")
        self.img_large_gif = data.get("img_large_gif", "")
        self.img_back = data.get("img_back", "")
        
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
    
    def obtener_porcentaje_hp(self):
        return (self.current_hp / self.max_hp) * 100


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
    
    def calcular_dano(self, atacante, defensor, movimiento, mostrar_efectividad=False):
        if movimiento.power == 0:
            return 0, 1.0, False
        
        if random.random() > movimiento.accuracy / 100:
            return 0, 1.0, True
        
        if movimiento.category == "special":
            ataque = atacante.current_spat
            defensa = atacante.current_spdf or 1
        else:
            ataque = atacante.current_attack
            defensa = defensor.current_defense or 1
        
        efectividad = obtener_efectividad(
            movimiento.type,
            defensor.tipo1,
            defensor.tipo2
        )
        
        stab = 1.5 if movimiento.type in (atacante.tipo1, atacante.tipo2) else 1.0
        
        termino1 = ((ataque / defensa) * movimiento.power * efectividad * stab)
        termino2 = (defensor.current_speed * self.k * 0.5)
        damage = max(1, math.floor(termino1 - termino2))
        
        if mostrar_efectividad:
            return damage, efectividad, False
        return damage, efectividad, False
    
    def aplicar_accion(self, jugador, accion):
        tipo, indice = accion
        if tipo == "CAMBIAR":
            if jugador == 1:
                self.pokemon_actual1 = self.equipo1[indice]
            else:
                self.pokemon_actual2 = self.equipo2[indice]
    
    def resolver_turno(self, accion1, accion2):
        tipo1, idx1 = accion1
        tipo2, idx2 = accion2
        
        log_turno = []
        log_turno.append(f"--- TURNO {self.turno_actual} ---")
        
        if tipo1 == "CAMBIAR":
            viejo = self.pokemon_actual1.name
            self.pokemon_actual1 = self.equipo1[idx1]
            log_turno.append(f"Jugador 1 retira a {viejo} y envía a {self.pokemon_actual1.name}!")
        
        if tipo2 == "CAMBIAR":
            viejo = self.pokemon_actual2.name
            self.pokemon_actual2 = self.equipo2[idx2]
            log_turno.append(f"El rival retira a {viejo} y envía a {self.pokemon_actual2.name}!")
        
        primero, segundo = 1, 2
        act1, act2 = accion1, accion2
        poke_primero, poke_segundo = self.pokemon_actual1, self.pokemon_actual2
        
        if self.pokemon_actual2.speed > self.pokemon_actual1.speed:
            primero, segundo = 2, 1
            act1, act2 = accion2, accion1
            poke_primero, poke_segundo = self.pokemon_actual2, self.pokemon_actual1
        
        if act1[0] == "ATACAR" and not poke_primero.esta_debilitado():
            mov = poke_primero.movimientos[act1[1]]
            dano, efectividad, fallo = self.calcular_dano(poke_primero, poke_segundo, mov)
            
            if fallo:
                log_turno.append(f"¡{poke_primero.name} usó {mov.name}!")
                log_turno.append("¡El ataque falló!")
            else:
                log_turno.append(f"¡{poke_primero.name} usó {mov.name}!")
                
                if efectividad > 1:
                    log_turno.append("¡Es muy efectivo!")
                elif efectividad < 1 and efectividad > 0:
                    log_turno.append("No es muy efectivo...")
                elif efectividad == 0:
                    log_turno.append("¡No afecta al objetivo!")
                
                poke_segundo.recibir_dano(dano)
                log_turno.append(f"El ataque hizo {dano} de daño.")
                
                if poke_segundo.esta_debilitado():
                    log_turno.append(f"¡{poke_segundo.name} se ha debilitado!")
        
        if act2[0] == "ATACAR" and not poke_segundo.esta_debilitado():
            mov = poke_segundo.movimientos[act2[1]]
            dano, efectividad, fallo = self.calcular_dano(poke_segundo, poke_primero, mov)
            
            if fallo:
                log_turno.append(f"¡{poke_segundo.name} usó {mov.name}!")
                log_turno.append("¡El ataque falló!")
            else:
                log_turno.append(f"¡{poke_segundo.name} usó {mov.name}!")
                
                if efectividad > 1:
                    log_turno.append("¡Es muy efectivo!")
                elif efectividad < 1 and efectividad > 0:
                    log_turno.append("No es muy efectivo...")
                elif efectividad == 0:
                    log_turno.append("¡No afecta al objetivo!")
                
                poke_primero.recibir_dano(dano)
                log_turno.append(f"El ataque hizo {dano} de daño.")
                
                if poke_primero.esta_debilitado():
                    log_turno.append(f"¡{poke_primero.name} se ha debilitado!")
        
        self.turno_actual += 1
        return log_turno


def cargar_equipos_desde_json(ruta_json):
    with open(ruta_json, "r", encoding="utf-8") as f:
        datos = json.load(f)
    
    equipo_jugador = [PokemonCombate(p) for p in datos.get("team_jugador", [])]
    equipo_ia = [PokemonCombate(p) for p in datos.get("team_ia", [])]
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