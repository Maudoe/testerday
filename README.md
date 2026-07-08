# Testerday — Alpega QA: Casos & Soluciones

Diagrama interactivo y bilingüe (🇪🇸 Español / 🇬🇧 English) de casos y soluciones de QA Automation para un TMS (Transportation Management Software), pensado como material de estudio para entrevista.

## Qué incluye

- **Recorrido e2e del TMS** (8 etapas) + problemas comunes de **logística**, **API**, **Selenium/automation**, **20 queries SQL** y un **laboratorio de ciberseguridad con 50 casos** (amenazas → capas de defensa y oportunidades de mejora: QR firmado, liveness anti-deepfake, aislamiento de tenant, MITM, GPS/VPN spoofing, inyección, fraude de flete, disponibilidad, móvil, privacidad).
- Cada tarjeta abre un panel con: **En simple** (explicación llana), **Caso/problema**, **Solución** (ampliada) y **Cómo lo prueba el tester**, con código donde aplica.
- **Narración por modal con voz + música** en ambos idiomas: cada paso tiene su audio que lee exactamente lo que muestra.
- **Playlist lateral** para reproducir todo de corrido; el nodo que suena se **resalta en dorado** en el diagrama.
- Estética oscura con FX (glow del cursor, órbitas, parallax 3D al scrollear).

## Estructura

```
index.html             # la app (self-contained; solo usa Google Fonts por CDN)
alpega_i18n.js         # TODO el texto ES/EN (fuente única de contenido)
audio_modales/es/*.mp3 # narración en español (118: 68 handbook + 50 seguridad)
audio_modales/en/*.mp3 # narración en inglés (118: 68 handbook + 50 seguridad)
guiones_seguridad.md   # guiones de narración del laboratorio (x1–x50, ES/EN)
assets/music/*.mp3     # cama de música (cyberpunk) del laboratorio de seguridad
pipeline/gen_audio.py  # generador de audios (TTS → clon de voz → EQ → música)
pipeline/dump_cyb.js   # extrae los 50 casos de alpega_i18n.js a cyb.json
```

> El **laboratorio 05 · Ciberseguridad** (`x1`–`x50`) está completo: diagrama, playlist y narración. Los audios de seguridad usan la **misma voz clonada** que el handbook (Alonso ES / Andrew EN → OpenVoice), el EQ del canal, cama de música cyberpunk de `assets/music/` (rotada por caso, al 10%), normalizados a **−24.5 LUFS** para igualar los 68 del handbook.

## Uso

Abrir `index.html` en el navegador → elegir idioma → explorar. Se puede publicar tal cual con **GitHub Pages** (raíz del repo, rama `main`).

## Regenerar los audios (pipeline con voz clonada)

Los textos viven en `alpega_i18n.js`. El pipeline es: **edge-tts → clon de voz OpenVoice → EQ del canal → cama de música → loudnorm**. La voz clonada es lo que hace que todos los audios suenen igual.

### Requisitos (una vez)
- **Python 3.10**, con `edge-tts`, `torch` (CUDA recomendado), `librosa`, `soundfile`, `wavmark`.
- **ffmpeg / ffprobe** en el PATH (o ajustar las rutas al inicio de `pipeline/gen_audio.py`).
- **OpenVoice** (ToneColorConverter). Rutas que espera el script (editables en su cabecera):
  - `OPENVOICE_PATH` → repo de OpenVoice (módulo `openvoice.api`).
  - `CKPT_PATH` → `.../openvoice_checkpoints/converter/` con `config.json` + `checkpoint.pth`.
  - `VOICE_REF` → **voz de referencia** a clonar (`reference_voice_en.wav`, ~3 min, 44.1 kHz). **Este WAV es "la voz" del canal** — para que un audio suene igual, cloná siempre contra el mismo archivo.

### Parámetros clave (cabecera de `gen_audio.py`)
- `VOICE_ES = es-US-AlonsoNeural` · `VOICE_EN = en-US-AndrewNeural` · `RATE=+0%` · `PITCH=+0Hz` (voz base antes del clon).
- `EQ_FILTER` = highpass 80 · lowshelf 180 +3 · dips en 6.5k/8k · volume 1.6.
- `MUSIC_DIR = assets/music` · `MUSIC_VOL = 0.10` (10%); el track **rota por número de caso**.
- Loudnorm final: `I=-24.5 : TP=-8 : LRA=7` (target medido en los 68 audios originales).
- Correcciones de **pronunciación** en `SUB_ES` (p. ej. `payload → péilod`, `QR → cu-erre`, `deepfake → dipféik`). Agregar ahí cualquier término que suene mal.
- Flags por entorno: `CLONE=1` (clon on), `MUSIC=1`, `RESUME=1` (saltea los ya generados), `VOICE_ES`, `MUSIC_DIR`.

### Pasos
```bash
cd pipeline
node dump_cyb.js cyb.json                 # 1) extrae los 50 casos a cyb.json
python gen_audio.py                        # 2) genera los 100 (x1–x50 ES+EN) + guiones_seguridad.md
python gen_audio.py x3 x7                   # (opcional) regenerar solo algunos casos
RESUME=1 python gen_audio.py                # (opcional) retomar sin rehacer lo existente
```
Luego, para encender los players de casos nuevos: agregar sus `id` (`x1…x50`) al array `ALLIDS` en `index.html`.

> El paso de clonación carga el modelo **una sola vez** y convierte cada narración cruda (edge-tts) al timbre de `VOICE_REF`; en GPU son ~2.5 s por audio. Con `CLONE=0` se omite y queda la voz base sin clonar (útil para pruebas rápidas).
