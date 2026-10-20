#!/usr/bin/env python3
"""Detector gratis (sin IA) de tramos muertos: avisa de los tramos en los que la imagen del mapa apenas cambia.

Uso: python3 tramos_muertos.py fotogramas/<video> [--umbral 0.004] [--minimo 1.5]
Usa el valor "cambio" que mide extraer_fotogramas.js entre cada fotograma y el anterior (0 = idéntico).
"""
import argparse, json, os

ap = argparse.ArgumentParser()
ap.add_argument('carpeta')
ap.add_argument('--umbral', type=float, default=0.004, help='por debajo, se considera que "no pasa nada"')
ap.add_argument('--minimo', type=float, default=1.5, help='segundos seguidos para avisar')
a = ap.parse_args()
meta = json.load(open(os.path.join(a.carpeta, 'meta.json'), encoding='utf-8'))
fr = meta['frames']
print(f"{os.path.basename(a.carpeta.rstrip('/'))}: {meta['duracion']} s\n")
for f in fr:
    print(f"{f['t']:5.1f} s  {'▇' * min(50, round(f['cambio'] * 2000)):<50} {f['cambio']:.4f}")
muertos, ini = [], None
for f in fr[1:] + [{'t': meta['duracion'] + 1, 'cambio': 1}]:
    if f['cambio'] < a.umbral:
        ini = f['t'] if ini is None else ini
    elif ini is not None:
        if f['t'] - ini >= a.minimo: muertos.append((ini, f['t']))
        ini = None
print()
if muertos:
    for i, j in muertos: print(f'⚠️  Tramo muerto: de {i:.1f} s a {j:.1f} s ({j - i:.1f} s sin cambios apreciables)')
else:
    print('✅ Sin tramos muertos.')
