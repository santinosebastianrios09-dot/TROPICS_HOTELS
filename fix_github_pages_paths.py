from pathlib import Path
import re, shutil

ROOT = Path(".").resolve()
EXTS = {".html", ".css", ".js"}

PATTERNS = [
    # src="/algo"  -> src="algo"   (sin tocar http/https// //cdn)
    (re.compile(r'(\bsrc\s*=\s*["\'])/(?!/|https?:)', re.I), r'\1'),
    # href="/algo" -> href="algo"
    (re.compile(r'(\bhref\s*=\s*["\'])/(?!/|https?:)', re.I), r'\1'),
    # url(/img/...) -> url(img/...)
    (re.compile(r'(\burl\(\s*)/(img/)', re.I), r'\1\2'),
    # " /img/..."  -> "img/..."
    (re.compile(r'(["\'])/(img/)', re.I), r'\1\2'),
    # " /visual/..." -> "visual/..."
    (re.compile(r'(["\'])/(visual/)', re.I), r'\1\2'),
    # /chat-simulacion.html -> chat-simulacion.html (en links o JS)
    (re.compile(r'(["\'])/chat-simulacion\.html(?=["\'])', re.I), r'\1chat-simulacion.html'),
    (re.compile(r'(window\s*\.\s*open\s*\(\s*["\'])/chat-simulacion\.html', re.I), r'\1chat-simulacion.html'),
    # Botón volver: ir a la carpeta actual (raíz del repo en Pages)
    (re.compile(r'(location\s*\.\s*href\s*=\s*["\'])/(\s*["\'])', re.I), r'\1./\2'),
    (re.compile(r'(window\s*\.\s*location\s*=\s*["\'])/(\s*["\'])', re.I), r'\1./\2'),
    (re.compile(r'(window\s*\.\s*location\s*\.\s*href\s*=\s*["\'])/(\s*["\'])', re.I), r'\1./\2'),
    # Defensa: remove dobles // solo en rutas relativas (no http/https)
    (re.compile(r'(["\'])(\./)?//(?![a-z]+:)', re.I), r'\1'),
]

def fix_file(p: Path) -> int:
    txt = p.read_text(encoding="utf-8", errors="ignore")
    orig = txt
    total = 0
    for rx, rep in PATTERNS:
        txt, n = rx.subn(rep, txt)
        total += n
    if txt != orig:
        bak = p.with_suffix(p.suffix + ".bak")
        if not bak.exists():
            shutil.copy2(p, bak)
        p.write_text(txt, encoding="utf-8")
    return total

def main():
    scanned = changed = replaced = 0
    for f in ROOT.rglob("*"):
        if f.is_file() and f.suffix.lower() in EXTS:
            scanned += 1
            n = fix_file(f)
            if n:
                changed += 1
                replaced += n
                print(f"[mod] {f.relative_to(ROOT)}  (+{n})")
    print("\n— Resumen —")
    print(f"Archivos escaneados : {scanned}")
    print(f"Archivos modificados: {changed}")
    print(f"Reemplazos totales  : {replaced}")
    print("✅ Listo. (Se crearon .bak junto a cada archivo tocado)")

if __name__ == "__main__":
    main()
