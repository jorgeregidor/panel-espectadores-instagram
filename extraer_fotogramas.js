// Extrae fotogramas de un escenario del estudio de SimuladorZero para el panel de espectadores.
// Se pega en la consola del estudio (http://localhost:8765) y guarda en videos/ (fuera de git):
//   panel__<nombre>__000.jpg ... y panel__<nombre>__meta.json
// Después: python3 mover_fotogramas.py (los lleva a fotogramas/<nombre>/).
// No toca nada del proyecto: solo lee los escenarios y dibuja.
//
// Uso: await panelFotogramas('eclipse-2026', 'eclipse-2026', { /* cambios al escenario, opcional */ })
window.panelFotogramas = async (escenario, nombre, cambios = {}, paso = 0.5) => {
  const { SCENARIOS } = await import('/js/core/scenarios.js');
  const { Player } = await import('/js/core/sim.js');
  const sc = JSON.parse(JSON.stringify(SCENARIOS.find(s => s.id === escenario)));
  delete sc.episode;
  Object.assign(sc, cambios);
  const pl = await sim.prepare(sc);
  const pr = new Player(pl, { fps: 30, labels: true });
  const W = 360, H = 640;
  const big = new OffscreenCanvas(1080, 1920), bx = big.getContext('2d');
  const sm = new OffscreenCanvas(W, H), sx = sm.getContext('2d', { willReadFrequently: true });
  const dur = pr.total / 30, frames = [];
  let prev = null;
  for (let t = 0, i = 0; t <= dur + 1e-6; t += paso, i++) {
    const f = Math.min(pr.total - 1, Math.round(t * 30));
    for (let k = Math.max(0, f - 14); k < f; k += 3) pr.render(bx, k);   // que los efectos "lleguen" al fotograma
    pr.render(bx, f);
    sx.drawImage(big, 0, 0, W, H);
    // cambio de imagen respecto al fotograma anterior (zona del mapa): 0 = idéntico, 1 = todo distinto
    const d = sx.getImageData(0, Math.round(H * 0.27), W, Math.round(H * 0.45)).data;
    let cambio = 0;
    if (prev) { let s = 0; for (let j = 0; j < d.length; j += 4) s += Math.abs(d[j] - prev[j]) + Math.abs(d[j + 1] - prev[j + 1]) + Math.abs(d[j + 2] - prev[j + 2]); cambio = s / (d.length / 4) / 765; }
    prev = d;
    const file = `panel__${nombre}__${String(i).padStart(3, '0')}.jpg`;
    await fetch('/api/save?name=' + file, { method: 'POST', body: await sm.convertToBlob({ type: 'image/jpeg', quality: 0.8 }) });
    frames.push({ t: +t.toFixed(1), file: file.split('__')[2], cambio: +cambio.toFixed(4) });
  }
  const meta = { titulo: (sc.title || '').replace(/\*/g, ''), duracion: +dur.toFixed(1), sonido: 'música de fondo, sin voz', frames };
  await fetch(`/api/save?name=panel__${nombre}__meta.json`, { method: 'POST', body: JSON.stringify(meta) });
  return `${frames.length} fotogramas de ${nombre}`;
};
