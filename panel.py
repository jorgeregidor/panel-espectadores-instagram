#!/usr/bin/env python3
"""Panel de espectadores sintéticos, para lanzarlo desde un chat de Claude Code (sin API).

  python3 panel.py preparar fotogramas/<video> [--n 100] [--grupo 10]
      Crea resultados/<video>/lotes/lote_XX.md: cada lote es el encargo de UN subagente (10 espectadores).
  (en el chat) se lanza un subagente por lote con el texto del lote; cada uno escribe resultados/<video>/respuestas/lote_XX.json
  python3 panel.py juntar resultados/<video>
      Junta las respuestas: curva de retención, métricas y resumen.md.

Ver CLAUDE.md (instrucciones para el chat) y LEEME.md.
"""
import argparse, glob, json, os, statistics, sys

from personas import generar

AQUI = os.path.dirname(os.path.abspath(__file__))

INSTRUCCIONES = """Eres un simulador de comportamiento de espectadores de vídeos cortos verticales (Reels, Shorts, TikTok).
NO sabes nada de quién hizo el vídeo ni de para qué es: solo ves lo que verías en el móvil.

Vas a encarnar, uno por uno, a {k} espectadores distintos (abajo). Para cada uno decide, con honestidad y sin
cortesía, cómo reaccionaría de verdad. Ten en cuenta cómo se ven los Reels en la realidad:
- La mayoría de la gente desliza en los primeros 1-3 segundos si no entiende de qué va o no ve nada que le enganche.
- Un tramo en el que la imagen apenas cambia hace que la gente se vaya, aunque el tema le interese.
- Un final largo sin novedad hace que se vaya antes de acabar.
- Ver el vídeo entero es lo menos habitual; compartir o guardar es raro y solo pasa con un motivo claro
  (le toca de cerca, le sorprende, quiere enseñárselo a alguien).
- Cada espectador es distinto: no repitas la misma respuesta para todos.

EL VÍDEO: «{titulo}», {duracion:.1f} s, {sonido}.
Mira EN ORDEN con la herramienta Read estos fotogramas (están en {carpeta}; el nombre es el número de fotograma y
t = número × 0,5 s): {lista}
({nimg} imágenes; en los 3 primeros segundos van cada medio segundo y después más espaciados). Míralos todos.

LOS ESPECTADORES:
{personas}

RESPUESTA: escribe con la herramienta Write el archivo {salida} con una lista JSON de {k} objetos (uno por
espectador, en el mismo orden), cada uno con exactamente estos campos:
  "id": número del espectador,
  "lo_ve_entero": true/false,
  "segundo_salida": segundo en que desliza (si lo ve entero, {duracion:.1f}),
  "motivo_salida": por qué se va o por qué se queda hasta el final (una frase),
  "primera_impresion": qué piensa en el primer segundo (una frase),
  "momento_mas_flojo": segundo más aburrido o confuso de lo que ha visto,
  "momento_mas_fuerte": segundo que más le ha enganchado de lo que ha visto,
  "guardaria": true/false, "compartiria": true/false,
  "comentario": lo que escribiría en comentarios, o "" si no comentaría.
No escribas nada más en el archivo. Cuando termines, responde solo "hecho".
"""


