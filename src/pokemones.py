import random
import os
import json

try:
    import pygame
    PYGAME_DISPONIBLE = True
except ImportError:
    PYGAME_DISPONIBLE = False
    print("Advertencia: pygame no está disponible. La funcionalidad de sprites estará limitada.")

base_path = os.path.dirname(__file__)
img_path = os.path.join(base_path, '..', 'img')

TIPOS = [
    "Normal", "Fuego", "Agua", "Planta", "Eléctrico", "Hielo",
    "Lucha", "Veneno", "Tierra", "Volador", "Psíquico", "Bicho",
    "Roca", "Fantasma", "Dragón", "Siniestro", "Acero", "Hada"
]

EFECTIVIDAD_TIPOS = {
    ("Normal", "Roca"): 0.5, ("Normal", "Fantasma"): 0, ("Normal", "Acero"): 0.5,
    ("Fuego", "Fuego"): 0.5, ("Fuego", "Agua"): 0.5, ("Fuego", "Planta"): 2,
    ("Fuego", "Hielo"): 2, ("Fuego", "Bicho"): 2, ("Fuego", "Roca"): 0.5,
    ("Fuego", "Dragón"): 0.5, ("Fuego", "Acero"): 2, ("Fuego", "Hada"): 2,
    ("Agua", "Fuego"): 2, ("Agua", "Agua"): 0.5, ("Agua", "Planta"): 0.5,
    ("Agua", "Tierra"): 2, ("Agua", "Roca"): 2, ("Agua", "Dragón"): 0.5,
    ("Planta", "Fuego"): 0.5, ("Planta", "Agua"): 2, ("Planta", "Planta"): 0.5,
    ("Planta", "Tierra"): 2, ("Planta", "Volador"): 0.5, ("Planta", "Bicho"): 0.5,
    ("Planta", "Roca"): 2, ("Planta", "Dragón"): 0.5, ("Planta", "Acero"): 0.5,
    ("Planta", "Hada"): 0.5,
    ("Eléctrico", "Agua"): 2, ("Eléctrico", "Planta"): 0.5, ("Eléctrico", "Eléctrico"): 0.5,
    ("Eléctrico", "Tierra"): 0, ("Eléctrico", "Volador"): 2, ("Eléctrico", "Dragón"): 0.5,
    ("Eléctrico", "Acero"): 0.5,
    ("Hielo", "Fuego"): 0.5, ("Hielo", "Agua"): 0.5, ("Hielo", "Planta"): 2,
    ("Hielo", "Tierra"): 2, ("Hielo", "Volador"): 2, ("Hielo", "Dragón"): 2,
    ("Hielo", "Acero"): 0.5, ("Hielo", "Hada"): 2,
    ("Lucha", "Normal"): 2, ("Lucha", "Hielo"): 2, ("Lucha", "Veneno"): 0.5,
    ("Lucha", "Volador"): 0.5, ("Lucha", "Psíquico"): 0.5, ("Lucha", "Bicho"): 0.5,
    ("Lucha", "Roca"): 2, ("Lucha", "Fantasma"): 0, ("Lucha", "Siniestro"): 2,
    ("Lucha", "Acero"): 2, ("Lucha", "Hada"): 0.5,
    ("Veneno", "Planta"): 2, ("Veneno", "Tierra"): 0.5, ("Veneno", "Roca"): 0.5,
    ("Veneno", "Fantasma"): 0.5, ("Veneno", "Acero"): 0, ("Veneno", "Hada"): 2,
    ("Tierra", "Fuego"): 2, ("Tierra", "Planta"): 0.5, ("Tierra", "Eléctrico"): 2,
    ("Tierra", "Hielo"): 0.5, ("Tierra", "Veneno"): 2, ("Tierra", "Volador"): 0,
    ("Tierra", "Bicho"): 0.5, ("Tierra", "Roca"): 2, ("Tierra", "Acero"): 2,
    ("Volador", "Eléctrico"): 0.5, ("Volador", "Planta"): 2, ("Volador", "Lucha"): 2,
    ("Volador", "Bicho"): 2, ("Volador", "Tierra"): 1, ("Volador", "Roca"): 0.5,
    ("Volador", "Acero"): 0.5,
    ("Psíquico", "Lucha"): 2, ("Psíquico", "Veneno"): 2, ("Psíquico", "Psíquico"): 0.5,
    ("Psíquico", "Bicho"): 0.5, ("Psíquico", "Fantasma"): 0, ("Psíquico", "Siniestro"): 0,
    ("Psíquico", "Acero"): 0.5,
    ("Bicho", "Fuego"): 0.5, ("Bicho", "Planta"): 2, ("Bicho", "Lucha"): 0.5,
    ("Bicho", "Veneno"): 0.5, ("Bicho", "Volador"): 0.5, ("Bicho", "Fantasma"): 0.5,
    ("Bicho", "Siniestro"): 2, ("Bicho", "Acero"): 0.5, ("Bicho", "Hada"): 0.5,
    ("Roca", "Fuego"): 2, ("Roca", "Hielo"): 2, ("Roca", "Lucha"): 0.5,
    ("Roca", "Tierra"): 0.5, ("Roca", "Volador"): 2, ("Roca", "Bicho"): 2,
    ("Roca", "Acero"): 0.5,
    ("Fantasma", "Normal"): 0, ("Fantasma", "Psíquico"): 2, ("Fantasma", "Fantasma"): 2,
    ("Fantasma", "Siniestro"): 0.5, ("Fantasma", "Acero"): 0.5, ("Fantasma", "Hada"): 0,
    ("Dragón", "Dragón"): 2, ("Dragón", "Acero"): 0.5, ("Dragón", "Hada"): 0,
    ("Siniestro", "Lucha"): 0.5, ("Siniestro", "Psíquico"): 2, ("Siniestro", "Fantasma"): 2,
    ("Siniestro", "Siniestro"): 0.5, ("Siniestro", "Acero"): 0.5, ("Siniestro", "Hada"): 0.5,
    ("Acero", "Fuego"): 0.5, ("Acero", "Agua"): 0.5, ("Acero", "Eléctrico"): 0.5,
    ("Acero", "Hielo"): 2, ("Acero", "Roca"): 2, ("Acero", "Acero"): 0.5,
    ("Acero", "Hada"): 2,
    ("Hada", "Fuego"): 0.5, ("Hada", "Lucha"): 2, ("Hada", "Veneno"): 0.5,
    ("Hada", "Siniestro"): 2, ("Hada", "Acero"): 0.5, ("Hada", "Dragón"): 0,
}

