import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import random
import json

try:
    import pygame
    PYGAME_DISPONIBLE = True
except ImportError:
    PYGAME_DISPONIBLE = False
    print("Advertencia: pygame no está disponible. La música estará desactivada.")

# Importamos nuestra lógica
from src.combate import Combate, PokemonCombate, guardar_equipos_en_json
from src.agents import AgenteAleatorio, AgenteHeuristicoHP, seleccionar_equipo_aleatorio
import config

def crear_equipo_desde_objetos(pokemons):
    """Crea una lista de objetos PokemonCombate para el combate desde objetos hardcodeados."""
    equipo = []
    for idx, pokemon in enumerate(pokemons, start=1):
        moves = []
        for mov in pokemon.movimientos:
            moves.append({
                "name": mov.name,
                "power": mov.power,
                "accuracy": mov.accuracy,
                "type": mov.type,
                "category": mov.category,
            })
        equipo.append(PokemonCombate({
            "name": pokemon.nombre,
            "tipo1": pokemon.type1,
            "tipo2": pokemon.type2 if pokemon.type2 != "null" else None,
            "hp": pokemon.ps,
            "atk": pokemon.atck,
            "def": pokemon.dfns,
            "spat": pokemon.spat,
            "spdf": pokemon.spdf,
            "spe": pokemon.vel,
            "gender": pokemon.gender,
            "position": idx,
            "img_mini": pokemon.sprite1,
            "img_large_gif": pokemon.sprite2,
            "img_back": pokemon.back_sprite1,
            "moves": moves,
        }))
    return equipo

