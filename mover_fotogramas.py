#!/usr/bin/env python3
"""Lleva los fotogramas que guardó extraer_fotogramas.js (en videos/ del proyecto) a fotogramas/<nombre>/."""
import glob, os, shutil, sys

ORIGEN = sys.argv[1] if len(sys.argv) > 1 else '../spain-simulator/videos'
for meta in glob.glob(os.path.join(ORIGEN, 'panel__*__meta.json')):
    nombre = os.path.basename(meta).split('__')[1]
    dst = os.path.join('fotogramas', nombre)
    os.makedirs(dst, exist_ok=True)
    n = 0
    for f in glob.glob(os.path.join(ORIGEN, f'panel__{nombre}__*')):
        destino = os.path.join(dst, 'meta.json' if f.endswith('meta.json') else os.path.basename(f).split('__')[2])
        shutil.move(f, destino); n += 1
    print(f'{nombre}: {n - 1} fotogramas -> {dst}/')
