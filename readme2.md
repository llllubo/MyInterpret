## Implementačná dokumentácia k 2. úlohe do IPP 2019/2020
## Meno a priezvisko: Ľuboš Vajčovec
## Login: xvajco00


## Interpret (interpret.py)
### Zdrojový kód
Skript pozostáva z väčšieho množstva funkcií vrátane hlavnej funkcie ```main()```, v ktorej prebieha interpretácia samotných inštrukcií.
### Analýza
Skript začína spustením analyzátora argumentov príkazového riadku, po ktorom následuje samostatný väčší blok kódu a tým je analyzátor vstupného XML kódu. Pre šikovnú prácu so vstupom bola využitá knižnica ```xml.etree.ElementTree```, ktorá rozčlenila XML kód do abstraktnej štruktúry strom, vďaka čomu sa stal prístup k jednotlivým inštrukčným elementom a elementom ich operandov veľmi jednoduchý a kontrolovaný. Analyzátor kontroluje koreňový, instrukčné elementy a elementy ich operandov z pohľadu lexikálneho a syntaktického na základe čoho vyvodí chybu s návratovým kódom 32, ak štruktúra XML nie je správna.
### Interpretácia
Skôr než dôjde k samotnému interpretovaniu XML kódu, je spustená kontrola redefinície návestí zozbieraných analyzátorom a deklarácia globálnych premenných - globálny rámec, dočasný ramec spolu s premennou booleovského typu pre indikáciu, či je tento rámec definovaný alebo nie, zásobník lokálnych rámcov, ktorý je na začiatku nedefinovaný (prázdny) a zásobník volaní a datový zásobník.
Inštrukcie zoradíme podľa hodnoty ```order``` a vo vzostupnom poradí ich začneme interpretovať. Nekonečný cyklus ```while True: ...``` každým cyklom spracuje inštrukciu v poradí a končí na základe podmienky kontrolujúcej posledný inštrukčný element.
### Implementačné detaily
Nutnou súčasťou bolo vytvorenie a dodržiavanie spôsobov zápisu špeciálnejších stavov. V prípade, že ide o hodnotu ```nil@nil``` je ukladaná a interne spracovavaná ako reťazec znakov ```\#n\#i\#l\#```, keďže Python-ovská hodnota ```None``` indikuje neinicializovanosť premennej pri jej vytvorení v ľubovoľnom rámci. Súčasťou implementácie je aj rozšírenie _STATI_ + podpora krátkych verzií prepínačov.

## Testovací rámec (test.php)
### Zdrojový kód
Skript je postavený na štruktúre _C-like_ jazyka. Hlavná časť kódu sa začína získaním zadaných prepínačov a ich lexikálnou analýzou, kde sa tiež kontrolujú ich zakázané kombinácie a existencia zadaných ciest skriptov/adresárov. Nasledujú volania kľúčových funkcií.
### Hlavná funkcia ```make_test()```
Jadrom skriptu je funkcia ```make_test()```, ktorej úlohou je prechádzať zadaný adresár s testami. Najskôr sa vygeneruje úvodný HTML kód obohatený o interný CSS kód pre lepšie formátovanie výstupu. Funkcia ```make_test()``` skenuje adresár, čím z neho získa všetky v ňom nachádzajúce sa súbory, ktorými vo ```foreach``` cykle prechádza a hľadá test s príponou ```.src```. Všetky nájdené testy spúšťa, kontroluje výsledky testov pomocou nástroja JExamXML alebo ```diff``` a jej výstupom je globálna premenná asociatívne pole, v ktorom je v zastúpení kľúča uložený reťazec - cesta k danému testu a hodnota v poli zodpovedá výsledku testu, teda opäť reťazec (úspech - OK, neúspech - X). Do poľa sú ukladané aj samotné adresáre, kde cesta k nim predstavuje kľúč a hodnota je reťazec DIR.
### Generovanie HTML 5 kódu
Filozofia generovania HTML kódu spočíva v pripojovaní jednotlivých častí HTML kódu do reťazca - premennej ```htmlCode```, ktorú na záver vypíšeme na štandardný výstup (STDOUT). Generovanie kódu je rozdelené do niekoľkých funkcií. Funkcia ```start_html()``` generuje všetok úvod HTML kódu vrátane hlavičky, titulu, metadat a CSS kódu, až po nadpis HTML stránky generovaný na začiatku bloku ```<body>```. Funkcia ```caption_html()``` generuje názov adresára a veľmi podstatnú informáciu o počte prejdených testov z celkového počtu nájdených testov v tomto adresári spolu s precentuálnym vyjadrením úspechu. ```summary_html()``` je funkcia, ktorá poskytuje celkový prehľad o úspešnosti testov, opäť vrátane percentuálneho vyjadrenia. Funkcia ```test_html()``` generuje konkrétne výsledky testov do tabuľky a záverečná funkcia ```end_html()``` ukončuje HTML kód. Výsledná HTML stránka zoraďuje testy v rámci adresárov abecedne do vzostupného poradia. Spôsob implementácie tejto vlastnosti rieši funkcia ```captions_tables_html()```, ktorá generuje všetok svoj kód najprv do dočasného reťazca - premennej ```htmlTables``` z dôvodu, že najprv musíme zistiť celkovú úspešnosť nájdených testov, vygenerovať príslušný kód a až potom následne doplniť už pripravený kód obsahujúci tabuľky s konkrétnymi testami, ich výsledkami a jednotlivými adresármi.
### Rozšírenia
Ako dobrovoľné rozšírenie bola implementovaná schopnosť skriptu pracovať aj s krátkymi verziami prepínačov a to v plnom rozsahu tak, ako tomu je aj u dlhých verzií a taktiež vyššie spomínané abecedné zoradenie testov v rámci adresárov.
