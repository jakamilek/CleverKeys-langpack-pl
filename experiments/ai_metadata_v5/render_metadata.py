"""Global schema explanations, never a dictionary of per-word meanings."""
import json
from pathlib import Path

GLOSSARY=json.loads(Path(__file__).with_name('glossary.json').read_text())
GUIDANCE=(
 'Jeżeli podano opisy słownika, są one alternatywami, nie faktami o zdaniu. '
 'Lemat to leksem źródłowy, wariant to dopuszczalna pisownia. Dobierz interpretację '
 'do kontekstu: imię/nazwisko dotyczy osoby, nazwa geograficzna miejsca. '
 'Nie wybieraj wielkiej litery tylko dlatego, że podano nazwę własną. '
 'Brak klasy nie rozstrzyga znaczenia. Wybierz podany wariant, bez dopisywania znaczeń.'
)

def explained_text(rows):
    out=[]
    for r in rows:
        pos=GLOSSARY['partOfSpeech'].get(r['partOfSpeech'],'nieobjaśniony kod '+r['partOfSpeech'])
        names=[GLOSSARY['nameClasses'].get(n,'nieobjaśniona kategoria '+n) for n in r['nameClasses']]
        labels=', '.join(r['labels']) or 'brak'
        forms=' / '.join(r['surfaces'])
        out.append('Forma „'+forms+'” od lematu „'+r['lemma']+'”: '+pos+
                   '; kategorie: '+
                   (', '.join(names) if names else 'nie podano klasy nazwy')+
                   '. Kwalifikatory: '+labels+'.')
    return '\n'.join(out)