def preparar(carpeta, n, grupo, cada=1):
    carpeta = os.path.abspath(carpeta)
    meta = json.load(open(os.path.join(carpeta, 'meta.json'), encoding='utf-8'))
    nombre = os.path.basename(carpeta.rstrip('/'))
    dst = os.path.join(AQUI, 'resultados', nombre)
    os.makedirs(os.path.join(dst, 'lotes'), exist_ok=True)
    os.makedirs(os.path.join(dst, 'respuestas'), exist_ok=True)
    for viejo in glob.glob(os.path.join(dst, 'lotes', 'lote_*.md')): os.remove(viejo)   # lotes de una preparación anterior
    gente = generar(n)
    json.dump({'video': nombre, 'meta': meta, 'personas': gente}, open(os.path.join(dst, 'panel.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    # modo barato: los 3 primeros segundos completos (ahí se decide casi todo) y luego 1 de cada `cada`
    frames = [f['file'] for k, f in enumerate(meta['frames']) if f['t'] <= 3 or k % cada == 0 or k == len(meta['frames']) - 1]
    lotes = [gente[i:i + grupo] for i in range(0, n, grupo)]
    for k, lote in enumerate(lotes, 1):
        salida = os.path.join(dst, 'respuestas', f'lote_{k:02d}.json')
        txt = INSTRUCCIONES.format(k=len(lote), titulo=meta.get('titulo', ''), duracion=meta['duracion'],
                                   sonido=meta.get('sonido', 'música de fondo'), carpeta=carpeta,
                                   lista=', '.join(frames), nimg=len(frames),
                                   personas='\n'.join(f"[{p['id']}] {p['texto']}" for p in lote), salida=salida)
        open(os.path.join(dst, 'lotes', f'lote_{k:02d}.md'), 'w', encoding='utf-8').write(txt)
    print(f'{nombre}: {len(lotes)} lotes de {grupo} espectadores en {dst}/lotes/')


def juntar(dst):
    dst = os.path.abspath(dst)
    panel = json.load(open(os.path.join(dst, 'panel.json'), encoding='utf-8'))
    meta, gente = panel['meta'], {p['id']: p for p in panel['personas']}
    D = meta['duracion']
    validas = []
    for f in sorted(glob.glob(os.path.join(dst, 'respuestas', 'lote_*.json'))):
        try:
            for r in json.load(open(f, encoding='utf-8')):
                if r.get('id') in gente: validas.append({'persona': gente[r['id']], 'r': r})
        except Exception as e:
            print('lote ilegible:', f, e)
    n = len(validas)
    if not n: sys.exit('No hay respuestas todavía.')
    sal = [D if f['r']['lo_ve_entero'] else min(D, float(f['r']['segundo_salida'])) for f in validas]
    pasos = [round(i * 0.5, 1) for i in range(int(D * 2) + 1)]
    curva = [(t, sum(1 for s in sal if s > t) / n) for t in pasos]
    with open(os.path.join(dst, 'curva.csv'), 'w') as f:
        f.write('segundo,porcentaje_viendo\n')
        for t, p in curva: f.write(f'{t},{p * 100:.1f}\n')
    om = sum(1 for s in sal if s < 3) / n
    ent = sum(1 for f in validas if f['r']['lo_ve_entero']) / n
    med = statistics.mean(sal)
    comp = sum(1 for f in validas if f['r']['compartiria']) / n
    guar = sum(1 for f in validas if f['r']['guardaria']) / n
    hist = lambda xs: sorted(((s, xs.count(s)) for s in set(xs)), key=lambda x: -x[1])[:5]
    flojos = [round(float(f['r']['momento_mas_flojo'])) for f in validas]
    fuertes = [round(float(f['r']['momento_mas_fuerte'])) for f in validas]
    L = [f"# Panel de espectadores: {panel['video']}", '', f'{n} espectadores · vídeo de {D:.1f} s', '',
         '| Métrica | Valor | Equivalente real |', '|---|---|---|',
         f'| Se van en los 3 primeros segundos | {om * 100:.0f} % | tasa de omisión de Instagram |',
         f'| Se quedan pasados los 3 s | {(1 - om) * 100:.0f} % | "se quedaron viendo" de YouTube |',
         f'| Tiempo medio | {med:.1f} s ({med / D * 100:.0f} %) | tiempo medio de Instagram |',
         f'| Lo ven entero | {ent * 100:.0f} % | "vieron el vídeo completo" de TikTok |',
         f'| Lo compartirían | {comp * 100:.0f} % | |', f'| Lo guardarían | {guar * 100:.0f} % | |', '',
         '## Curva de retención', '```']
    L += [f'{t:5.1f} s  {"█" * round(p * 40):<40} {p * 100:4.0f} %' for t, p in curva[::2]]
    L += ['```', '', '## Dónde se aburren (segundo más flojo)', ', '.join(f'{s} s ({c})' for s, c in hist(flojos)),
          '', '## Qué engancha (segundo más fuerte)', ', '.join(f'{s} s ({c})' for s, c in hist(fuertes)),
          '', '## Por qué se van']
    for f in sorted([f for f in validas if not f['r']['lo_ve_entero']], key=lambda f: float(f['r']['segundo_salida']))[:25]:
        L.append(f"- {float(f['r']['segundo_salida']):.1f} s · {f['persona']['edad']} años, {f['persona']['lugar']}: {f['r']['motivo_salida']}")
    L += ['', '## Primeras impresiones (10)'] + [f"- {f['r']['primera_impresion']}" for f in validas[::max(1, n // 10)][:10]]
    L += ['', '## Comentarios que escribirían'] + [f"- «{f['r']['comentario'].strip()}»" for f in validas if f['r']['comentario'].strip()][:15]
    open(os.path.join(dst, 'resumen.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    json.dump({'n': n, 'omision': om, 'medio': med, 'medio_pct': med / D, 'entero': ent, 'compartir': comp, 'guardar': guar},
              open(os.path.join(dst, 'metricas.json'), 'w'), indent=1)
    print('\n'.join(L[:20]))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('accion', choices=['preparar', 'juntar'])
    ap.add_argument('carpeta')
    ap.add_argument('--n', type=int, default=100)
    ap.add_argument('--grupo', type=int, default=25, help='espectadores por subagente (más = menos subagentes = más barato)')
    ap.add_argument('--cada', type=int, default=2, help='pasados 3 s, 1 fotograma de cada N (2 = uno por segundo)')
    a = ap.parse_args()
    preparar(a.carpeta, a.n, a.grupo, a.cada) if a.accion == 'preparar' else juntar(a.carpeta)
