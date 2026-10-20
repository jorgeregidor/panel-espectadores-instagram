#!/usr/bin/env python3
"""Compara lo que predice el panel con lo que pasó de verdad en los vídeos ya publicados.

Lee resultados/<video>/metricas.json (de panel.py) y datos_reales.json, y calcula si el panel ORDENA los vídeos
igual que la realidad (correlación de rangos de Spearman). Si no los ordena bien, el panel no sirve.
"""
import json, os

def rangos(xs):
    orden = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0] * len(xs)
    for pos, i in enumerate(orden): r[i] = pos
    return r

def spearman(a, b):
    n = len(a)
    if n < 3: return None
    ra, rb = rangos(a), rangos(b)
    d2 = sum((x - y) ** 2 for x, y in zip(ra, rb))
    return 1 - 6 * d2 / (n * (n * n - 1))

import subprocess

# Los datos reales viven en el proyecto del estudio (rama main): ../spain-simulator/metricas/videos.json
EDITOR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'spain-simulator')
def cargar_reales():
    subprocess.run(['git', '-C', EDITOR, 'fetch', '-q', 'origin'], check=False)
    txt = subprocess.run(['git', '-C', EDITOR, 'show', 'origin/main:metricas/videos.json'], capture_output=True, text=True, check=True).stdout
    out = {}
    for k, v in json.loads(txt)['videos'].items():
        ig, yt = v.get('instagram', {}), v.get('youtube', {})
        dur = v.get('duracion')
        out[k] = {'omision_ig': ig.get('omision'),
                  'medio_pct_ig': (ig['tiempo_medio'] / dur) if ig.get('tiempo_medio') and dur else None,
                  'quedaron_yt': yt.get('quedaron'), 'curva_yt': yt.get('curva')}
    return out

real = cargar_reales()
pred = {}
for k in real:
    p = os.path.join('resultados', k, 'metricas.json')
    if os.path.exists(p): pred[k] = json.load(open(p))

print(f'Vídeos con panel y datos reales: {len(pred)}\n')
print(f"{'vídeo':<20}{'omisión real':>14}{'panel':>8}{'t. medio real':>15}{'panel':>8}{'YT real':>9}{'panel':>8}")
for k, m in pred.items():
    r = real[k]
    f = lambda x: '—' if x is None else f'{x * 100:.0f} %'
    print(f"{k:<20}{f(r['omision_ig']):>14}{f(m['omision']):>8}{f(r['medio_pct_ig']):>15}{f(m['medio_pct']):>8}"
          f"{f(r['quedaron_yt']):>9}{f(1 - m['omision']):>8}")

print()
for nombre, real_k, pred_f in [('Omisión (Instagram)', 'omision_ig', lambda m: m['omision']),
                               ('Tiempo medio (Instagram)', 'medio_pct_ig', lambda m: m['medio_pct']),
                               ('Se quedaron viendo (YouTube)', 'quedaron_yt', lambda m: 1 - m['omision'])]:
    pares = [(real[k][real_k], pred_f(m)) for k, m in pred.items() if real[k][real_k] is not None]
    s = spearman([a for a, _ in pares], [b for _, b in pares])
    veredicto = 'sin datos suficientes' if s is None else ('ORDENA BIEN' if s >= 0.6 else 'regular' if s >= 0.3 else 'NO SIRVE')
    print(f"{nombre:<30} Spearman = {'—' if s is None else f'{s:+.2f}'}  ({len(pares)} vídeos)  → {veredicto}")
print('\n(+1 = ordena los vídeos exactamente como la realidad; 0 = al azar; −1 = al revés)')
