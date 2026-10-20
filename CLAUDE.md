# Panel de espectadores — instrucciones para el chat

Esta carpeta es independiente del proyecto `spain-simulator` (no se modifica nada de allí).
Sirve para pasar un vídeo por 100 espectadores simulados usando **subagentes del chat** (sin API ni claves).

## Cuando el usuario pida "pasa el vídeo X por el panel"

1. Si no hay `fotogramas/X/`: en el estudio de la versión `main` (navegador), pegar `extraer_fotogramas.js` y ejecutar
   `await panelFotogramas('<escenario>', 'X')`; luego `python3 mover_fotogramas.py`.
2. `python3 tramos_muertos.py fotogramas/X` (gratis, sin IA) y comentar los tramos muertos.
3. `python3 panel.py preparar fotogramas/X` → crea 4 lotes de 25 espectadores (modo barato: 1 fotograma por segundo
   pasados los 3 primeros).
4. Lanzar **un subagente por lote** con `model: "sonnet"` (más barato; tipo general-purpose, en segundo plano;
   máximo 20 a la vez) con el texto del lote
   tal cual como prompt. Cada uno lee los fotogramas y escribe `resultados/X/respuestas/lote_NN.json`.
   No dar a los subagentes ningún contexto del proyecto: la gracia es que vean el vídeo "en frío".
5. Cuando terminen: `python3 panel.py juntar resultados/X` y enseñar `resultados/X/resumen.md`.
6. Para saber si el panel es fiable: pasar los vídeos ya publicados (datos reales en `../spain-simulator`, rama `main`, `metricas/videos.json`; se apuntan allí, nunca aquí) y ejecutar
   `python3 calibrar.py`. Solo si ordena bien los vídeos reales, usarlo para decidir.

Nunca usar worktrees.