def obtener_efectividad(tipo_ataque, tipo_defensor1, tipo_defensor2=None):
    clave = (tipo_ataque, tipo_defensor1)
    multiplicador = EFECTIVIDAD_TIPOS.get(clave, 1.0)
    
    if tipo_defensor2 and tipo_defensor2 not in ("null", None, ""):
        clave2 = (tipo_ataque, tipo_defensor2)
        multiplicador *= EFECTIVIDAD_TIPOS.get(clave2, 1.0)
    
    return multiplicador


def cargar_movimientos_json():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(os.path.join(base_dir, "..", "data", "pokemons.json"), encoding="utf-8") as f:
            data = json.load(f)
            moves_dict = {}
            for pokemon in data:
                moves_dict[pokemon["name"]] = pokemon.get("moves", [])
            return moves_dict
    except Exception as e:
        print(f"Error cargando movimientos: {e}")
        return {}


MOVIMIENTOS_DATA = cargar_movimientos_json()


class Movimiento:
    def __init__(self, name, power, accuracy, move_type, category="physical"):
        self.name = name
        self.power = power
        self.accuracy = accuracy
        self.type = move_type
        self.category = category.lower() if isinstance(category, str) else "physical"
    
    def __repr__(self):
        return f"Movimiento({self.name}, pow={self.power}, acc={self.accuracy}, tipo={self.type})"