class PantallaBatalla(tk.Frame):
    def __init__(self, parent, nombres_jugador, al_terminar):
        super().__init__(parent)
        self.parent = parent
        self.al_terminar = al_terminar
        self.nombres_jugador = nombres_jugador
        
        # 1. Cargar equipos
        # Equipo del jugador (seleccionado manualmente)
        ruta_equipos = os.path.join(os.path.dirname(__file__), "..", "data", "equipos.json")
        equipo_jugador, _ = self._cargar_equipos_jugador(ruta_equipos)

        # Equipo de la IA (selección aleatoria desde objetos hardcodeados)
        pokemons_ia = seleccionar_equipo_aleatorio(cantidad=4)
        equipo_ia = crear_equipo_desde_objetos(pokemons_ia)
        
        self.ruta_equipos = ruta_equipos
        self.batalla = Combate(equipo_jugador, equipo_ia)
        self._cambio_forzado = False
        guardar_equipos_en_json(self.ruta_equipos, self.batalla.equipo1, self.batalla.equipo2)
        
        # Iniciar música de batalla
        if PYGAME_DISPONIBLE:
            try:
                ruta_musica = os.path.join(os.path.dirname(__file__), "..", "assets", "music", "batalla.mp3")
                if os.path.exists(ruta_musica):
                    pygame.mixer.music.load(ruta_musica)
                    pygame.mixer.music.play(-1)  # -1 para bucle infinito
            except Exception as e:
                print(f"Error reproduciendo música de batalla: {e}")
        
        # 2. Configurar Interfaz
        self.config(bg="#f4fcf2") # Color de fondo
        self.crear_widgets()
        self.actualizar_hud()
        self.escribir_mensaje(f"¡El Entrenador Rival te desafía!\n¡Envió a {self.batalla.pokemon_actual2.name}!")

    def _cargar_equipos_jugador(self, ruta_json):
        """Carga solo el equipo del jugador desde equipos.json"""
        with open(ruta_json, "r", encoding="utf-8") as f:
            datos = json.load(f)
        equipo = [PokemonCombate(p) for p in datos.get("team_jugador", [])]
        return equipo, []

    def crear_widgets(self):
        # --- ZONA DE DIBUJO (CANVAS) ---
        self.canvas = tk.Canvas(self, width=800, height=400, bg="#e8f4f8", highlightthickness=2, highlightbackground="#4a76a8")
        self.canvas.pack(pady=20)

        # Referencias para que las imágenes no se borren de la memoria
        self.img_ref_rival = None
        self.img_ref_jugador = None
        self.sprite_rival = self.canvas.create_image(500, 50, anchor="nw")
        self.sprite_jugador = self.canvas.create_image(150, 180, anchor="nw")

        # HUD Rival
        self.hud_rival = tk.Frame(self.canvas, bg="white", bd=2, relief="ridge")
        self.canvas.create_window(200, 80, window=self.hud_rival, width=260, height=80)
        self.hud_rival_top = tk.Frame(self.hud_rival, bg="white")
        self.hud_rival_top.pack(fill="x", padx=8, pady=(6, 2))
        self.lbl_nombre_rival = tk.Label(self.hud_rival_top, text="RIVAL", font=("Arial", 11, "bold"), bg="white")
        self.lbl_nombre_rival.pack(side="left", anchor="w")
        self.lbl_gender_rival = tk.Label(self.hud_rival_top, text="", font=("Arial", 11, "bold"), bg="white")
        self.lbl_gender_rival.pack(side="left", anchor="w", padx=(4,0))
        self.lbl_hp_text_rival = tk.Label(self.hud_rival_top, text="0/0", font=("Courier", 9, "bold"), bg="white", fg="#333")
        self.lbl_hp_text_rival.pack(side="right", anchor="e")
        self.lbl_state_rival = tk.Label(self.hud_rival, text="", font=("Arial", 9), bg="white", fg="#666")
        self.lbl_state_rival.pack(fill="x", padx=8)
        self.hp_canvas_rival = tk.Canvas(self.hud_rival, bg="white", height=22, highlightthickness=0)
        self.hp_canvas_rival.pack(fill="x", padx=8, pady=(3,8))
        self.hp_bg_rect_rival = self.hp_canvas_rival.create_rectangle(0, 0, 236, 22, outline="#20323c", width=2, fill="#d7e2e8")
        self.hp_fill_rect_rival = self.hp_canvas_rival.create_rectangle(2, 2, 2, 20, outline="", fill="#4caf50")

        # HUD Jugador
        self.hud_jugador = tk.Frame(self.canvas, bg="white", bd=2, relief="ridge")
        self.canvas.create_window(600, 280, window=self.hud_jugador, width=260, height=90)
        self.hud_jugador_top = tk.Frame(self.hud_jugador, bg="white")
        self.hud_jugador_top.pack(fill="x", padx=8, pady=(6, 2))
        self.lbl_nombre_jugador = tk.Label(self.hud_jugador_top, text="TU POKÉMON", font=("Arial", 11, "bold"), bg="white")
        self.lbl_nombre_jugador.pack(side="left", anchor="w")
        self.lbl_gender_jugador = tk.Label(self.hud_jugador_top, text="", font=("Arial", 11, "bold"), bg="white")
        self.lbl_gender_jugador.pack(side="left", anchor="w", padx=(4,0))
        self.lbl_hp_num = tk.Label(self.hud_jugador_top, text="0/0", font=("Courier", 9, "bold"), bg="white", fg="#333")
        self.lbl_hp_num.pack(side="right", anchor="e")
        self.lbl_state_jugador = tk.Label(self.hud_jugador, text="", font=("Arial", 9), bg="white", fg="#666")
        self.lbl_state_jugador.pack(fill="x", padx=8)
        self.hp_canvas_jugador = tk.Canvas(self.hud_jugador, bg="white", height=22, highlightthickness=0)
        self.hp_canvas_jugador.pack(fill="x", padx=8, pady=(3,8))
        self.hp_bg_rect_jugador = self.hp_canvas_jugador.create_rectangle(0, 0, 236, 22, outline="#20323c", width=2, fill="#d7e2e8")
        self.hp_fill_rect_jugador = self.hp_canvas_jugador.create_rectangle(2, 2, 2, 20, outline="", fill="#4caf50")

        # --- CAJA DE DIÁLOGO Y MENÚ INFERIOR ---
        self.frame_inferior = tk.Frame(self, height=180, bg="#2b2b2b", bd=5, relief="groove")
        self.frame_inferior.pack(fill="x", side="bottom", padx=20, pady=20)

        self.lbl_mensaje = tk.Label(self.frame_inferior, text="", fg="white", bg="#2b2b2b", 
                                   font=("Courier", 16, "bold"), wraplength=450, justify="left")
        self.lbl_mensaje.place(x=30, y=40)

        # Menú Principal
        self.menu_acciones = tk.Frame(self.frame_inferior, bg="#2b2b2b")
        self.menu_acciones.place(x=500, y=20)

        self.btn_luchar = tk.Button(self.menu_acciones, text="LUCHAR", width=12, height=2, bg="#e3350d", fg="white", font=("Arial", 12, "bold"), command=self._accion_luchar)
        self.btn_luchar.grid(row=0, column=0, padx=5, pady=5)
        
        self.btn_bolsa = tk.Button(self.menu_acciones, text="MOCHILA", width=12, height=2, bg="#eec608", font=("Arial", 12, "bold"), command=lambda: self.escribir_mensaje("No se permiten objetos."))
        self.btn_bolsa.grid(row=0, column=1, padx=5, pady=5)
        
        self.btn_pkmn = tk.Button(self.menu_acciones, text="POKÉMON", width=12, height=2, bg="#4dad5b", fg="white", font=("Arial", 12, "bold"), command=self.mostrar_cambio_pokemon)
        self.btn_pkmn.grid(row=1, column=0, padx=5, pady=5)
        
        self.btn_huir = tk.Button(self.menu_acciones, text="HUIR", width=12, height=2, bg="#30a7d7", fg="white", font=("Arial", 12, "bold"), command=lambda: self.escribir_mensaje("¡No puedes huir!"))
        self.btn_huir.grid(row=1, column=1, padx=5, pady=5)

        # Menú Ataques (Oculto)
        self.menu_ataques = tk.Frame(self.frame_inferior, bg="#2b2b2b")

    def escribir_mensaje(self, texto):
        self.lbl_mensaje.config(text=texto)
        self.update() # Fuerza a la pantalla a actualizarse

    def formatear_genero(self, gender):
        if gender is None:
            return "", "#000000"
        if isinstance(gender, str) and gender.lower() == "hembra":
            return "♀", "#e91e63"
        return "♂", "#1e88e5"

    def actualizar_hud(self):
        p1 = self.batalla.pokemon_actual1
        p2 = self.batalla.pokemon_actual2

        gender_symbol2, gender_color2 = self.formatear_genero(getattr(p2, "gender", "macho"))
        estado2 = getattr(p2, "state", None)
        self.lbl_nombre_rival.config(text=f"{p2.name.upper()} Lv.50")
        self.lbl_gender_rival.config(text=gender_symbol2, fg=gender_color2)
        self.lbl_state_rival.config(text=f"{estado2.upper()}" if estado2 else "")
        self.lbl_hp_text_rival.config(text=f"{p2.current_hp} / {p2.max_hp}")
        self._actualizar_barra_hp(self.hp_canvas_rival, self.hp_fill_rect_rival, p2.obtener_porcentaje_hp())

        gender_symbol1, gender_color1 = self.formatear_genero(getattr(p1, "gender", "macho"))
        estado1 = getattr(p1, "state", None)
        self.lbl_nombre_jugador.config(text=f"{p1.name.upper()} Lv.50")
        self.lbl_gender_jugador.config(text=gender_symbol1, fg=gender_color1)
        self.lbl_state_jugador.config(text=f"{estado1.upper()}" if estado1 else "")
        self.lbl_hp_num.config(text=f"{p1.current_hp} / {p1.max_hp}")
        self._actualizar_barra_hp(self.hp_canvas_jugador, self.hp_fill_rect_jugador, p1.obtener_porcentaje_hp())

        # Dibujar Imágenes
        ruta_rival = os.path.join(os.path.dirname(__file__), "..", p2.img_large_gif)
        ruta_jugador = os.path.join(os.path.dirname(__file__), "..", p1.img_back)

        if os.path.exists(ruta_rival):
            img_r = Image.open(ruta_rival).convert("RGBA").resize((180, 180), Image.Resampling.LANCZOS)
            self.img_ref_rival = ImageTk.PhotoImage(img_r)
            self.canvas.itemconfig(self.sprite_rival, image=self.img_ref_rival)

        if os.path.exists(ruta_jugador):
            img_j = Image.open(ruta_jugador).convert("RGBA").resize((200, 200), Image.Resampling.LANCZOS)
            self.img_ref_jugador = ImageTk.PhotoImage(img_j)
            self.canvas.itemconfig(self.sprite_jugador, image=self.img_ref_jugador)

        self._actualizar_boton_luchar()

    def _actualizar_barra_hp(self, canvas, fill_rect, porcentaje):
        porcentaje = max(0, min(100, porcentaje))
        ancho_total = 232
        ancho_relleno = int(ancho_total * (porcentaje / 100))
        ancho_relleno = max(2, ancho_relleno)

        color = "#4caf50"
        if porcentaje <= 40:
            color = "#f44336"
        elif porcentaje <= 75:
            color = "#ffb300"

        canvas.coords(fill_rect, 2, 2, 2 + ancho_relleno, 20)
        canvas.itemconfig(fill_rect, fill=color)

    def mostrar_ataques(self):
        self.menu_acciones.place_forget()
        self.menu_ataques.place(x=450, y=10)
        
        for widget in self.menu_ataques.winfo_children():
            widget.destroy()

        p1 = self.batalla.pokemon_actual1
        for i, mov in enumerate(p1.movimientos):
            btn = tk.Button(self.menu_ataques, text=f"{mov.name.upper()}\n{mov.type}", width=15, height=2,
                           font=("Arial", 10, "bold"), command=lambda idx=i: self.ejecutar_turno(("ATACAR", idx)))
            btn.grid(row=i//2, column=i%2, padx=5, pady=5)
        
        btn_volver = tk.Button(self.menu_ataques, text="ATRÁS", width=32, bg="gray", fg="white", font=("Arial", 10, "bold"), command=self.ocultar_ataques)
        btn_volver.grid(row=2, column=0, columnspan=2, pady=5)

    def ocultar_ataques(self):
        self.menu_ataques.place_forget()
        self.menu_acciones.place(x=500, y=20)

    def _accion_luchar(self):
        if self.batalla.pokemon_actual1.esta_debilitado():
            self.escribir_mensaje("Tu Pokémon está debilitado y no puede luchar.")
            return
        self.mostrar_ataques()

    def _actualizar_boton_luchar(self):
        if self.batalla.pokemon_actual1.esta_debilitado():
            self.btn_luchar.config(state="disabled", text="LUCHAR (DEBILITADO)")
        else:
            self.btn_luchar.config(state="normal", text="LUCHAR")

    def mostrar_cambio_pokemon(self, es_forzado=False):
        self.menu_acciones.place_forget()
        self._cambio_forzado = es_forzado
        self._crear_popup_cambio()

    def _verificar_cambios_forzados(self):
        if self.batalla.juego_terminado() != 0:
            return False

        if self.batalla.pokemon_actual1.esta_debilitado():
            self.escribir_mensaje("¡Tu Pokémon se debilitó! Elige otro para continuar.")
            self._actualizar_boton_luchar()
            self.mostrar_cambio_pokemon(es_forzado=True)
            return True

        if self.batalla.pokemon_actual2.esta_debilitado():
            opciones = [i for i, p in enumerate(self.batalla.equipo2) if not p.esta_debilitado() and p != self.batalla.pokemon_actual2]
            if opciones:
                indice = random.choice(opciones)
                viejo = self.batalla.pokemon_actual2.name
                self.batalla.pokemon_actual2 = self.batalla.equipo2[indice]
                self.escribir_mensaje(f"El rival retira a {viejo} y envía a {self.batalla.pokemon_actual2.name}.")
                self.actualizar_hud()
                guardar_equipos_en_json(self.ruta_equipos, self.batalla.equipo1, self.batalla.equipo2)
                return True

        self._actualizar_boton_luchar()
        return False

    def _crear_popup_cambio(self):
        if hasattr(self, 'popup_cambio') and self.popup_cambio.winfo_exists():
            return

        self.popup_cambio = tk.Toplevel(self)
        self.popup_cambio.title("Cambiar Pokémon")
        self.popup_cambio.transient(self.parent)
        self.popup_cambio.grab_set()
        self.popup_cambio.configure(bg="#f4fcf2")
        self.popup_cambio.geometry("840x520")
        self.popup_cambio.resizable(False, False)
        self.popup_cambio.protocol("WM_DELETE_WINDOW", self._cerrar_popup_cambio)

        tk.Label(self.popup_cambio, text="Selecciona un Pokémon para cambiar", font=("Arial", 18, "bold"), bg="#f4fcf2").pack(pady=14)

        contenedor = tk.Frame(self.popup_cambio, bg="#f4fcf2")
        contenedor.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        contenedor.grid_columnconfigure(0, weight=1)
        contenedor.grid_columnconfigure(1, weight=1)

        for idx, poke in enumerate(self.batalla.equipo1):
            fila = tk.Frame(contenedor, bg="white", bd=2, relief="raised")
            fila.grid(row=idx//2, column=idx%2, padx=8, pady=8, sticky="nsew")
            contenedor.grid_columnconfigure(idx%2, weight=1)

            nombre = tk.Label(fila, text=poke.name.upper(), font=("Arial", 12, "bold"), bg="white")
            nombre.pack(anchor="w", padx=10, pady=(10, 2))

            info = f"Lv.50   HP: {poke.current_hp}/{poke.max_hp}"
            tk.Label(fila, text=info, font=("Arial", 10), bg="white").pack(anchor="w", padx=10)

            img_path = os.path.join(os.path.dirname(__file__), "..", poke.img_mini)
            if os.path.exists(img_path):
                img = Image.open(img_path).convert("RGBA").resize((80, 80), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                label_img = tk.Label(fila, image=photo, bg="white")
                label_img.image = photo
                label_img.pack(padx=10, pady=8)

            estado = ""
            if poke == self.batalla.pokemon_actual1:
                estado = "EN COMBATE"
            elif poke.esta_debilitado():
                estado = "DEBILITADO"
            if estado:
                tk.Label(fila, text=estado, font=("Arial", 10, "bold"), fg="#d32f2f" if "DEBILITADO" in estado else "#1e88e5", bg="white").pack(anchor="w", padx=10)

            estado_btn = "normal"
            texto_btn = "SELECCIONAR"
            if poke == self.batalla.pokemon_actual1:
                estado_btn = "disabled"
                texto_btn = "ACTIVO"
            elif poke.esta_debilitado():
                estado_btn = "disabled"
                texto_btn = "DEBILITADO"

            btn = tk.Button(fila, text=texto_btn, width=16, bg="#4dad5b" if estado_btn == "normal" else "#999999", fg="white", font=("Arial", 10, "bold"), state=estado_btn, command=lambda idx=idx: self._seleccionar_pokemon_cambio(idx))
            btn.pack(pady=8)

        btn_cancel = tk.Button(self.popup_cambio, text="CANCELAR", width=18, bg="#e3350d", fg="white", font=("Arial", 12, "bold"), command=self._cerrar_popup_cambio)
        btn_cancel.pack(pady=(0, 12))

    def _cerrar_popup_cambio(self):
        if hasattr(self, 'popup_cambio') and self.popup_cambio.winfo_exists():
            self.popup_cambio.destroy()
        self.menu_acciones.place(x=500, y=20)

    def _seleccionar_pokemon_cambio(self, idx, es_forzado=None):
        if es_forzado is None:
            es_forzado = self._cambio_forzado
        self._cambio_forzado = False

        if self.batalla.equipo1[idx] == self.batalla.pokemon_actual1:
            self.escribir_mensaje("Ese Pokémon ya está en combate.")
            self._cerrar_popup_cambio()
            return
        if self.batalla.equipo1[idx].esta_debilitado():
            self.escribir_mensaje("No puedes elegir un Pokémon debilitado.")
            self._cerrar_popup_cambio()
            return

        viejo = self.batalla.pokemon_actual1.name
        self._cerrar_popup_cambio()

        if es_forzado:
            self.batalla.pokemon_actual1 = self.batalla.equipo1[idx]
            self.escribir_mensaje(f"¡{viejo} se debilitó! ¡Entra {self.batalla.pokemon_actual1.name}!")
            self.actualizar_hud()

            if self.batalla.pokemon_actual2.esta_debilitado():
                opciones = [i for i, p in enumerate(self.batalla.equipo2) if not p.esta_debilitado() and p != self.batalla.pokemon_actual2]
                if opciones:
                    indice = random.choice(opciones)
                    viejo_ia = self.batalla.pokemon_actual2.name
                    self.batalla.pokemon_actual2 = self.batalla.equipo2[indice]
                    self.escribir_mensaje(f"El rival retira a {viejo_ia} y envía a {self.batalla.pokemon_actual2.name}.")
                    self.actualizar_hud()

            self.batalla.turno_actual += 1
            guardar_equipos_en_json(self.ruta_equipos, self.batalla.equipo1, self.batalla.equipo2)
            self._actualizar_boton_luchar()
            self.menu_acciones.place(x=500, y=20)
        else:
            self.ejecutar_turno(("CAMBIAR", idx))

    def ejecutar_turno(self, accion_jugador):
        self.ocultar_ataques()
        self.menu_acciones.place_forget() # Ocultar menú para que no spammee clicks
        
        # IA del rival (según configuración)
        if config.NIVEL_IA == "aleatorio":
            ia = AgenteAleatorio()
        else:
            ia = AgenteHeuristicoHP()
        accion_ia = ia.elegir_accion(self.batalla, es_jugador_1=False)

        # Resolver
        logs = self.batalla.resolver_turno(accion_jugador, accion_ia)
        
        # Logging en consola
        pokemon_jugador = self.batalla.pokemon_actual1.name
        pokemon_ia = self.batalla.pokemon_actual2.name
        nombre_mov_jugador = self.batalla.pokemon_actual1.movimientos[accion_jugador[1]].name if accion_jugador[0] == "ATACAR" else f"Cambio a {self.batalla.equipo1[accion_jugador[1]].name}"
        nombre_mov_ia = self.batalla.pokemon_actual2.movimientos[accion_ia[1]].name if accion_ia[0] == "ATACAR" else f"Cambio a {self.batalla.equipo2[accion_ia[1]].name}"
        
        self.procesar_logs(logs)

    def procesar_logs(self, logs):
        if logs:
            msg = logs.pop(0)
            
            self.escribir_mensaje(msg)
            self.actualizar_hud()
            self.parent.after(1200, lambda: self.procesar_logs(logs)) # Pausa de 1.2 segundos por mensaje
        else:
            guardar_equipos_en_json(self.ruta_equipos, self.batalla.equipo1, self.batalla.equipo2)
            self.menu_acciones.place(x=500, y=20) # Devolver los botones
            if not self._verificar_cambios_forzados():
                self.verificar_final()

    def verificar_final(self):
        resultado = self.batalla.juego_terminado()
        if resultado != 0:
            ganador = "¡GANASTE!" if resultado == 1 else "¡PERDISTE! Ganó la IA."
            if PYGAME_DISPONIBLE:
                try:
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.stop()
                except Exception as e:
                    print(f"Error deteniendo música: {e}")
            messagebox.showinfo("Fin del Combate", ganador)
            self.al_terminar() # Llama a la función de main.py para volver