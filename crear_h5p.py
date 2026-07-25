#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de actividades H5P para Aules
========================================
Convierte un archivo de texto simple en un .h5p listo para subir mediante
"Substitueix amb el fitxer" en el Banco de contenido de Aules.

USO:
  python crear_h5p.py TIPO entrada.txt [-o salida.h5p] [-p plantilla.h5p] [-t "Titulo"]

TIPO: crossword | quiz | blanks | dragtext | accordion | advblanks

Cada tipo necesita una PLANTILLA .h5p del mismo tipo en la carpeta plantillas/
(se exporta una sola vez desde el Banco de contenido de Aules -> "Baixa").
"""
import argparse, json, os, sys, uuid, zipfile, re

HERE  = os.path.dirname(os.path.abspath(__file__))
PLANT = os.path.join(HERE, "plantillas")
DEFAULT_TPL = {"crossword": "crossword.h5p", "quiz": "quiz.h5p",
               "blanks": "blanks.h5p", "dragtext": "dragtext.h5p",
               "advblanks": "advblanks.h5p",
               "findwords": "findwords.h5p"}

def _lang(idioma):
    i=(idioma or "").strip().lower()
    if i in ("va","valenciano","valencià","valencia","catalan","català","cat"): return "va"
    if i in ("en","ingles","inglés","english"): return "en"
    return "es"
TASKDESC = {
 "es":{"crossword":"Completa el crucigrama.","findwords":"Encuentra las palabras escondidas en la sopa de letras.","advblanks":"Rellena los huecos.","dragtext":"Arrastra cada palabra a su hueco.","quiz":"Responde a las preguntas.","blanks":"Rellena los huecos."},
 "va":{"crossword":"Completa l'encreuat.","findwords":"Troba les paraules amagades en la sopa de lletres.","advblanks":"Ompli els buits.","dragtext":"Arrossega cada paraula al seu buit.","quiz":"Respon les preguntes.","blanks":"Ompli els buits."},
 "en":{"crossword":"Complete the crossword.","findwords":"Find the hidden words in the word search.","advblanks":"Fill in the blanks.","dragtext":"Drag each word to its gap.","quiz":"Answer the questions.","blanks":"Fill in the blanks."},
}


def lineas_utiles(raw):
    return [l.strip() for l in raw.splitlines() if l.strip() and not l.strip().startswith("#")]

def bloques(raw):
    bs, cur = [], []
    for l in raw.splitlines():
        if l.strip().startswith("#"):
            continue
        if l.strip() == "":
            if cur: bs.append(cur); cur = []
        else:
            cur.append(l.rstrip())
    if cur: bs.append(cur)
    return bs

# ---------- constructores de content.json por tipo ----------
def build_crossword(c, raw):
    words = []
    for s in lineas_utiles(raw):
        if "|" not in s:
            sys.exit(f"[crossword] Falta '|' en: {s}\n  Formato: RESPUESTA | pista")
        ans, clue = s.split("|", 1)
        words.append({"fixWord": False, "orientation": "across",
                      "clue": clue.strip(), "answer": ans.strip()})
    if len(words) < 2:
        sys.exit("[crossword] Se necesitan al menos 2 palabras.")
    c["words"] = words
    return c

def build_blanks(c, raw):
    qs = [f"<p>{s}</p>" for s in lineas_utiles(raw)]
    if not qs:
        sys.exit("[blanks] No hay frases. Marca la respuesta entre *asteriscos*.")
    c["questions"] = qs
    return c

def build_dragtext(c, raw):
    txt = "\n".join(lineas_utiles(raw))
    if "*" not in txt:
        sys.exit("[dragtext] No hay palabras marcadas. Usa *palabra* para las arrastrables.")
    c["textField"] = txt
    return c

def build_quiz(c, raw):
    bs = bloques(raw)
    if not bs:
        sys.exit("[quiz] No hay preguntas.")
    if not c.get("questions"):
        sys.exit("[quiz] La plantilla no tiene preguntas. Crea un Question Set con al menos "
                 "1 'Multiple Choice' y exportalo como plantilla.")
    proto = c["questions"][0]
    if "MultiChoice" not in proto.get("library", ""):
        sys.exit("[quiz] La 1a pregunta de la plantilla debe ser de tipo Multiple Choice.")
    nuevas = []
    for b in bs:
        if len(b) < 3:
            sys.exit(f"[quiz] Cada pregunta = enunciado + >=2 opciones. Revisa:\n  {b}")
        q = json.loads(json.dumps(proto))
        q["subContentId"] = str(uuid.uuid4())
        q["params"]["question"] = f"<p>{b[0].strip()}</p>"
        answers = []
        for opt in b[1:]:
            correct = opt.strip().startswith("*")
            text = opt.strip()[1:].strip() if correct else opt.strip()
            answers.append({"text": f"<div>{text}</div>", "correct": correct,
                            "tipsAndFeedback": {"tip": "", "chosenFeedback": "", "notChosenFeedback": ""}})
        if not any(a["correct"] for a in answers):
            sys.exit(f"[quiz] Marca al menos una opcion correcta con '*':\n  {b}")
        q["params"]["answers"] = answers
        if isinstance(q.get("metadata"), dict):
            q["metadata"]["title"] = b[0].strip()[:60]
        nuevas.append(q)
    c["questions"] = nuevas
    return c

def build_advblanks(c, raw):
    lines = lineas_utiles(raw)
    if not lines:
        sys.exit("[advblanks] No hay frases. Marca la respuesta entre *asteriscos*.")
    answers = []
    partes = []
    for line in lines:
        def repl(m):
            answers.append(m.group(1).strip())
            return "__________"
        nueva = re.sub(r"\*([^*]+)\*", repl, line)
        partes.append(f"<p>{nueva}</p>")
    if not answers:
        sys.exit("[advblanks] No hay huecos. Marca cada respuesta entre *asteriscos*.")
    if "content" not in c or not isinstance(c["content"], dict):
        c["content"] = {}
    c["content"]["blanksText"] = "".join(partes) + '<div class="table-overflow-protection"></div>'
    c["content"]["blanksList"] = [{"correctAnswerText": a, "hint": ""} for a in answers]
    return c

def build_findwords(c, raw):
    palabras = []
    for s in lineas_utiles(raw):
        for w in s.split(","):
            w = w.strip()
            if w:
                palabras.append(w)
    if len(palabras) < 2:
        sys.exit("[findwords] Se necesitan al menos 2 palabras (una por linea).")
    c["wordList"] = ",".join(palabras)
    c["taskDescription"] = "Encuentra las palabras escondidas en la sopa de letras."
    return c

BUILDERS = {"crossword": build_crossword, "quiz": build_quiz,
            "blanks": build_blanks, "dragtext": build_dragtext,
            "advblanks": build_advblanks,
            "findwords": build_findwords}

# ---------- empaquetado ----------
def repack(tpl, out, content, title):
    with zipfile.ZipFile(tpl) as z:
        names = z.namelist()
        data  = {n: z.read(n) for n in names}
    h5p = json.loads(data["h5p.json"].decode("utf-8"))
    if title:
        h5p["title"] = title
    data["h5p.json"] = json.dumps(h5p, ensure_ascii=False).encode("utf-8")
    data["content/content.json"] = json.dumps(content, ensure_ascii=False).encode("utf-8")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for n in names:
            if n.endswith("/"):
                continue
            z.writestr(n, data[n])
    return out

def n_elementos(content):
    for k in ("words", "questions", "panels"):
        if isinstance(content.get(k), list):
            return len(content[k])
    if isinstance(content.get("wordList"), str):
        return len([w for w in content["wordList"].split(",") if w.strip()])
    if isinstance(content.get("textField"), str):
        return len(re.findall(r"\*[^*]+\*", content["textField"]))
    bl = content.get("content", {})
    if isinstance(bl, dict) and isinstance(bl.get("blanksList"), list):
        return len(bl["blanksList"])
    return "?"

def main():
    ap = argparse.ArgumentParser(description="Genera un .h5p para Aules desde un .txt simple.")
    ap.add_argument("tipo", choices=list(BUILDERS))
    ap.add_argument("entrada")
    ap.add_argument("-o", "--salida")
    ap.add_argument("-p", "--plantilla")
    ap.add_argument("-t", "--titulo", default="")
    ap.add_argument("--no-sol", action="store_true", help="oculta el boton de Mostrar solucion")
    ap.add_argument("--idioma", default="castellano", help="castellano | valenciano | ingles (idioma del enunciado)")
    a = ap.parse_args()

    tpl = a.plantilla or os.path.join(PLANT, DEFAULT_TPL[a.tipo])
    if not os.path.exists(tpl):
        sys.exit(f"No encuentro la plantilla:\n  {tpl}\n"
                 f"Crea un '{a.tipo}' en el Banco de contenido de Aules, dale a 'Baixa' y "
                 f"guardalo con ese nombre en la carpeta plantillas/.")
    if not os.path.exists(a.entrada):
        sys.exit(f"No encuentro el archivo de entrada: {a.entrada}")

    with open(a.entrada, encoding="utf-8") as f:
        raw = f.read()
    with zipfile.ZipFile(tpl) as z:
        content = json.loads(z.read("content/content.json").decode("utf-8"))

    content = BUILDERS[a.tipo](content, raw)
    if a.no_sol:
        content.setdefault("behaviour", {})
        if a.tipo == "findwords": content["behaviour"]["enableShowSolution"] = False
        else: content["behaviour"]["enableSolutionsButton"] = False
    # FORZAR puntuacion y comprobacion (siempre, para que suba nota a calificaciones)
    content.setdefault("behaviour", {})
    if a.tipo == "crossword": content["behaviour"]["scoreWords"] = True
    if a.tipo in ("advblanks", "dragtext"): content["behaviour"]["enableCheckButton"] = True
    # enunciado en el idioma pedido
    _td = TASKDESC.get(_lang(a.idioma), {}).get(a.tipo)
    if _td:
        if a.tipo == "findwords": content["taskDescription"] = _td
        elif a.tipo == "advblanks": content.setdefault("content", {})["task"] = "<p>" + _td + "</p>"
        else: content["taskDescription"] = "<p>" + _td + "</p>"
    out = a.salida or (os.path.splitext(a.entrada)[0] + ".h5p")
    titulo = a.titulo or os.path.splitext(os.path.basename(a.entrada))[0]
    repack(tpl, out, content, titulo)

    print(f"OK  ->  {out}")
    print(f"    tipo={a.tipo}  elementos={n_elementos(content)}  titulo='{titulo}'")
    print("    Subelo en el Banco de contenido con 'Substitueix amb el fitxer'.")

if __name__ == "__main__":
    main()
