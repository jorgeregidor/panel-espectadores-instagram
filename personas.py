"""Genera N espectadores sintéticos parecidos al público real de SimuladorZero.

Base (datos reales de Instagram, oct 2026): sobre todo hombres de 25 a 34 años, en España; el 96 % de las vistas
de un Reel son de no seguidores que llegan desde la pestaña Reels o Explorar.
Cada persona es reproducible (misma semilla -> mismas personas) para poder comparar vídeos entre sí.
"""
import random

EDADES = [(18, 24, 0.20), (25, 34, 0.50), (35, 44, 0.22), (45, 60, 0.08)]
GENERO = [('hombre', 0.78), ('mujer', 0.22)]
# reparto aproximado por población (las grandes pesan más)
LUGARES = [
    ('Madrid', 'ciudad grande', 14), ('Barcelona', 'ciudad grande', 12), ('Valencia', 'ciudad mediana', 6),
    ('Sevilla', 'ciudad mediana', 6), ('Málaga', 'ciudad mediana', 4), ('Zaragoza', 'ciudad mediana', 3),
    ('Bilbao', 'ciudad mediana', 3), ('Murcia', 'ciudad mediana', 3), ('A Coruña', 'ciudad mediana', 2),
    ('Valladolid', 'ciudad mediana', 2), ('Alicante', 'ciudad mediana', 3), ('Granada', 'ciudad mediana', 2),
    ('Palma', 'ciudad mediana', 2), ('Las Palmas', 'ciudad mediana', 2), ('Oviedo', 'ciudad mediana', 2),
    ('un pueblo de Soria', 'pueblo', 2), ('un pueblo de Jaén', 'pueblo', 3), ('un pueblo de Lugo', 'pueblo', 2),
    ('un pueblo de Cáceres', 'pueblo', 2), ('un pueblo de Teruel', 'pueblo', 1), ('un pueblo de Toledo', 'pueblo', 3),
    ('una ciudad dormitorio de Madrid', 'periferia', 6), ('una ciudad dormitorio de Barcelona', 'periferia', 5),
]
ESTILOS = [
    ('desliza muy rápido: si en 1-2 segundos no pasa algo que le llame la atención, se va', 0.35),
    ('ritmo normal: da 2-3 segundos de margen; si entiende de qué va y le interesa, sigue', 0.40),
    ('curioso: si el tema le engancha lo ve entero, pero se va en cuanto algo se repite o se alarga', 0.25),
]
INTERESES = ['fútbol', 'videojuegos', 'mapas y geografía', 'historia', 'ciencia y espacio', 'actualidad y noticias',
             'memes', 'coches', 'gimnasio', 'viajes', 'política', 'series', 'música', 'tecnología', 'naturaleza',
             'curiosidades', 'crypto e inversión', 'cocina']
CONTEXTOS = ['en el sofá por la noche', 'en el metro o el autobús', 'en un descanso del trabajo',
             'en la cama antes de dormir', 'esperando en una cola', 'en el baño']
SONIDO = [('con el sonido quitado', 0.6), ('con sonido', 0.4)]


def _pick(rng, opciones):
    total = sum(w for *_, w in opciones)
    r = rng.random() * total
    for *v, w in opciones:
        r -= w
        if r <= 0:
            return v[0] if len(v) == 1 else tuple(v)
    return opciones[-1][0]


def generar(n=100, semilla=7):
    rng = random.Random(semilla)
    gente = []
    for i in range(n):
        a, b = _pick(rng, [((x, y), w) for x, y, w in EDADES])
        edad = rng.randint(a, b)
        genero = _pick(rng, GENERO)
        lugar, tipo = _pick(rng, [((l, t), w) for l, t, w in LUGARES])
        estilo = _pick(rng, ESTILOS)
        intereses = rng.sample(INTERESES, 3)
        contexto = rng.choice(CONTEXTOS)
        sonido = _pick(rng, SONIDO)
        texto = (f"Eres {'un hombre' if genero == 'hombre' else 'una mujer'} de {edad} años que vive en {lugar} ({tipo}). "
                 f"Te interesan {intereses[0]}, {intereses[1]} y {intereses[2]}. Estás pasando Reels {contexto}, {sonido}. "
                 f"No sigues a esta cuenta: te ha salido en la pestaña Reels entre otros vídeos. "
                 f"Tu forma de ver Reels: {estilo}.")
        gente.append({'id': i + 1, 'edad': edad, 'genero': genero, 'lugar': lugar, 'tipo': tipo,
                      'estilo': estilo, 'intereses': intereses, 'contexto': contexto, 'sonido': sonido, 'texto': texto})
    return gente


if __name__ == '__main__':
    for p in generar(5):
        print(p['texto'], '\n')
