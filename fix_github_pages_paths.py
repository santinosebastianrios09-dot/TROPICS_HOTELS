import re
from pathlib import Path
import shutil

# Carpeta raíz del repo (puede ser "." si lo ejecutas en la raíz)
ROOT = Path(".").resolve()

# Extensiones a procesar
EXTS = {".html", ".css", ".js"}

# Compilamos patrones de reemplazo en orden
REPLACEMENTS = [
    # src="/algo" -> src="algo"  (sin tocar http/https)
    (re.compile(r'(\bsrc\s*=\s*["\'])/(?!/|https?:)', re.I), r'\1'),
    # href="/algo" -> href="algo"
    (re.compile(r'(\bhref\s*=\s*["\'])/(?!/|https?:)', re.I), r'\1'),
    # url(/img/...) -> url(img/...)
    (re.compile(r'(\burl\(\s*)/(img/)', re.I), r'\1\2'),
    # " /img/..." -> "img/..."  (comillas simples o dobles)
    (re.compile(r'(["\'])/(img/)', re.I), r'\1\2'),
    # " /visual/..." -> "visual/..."
    (re.compile(r'(["\'])/(visual/)', re.I), r'\1\2'),
    # Enlaces a la simulación: "/chat-simulacion.html" -> "chat-simulacion.html"
    (re.compile(r'(["\'])/chat-simulacion\.html(?=["\'])', re.I), r'\1chat-simulacion.html'),
    # window.open('/chat-simulacion.html' ...) -> window.open('chat-simulacion.html' ...)
    (re.compile(r'(window\s*\.\s*open\s*\(\s*["\'])/chat-simulacion\.html', re.I), r'\1chat-simulacion.html'),
    # Volver a raíz: location.href='/' -> './'
    (re.compile(r'(\blocation\s*\.\s*href\s*=\s*["\'])/(["\'])', re.I), r'\1./\2'),
    (re.compile(r'(window\s*\.\s*location\s*\.\s*assign\s*\(\s*["\'])/(["\'])', re.I), r'\1./\2'),
]

def process_file(path: Path) -> int:
    """Aplica los reemplazos al archivo. Devuelve cantidad de cambios."""
    txt = path.read_text(encoding="utf-8", errors="ignore")
    original = txt
    total_changes = 0
    for rx, repl in REPLACEMENTS:
        txt, n = rx.subn(repl, txt)
        total_changes += n
    if txt != original:
        # backup
        bak = path.with_suffix(path.suffix + ".bak")
        if not bak.exists():
            shutil.copy2(path, bak)
        path.write_text(txt, encoding="utf-8")
    return total_changes

def main():
    changed_files = 0
    total_changes = 0
    scanned = 0

    for p in ROOT.rglob("*"):
        if p.is_file() and p.suffix.lower() in EXTS:
            scanned += 1
            n = process_file(p)
            if n:
                changed_files += 1
                total_changes += n
                print(f"[mod] {p.relative_to(ROOT)}  (+{n} cambios)")
    print("\n— Resumen —")
    print(f"Archivos escaneados: {scanned}")
    print(f"Archivos modificados: {changed_files}")
    print(f"Reemplazos totales : {total_changes}")
    if changed_files:
        print("Se crearon backups .bak junto a cada archivo modificado.")

if __name__ == "__main__":
    main()
print("✅ FIX TERMINADO: Rutas corregidas para GitHub Pages")
