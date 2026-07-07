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
index.html            # la app (self-contained; solo usa Google Fonts por CDN)
alpega_i18n.js        # TODO el texto ES/EN (fuente única de contenido)
audio_modales/es/*.mp3 # narración en español (118: 68 handbook + 50 seguridad)
audio_modales/en/*.mp3 # narración en inglés (118: 68 handbook + 50 seguridad)
guiones_seguridad.md   # guiones de narración del laboratorio (x1–x50, ES/EN)
```

> El **laboratorio 05 · Ciberseguridad** (`x1`–`x50`) está completo: diagrama, playlist y narración. Los audios de seguridad se generaron con voz `es-US-AlonsoNeural` (ES) / `en-US-AndrewNeural` (EN), el EQ del canal y cama de música al 10%, normalizados a −24.5 LUFS para igualar los 68 del handbook.

## Uso

Abrir `index.html` en el navegador → elegir idioma → explorar. Se puede publicar tal cual con **GitHub Pages** (raíz del repo, rama `main`).

## Regenerar contenido / audios

Los textos viven en `alpega_i18n.js`. La narración se extrae de ese archivo y se genera con un pipeline TTS (edge-tts → clonado de voz OpenVoice → EQ + cama de música). Editar el texto, re-extraer y regenerar el audio del `id` correspondiente.
