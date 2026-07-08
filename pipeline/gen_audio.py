#!/usr/bin/env python3
# Genera guiones + audios (edge-tts -> ffmpeg 44.1k estereo + cama de musica sutil)
# para los casos de ciberseguridad x1..x50 del laboratorio testerday.
import json, os, re, subprocess, sys, html

SP   = os.path.dirname(os.path.abspath(__file__))
FFMPEG = r"C:\Users\ASUS\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"
EDGE = r"C:\Users\ASUS\AppData\Local\Programs\Python\Python310\Scripts\edge-tts.exe"
OUT_ES = r"E:\testerday\audio_modales\es"
OUT_EN = r"E:\testerday\audio_modales\en"

# === config replicada de E:\lost_histories\pipeline\config.py ===
VOICE_ES = os.environ.get("VOICE_ES", "es-US-AlonsoNeural")   # voz oficial ES del canal
VOICE_EN = os.environ.get("VOICE_EN", "en-US-AndrewNeural")   # voz oficial EN del canal
RATE     = os.environ.get("RATE", "+0%")
PITCH    = os.environ.get("PITCH", "+0Hz")
EQ_FILTER = "highpass=f=80,lowshelf=f=180:g=3,equalizer=f=6500:t=q:w=1.5:g=-4,equalizer=f=8000:t=q:w=1:g=-3,volume=1.6"
MUSIC     = os.environ.get("MUSIC", "1") == "1"
MUSIC_VOL = float(os.environ.get("MUSIC_VOL", "0.10"))        # 10% de la narracion
MUSIC_DIR = os.environ.get("MUSIC_DIR", r"E:\testerday\assets\music")
FFPROBE = FFMPEG.replace("ffmpeg.exe", "ffprobe.exe")
TRACKS = sorted(os.path.join(MUSIC_DIR, f) for f in os.listdir(MUSIC_DIR)
                if f.lower().endswith(".mp3")) if os.path.isdir(MUSIC_DIR) else []

# === clonacion de voz (OpenVoice) — para igualar la voz del handbook ===
CLONE      = os.environ.get("CLONE", "1") == "1"
OPENVOICE_PATH = r"D:/THAI_YT_CHANNEL/TTS-repo-lypsinc/tools/OpenVoice"
CKPT_PATH  = r"E:/lost_histories/models/openvoice_checkpoints/converter"
VOICE_REF  = r"E:/lost_histories/voice_reference/reference_voice_en.wav"
_CONV = {"c": None, "tgt": None}   # cache: modelo + speaker embedding destino

def _get_converter():
    if _CONV["c"] is None:
        sys.path.insert(0, OPENVOICE_PATH)
        import torch
        from openvoice.api import ToneColorConverter
        dev = "cuda" if torch.cuda.is_available() else "cpu"
        c = ToneColorConverter(os.path.join(CKPT_PATH, "config.json"), device=dev)
        c.load_ckpt(os.path.join(CKPT_PATH, "checkpoint.pth"))
        c.watermark_model = None
        _CONV["c"] = c
        _CONV["tgt"] = c.extract_se(VOICE_REF)   # timbre destino, una sola vez
        print("OpenVoice cargado (device: %s)" % dev)
    return _CONV["c"], _CONV["tgt"]

def clone_voice(raw_mp3, cloned_wav):
    c, tgt = _get_converter()
    src = c.extract_se(raw_mp3)
    c.convert(raw_mp3, src, tgt, output_path=cloned_wav, tau=1.0)
    return cloned_wav

