# Changelog PokeFISI

## [En desarrollo]

### Agregado
- **Sistema de logging en consola**: Ahora se muestran todos los movimientos del jugador y de la IA en la consola durante la batalla.
  - Formato de turno: muestra el número de turno y los nombres de los Pokémon enfrentado
  - Acciones del jugador: prefijadas con "▶"
  - Acciones de la IA: prefijadas con "◀"
  - Otros mensajes: prefijados con "•"
  - Ubicación: `src/battle_ui.py` (funciones `ejecutar_turno` y `procesar_logs`)

### Cómo usar
Para ver los logs, ejecutar el juego desde terminal:
```bash
python src/main.py
```

---

## [Versiones anteriores]
- Sin registro aún