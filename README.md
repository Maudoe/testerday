# Testerday — Alpega QA: Casos & Soluciones

Diagrama interactivo y bilingüe (🇪🇸 Español / 🇬🇧 English) de casos y soluciones de QA Automation para un TMS (Transportation Management Software), pensado como material de estudio para entrevista.

## Qué incluye

- **Recorrido e2e del TMS** (8 etapas) + problemas comunes de **logística**, **API**, **Selenium/automation** y **20 queries SQL**.
- Cada tarjeta abre un panel con: **En simple** (explicación llana), **Caso/problema**, **Solución** (ampliada) y **Cómo lo prueba el tester**, con código donde aplica.
- **Narración por modal con voz + música** en ambos idiomas: cada paso tiene su audio que lee exactamente lo que muestra.
- **Playlist lateral** para reproducir todo de corrido; el nodo que suena se **resalta en dorado** en el diagrama.
- Estética oscura con FX (glow del cursor, órbitas, parallax 3D al scrollear).

## Estructura

```
index.html            # la app (self-contained; solo usa Google Fonts por CDN)
alpega_i18n.js        # TODO el texto ES/EN (fuente única de contenido)
audio_modales/es/*.mp3 # narración en español (68)
audio_modales/en/*.mp3 # narración en inglés (68)
```

## Uso

Abrir `index.html` en el navegador → elegir idioma → explorar. Se puede publicar tal cual con **GitHub Pages** (raíz del repo, rama `main`).

## Regenerar contenido / audios

Los textos viven en `alpega_i18n.js`. La narración se extrae de ese archivo y se genera con un pipeline TTS (edge-tts → clonado de voz OpenVoice → EQ + cama de música). Editar el texto, re-extraer y regenerar el audio del `id` correspondiente.