# --- aclaracion de siglas/herramientas (tu estilo: "aclarar herramientas en el audio") ---
SUB_ES = [
    # --- pronunciacion de terminos ingleses (fonetica ES) ---
    (r"\bpayload\b", "péilod"), (r"\bpayloads\b", "péilods"),
    (r"\bQR\b", "cu-erre"), (r"\bdeepfake\b", "dipféik"), (r"\bdeepfakes\b", "dipféiks"),
    (r"\breplay\b", "riplói"), (r"\bliveness\b", "láivnes"), (r"\bwebhook\b", "webjúk"),
    (r"\bwebhooks\b", "webjúks"), (r"\bbackup\b", "bákap"), (r"\bbackups\b", "bákaps"),
    (r"\bscreenshot\b", "escrínshot"), (r"\bnonce\b", "nons"), (r"\bhash\b", "jash"),
    (r"\bjailbreak\b", "yeilbréik"), (r"\bgeofence\b", "yioféns"), (r"\btoken\b", "tóken"),
    (r"\btokens\b", "tókens"), (r"\bfirmware\b", "fírmwer"), (r"\bmock\b", "mok"),
    # --- siglas/herramientas ---
    (r"\bMITM\b", "man in the midel"), (r"\bman-in-the-middle\b", "man in the midel"),
    (r"\bMFA\b", "doble factor de autenticacion"), (r"\bDoS\b", "denegacion de servicio"),
    (r"\bReDoS\b", "re-dos"), (r"\bPOD\b", "prueba de entrega"),
    (r"\bHMAC\b", "hache-mac"), (r"\bJWT\b", "token jota-doble-ve-te"),
    (r"\bTLS\b", "te-ele-ese"), (r"\bmTLS\b", "te-ele-ese mutuo"), (r"\bHSTS\b", "hache-ese-te-ese"),
    (r"\bIDOR\b", "aidor"), (r"\bGPS\b", "ge-pe-ese"), (r"\bVPN\b", "ve-pe-ene"),
    (r"\bOAuth2?\b", "o-aut"), (r"\bPKCE\b", "pi-ka-ce-e"), (r"\bRBAC\b", "control de acceso por roles"),
    (r"\bSCA\b", "analisis de dependencias"), (r"\bSBOM\b", "inventario de dependencias"),
    (r"\bCVE\b", "ce-ve-e"), (r"\bEDI\b", "e-di"), (r"\bXSS\b", "equis-ese-ese"),
    (r"\bXXE\b", "equis-equis-e"), (r"\bSSRF\b", "ese-ese-erre-efe"), (r"\bCSP\b", "ce-ese-pe"),
    (r"\bSRI\b", "ese-erre-i"), (r"\bCSV\b", "ce-ese-ve"), (r"\bPII\b", "datos personales"),
    (r"\bGDPR\b", "ge-de-pe-erre"), (r"\bKYC\b", "conoce a tu cliente"), (r"\bKYB\b", "conoce a tu empresa"),
    (r"\bDLQ\b", "cola de descarte"), (r"\bUUID\b", "u-u-i-de"), (r"\bKMS\b", "gestor de claves"),
    (r"\bTOCTOU\b", "tiempo-de-chequeo tiempo-de-uso"), (r"\bCDN\b", "ce-de-ene"),
    (r"\bURL\b", "u-erre-ele"), (r"\bAPI\b", "a-pe-i"), (r"\bSQL\b", "ese-cu-ele"),
    (r"\bOTP\b", "codigo de un solo uso"), (r"\bUA\b", "user-agent"), (r"\bIP\b", "i-pe"),
    (r"\bTMS\b", "te-eme-ese"), (r"\bETag\b", "i-tag"), (r"\balg=none\b", "algoritmo none"),
]
SUB_EN = [
    (r"\bMITM\b", "man in the middle"), (r"\bMFA\b", "multi factor authentication"),
    (r"\bReDoS\b", "re-doss"), (r"\bDoS\b", "denial of service"),
    (r"\bHMAC\b", "H-MAC"), (r"\bJWT\b", "J-W-T token"), (r"\bmTLS\b", "mutual T-L-S"),
    (r"\bIDOR\b", "eye-door"), (r"\bOAuth2?\b", "oh-auth"), (r"\bPKCE\b", "P-K-C-E"),
    (r"\bRBAC\b", "role based access control"), (r"\bSCA\b", "software composition analysis"),
    (r"\bSBOM\b", "S-bomb"), (r"\bSSRF\b", "S-S-R-F"), (r"\bXXE\b", "X-X-E"),
    (r"\bPII\b", "personal data"), (r"\bKYC\b", "know your customer"), (r"\bKYB\b", "know your business"),
    (r"\bDLQ\b", "dead letter queue"), (r"\bTOCTOU\b", "time of check time of use"),
    (r"\bPOD\b", "proof of delivery"), (r"\balg=none\b", "algorithm none"),
]

