import pytest
import sys
import os
import json
import tempfile

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, 'src'))

from pokemones import obtener_efectividad as obtener_efectividad_poke, TIPOS as TIPOS_POKE, EFECTIVIDAD_TIPOS as EFECTIVIDAD_POKE
from combate import obtener_efectividad as obtener_efectividad_combate, TIPOS as TIPOS_COMBATE
from game_logic import cargar_equipos_desde_json, guardar_equipos_en_json
from main import normalize_name


class TestObtenerEfectividadPokemones:
    def test_efectividad_fuego_vs_planta(self):
        assert obtener_efectividad_poke("Fuego", "Planta") == 2.0
    
    def test_efectividad_fuego_vs_agua(self):
        assert obtener_efectividad_poke("Fuego", "Agua") == 0.5
    
    def test_efectividad_fuego_vs_fuego(self):
        assert obtener_efectividad_poke("Fuego", "Fuego") == 0.5
    
    def test_agua_vs_fuego(self):
        assert obtener_efectividad_poke("Agua", "Fuego") == 2.0
    
    def test_agua_vs_agua(self):
        assert obtener_efectividad_poke("Agua", "Agua") == 0.5
    
    def test_electrico_vs_tierra(self):
        assert obtener_efectividad_poke("Eléctrico", "Tierra") == 0
    
    def test_electrico_vs_agua(self):
        assert obtener_efectividad_poke("Eléctrico", "Agua") == 2.0
    
    def test_normal_vs_fantasma(self):
        assert obtener_efectividad_poke("Normal", "Fantasma") == 0
    
    def test_lucha_vs_normal(self):
        assert obtener_efectividad_poke("Lucha", "Normal") == 2.0
    
    def test_fantasma_vs_normal(self):
        assert obtener_efectividad_poke("Fantasma", "Normal") == 0
    
    def test_dragón_vs_dragón(self):
        assert obtener_efectividad_poke("Dragón", "Dragón") == 2.0
    
    def test_efectividad_default(self):
        assert obtener_efectividad_poke("Normal", "Normal") == 1.0
    
    def test_tipo_extrano(self):
        assert obtener_efectividad_poke("Fuego", "Desconocido") == 1.0


class TestObtenerEfectividadCombate:
    def test_efectividad_fuego_vs_planta(self):
        assert obtener_efectividad_combate("Fuego", "Planta") == 2.0
    
    def test_efectividad_fuego_vs_agua(self):
        assert obtener_efectividad_combate("Fuego", "Agua") == 0.5
    
    def test_electrico_vs_tierra(self):
        assert obtener_efectividad_combate("Eléctrico", "Tierra") == 0
    
    def test_normal_vs_fantasma(self):
        assert obtener_efectividad_combate("Normal", "Fantasma") == 0
    
    def test_efectividad_default(self):
        assert obtener_efectividad_combate("Normal", "Normal") == 1.0


class TestNormalizeName:
    def test_normalize_name_basic(self):
        assert normalize_name("pikachu") == "pikachu"
    
    def test_normalize_name_with_spaces(self):
        assert normalize_name("mr mime") == "mr mime"
    
    def test_normalize_name_capitalized(self):
        assert normalize_name("Pikachu") == "Pikachu"
    
    def test_normalize_name_special(self):
        assert normalize_name("mr. mime") == "mr mime"


class TestCargarEquipos:
    def test_cargar_equipos_vacio(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"jugador": [], "ia": []}, f)
            temp_path = f.name
        
        try:
            equipos = cargar_equipos_desde_json(temp_path)
            assert equipos is not None
            assert "jugador" in equipos
            assert "ia" in equipos
        finally:
            os.unlink(temp_path)
    
    def test_guardar_y_cargar_equipos(self):
        equipo_jugador = [{"name": "pikachu"}]
        equipo_ia = [{"name": "charizard"}]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            guardar_equipos_en_json(temp_path, equipo_jugador, equipo_ia)
            equipos = cargar_equipos_desde_json(temp_path)
            assert equipos["jugador"] == equipo_jugador
            assert equipos["ia"] == equipo_ia
        finally:
            os.unlink(temp_path)


class TestTipos:
    def test_tipos_pokemones(self):
        assert "Fuego" in TIPOS_POKE
        assert "Agua" in TIPOS_POKE
        assert "Planta" in TIPOS_POKE
        assert "Eléctrico" in TIPOS_POKE
    
    def test_tipos_combate(self):
        assert "Fuego" in TIPOS_COMBATE
        assert "Agua" in TIPOS_COMBATE
        assert "Planta" in TIPOS_COMBATE
        assert "Eléctrico" in TIPOS_COMBATE