"""Assemble la carte : fiches (entries.json) + contours (geo/) -> un seul fichier HTML."""
import json
import locale
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
GEO_DIR = ROOT / "data" / "geo"

entries_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "entries.json"
out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "index.html"
date_txt = sys.argv[3] if len(sys.argv) > 3 else "6 octobre 2026"  # date de mise à jour affichée

CATS = [
    "anti-police", "anti-presse", "bordélisateur", "complaisant avec le Hamas",
    "complaisant avec les dictatures", "complotiste", "raciste et antisémite", "sexiste",
    "soupçonné de fraude", "un peu de tout", "violent",
]

entries = json.loads(entries_path.read_text())
circos = json.loads((GEO_DIR / "circos_packed.json").read_text())
depts = json.loads((GEO_DIR / "depts.json").read_text())
dep_names = {d["code"]: d["nom"] for d in depts}


def rnd(c, nd):
    if isinstance(c[0], (int, float)):
        return [round(c[0], nd), round(c[1], nd)]
    return [rnd(x, nd) for x in c]


for d in depts:
    d["g"]["coordinates"] = rnd(d["g"]["coordinates"], 3)


def ordinal(n):
    return "1ère" if n == 1 else f"{n}e"


def fold(s):
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()


data, geo = [], {}
for i, e in enumerate(entries):
    for k in e["cats"]:
        assert k in CATS and k != "un peu de tout", (e["name"], k)
    assert e["sources"], e["name"]
    dep, circo = e.get("dep"), e.get("circo")
    key = f"{dep}-{circo}" if dep and circo else None
    if key:
        assert key in circos, (e["name"], key)
        geo[key] = circos[key]
        label = e.get("label") or f"{e.get('dep_name') or dep_names[dep]}, {ordinal(circo)} circonscription"
    else:
        label = e["label"]
    data.append({
        "id": i, "key": key, "label": label, "name": e["name"], "role": e.get("role", ""),
        "cats": e["cats"], "paras": e["paras"], "sources": e["sources"], "elu": bool(e.get("elu")),
        "_sort": (1 if not key else 0, fold(label.split(",")[0]), circo or 0, fold(e["name"])),
    })

data.sort(key=lambda d: d["_sort"])
for i, d in enumerate(data):
    d["id"] = i
    del d["_sort"]

n = len(data)
present = [k for k in CATS if k != "un peu de tout" and any(k in d["cats"] for d in data)]
desc = f"{n} preuves que LFI est " + ", ".join(present[:-1]) + (f" et {present[-1]}" if len(present) > 1 else "".join(present)) + ", voire tout à la fois."

html = (HERE / "template.html").read_text()
dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
html = (html.replace("/*__DATA__*/[]", dump(data))
            .replace("/*__GEO__*/{}", dump(geo))
            .replace("/*__DEPTS__*/[]", dump(depts))
            .replace("__N__", str(n))
            .replace("__DESC__", desc.replace('"', "&quot;"))
            .replace("__DATE__", date_txt))
out_path.write_text(html)
print(f"{out_path} : {n} fiches, {sum(d['elu'] for d in data)} élu(e)s, {len(geo)} circonscriptions, {len(html)//1024} Ko")
print("catégories présentes :", present)