class Pokemon:
    def __init__(
        self,
        nombre,
        ps,
        atck,
        dfns,
        spat,
        spdf,
        vel,
        ability,
        gender,
        type1,
        type2,
        move1,
        move2,
        move3,
        move4,
        sprite1,
        sprite2,
        back_sprite1,
        back_sprite2,
    ):
        self.nombre = nombre
        self.ps = ps
        self.atck = atck
        self.dfns = dfns
        self.spat = spat
        self.spdf = spdf
        self.vel = vel
        self.ability = ability
        self.gender = gender
        self.type1 = type1
        self.type2 = type2
        self.move1 = move1
        self.move2 = move2
        self.move3 = move3
        self.move4 = move4

        self.sprite1 = sprite1
        self.sprite2 = sprite2
        self.back_sprite1 = back_sprite1
        self.back_sprite2 = back_sprite2

        self.s1 = None
        self.s2 = None
        self.b1 = None
        self.b2 = None

        self.animando_f = False
        self.animando_b = False
        self.frame_f = 1
        self.frame_b = 1
        self.inicio_f = 0
        self.inicio_b = 0
        self.duracion_frame = 100

        self.movimientos = self._cargar_movimientos_desde_json()
    
    def _cargar_movimientos_desde_json(self):
        moves_data = MOVIMIENTOS_DATA.get(self.nombre, [])
        if not moves_data:
            return []
        cantidad = min(4, len(moves_data))
        seleccionados = random.sample(moves_data, cantidad)
        return [
            Movimiento(
                m.get("name", ""),
                m.get("power", 0),
                m.get("accuracy", 100),
                m.get("type", "Normal"),
                m.get("category", "physical"),
            )
            for m in seleccionados
        ]
    
    def obtener_movimientos(self):
        return self.movimientos
    
    def esta_debilitado(self):
        return getattr(self, 'current_hp', self.ps) <= 0
    
    def calcular_efectividad(self, tipo_ataque):
        return obtener_efectividad(tipo_ataque, self.type1, self.type2)

    def load_sprites(self, nuevo_tamano=(200, 200), image_folder=img_path):
        if not PYGAME_DISPONIBLE:
            return
        temp_s1 = pygame.image.load(os.path.join(image_folder, self.sprite1)).convert_alpha()
        temp_s2 = pygame.image.load(os.path.join(image_folder, self.sprite2)).convert_alpha()
        temp_b1 = pygame.image.load(os.path.join(image_folder, self.back_sprite1)).convert_alpha()
        temp_b2 = pygame.image.load(os.path.join(image_folder, self.back_sprite2)).convert_alpha()

        self.s1 = pygame.transform.scale(temp_s1, nuevo_tamano)
        self.s2 = pygame.transform.scale(temp_s2, nuevo_tamano)
        self.b1 = pygame.transform.scale(temp_b1, nuevo_tamano)
        self.b2 = pygame.transform.scale(temp_b2, nuevo_tamano)

    def activar_animacion(self, vista="frente"):
        if not PYGAME_DISPONIBLE:
            return
        if vista == "frente":
            self.animando_f = True
            self.inicio_f = pygame.time.get_ticks()
        else:
            self.animando_b = True
            self.inicio_b = pygame.time.get_ticks()

    def actualizar(self):
        if not PYGAME_DISPONIBLE:
            return
        ahora = pygame.time.get_ticks()

        if self.animando_f:
            t_f = ahora - self.inicio_f
            if t_f < 400:
                self.frame_f = 2 if (t_f // self.duracion_frame) % 2 == 1 else 1
            else:
                self.animando_f = False
                self.frame_f = 1

        if self.animando_b:
            t_b = ahora - self.inicio_b
            if t_b < 400:
                self.frame_b = 2 if (t_b // self.duracion_frame) % 2 == 1 else 1
            else:
                self.animando_b = False
                self.frame_b = 1

    def dibujar(self, superficie, pos, vista="frente"):
        if not PYGAME_DISPONIBLE:
            return
        if vista == "frente":
            img = self.s2 if self.frame_f == 2 else self.s1
        else:
            img = self.b2 if self.frame_b == 2 else self.b1
        superficie.blit(img, pos)

ability = {
    1: "Espesura",
    2: "Mar Llamas",
    3: "Torrente",
    4: "Intimidación",
    5: "Punto Tóxico",
    6: "Colector",
    7: "Levitación",
    8: "Insomnio",
    9: "Presión",
    10: "Velo Arena",
    11: "Fuerza Mental",
    12: "Chorro Arena",
    13: "Francotirador",
    14: "Robustez",
    15: "Roca Sólida",
    16: "Electromotor",
    17: "Cuerpo Llama",
    18: "Entusiasmo",
    19: "Impulso",
    20: "Defensa Hoja",
    21: "Manto Níveo",
    22: "Adaptable",
    23: "Impasible",
}

torterra_abilities = [1]
infernape_abilities = [2]
empoleon_abilities = [3]
staraptor_abilities = [4]
luxray_abilities = [4]
roserade_abilities = [5]
gastrodon_abilities = [6]
mismagius_abilities = [7]
honchkrow_abilities = [8]
bronzong_abilities = [7]
spiritomb_abilities = [9]
garchomp_abilities = [10]
lucario_abilities = [11, 23]
hippowdon_abilities = [12]
drapion_abilities = [13]
weavile_abilities = [9]
togekiss_abilities = [18]
magnezone_abilities = [14]
gliscor_abilities = [10]
gallade_abilities = [23]
leafeon_abilities = [20]
glaceon_abilities = [21]
yanmega_abilities = [19]
porygon_z_abilities = [22]
mamoswine_abilities = [21]
rhyperior_abilities = [15]
electivire_abilities = [16]
froslass_abilities = [21]
dusknoir_abilities = [9]
magmortar_abilities = [17]


torterra = Pokemon(
    "Torterra",
    170,
    161,
    125,
    85,
    106,
    118,
    ability[random.choice(torterra_abilities)],
    random.choice(["macho", "hembra"]),
    "planta",
    "tierra",
    1,
    2,
    3,
    4,
    "torterra1.png",
    "torterra2.png",
    "torterra_espalda1.png",
    "torterra_espalda2.png",
)

infernape = Pokemon(
    "Infernape",
    151,
    111,
    92,
    156,
    91,
    176,
    ability[random.choice(infernape_abilities)],
    random.choice(["macho", "hembra"]),
    "fuego",
    "lucha",
    1,
    2,
    3,
    4,
    "infernape1.png",
    "infernape2.png",
    "infernape_espalda1.png",
    "infernape_espalda2.png",
)

empoleon = Pokemon(
    "Empoleon",
    177,
    95,
    108,
    165,
    121,
    107,
    ability[random.choice(empoleon_abilities)],
    random.choice(["macho", "hembra"]),
    "agua",
    "acero",
    1,
    2,
    3,
    4,
    "empoleon1.png",
    "empoleon2.png",
    "empoleon_espalda1.png",
    "empoleon_espalda2.png",
)

staraptor = Pokemon(
    "Staraptor",
    160,
    172,
    91,
    63,
    80,
    167,
    ability[random.choice(staraptor_abilities)],
    random.choice(["macho", "hembra"]),
    "normal",
    "vuelo",
    1,
    2,
    3,
    4,
    "staraptor1.png",
    "staraptor2.png",
    "staraptor_espalda1.png",
    "staraptor_espalda2.png",
)

luxray = Pokemon(
    "Luxray",
    155,
    189,
    100,
    115,
    89,
    122,
    ability[random.choice(luxray_abilities)],
    random.choice(["macho", "hembra"]),
    "eléctrico",
    "null",
    1,
    2,
    3,
    4,
    "luxray1.png",
    "luxray2.png",
    "luxray_espalda1.png",
    "luxray_espalda2.png",
)

roserade = Pokemon(
    "Roserade",
    135,
    81,
    85,
    177,
    126,
    156,
    ability[random.choice(roserade_abilities)],
    random.choice(["macho", "hembra"]),
    "planta",
    "veneno",
    1,
    2,
    3,
    4,
    "roserade1.png",
    "roserade2.png",
    "roserade_espalda1.png",
    "roserade_espalda2.png",
)

gastrodon = Pokemon(
    "Gastrodon",
    218,
    103,
    132,
    112,
    103,
    53,
    ability[random.choice(gastrodon_abilities)],
    random.choice(["macho", "hembra"]),
    "agua",
    "tierra",
    1,
    2,
    3,
    4,
    "gastrodon1.png",
    "gastrodon2.png",
    "gastrodon_espalda1.png",
    "gastrodon_espalda2.png",
)

mismagius = Pokemon(
    "Mismagius",
    135,
    72,
    81,
    157,
    125,
    172,
    ability[random.choice(mismagius_abilities)],
    random.choice(["macho", "hembra"]),
    "fantasma",
    "null",
    1,
    2,
    3,
    4,
    "mismagius1.png",
    "mismagius2.png",
    "mismagius_espalda1.png",
    "mismagius_espalda2.png",
)

honchkrow = Pokemon(
    "Honchkrow",
    175,
    177,
    72,
    112,
    73,
    135,
    ability[random.choice(honchkrow_abilities)],
    random.choice(["macho", "hembra"]),
    "siniestro",
    "vuelo",
    1,
    2,
    3,
    4,
    "honchkrow1.png",
    "honchkrow2.png",
    "honchkrow_espalda1.png",
    "honchkrow_espalda2.png",
)

bronzong = Pokemon(
    "Bronzong",
    174,
    109,
    157,
    99,
    162,
    47,
    ability[random.choice(bronzong_abilities)],
    None,
    "acero",
    "psíquico",
    1,
    2,
    3,
    4,
    "bronzong1.png",
    "bronzong2.png",
    "bronzong_espalda1.png",
    "bronzong_espalda2.png",
)

spiritomb = Pokemon(
    "Spiritomb",
    157,
    112,
    128,
    158,
    129,
    49,
    ability[random.choice(spiritomb_abilities)],
    random.choice(["macho", "hembra"]),
    "fantasma",
    "siniestro",
    1,
    2,
    3,
    4,
    "spiritomb1.png",
    "spiritomb2.png",
    "spiritomb_espalda1.png",
    "spiritomb_espalda2.png",
)

garchomp = Pokemon(
    "Garchomp",
    215,
    150,
    156,
    90,
    105,
    127,
    ability[random.choice(garchomp_abilities)],
    random.choice(["macho", "hembra"]),
    "dragon",
    "tierra",
    1,
    2,
    3,
    4,
    "garchomp1.png",
    "garchomp2.png",
    "garchomp_espalda1.png",
    "garchomp_espalda2.png",
)

lucario = Pokemon(
    "Lucario",
    145,
    162,
    90,
    121,
    91,
    156,
    ability[random.choice(lucario_abilities)],
    random.choice(["macho", "hembra"]),
    "lucha",
    "acero",
    1,
    2,
    3,
    4,
    "lucario1.png",
    "lucario2.png",
    "lucario_espalda1.png",
    "lucario_espalda2.png",
)

hippowdon = Pokemon(
    "Hippowdon",
    214,
    132,
    167,
    79,
    111,
    67,
    ability[random.choice(hippowdon_abilities)],
    random.choice(["macho", "hembra"]),
    "tierra",
    "null",
    1,
    2,
    3,
    4,
    "hippowdon1.png",
    "hippowdon2.png",
    "hippowdon_espalda1.png",
    "hippowdon_espalda2.png",
)

drapion = Pokemon(
    "Drapion",
    146,
    156,
    162,
    72,
    95,
    115,
    ability[random.choice(drapion_abilities)],
    random.choice(["macho", "hembra"]),
    "veneno",
    "siniestro",
    1,
    2,
    3,
    4,
    "drapion1.png",
    "drapion2.png",
    "drapion_espalda1.png",
    "drapion_espalda2.png",
)

weavile = Pokemon(
    "Weavile",
    145,
    172,
    85,
    58,
    106,
    194,
    ability[random.choice(weavile_abilities)],
    random.choice(["macho", "hembra"]),
    "siniestro",
    "hielo",
    1,
    2,
    3,
    4,
    "weavile1.png",
    "weavile2.png",
    "weavile_espalda1.png",
    "weavile_espalda2.png",
)

togekiss = Pokemon(
    "Togekiss",
    192,
    63,
    115,
    159,
    163,
    100,
    ability[random.choice(togekiss_abilities)],
    random.choice(["macho", "hembra"]),
    "normal",
    "volador",
    1,
    2,
    3,
    4,
    "togekiss1.png",
    "togekiss2.png",
    "togekiss_espalda1.png",
    "togekiss_espalda2.png",
)

magnezone = Pokemon(
    "Magnezone",
    145,
    81,
    135,
    200,
    111,
    112,
    ability[random.choice(magnezone_abilities)],
    None,
    "eléctrico",
    "acero",
    1,
    2,
    3,
    4,
    "magnezone1.png",
    "magnezone2.png",
    "magnezone_espalda1.png",
    "magnezone_espalda2.png",
)

gliscor = Pokemon(
    "Gliscor",
    181,
    100,
    150,
    58,
    136,
    115,
    ability[random.choice(gliscor_abilities)],
    random.choice(["macho", "hembra"]),
    "tierra",
    "volador",
    1,
    2,
    3,
    4,
    "gliscor1.png",
    "gliscor2.png",
    "gliscor_espalda1.png",
    "gliscor_espalda2.png",
)

gallade = Pokemon(
    "Gallade",
    143,
    177,
    85,
    76,
    136,
    145,
    ability[random.choice(gallade_abilities)],
    "macho",
    "psíquico",
    "lucha",
    1,
    2,
    3,
    4,
    "gallade1.png",
    "gallade2.png",
    "gallade_espalda1.png",
    "gallade_espalda2.png",
)

leafeon = Pokemon(
    "Leafeon",
    140,
    178,
    150,
    72,
    86,
    147,
    ability[random.choice(leafeon_abilities)],
    random.choice(["macho", "hembra"]),
    "planta",
    "null",
    1,
    2,
    3,
    4,
    "leafeon1.png",
    "leafeon2.png",
    "leafeon_espalda1.png",
    "leafeon_espalda2.png",
)

glaceon = Pokemon(
    "Glaceon",
    141,
    72,
    162,
    200,
    115,
    85,
    ability[random.choice(glaceon_abilities)],
    random.choice(["macho", "hembra"]),
    "hielo",
    "null",
    1,
    2,
    3,
    4,
    "glaceon1.png",
    "glaceon2.png",
    "glaceon_espalda1.png",
    "glaceon_espalda2.png",
)

yanmega = Pokemon(
    "Yanmega",
    161,
    86,
    106,
    184,
    77,
    147,
    ability[random.choice(yanmega_abilities)],
    random.choice(["macho", "hembra"]),
    "bicho",
    "volador",
    1,
    2,
    3,
    4,
    "yanmega1.png",
    "yanmega2.png",
    "yanmega_espalda1.png",
    "yanmega_espalda2.png",
)

rhyperior = Pokemon(
    "Rhyperior",
    222,
    178,
    150,
    67,
    105,
    60,
    ability[random.choice(rhyperior_abilities)],
    random.choice(["macho", "hembra"]),
    "tierra",
    "roca",
    1,
    2,
    3,
    4,
    "rhyperior1.png",
    "rhyperior2.png",
    "rhyperior_espalda1.png",
    "rhyperior_espalda2.png",
)

dusknoir = Pokemon(
    "Dusknoir",
    152,
    167,
    155,
    76,
    156,
    65,
    ability[random.choice(dusknoir_abilities)],
    random.choice(["macho", "hembra"]),
    "fantasma",
    "null",
    1,
    2,
    3,
    4,
    "dusknoir1.png",
    "dusknoir2.png",
    "dusknoir_espalda1.png",
    "dusknoir_espalda2.png",
)

porygon_z = Pokemon(
    "Porygon-Z",
    160,
    90,
    90,
    205,
    96,
    142,
    ability[random.choice(porygon_z_abilities)],
    "null",
    "normal",
    "null",
    1,
    2,
    3,
    4,
    "porygon_z1.png",
    "porygon_z2.png",
    "porygon_z_espalda1.png",
    "porygon_z_espalda2.png",
)

electivire = Pokemon(
    "Electivire",
    169,
    192,
    101,
    115,
    94,
    115,
    ability[random.choice(electivire_abilities)],
    random.choice(["macho", "hembra"]),
    "eléctrico",
    "null",
    1,
    2,
    3,
    4,
    "electivire1.png",
    "electivire2.png",
    "electivire_espalda1.png",
    "electivire_espalda2.png",
)

magmortar = Pokemon(
    "Magmortar",
    150,
    103,
    88,
    177,
    115,
    148,
    ability[random.choice(magmortar_abilities)],
    random.choice(["macho", "hembra"]),
    "fuego",
    "null",
    1,
    2,
    3,
    4,
    "magmortar1.png",
    "magmortar2.png",
    "magmortar_espalda1.png",
    "magmortar_espalda2.png",
)

mamoswine = Pokemon(
    "Mamoswine",
    185,
    200,
    101,
    81,
    80,
    132,
    ability[random.choice(mamoswine_abilities)],
    random.choice(["macho", "hembra"]),
    "hielo",
    "tierra",
    1,
    2,
    3,
    4,
    "mamoswine1.png",
    "mamoswine2.png",
    "mamoswine_espalda1.png",
    "mamoswine_espalda2.png",
)

froslass = Pokemon(
    "Froslass",
    145,
    132,
    90,
    90,
    91,
    178,
    ability[random.choice(froslass_abilities)],
    "hembra",
    "hielo",
    "fantasma",
    1,
    2,
    3,
    4,
    "froslass1.png",
    "froslass2.png",
    "froslass_espalda1.png",
    "froslass_espalda2.png",
)

all_pokemons = [
    torterra,
    infernape,
    empoleon,
    staraptor,
    luxray,
    roserade,
    gastrodon,
    mismagius,
    honchkrow,
    bronzong,
    spiritomb,
    garchomp,
    lucario,
    hippowdon,
    drapion,
    weavile,
    togekiss,
    magnezone,
    gliscor,
    gallade,
    leafeon,
    glaceon,
    yanmega,
    rhyperior,
    dusknoir,
    porygon_z,
    electivire,
    magmortar,
    mamoswine,
    froslass,
]


def load_all_pokemon_sprites(nuevo_tamano=(200, 200)):
    for pok in all_pokemons:
        pok.load_sprites(nuevo_tamano)
