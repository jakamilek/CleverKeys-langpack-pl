# Selekcja kandydatów względem v11

To rekomendacja redakcyjna do kolejnego etapu, nie zgoda na instalację. V11 i jej wagi pozostają niezmienione. V12 pominięta.

| Wynik | Liczba |
|---|---:|
| Rekomendowane | 1356 |
| Rezerwa | 4253 |
| Wstrzymane | 1961 |

## Zasady i ograniczenia

SGJP potwierdza formę; wordfreq opisuje częstość zapisu, nie znaczenia. Rekomendacja nie dowodzi codziennej użyteczności każdego wpisu. Pozostawiono dotychczasowy próg oraz osobno wybrano formy >= 1 z wyraźnym kwalifikatorem praktycznej dziedziny. Potoczność i slang nie wykluczają. Rzadkie, obraźliwe i wulgarne oraz wybrane specjalistyczne dziedziny są w rezerwie. Dokładne, jawne zbiory kwalifikatorów są w selection-policy.json; to wybór redakcyjny, nie nowa wiedza źródłowa.

171 kandydatur z Wikisłownika pozostaje w rezerwie: przypisano komórki tabeli do zakresu znaczenia, ale nie zamknięto dowodu użycia konkretnego polskiego znaczenia ani jego docelowych metadanych. Każda ma rekord z tabelą, wersją strony, kwalifikatorami strony i dalszymi brakami. Kwalifikatorów strony nie przypisano automatycznie do znaczenia. Brak znacznika referencji nie oznacza braku wszystkich możliwych dowodów.

Wstrzymanie nie oznacza uznania słowa za błędne. Obejmuje m.in. nazwy wymagające weryfikacji tożsamości, kapitalizację, profil historyczny i brak wystarczającego dowodu. Poprzednie potwierdzenia językowe zachowano w sourceStatus.

## Czytnik v11

Osiem form: googlować, googluje, powerbank, powerbanki, streaming, streamingu, streamować, streamuje. Test uruchomiono na niezmienionych źródłach czytnika z commitu 0b94e323789e96c44a77f762a6f83fa11e285699: 4 pary dodatnie, 2 ujemne, zachowanie dwóch znaczeń streamować i wszystkich 114299 istniejących wpisów. Kategorie części mowy są dosłownymi kategoriami źródeł, nie tagami SGJP. To test JVM, nie pomiar RAM telefonu i nie test jakości Top-3.

## Koszt rekomendacji

1356 wpisów; 14392 elementów JSON; 227258 bajtów metadanych. Pozostaje 4345 wpisów, 184271 elementów JSON i 4731001 bajtów limitu. Koszt obejmuje źródła przy wpisach, ale nie przyszły opis etapu. Nie jest to rozmiar ZIP ani RAM.

## Przykłady według powodów