def clean(s, subs):
    s = re.sub(r"<code>(.*?)</code>", r"\1", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)          # quita <b> etc
    s = html.unescape(s)
    s = s.replace("→", ", da ").replace("×", " por ").replace("≠", " distinto de ")
    s = s.replace("&", " y ")
    for pat, rep in subs:
        s = re.sub(pat, rep, s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def narration(card, lang):
    loc = card[lang]
    subs = SUB_ES if lang == "es" else SUB_EN
    t, simple, caso, sol, test = (clean(loc[k], subs) for k in ("t","simple","caso","sol","test"))
    # quita el prefijo numerico tipo "1 . " que no aplica aca; los t de cyb no lo tienen
    if lang == "es":
        parts = [t + ".", simple, "El caso:", caso, "La solucion:", sol,
                 "Y como lo prueba el tester:", test]
    else:
        parts = [t + ".", simple, "The case:", caso, "The solution:", sol,
                 "And how the tester checks it:", test]
    return " ".join(parts)

def raw_text(card, lang):
    """Texto legible para el archivo de guiones (sin sustituciones foneticas)."""
    loc = card[lang]
    def c(s):
        s = re.sub(r"<code>(.*?)</code>", r"\1", s, flags=re.S)
        s = re.sub(r"<[^>]+>", "", s); return html.unescape(s).strip()
    return c(loc["t"]), c(loc["simple"]), c(loc["caso"]), c(loc["sol"]), c(loc["test"])

import time
def tts(text, voice, wav):
    txtfile = wav + ".txt"
    with open(txtfile, "w", encoding="utf-8") as fh:
        fh.write(text)
    last = None
    for attempt in range(5):
        r = subprocess.run([EDGE, "--voice", voice, "--rate=" + RATE, "--pitch=" + PITCH,
                            "--file", txtfile, "--write-media", wav],
                           capture_output=True, text=True)
        if r.returncode == 0 and os.path.exists(wav) and os.path.getsize(wav) > 1000:
            return
        last = (r.stderr or "")[-300:]
        print("  edge-tts retry %d (%s)" % (attempt + 1, last.strip()[:80]))
        time.sleep(3 * (attempt + 1))
    raise RuntimeError("edge-tts failed after retries: " + str(last))

def _dur(path):
    r = subprocess.run([FFPROBE, "-v", "quiet", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    return float(r.stdout.strip())

def to_final(raw_wav, dst_mp3, music_track):
    # 1) EQ oficial del canal sobre la narracion (ya clonada)
    eq_wav = raw_wav.replace(".mp3", "_eq.wav").replace(".wav", "_eq.wav")
    subprocess.run([FFMPEG, "-y", "-i", raw_wav, "-af", EQ_FILTER, eq_wav],
                   check=True, capture_output=True)
    # loudnorm al target medido en los 68 audios existentes: I=-24.5 LUFS, TP=-8 dB
    LN = "loudnorm=I=-24.5:TP=-8:LRA=7"
    if not MUSIC or not music_track:
        subprocess.run([FFMPEG, "-y", "-i", eq_wav, "-af", LN, "-c:a", "libmp3lame",
                        "-b:a", "128k", "-ar", "44100", "-ac", "2", dst_mp3],
                       check=True, capture_output=True)
        return
    # 2) cama de musica al 10%, en loop, con fade in/out; narracion primaria
    d = _dur(eq_wav)
    fout = max(0.0, d - 1.4)
    af = ("[1:a]volume=%.3f,afade=t=in:st=0:d=1.5[m];"
          "[0:a][m]amix=inputs=2:duration=first:normalize=0:dropout_transition=0[mix];"
          "[mix]afade=t=out:st=%.2f:d=1.4,aresample=44100,"
          "aformat=channel_layouts=stereo,%s[a]") % (MUSIC_VOL, fout, LN)
    subprocess.run([FFMPEG, "-y", "-i", eq_wav, "-stream_loop", "-1", "-i", music_track,
                    "-filter_complex", af, "-map", "[a]", "-shortest",
                    "-c:a", "libmp3lame", "-b:a", "128k", "-ar", "44100", "-ac", "2",
                    dst_mp3], check=True, capture_output=True)

def main():
    cards = json.load(open(os.path.join(SP, "cyb.json"), encoding="utf-8"))
    ids = sys.argv[1:] if len(sys.argv) > 1 else [c["id"] for c in cards]
    by = {c["id"]: c for c in cards}
    os.makedirs(OUT_ES, exist_ok=True); os.makedirs(OUT_EN, exist_ok=True)
    tmp = os.path.join(SP, "tmp"); os.makedirs(tmp, exist_ok=True)

    guion = ["# Guiones de narracion — Laboratorio de seguridad (x1–x50)\n",
             "Voz ES: `%s` · Voz EN: `%s` · rate `%s` · musica: %s\n" % (VOICE_ES, VOICE_EN, RATE, MUSIC),
             "> Texto que lee cada audio. En el MP3 las siglas se pronuncian aclaradas (HMAC→hache-mac, etc.).\n"]
    all_ids = [c["id"] for c in cards]
    for cid in ids:
        card = by[cid]
        # rotar la musica cyberpunk por indice de caso (mismo track para ES y EN del caso)
        track = TRACKS[all_ids.index(cid) % len(TRACKS)] if TRACKS else None
        for lang, voice, outdir in (("es", VOICE_ES, OUT_ES), ("en", VOICE_EN, OUT_EN)):
            text = narration(card, lang)
            wav = os.path.join(tmp, "%s_%s.mp3" % (cid, lang))
            dst = os.path.join(outdir, "%s.mp3" % cid)
            if os.environ.get("RESUME") == "1" and os.path.exists(dst) and os.path.getsize(dst) > 1000:
                print("skip (exists)", cid, lang); continue
            tts(text, voice, wav)
            src = wav
            if CLONE:
                src = clone_voice(wav, os.path.join(tmp, "%s_%s_cl.wav" % (cid, lang)))
            to_final(src, dst, track)
            print("OK", cid, lang, "->", dst, "| music:", os.path.basename(track) if track else "-")
        t,s,ca,so,te = raw_text(card, "es")
        guion.append("\n## %s — %s\n" % (cid, t))
        guion.append("**ES:** %s El caso: %s La solución: %s Y cómo lo prueba el tester: %s\n" % (s,ca,so,te))
        t,s,ca,so,te = raw_text(card, "en")
        guion.append("**EN (%s):** %s The case: %s The solution: %s And how the tester checks it: %s\n" % (t,s,ca,so,te))

    if len(sys.argv) <= 1:  # solo escribir guiones en corrida completa
        open(r"E:\testerday\guiones_seguridad.md","w",encoding="utf-8").write("\n".join(guion))
        print("guiones -> E:\\testerday\\guiones_seguridad.md")

if __name__ == "__main__":
    main()
