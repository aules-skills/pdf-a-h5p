# 🧩 PDF a H5P para Aules (crucigrama, sopa de letras, huecos, arrastrar)

Genera actividades H5P evaluables para Aules (Moodle de la GVA) a partir de un PDF, una imagen/captura o un tema. Es la variante de la skill [`h5p`](https://github.com/aules-skills/h5p) centrada específicamente en partir de un PDF como fuente.

> **Nota:** si no partes de un PDF, mira también el repositorio [`h5p`](https://github.com/aules-skills/h5p) — ambas skills comparten motor y plantillas.

## Tipos soportados

| Tipo | Qué es |
|---|---|
| `crossword` | Crucigrama |
| `findwords` | Sopa de letras |
| `advblanks` | Huecos avanzados (Advanced Blanks) |
| `dragtext` | Arrastrar palabras (Drag the Words) |

## Requisitos

- Python 3.
- La carpeta `plantillas/` (incluida) con los 4 `.h5p` base.

## Cómo se usa

**Con Claude / un asistente IA:** dale el PDF y pídele "hazme un crucigrama/sopa de letras/huecos/arrastrar sobre este PDF para Aules".

**A mano:**

1. Redacta el contenido extraído del PDF en un `.txt` según el tipo (formato exacto abajo).
2. Ejecuta:
   ```bash
   python crear_h5p.py TIPO ejemplos/archivo.txt --no-sol --idioma castellano -t "Título de la actividad"
   ```
3. Sube el `.h5p` resultante a Aules como **Actividad H5P** (no incrustado), con **Calificación = Puntuación**.

### Formato exacto por tipo

- **crossword**: `RESPUESTA | pista` (una por línea). Respuesta en MAYÚSCULAS, sin tildes ni espacios.
- **findwords**: una palabra por línea, en MAYÚSCULAS, sin tildes ni espacios.
- **advblanks**: frases con la respuesta entre `*asteriscos*`.
- **dragtext**: frases con las palabras a arrastrar entre `*asteriscos*`.

## Estructura

```
pdf-a-h5p/
├── crear_h5p.py     # generador
├── plantillas/       # plantillas base .h5p (una por tipo)
└── SKILL.md          # instrucciones detalladas (uso con Claude)
```

## Licencia

CC BY-SA 4.0 — ver [LICENSE.md](LICENSE.md). Libre de usar y adaptar citando la autoría.
