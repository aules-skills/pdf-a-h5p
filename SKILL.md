---
name: pdf-a-h5p
description: Genera actividades H5P evaluables para Aules (Moodle de la GVA) a partir de un PDF, una imagen/captura o una temática dada. Úsala siempre que el usuario quiera crear un crucigrama, una sopa de letras, huecos avanzados (fill in the blanks) o arrastrar palabras (drag the words) basándose en un documento, unos apuntes, una captura o un tema. Palabras que la activan: "crea/genera un H5P", "actividad para Aules", "crucigrama/sopa de letras/huecos/arrastrar a partir de este PDF o tema", "hazme una actividad sobre X". Produce un archivo .h5p listo para subir a Aules con "Substitueix amb el fitxer".
---

# Generar actividades H5P para Aules desde un PDF, imagen o tema

## Qué hace
Convierte una temática (indicada por el usuario o extraída de un PDF/imagen) en un archivo **.h5p evaluable**, usando plantillas base que ya incluyen las librerías de Aules. El .h5p resultante se autocorrige, puntúa y está listo para el libro de calificaciones.

## Tipos soportados
- **crossword** — crucigrama
- **findwords** — sopa de letras
- **advblanks** — huecos avanzados (Advanced Blanks)
- **dragtext** — arrastrar palabras (Drag the Words)

## Pasos a seguir (Claude)
1. **Reúne los datos.** Si faltan, pregúntalos: tipo de actividad, temática, curso/nivel, nº de elementos e **idioma** (castellano/valenciano/inglés; por defecto castellano).
2. **Si hay PDF o imagen/captura, léelo** con la herramienta Read para extraer el contenido y basar la actividad en él.
3. **Redacta el contenido** adaptado al curso/nivel, en el FORMATO EXACTO del tipo (ver abajo). El texto de entrada del usuario está en **castellano**; genera la actividad en el **idioma pedido** (por defecto, castellano). Si piden otro idioma, traduce el contenido.
4. **Guarda el contenido** en un `.txt` dentro de `ejemplos/`.
5. **Ejecuta** (desde la carpeta de esta skill):
   `python crear_h5p.py TIPO ejemplos/archivo.txt --no-sol --idioma valenciano -t "Título de la actividad"`
   - El script ya **fuerza puntuación y botón de comprobar**; `--no-sol` oculta el botón de solución; `--idioma castellano|valenciano|ingles` pone el **enunciado** en ese idioma.
   - Redacta también el **contenido** (palabras, pistas, frases) en el idioma pedido.
6. **Verifica** el .h5p (0 entradas de carpeta, ZIP íntegro) y **entrégalo** al usuario.
7. **Recuérdale**: en Aules, añádelo como **Actividad H5P** (no incrustado) con **Calificación = Puntuación** para que cuente en el libro de calificaciones.

## Formato exacto por tipo
- **crossword**: `RESPUESTA | pista` (una por línea). La RESPUESTA en MAYÚSCULAS y **sin tildes ni espacios**.
- **findwords**: una palabra por línea, en MAYÚSCULAS y **sin tildes ni espacios**.
- **advblanks**: frases con la respuesta entre `*asteriscos*`.
- **dragtext**: frases con las palabras a arrastrar entre `*asteriscos*`.

## Reglas de calidad (importantes)
- Adapta vocabulario y dificultad al **curso/nivel**.
- Respeta el **nº de elementos** pedido.
- En **crucigrama** y **sopa de letras**, respuestas **sin tildes ni espacios** (para que la cuadrícula encaje).
- En **arrastrar** y **huecos**, cada hueco debe tener **UNA sola respuesta correcta** según el contexto de la frase: NO pongas dos palabras intercambiables en la misma frase (p. ej. "El *teclado* y el *ratón* son de entrada" es incorrecto porque se pueden intercambiar).
- No reveles soluciones por defecto (usa `--no-sol`).
- **Idioma:** redacta el contenido en el idioma pedido y pasa `--idioma`. Nota: los botones de la actividad (Comprova, Mostra la solució…) provienen de la plantilla de Aules (valenciano en la GVA); el enunciado y el contenido sí salen en el idioma elegido.

## Trucos avanzados (opcionales)
- **Cuadrícula por niveles** (advblanks): `blanksText` admite `<table>`; puedes colocar cada nivel en una columna. El orden de las respuestas en `blanksList` debe seguir el orden de lectura (fila a fila, izquierda→derecha).
- **Pista adicional** (crossword): cada palabra admite `extraClue` (subcontenido H5P.AdvancedText); declara la dependencia en h5p.json. Aules GVA tiene esa librería instalada.

## Requisitos
- Python 3.
- La carpeta `plantillas/` (incluida) con: `crossword.h5p`, `findwords.h5p`, `advblanks.h5p`, `dragtext.h5p`.