- excluded-by-lexical-profile: 157; przykłady: abakus, agrafa, akcesorium, aktorat, aktuariusz, alimenta, alkierz, alkowa, antykamera, apiać, bajdura, bajura, basteja, beduin, bezdziedziczny, bigosować, byczyć, błaźnica, chabanina, charakternik, chudoba, chybki, ciepać, ciepnąć, cudować
- polish-dictionary-entry-needs-morphology-and-usage: 1605; przykłady: abalienacja, abandonware, abaton, aberrometr, abertam, abi, abrenuncjacja, absznyt, abwera, adiacent, adios, administratywista, adobe, adopciak, adżika, adżyka, affogato, aglet, agrafeczka, agregatornia, agrestówka, agrorafineria, airfryer,
- lower-frequency-no-source-domain-priority: 1642; przykłady: abandon, abrazja, absorber, acetylen, acetylenowy, adwokatka, aerograf, aferzysta, afgan, afgani, afghani, agawa, agitka, agnostyczny, agraryzm, airbag, akant, akcept, akcjonariat, akordowy, akredytywa, aktoreczka, akumulatorowy, akuratnie,
- page-without-parsed-polish-definition: 8; przykłady: abd, abio, adac, ags, bael, fps, shake, split
- SGJP-form-confirmed-frequency-below-1: 2295; przykłady: abisynka, abisyńczyk, abiudykacja, abolicyjny, abrazyjny, abrogacja, abrogowanie, abrogować, abuzywny, achanie, achać, adiudykacja, adoptacja, adresarka, adresografia, adwokatowanie, adwokatować, aedicula, aeroelastyczność, aerofoto, aerogr
- no-lexical-proof-yet: 53; przykłady: abiu, acea, acrs, akwaplaning, amla, antipasti, atd, atf, awd, cheesesteak, chrienowucha, chrzanówka, cid, dśu, egr, eintopf, eobd, geotechniczny, gewuina, github, gojawa, guajawa, hba, jerzynówka, knnr, korbaczyk, lahmacun, linguine, macad
- specialist-domain:bot.: 25; przykłady: acerola, agrest, azalia, batat, cynia, cząber, durian, endywia, fenkuł, fistaszek, guawa, hoj, hoja, hojo, kabaczek, kalarepa, karambola, karczoch, maciejka, mahonia, makadamia, maniok, suchodrzew, wiciokrzew, zawilec
- name-or-brand-needs-identity-review: 99; przykłady: adium, amsn, badoo, bebo, bewelcome, bluesky, chatbot, chatgpt, deepseek, deezer, digsby, discord, discorda, dogmazic, emoji, empathy, facetime, familysearch, fansly, fediwersum, fire, friendica, gajim, gaydar, gossip, grindr, grok, ichat, 
- dictionary-case-table-confirmed-needs-sense-specific-usage-and-metadata: 171; przykłady: adware, ajfon, aliasing, amarok, amerykaniec, arteon, authoring, backend, bait, bazgroł, biedra, bima, blockchain, border, brunch, bruschetta, bulgur, buma, bysio, cache, camper, celadon, chatroom, cheat, chomiczek, cobbler, content, cringe
- SGJP-exact-form-and-original-frequency-policy: 1302; przykłady: agentur, amanie, amanu, amorów, anatom, antydepresant, antydepresantach, apelowanie, armadą, asesorzy, autek, autentyki, autka, autkiem, autokorekty, automobilem, automobili, automobilu, bajecznego, bajecznej, bajecznych, bajecznym, bajkowe
- dictionary-entry-flagged-for-verification: 7; przykłady: ajlauf, botnik, pirożki, pismaniye, rgt, ssp, szczi
- marked-usage:pogard.: 19; przykłady: aktorzyna, bezmózgowie, chamidło, gimbazą, gimbazę, gryzmoły, kacap, kanalię, kuternoga, lafirynda, lesbą, naziolem, naziolom, naziolu, pokurcz, szczujnia, wieśniara, ślepak, żołdak
- specialist-domain:paleont.: 1; przykłady: amonit
- SGJP-exact-form-lower-frequency-practical-domain:elektr.: 3; przykłady: amper, amperomierz, przekładnik
- SGJP-exact-form-lower-frequency-practical-domain:kulin.: 20; przykłady: antrykot, bakalie, baklawa, bawarka, befsztyk, burgund, cannelloni, chateaubriand, cheeseburger, czulent, kisz, mamałyga, miodownik, ouzo, ratatuj, strudel, tapenada, tempeh, zabaglione, zraz
- SGJP-exact-form-lower-frequency-practical-domain:techn.: 9; przykłady: areometr, ekscentryk, ekstraktor, frezowanie, konsoleta, korbowód, kątownik, opornik, potencjometr
- specialist-domain:astrol.: 1; przykłady: ascendent
- specialist-domain:żegl.: 5; przykłady: bant, cuma, slipach, slipów, sztag
- SGJP-exact-form-lower-frequency-practical-domain:bud.: 5; przykłady: barbakan, belkowanie, boniowanie, czerpnia, kaseton
- specialist-domain:mikol.: 4; przykłady: boczniak, mleczaj, opieńka, podgrzybek
- specialist-domain:monet.: 7; przykłady: boliwar, dirham, floren, forint, gourde, hrywna, peseta
- specialist-domain:zool.: 16; przykłady: bombardierów, charty, garłacz, jedwabnik, kałamarnica, kudu, kątnik, maltańczyk, marabut, okularnik, orzechowiec, patyczak, tapir, wrotka, zausznik, śmierdziel
- marked-usage:lekcew.: 11; przykłady: bzdet, ciamajda, gadanina, gadaniną, gruchot, jankesa, jankesom, oferma, półgłówek, szczawik, łamaga
- specialist-domain:num.: 2; przykłady: cekinów, halerz
- specialist-domain:mors.: 1; przykłady: chiefa
- marked-usage:wulg.: 22; przykłady: chujni, chujom, huju, odpierdalali, odpierdalam, opierdoli, opierdolimy, pierdolce, posra, posram, posrana, posrasz, posrała, przejebali, przejebana, przejebać, przejebał, przesrany, srajtaśma, zapierdolić, zapierdolił, zjebka
- marked-usage:rzad.: 22; przykłady: chłopisko, czujka, dilda, dopatrzeć, dopatrzy, eurosporcie, haro, jabol, komuszy, krokiet, krokieta, krokietów, malizna, mauzer, nawidzisz, niedopatrzenia, niedopatrzeń, podlec, przemądrzały, przesłodki, zajob, zblazowany
- specialist-domain:mit.: 1; przykłady: disa
- specialist-domain:geol.: 2; przykłady: fanga, lessu
- SGJP-exact-form-lower-frequency-practical-domain:komp.: 7; przykłady: gigabit, intranet, kilobajt, megabajt, mikrokomputer, touchpad, walidator
- explicit-external-form-link-and-positive-frequency-reader-tested: 8; przykłady: googlować, googluje, powerbank, powerbanki, streaming, streamingu, streamować, streamuje
- external-source-supported-needs-metadata: 25; przykłady: googlujesz, googlują, googluję, hashtag, hashtaga, powerbankach, powerbankami, powerbankiem, powerbankom, powerbankowi, powerbanku, powerbanków, scrollować, scrolluje, scrollujesz, scrolluję, streamingach, streamingami, streamingi, streamin
- marked-usage:reg.: 3; przykłady: gzik, kluseczka, skwarka
- source-capitalization-needs-review: 7; przykłady: iksińska, iksiński, kongresówka, lisp, marych, nek, trójmorze
- SGJP-exact-form-lower-frequency-practical-domain:praw.: 2; przykłady: powódka, zstępny
- marked-usage:indyw.: 1; przykłady: pój
- specialist-domain:archeol.: 1; przykłady: stoa
- specialist-domain:poligr.: 1; przykłady: tiret

## Odtworzenie

Najpierw istniejące review_candidate_pool.py oraz map_dictionary_case_evidence.py i prepare_external_33.py; następnie bridge_external_lemmas.py BASE_ZIP oraz select_reviewed_candidates.py BASE_ZIP. Dane i hashe wejść zachowano w paczce. Żaden krok nie tworzy pakietu instalacyjnego.
