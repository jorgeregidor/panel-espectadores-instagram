# Panel de espectadores (SimuladorZero)

Carpeta aparte del proyecto: no toca `spain-simulator`. Sirve para "enseñar" un vídeo a 100 espectadores simulados
(subagentes de un chat de Claude Code, sin API) antes de publicarlo y ver en qué segundo se irían, qué les engancha y si lo compartirían.

## Piezas

| Archivo | Qué hace | ¿Cuesta? |
|---|---|---|
| `extraer_fotogramas.js` | En el estudio, dibuja el vídeo cada 0,5 s (360×640) y mide cuánto cambia la imagen | No |
| `mover_fotogramas.py` | Lleva esos fotogramas de `../spain-simulator/videos/` a `fotogramas/<vídeo>/` | No |
| `tramos_muertos.py` | Avisa de tramos en los que la imagen casi no cambia (sin IA) | No |
| `personas.py` | Crea 100 espectadores parecidos al público real (hombres 25–34, España, no seguidores…) | No |
| `panel.py` | `preparar`: crea 10 lotes de 10 espectadores; `juntar`: junta las respuestas y saca la curva | No |
| `CLAUDE.md` | Instrucciones para el chat: lanza un subagente por lote | Usa tu plan de Claude |
| `calibrar.py` | Compara el panel con los datos reales de vídeos ya publicados | No |
| (datos reales) | Se leen de `../spain-simulator` rama `main`, `metricas/videos.json`: la única fuente | — |

## Cómo se usa

1. **Fotogramas** (en el estudio con la versión de `main`): `await panelFotogramas('eclipse-2026', 'eclipse-2026')`
   y luego `python3 mover_fotogramas.py`.
2. **Gratis:** `python3 tramos_muertos.py fotogramas/eclipse-2026`
3. **Panel:** en un chat de Claude Code abierto en esta carpeta, pedir "pasa el vídeo X por el panel"
   (sigue `CLAUDE.md`) → `resultados/X/resumen.md`
4. **Calibración** (después de pasar los vídeos ya publicados): `python3 calibrar.py`

## Requisitos

Ninguno aparte de Python 3 y Claude Code: no hace falta API ni claves.

## Ojo

- Es una **aproximación**: la IA no se aburre de verdad y ve fotogramas, no movimiento ni música. Solo vale para
  **comparar** versiones y detectar fallos (arranque confuso, tramos muertos, final flojo) si `calibrar.py` dice que
  ordena bien los vídeos ya publicados.
- Los vídeos antiguos se regeneran con el escenario actual, que puede no ser idéntico a lo que se publicó
  (títulos, pausas iniciales…). Para la calibración es suficiente, pero conviene tenerlo en cuenta.
- Cada vídeo son 10 subagentes que leen ~50 imágenes cada uno: gasta uso de tu plan de Claude.
