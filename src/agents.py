import random

# ==========================================
# AGENTE NIVEL 1: ALEATORIO
# ==========================================
class AgenteAleatorio:
    def elegir_accion(self, batalla, es_jugador_1=False):
        """Elige un movimiento completamente al azar, sin pensar."""
        mov_idx = random.randint(0, 3)
        return ("ATACAR", mov_idx)


# ==========================================
# AGENTE NIVEL 2: HEURÍSTICO BASADO EN HP
# ==========================================
class AgenteHeuristicoHP:
    def elegir_accion(self, batalla, es_jugador_1=False):
        """Elige acción basada en la diferencia de HP entre jugadores."""
        mi_equipo = batalla.equipo1 if es_jugador_1 else batalla.equipo2
        equipo_rival = batalla.equipo2 if es_jugador_1 else batalla.equipo1

        mi_pokemon = batalla.pokemon_actual1 if es_jugador_1 else batalla.pokemon_actual2
        rival_pokemon = batalla.pokemon_actual2 if es_jugador_1 else batalla.pokemon_actual1

        # Calcular HP total de cada equipo
        hp_mi_equipo = sum(p.current_hp for p in mi_equipo if not p.esta_debilitado())
        hp_rival_equipo = sum(p.current_hp for p in equipo_rival if not p.esta_debilitado())

        diferencia_hp = hp_mi_equipo - hp_rival_equipo

        # Si mi Pokémon está debilitado, cambio obligatorio
        if mi_pokemon.esta_debilitado():
            opciones = [i for i, p in enumerate(mi_equipo) if not p.esta_debilitado() and p != mi_pokemon]
            if opciones:
                return ("CAMBIAR", random.choice(opciones))

        # Lógica basada en diferencia de HP
        if diferencia_hp < -50:
            # Estoy en desventaja significativa: mayor probabilidad de cambiar
            posibles_cambios = [i for i, p in enumerate(mi_equipo) if not p.esta_debilitado() and p != mi_pokemon]
            if posibles_cambios and random.random() < 0.7:
                return ("CAMBIAR", random.choice(posibles_cambios))

        elif diferencia_hp > 50:
            # Tengo ventaja: prefiero atacar
            posibles_cambios = [i for i, p in enumerate(mi_equipo) if not p.esta_debilitado() and p != mi_pokemon]
            if posibles_cambios and random.random() < 0.2:
                return ("CAMBIAR", random.choice(posibles_cambios))

        # Evaluación de ataques: elegir el que haga más daño
        if not mi_pokemon.movimientos:
            return ("ATACAR", 0)

        mejor_dano = -1
        mejor_mov_idx = 0

        for i, mov in enumerate(mi_pokemon.movimientos):
            dano = batalla.calcular_dano(mi_pokemon, rival_pokemon, mov)[0]
            if dano > mejor_dano:
                mejor_dano = dano
                mejor_mov_idx = i

        return ("ATACAR", mejor_mov_idx)


# ==========================================
# FUNCIÓN DE SELECCIÓN ALEATORIA DE EQUIPO
# ==========================================
def seleccionar_equipo_aleatorio(cantidad=4):
    """Selecciona aleatoriamente Pokémon de los objetos hardcodeados."""
    from pokemones import all_pokemons
    return random.sample(all_pokemons, min(cantidad, len(all_pokemons)))