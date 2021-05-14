"""
PROJEKT:        Interpret jazyka IPPcode20 v XML reprezentacii kodu
VERZIA:         1.0
AUTOR:          Lubos Bever
DATUM:          14.04.2020
PREDMET:        Principy programovacich jazykov a OOP (IPP)
"""


import sys
import getopt
import re
import xml.etree.ElementTree as ElemTree


## DEFINICIE KONSTANT PRE CHYBOVE HLASENIA.
ERR_OPTS = 10               ## Zakazana kombinacia prepinacov.
ERR_INPUT_FOPEN = 11        ## Chyba pri praci so vstupnym suborom.
ERR_OUTPUT_FOPEN = 12       ## Chyba pri praci s vystupnym suborom.
ERR_XML_PARSE = 31          ## Chybna analyza vstupneho XML kodu pri prevode na strom.
ERR_XML_STRUCT = 32         ## Chybna struktura stromu reprezentujuceho XML kod.
ERR_SEMANTIC = 52           ## Semanticka chyba (pouzitie nedefinovaneho navestia, redefinicia premennej).
ERR_OPERANDS = 53           ## Chybne typy operandov (behova chyba).
ERR_NOT_EXISTS_VAR = 54     ## Pristup k neexistujucej premennej (behova chyba).
ERR_NOT_EXISTS_FRAME = 55   ## Ramec neexistuje - citanie z prazdneho zasobnika ramcov (behova chyba).
ERR_MISSING_VALUE = 56      ## Chybajuca hodnota - v premennej, na datovom zasobniku, v zasobniku volani (behova chyba).
ERR_WRONG_OP_VALUE = 57     ## Chybna hodnota operandu - delenie nulou, chybna navratova hodnota v EXIT (behova chyba).
ERR_STRING = 58             ## Chybna praca s retazcom (behova chyba).
ERR_INTERNAL = 99           ## Interna chyba skriptu.


def write_err(errno):
    """
    Vypis chyboveho hlasenia na standardny chybovy vystup (STDERR) a ukoncenie skriptu s navratovym kodom chyby.
    :param errno:   Unikatne cislo chyby.
    """
    if errno == 10:
        print("CHYBA! Zakazana kombinacia prepinacov alebo chybajuci/nadbytocny prepinac.", file=sys.stderr)
        exit(10)
    elif errno == 11:
        print("CHYBA! Neuspesna praca so vstupnym suborom.", file=sys.stderr)
        exit(11)
    elif errno == 12:
        print("CHYBA! Neuspesna praca s vystupnym suborom.", file=sys.stderr)
        exit(12)
    elif errno == 31:
        print("CHYBA! Zlyhala analyza XML kodu (chybny XML kod).", file=sys.stderr)
        exit(31)
    elif errno == 32:
        print("CHYBA! Zla struktura XML kodu alebo lexikalna/syntakticka chyba vstupneho XML.", file=sys.stderr)
        exit(32)
    elif errno == 52:
        print("CHYBA! Semanticka chyba (pouzitie nedefinovaneho navestia, redefinicia premennej).", file=sys.stderr)
        exit(52)
    elif errno == 53:
        print("CHYBA! Chybne typy operandov (behova chyba).", file=sys.stderr)
        exit(53)
    elif errno == 54:
        print("CHYBA! Pristup k neexistujucej premennej (behova chyba).", file=sys.stderr)
        exit(54)
    elif errno == 55:
        print("CHYBA! Ramec neexistuje alebo nie je definovany (behova chyba).", file=sys.stderr)
        exit(55)
    elif errno == 56:
        print("CHYBA! Chybajuca hodnota - v premennej, na datovom zasobniku, v zasobniku volani (behova chyba).", file=sys.stderr)
        exit(56)
    elif errno == 57:
        print("CHYBA! Chybna hodnota operandu - delenie nulou, chybna navratova hodnota v EXIT (behova chyba).", file=sys.stderr)
        exit(57)
    elif errno == 58:
        print("CHYBA! Chybna praca s retazcom (behova chyba).", file=sys.stderr)
        exit(58)
    else:
        print("CHYBA! Interna chyba skriptu.", file=sys.stderr)
        exit(99)


def write_help():
    """Vypis HELP napovedy na standardny vystup (STDOUT) a korektne ukoncenie skriptu."""
    print("POUZITIE: python3.8 interpret.py [--help] | [--source=file] [--intput=file] [--stats=file [--insts] [--vars]]")
    print("POUZITIE: python3.8 interpret.py [-h] | [-s file] [-i file] [-t file [-n] [-v]]\n")

    print("MOZNE PREPINACE:")
    print("\t-h,\t--help\t\tVypis napovedy HELP.")
    print("\t-s,\t--source=file\tVstupny subor obsahujuci XML reprezentaciu jazyka IPPcode20.")
    print("\t-i,\t--input=file\tSubor so vstupmi pre samotnu interpretaciu zadaneho zdrojoveho kodu.")
    print("\t-t,\t--stats=file\tSubor pre vypis statistik rozsirenia STATI.")
    print("\t-n,\t--insts\t\tVypis poctu vykonanych instrukcii do suboru (STATI).")
    print("\t-v,\t--vars\t\tVypis maximalneho poctu inicializovanych premennych do suboru (STATI).\n")

    print("Skript 'interpret.py' nacita XML reprezentaciu programu a s vyuzitim vstupu na zaklade parametrov")
    print("prikazoveho riadku interpretuje a generuje vystup. Skript je odporucane spustat s interpretom python verzia 3.8.\n")

    print("PRIKLADY SPUSTENIA:")
    print("python3.8 interpret.py --help")
    print("python3.8 interpret.py --source=file.src --input=file.in --stats=file --insts --vars\n")

    print("CHYBOVE NAVRATOVE KODY:")
    print("10 - Zakazana kombinacia prepinacov.")
    print("11 - Chyba pri otvarani vstupnych suborov (napr. neexistencia, nedostatocne prava).")
    print("12 - Chyba pri otvarani vystupnych suborov pre zapis (napr. neexistencia, nedostatocne prava).")
    print("31 - Chybny XML format vo vstupnom subore (nie je dobre formatovany).")
    print("32 - Neocakavana struktura XML (napr. element pre argument mimo elementu pre instrukciu), lexikalna ")
    print("     alebo syntakticka chyba textovych elementov a atributov vo vstupnom XML subore (napr. chybny ")
    print("     lexem pre retazcovy literal, neznamy operacny kod, ...).")
    print("52 - Chyba pri semantickych kontrolach vstupneho kodu v IPPcode20 (napr. pouzitie nedefinovaneho ")
    print("     navestia, redefinicia premennej.")
    print("53 - behova chyba interpretacie - nespravne typy operandov.")
    print("54 - behova chyba interpretacie - pristup k neexistujucej premennej (ramec neexistuje).")
    print("55 - behova chyba interpretacie - ramec neexistuje (napr. citanie z prazdneho zasobniku ramcov).")
    print("56 - behova chyba interpretacie - chybajuca hodnota (v premennej, na datovom zasobniku alebo v zasobniku volani).")
    print("57 - behova chyba interpretacie - nespravna hodnota operandu (napr. delenie nulou, nespravna navratova ")
    print("     hodnota instrukcie EXIT).")
    print("58 - behova chyba interpretacie - chybna praca s retazcom.")
    print("99 - Interna chyba skriptu (napr. chyba v analyze parametrov prikazoveho riadku).")
    exit(0)


def options_parsing():
    """
    Analyza argumentov prikazoveho riadku a vytvorenie stromu XML na zaklade vstupu.
    :returns tree, infile   Funkcia vracia referenciu na vytvoreny XML strom na zaklade vstupneho
                            XML a nazov suboru odkial sa bude citat vstup pre interpretaciu kodu.
    """
    ## Inicializacia.
    tree = None
    opts = None
    tmp_sys_stdin = None
    global fstats, stati
    fstats = None

    ## Spracovanie paramterov prikazoveho riadku.
    try:
        opts, reminder = getopt.getopt(sys.argv[1:], 'hs:i:t:nv', ['help', 'source=', 'input=', 'stats=', 'insts', 'vars'])
    except getopt.GetoptError or Exception:
        write_err(ERR_INTERNAL)

    optsSize = len(opts)
    if optsSize == 0:                   ## Nezadany ziaden prepinac.
        write_err(ERR_OPTS)

    for opt, val in opts:

        if opt in ('-h', '--help'):
            if optsSize > 1:
                write_err(ERR_OPTS)
            write_help()

        elif opt in ('-s', '--source'):
            if tree is None:                ## Prvy vyskyt --source je OK.
                try:
                    tree = ElemTree.parse(val)
                except ElemTree.ParseError:
                    write_err(ERR_XML_PARSE)
                except FileNotFoundError or PermissionError:
                    write_err(ERR_INPUT_FOPEN)

        elif opt in ('-i', '--input'):
            if tmp_sys_stdin is None:                   ## Prvy vyskyt --input je OK.
                try:
                    tmp_sys_stdin = sys.stdin           ## Presmerovanie STDIN.
                    sys.stdin = open(val)               ## Presmerovanie otvoreneho suboru na STDIN.
                except IOError:
                    write_err(ERR_INPUT_FOPEN)

        elif opt in ('-t', '--stats'):                  ## Ziskanie nazvu suboru pre STATI.
            if fstats is None:               ## Len prvy vyskyt potom ignor.
                fstats = val

        elif opt in ('-n', '--insts', '-v', '--vars'):  ## Zozbieranie poziadavok na STATI.
            stati.append(opt)

    if tmp_sys_stdin is None and tree is None:
        write_err(ERR_OPTS)

    if fstats is None and len(stati) != 0:               ## Chyba subor pre vypis STATI.
        write_err(ERR_OPTS)

    ## Nacitanie chybajuceho vstupu z STDIN.
    if tree is None:
        try:
            tree = ElemTree.parse(sys.stdin)
        except ElemTree.ParseError:
            write_err(ERR_XML_PARSE)
        except IOError:
            write_err(ERR_INPUT_FOPEN)

    ## Ak nie je zadany vstupny subor pre instrukciu READ, ocakava sa na STDIN.

    return tree


def sort_instructions(root):
    """
    Zoradenie instrukcii podla 'order' hodnoty vzostupne a kontrola duplicity tejto hodnoty.
    :param root:    Ukazatel na korenovy element v XML strome.
    """
    instrs = []                                 ## Docasne pole instrukcii, ktore bude radene vzostupne.

    for inst in root.findall('instruction'):    ## Vyhladanie instrukcnych elementov a priradena kopia do pola.
        instrs.append(inst)

    instrs = sorted(instrs, key=lambda ch: int(ch.get('order')))  ## Zoradenie instrukcii podla 'order' hodnoty.

    for inst in root.findall('instruction'):    ## Odstranenie vsetkych instrukcnych elementov.
        root.remove(inst)

    for inst in instrs:                         ## Pridanie zoradenych instrukcnych elementov.
        root.append(inst)

    ## Kontrola duplicity hodnoty atributu 'order'.
    orders = []
    for inst in root:
        orders.append(inst.get('order'))
    else:
        i = 1
        while i < len(orders):
            if orders[i - 1] == orders[i]:
                write_err(ERR_XML_STRUCT)
            i += 1


def xml_check_arg_var(arg):
    """
    Kontrola 'argX' elementu instrukcie s typom premenna ('var').
    :param arg: Referencia na objekt - 'argX' element danej instrukcie.
    """
    attval = arg.items()                ## Pole dvojic (atribut, hodnota).
    text = arg.text                     ## Hodnota ulozena ako textovy element v 'argX'.

    ## Funkcia arg.items() vracia pole dvojic [(atribut, hodnota), ...] pre dany element.
    if len(attval) != 1 or attval[0][0] != 'type' or attval[0][1] != 'var':
        write_err(ERR_XML_STRUCT)

    if (text is None) or (re.fullmatch(r'^(GF|LF|TF)@[a-zA-Z_\-$&%*!?][0-9a-zA-Z_\-$&%*!?]*$', text) is None):
        write_err(ERR_XML_STRUCT)


def xml_check_arg_label(arg):
    """
    Kontrola 'argX' elementu instrukcie s typom navestie ('label').
    :param arg: Referencia na objekt - 'argX' element danej instrukcie.
    """
    attval = arg.items()                ## Pole dvojic (atribut, hodnota).
    text = arg.text                     ## Hodnota ulozena ako textovy element v 'argX'.

    ## Funkcia arg.items() vracia pole dvojic [(atribut, hodnota), ...] pre dany element.
    if len(attval) != 1 or attval[0][0] != 'type' or attval[0][1] != 'label':
        write_err(ERR_XML_STRUCT)

    if (text is None) or (re.fullmatch(r'^[a-zA-Z_\-$&%*!?][0-9a-zA-Z_\-$&%*!?]*$', text) is None):
        write_err(ERR_XML_STRUCT)


def xml_check_arg_symb(arg):
    """
    Kontrola 'argX' elementu instrukcie s typom konstanta alebo premenna ('symb').
    :param arg: Referencia na objekt - 'argX' element danej instrukcie.
    """
    attval = arg.items()                ## Pole dvojic (atribut, hodnota).
    text = arg.text                     ## Hodnota ulozena ako textovy element v 'argX'.

    ## Funkcia arg.items() vracia pole dvojic [(atribut, hodnota), ...] pre dany element.
    if len(attval) != 1 or attval[0][0] != 'type' or re.fullmatch(r'^var|int|bool|string|nil$', attval[0][1]) is None:
        write_err(ERR_XML_STRUCT)

    ## Kontrola konstanty podla jej typu.
    if attval[0][1] == 'var':

        ## Textovy element nezodpoveda premennej alebo je prazdny.
        if (text is None) or (re.fullmatch(r'^(GF|LF|TF)@[a-zA-Z_\-$&%*!?][0-9a-zA-Z_\-$&%*!?]*$', text) is None):
            write_err(ERR_XML_STRUCT)

    elif attval[0][1] == 'int':

        ## Textovy element nezodpoveda cislu alebo je prazdny.
        if (text is None) or (re.fullmatch(r'^[-+]?[0-9]+$', text) is None):
            write_err(ERR_XML_STRUCT)

    elif attval[0][1] == 'bool':

        ## Textovy element nezodpoveda hodnote 'true' ani 'false' alebo je prazdny.
        if (text is None) or (re.fullmatch(r'^false|true$', text) is None):
            write_err(ERR_XML_STRUCT)

    elif attval[0][1] == 'string':

        ## Regularny vyraz akceptuje vsetky znaky okrem '#' a '\'.
        ## '\' je v poriadku len ak ide o 'escape' sekvenciu ('\000').
        ## Znaky '<', '>', '&' su kontrolovane uz samotnym analyzatorom pre 'Element Tree'
        ##    a su akceptovane len ako XML entity (napr. &amp;), tiez podpora UTF-8.
        if (text is not None) and (re.fullmatch(r'(?:(?:\\[0-9]{3})*[^\\#\s]*)*', text, re.UNICODE) is None):
            write_err(ERR_XML_STRUCT)                       ## Textovy element obsahuje nejaky zakazany znak.

    elif attval[0][1] == 'nil' and text != 'nil':
        write_err(ERR_XML_STRUCT)


def xml_check_arg_type(arg):
    """
    Kontrola 'argX' elementu instrukcie s typom typ ('type') nacitavanej hodnoty (instrukcia READ).
    :param arg: Referencia na objekt - 'argX' element danej instrukcie.
    """
    attval = arg.items()                ## Pole dvojic (atribut, hodnota).
    text = arg.text                     ## Hodnota ulozena ako textovy element v 'argX'.

    ## Funkcia arg.items() vracia pole dvojic [(atribut, hodnota), ...] pre dany element.
    if len(attval) != 1 or attval[0][0] != 'type' or attval[0][1] != 'type':
        write_err(ERR_XML_STRUCT)

    if (text is None) or (re.fullmatch(r'^int|string|bool$', text) is None):
        write_err(ERR_XML_STRUCT)


def xml_check_args(instr, args):
    """
    Dodatocna kontrola poctu argumentov pre instrukcie 2 a 3 argumentove.
    Kontrola duplikacie argumentov pre vsetky instrukcie.
    :param instr:   Operacny kod instrukcie.
    :param args:    Pole ziskanych argumentov.21
    """
    ## Dodatocna kontrola chybajucich argumentov pri poziadavke 2 alebo 3.
    if instr in ('move', 'int2char', 'read', 'strlen', 'type', 'not'):     ## Ocakavane 2 argumenty.

        if len(args) != 2:
            write_err(ERR_XML_STRUCT)

    elif instr in ('add', 'sub', 'mul', 'idiv', 'lt', 'gt', 'eq', 'and', 'or', 'stri2int', 'concat', 'getchar', 'setchar', 'jumpifeq', 'jumpifneq'):
        if len(args) != 3:
            write_err(ERR_XML_STRUCT)

    args = sorted(args)
    ## Kontrola duplikacie 'argX' pre danu instrukciu.
    if (len(args) == 1 and args[0] != 'arg1') \
            or (len(args) == 2 and (args[0] != 'arg1' or args[1] != 'arg2')) \
            or (len(args) == 3 and (args[0] != 'arg1' or args[1] != 'arg2' or args[2] != 'arg3')):
        write_err(ERR_XML_STRUCT)


def xml_check_instr_args(instrElem):
    """
    Kontrola argumentov (operandov) pre prislusnu instrukciu.
    :param instrElem:   Referencia na objekt - instrukcny element v strome XML.
    """
    global labels
    args = []                                   ## Pole pre nazvy elementov 'argX' pre danu instrukciu (kontrola duplicity).
    instr = instrElem.get('opcode').lower()     ## Nazov operacneho kodu instrukcie malymi pismenami.

    isarg = None                                ## None - nevykonava sa kontrola; Instrukcia bez argumentov.
    if not re.fullmatch(r'^createframe|pushframe|popframe|return|break$', instr):
        isarg = False                           ## Ide o instrukciu s aspon jednym povinnym argumentom.

    for arg in instrElem:

        ## Operacne kody nevyzadujuce argument v instrukcii, no vyskytuje sa.
        if re.fullmatch(r'^createframe|pushframe|popframe|return|break$', instr):

            tmp = arg                           ## Ak je tmp None, dana instrukcia arg nema.
            if tmp is not None:                 ## Test existencie objektu - podelement instrukcneho elementu.
                write_err(ERR_XML_STRUCT)

        ## Operacne kody vyzadujuce argument <var> v instrukcii.
        if re.fullmatch(r'^defvar|pops$', instr):

            if arg.tag != 'arg1':
                write_err(ERR_XML_STRUCT)

            xml_check_arg_var(arg)
            isarg = True

        ## Operacne kody vyzadujuce argument <label> v instrukcii.
        elif re.fullmatch(r'^call|label|jump$', instr):

            if arg.tag != 'arg1':
                write_err(ERR_XML_STRUCT)

            xml_check_arg_label(arg)

            if instr == 'label':        ## Ulozenie navestia vopred kvoli skokom na este nedefinovane navestia.
                labels.append(arg.text)

            isarg = True

        ## Operacne kody vyzadujuce argument <symb> v instrukcii.
        elif re.fullmatch(r'^pushs|write|exit|dprint$', instr):

            if arg.tag != 'arg1':
                write_err(ERR_XML_STRUCT)

            xml_check_arg_symb(arg)
            isarg = True

        ## Operacne kody vyzadujuce argumenty <var> <symb> v instrukcii.
        elif re.fullmatch(r'^move|int2char|strlen|type|not$', instr):

            if arg.tag == 'arg1':
                xml_check_arg_var(arg)

            elif arg.tag == 'arg2':
                xml_check_arg_symb(arg)

            else:
                write_err(ERR_XML_STRUCT)

            isarg = True

        ## Operacne kody vyzadujuce argument <var> <type> v instrukcii.
        elif re.fullmatch(r'^read$', instr):

            if arg.tag == 'arg1':
                xml_check_arg_var(arg)

            elif arg.tag == 'arg2':
                xml_check_arg_type(arg)

            else:
                write_err(ERR_XML_STRUCT)

            isarg = True

        ## Operacne kody vyzadujuce argument <label> <symb1> <symb2> v instrukcii.
        elif re.fullmatch(r'^jumpifeq|jumpifneq$', instr):

            if arg.tag == 'arg1':
                xml_check_arg_label(arg)

            elif arg.tag == 'arg2' or arg.tag == 'arg3':
                xml_check_arg_symb(arg)

            else:
                write_err(ERR_XML_STRUCT)

            isarg = True

        ## Operacne kody vyzadujuce argument <var> <symb1> <symb2> v instrukcii.
        elif re.fullmatch(r'^add|sub|mul|idiv|lt|gt|eq|and|or|stri2int|concat|getchar|setchar$', instr):

            if arg.tag == 'arg1':
                xml_check_arg_var(arg)

            elif arg.tag == 'arg2' or arg.tag == 'arg3':
                xml_check_arg_symb(arg)

            else:
                write_err(ERR_XML_STRUCT)

            isarg = True

        ## Nemalo by k tomuto dojst => chyba neznamy oper. kod je vyvodena vo funkcii 'xml_parsing()'.
        else:
            write_err(ERR_XML_STRUCT)

        args.append(arg.tag)                ## Nazov kazdeho 'argX' elementu ulozeny v poli kvoli dalsej kontrole.

    ## Kontrola vyskytu argumentu(ov) v pripade jeho (ich) nutnosti.
    if isarg is not None and isarg is False:
        write_err(ERR_XML_STRUCT)

    xml_check_args(instr, args)             ## Kontrola poctu argumentov a ich duplikacie.


def xml_parsing(root):
    """
    Analyza vstupneho XML.
    :param root:    Referencia na objekt - korenovy element stromu XML.
    """
    ## Kontrola korenoveho elementu.
    if root.tag != 'program':
        write_err(ERR_XML_STRUCT)

    ## Korenovy element bez atributov.
    if len(root.items()) == 0:
        write_err(ERR_XML_STRUCT)

    lang = None                             ## Pomocna premenna pre detekciu povinneho atributu.
    ## Kontrola atributov a ich hodnot v korenovom elemente.
    for att, val in root.items():

        ## Nie je akceptovany iny atribut ako 'name', 'description' a 'language' s hodnotou 'IPPcode20'.
        if (att != 'language' or not re.fullmatch(r'^ippcode20$', val, re.IGNORECASE)) \
                and att != 'name' \
                and att != 'description':
            write_err(ERR_XML_STRUCT)

        ## Detekcia povinneho atributu 'language' so spravnou hodnotou.
        if att == 'language' and re.fullmatch(r'^ippcode20$', val, re.IGNORECASE) is not None:
            lang = True

    ## Chybajuci povinny atribut 'language' s hodnotou 'IPPcode20'.
    if lang is None:
        write_err(ERR_XML_STRUCT)

    ## Kontrola vyskytu neznameho elementu.
    for elem in root.findall(".//*"):
        if re.fullmatch(r'^instruction|arg1|arg2|arg3$', elem.tag) is None:
            write_err(ERR_XML_STRUCT)

    ## Kontrola konkretnych instrukcnych elementov vratane ich podelementov ('argX').
    for instrElem in root:

        ## Kontrola nazvu instrukcneho elementu.
        if instrElem.tag != 'instruction':
            write_err(ERR_XML_STRUCT)

        ## Kontrola textoveho elementu v instrukcnom elemente.
        for txt in root.text:
            if re.fullmatch(r'^\s*$', txt) is None:
                write_err(ERR_XML_STRUCT)

        ## Kontrola atributov a ich hodnot.
        for att, val in instrElem.items():

            opcodeVal = re.fullmatch(r'^move|createframe|pushframe|popframe|defvar|call|return|pushs|pops|add|sub|mul|'
                                     r'idiv|lt|gt|eq|and|or|not|int2char|stri2int|read|write|concat|strlen|getchar|'
                                     r'setchar|type|label|jump|jumpifeq|jumpifneq|exit|dprint|break$', val, re.IGNORECASE)
            if (att != 'order' or re.fullmatch(r'^[1-9][0-9]*$', val) is None) and (att != 'opcode' or opcodeVal is None):
                write_err(ERR_XML_STRUCT)

            # Kontrola prislusnych argumentov a ich hodnot pre danu instrukciu.
            if opcodeVal is not None:
                xml_check_instr_args(instrElem)


def check_redef_label():
    """Kontrola redefinicie navesti. V pripade redefinicie chyba 52."""
    global labels

    if len(labels) > 1:
        seen = []
        for lbl in labels:
            if lbl in seen:
                write_err(ERR_SEMANTIC)
            seen.append(lbl)


def get_top_frame():
    """
    Funkcia vracia vrchol zasobnika (lokalnych) ramcov - aktualne viditelny ramec.
    :return:            Vrchol zasobnika ramcov - viditelny lokalny ramec
                        V pripade nedefinovaneho ramca (prazdneho zasobnika) vracia None.
    """
    global stackFrame
    size = len(stackFrame)
    if size == 0:
        return None
    return stackFrame[size - 1]


def get_vars_number():
    """
    **ROZSIRENIE STATI**
    Zisti pocet momentalne inicializovanych premennych vo vsetkych ramcoch.
    Hodnotu uklada do globalnej premennej.
    """
    global maxvars, vars, tmpFrameDef, tmpFrame, gFrame, stackFrame
    vars = 0

    for v in gFrame:
        if v is not None:
            vars += 1

    if tmpFrameDef is True:
        for v in tmpFrame:
            if v is not None:
                vars += 1

    if len(stackFrame) != 0:
        for lf in stackFrame:
            for v in lf:
                if v is not None:
                    vars += 1

    if maxvars < vars:
        maxvars = vars


def get_instElem_and_pos(root, jumpTo):
    """
    Najdenie instrukcneho elemntu s navestim definovanym pre skok.
    :param root:    Referencia na koren stromu XML.
    :param jumpTo:  Nazov navestia, ktore sa hlada.
    :return:        Instrukcny element s hladanym navestim a pozicia tejto instrukcie.
    """
    ## Najdenie vsetkych instrukcnych elementov s textom hladaneho navestia.
    xpathToLabel = "./instruction[arg1='" + jumpTo + "']"
    instElemsLabel = root.findall(xpathToLabel)             ## Najprv pole najdenych elementov.
    instElem = None

    ## Najdenie instrukcie s definiciou hladaneho navestia pre skok.
    for elem in instElemsLabel:

        opcode = elem.get('opcode')

        if re.fullmatch(r'^LABEL$', opcode, re.IGNORECASE):

            instElem = elem                                 ## Najdenie a nastavenie elementu.
            break

    if instElem is None:                                    ## Pouzitie nedefinovaneho navesti.
        write_err(ERR_SEMANTIC)

    ## Zistenie pozicie najdeneho instrukcneho elementu.
    pos = 1
    for inst in root:

        if inst == instElem:
            break

        pos += 1

    return instElem, pos


def get_value_from_symb(opType, opVal):
    """
    Najde a konvertuje hladanu hodnotu na prislusny typ.
    :param opType:  Typ operandu, ktoreho hodnota sa ide ziskat (var/symb).
    :param opVal:   Hodnota operandu z XML stromu.
    :return:        Vracia hodnotu konvertovanu na dany typ.
    """
    global tmpFrameDef, tmpFrame, stackFrame, gFrame
    val = None                  ## Hodnota, ktora sa bude vraciat.

    if opType == 'var':
        parts = opVal.split('@')
        frame = parts[0]
        varName = parts[1]

        if frame == 'TF':
            if not tmpFrameDef:                     ## Ramec nie je definovany - nie je mozne pouzivat.
                write_err(ERR_NOT_EXISTS_FRAME)

            throwErr = True
            for var in tmpFrame:                    ## Kontrola ci premenna je definovana v danom ramci.
                if var == varName:
                    if tmpFrame[varName] is None:   ## Pristup k neinicializovanej premennej.
                        write_err(ERR_MISSING_VALUE)
                    throwErr = False
                    val = tmpFrame[varName]
                    break

            if throwErr:
                write_err(ERR_NOT_EXISTS_VAR)

        elif frame == 'LF':
            lf = get_top_frame()
            if lf is None:                          ## Nedefinovany LF.
                write_err(ERR_NOT_EXISTS_FRAME)

            throwErr = True
            for var in lf:                          ## Kontrola ci premenna je definovana v danom ramci.
                if var == varName:
                    if lf[varName] is None:         ## Pristup k neinicializovanej premennej.
                        write_err(ERR_MISSING_VALUE)
                    throwErr = False
                    val = lf[varName]
                    break

            if throwErr:
                write_err(ERR_NOT_EXISTS_VAR)

        elif frame == 'GF':
            throwErr = True
            for var in gFrame:                      ## Kontrola ci premenna je definovana v danom ramci.
                if var == varName:
                    if gFrame[varName] is None:     ## Pristup k neinicializovanej premennej.
                        write_err(ERR_MISSING_VALUE)
                    throwErr = False
                    val = gFrame[varName]
                    break

            if throwErr:
                write_err(ERR_NOT_EXISTS_VAR)

    if opType == 'int':
        try:
            val = int(opVal)
        except ValueError:
            write_err(ERR_OPERANDS)
        except Exception:
            write_err(ERR_INTERNAL)

    elif opType == 'bool':
        if opVal == 'false':
            val = False
        elif opVal == 'true':
            val = True

    elif opType == 'string':
        val = convert_escape_seq(opVal)

    elif opType == 'nil':
        val = '\#n\#i\#l\#'

    return val


def exec_createframe():
    """Vytvorenie noveho docasneho ramca."""
    global tmpFrame, tmpFrameDef
    tmpFrame = {}
    tmpFrameDef = True


def exec_pushframe():
    """Presun docasneho ramca (TF) na zasobnik (lokalnych) ramcov (LF)."""
    global tmpFrame, tmpFrameDef, stackFrame

    if not tmpFrameDef:
        write_err(ERR_NOT_EXISTS_FRAME)

    stackFrame.append(tmpFrame)
    tmpFrame = {}
    tmpFrameDef = False


def exec_popframe():
    """Presun lokalneho ramca (LF) zo zasobniku ramcov na docasny ramec (TF)."""
    global tmpFrame, tmpFrameDef, stackFrame

    lf = get_top_frame()
    if lf is None:
        write_err(ERR_NOT_EXISTS_FRAME)

    tmpFrame = lf
    tmpFrameDef = True
    stackFrame.remove(lf)


def exec_defvar(instrElem):
    """
    Definuje premennu v zadanom ramci (hodnota 'None'), ale neinicializuje!
    :param instrElem:   Instrukcny element danej instrukcie.
    """
    opVal = instrElem.find("arg1").text

    parts = opVal.split('@')
    frame = parts[0]
    varName = parts[1]
    global gFrame, tmpFrame, tmpFrameDef, stackFrame

    if frame == 'TF':
        if not tmpFrameDef:                         ## Ramec nie je definovany - nie je mozne pouzivat.
            write_err(ERR_NOT_EXISTS_FRAME)

        for var in frame:                           ## Kontrola redefinicie premennej v TF.
            if var == varName:
                write_err(ERR_SEMANTIC)
        tmpFrame[varName] = None                    ## Definovanie neinicializovanej premennej v TF.

    elif frame == 'LF':
        lf = get_top_frame()
        if lf is None:                              ## Nedefinovany LF.
            write_err(ERR_NOT_EXISTS_FRAME)

        for var in frame:                           ## Kontrola redefinicie premennej v LF.
            if var == varName:
                write_err(ERR_SEMANTIC)
        lf[varName] = None                          ## Definovanie neinicializovanej premennej v LF.

    elif frame == 'GF':
        for var in frame:                           ## Kontrola redefinicie premennej v GF.
            if var == varName:
                write_err(ERR_SEMANTIC)
        gFrame[varName] = None                      ## Definovanie neinicializovanej premennej v GF.


def save_value_in_var(opVar, val):
    """
    Uklada danu hodnotu do zadanej premennej.
    :param opVar:   Nazov premennej.
    :param val:     Ukladana hodnota uz konvertovana na prislusny typ.
    """
    global gFrame, tmpFrame, tmpFrameDef, stackFrame
    parts = opVar.split('@')
    frame = parts[0]
    varName = parts[1]

    if frame == 'TF':
        if not tmpFrameDef:                 ## Ramec nie je definovany - nie je mozne pouzivat.
            write_err(ERR_NOT_EXISTS_FRAME)

        throwErr = True
        for var in tmpFrame:                ## Kontrola ci premenna je definovana v danom ramci.
            if var == varName:
                throwErr = False
                break

        if throwErr:
            write_err(ERR_NOT_EXISTS_VAR)

        tmpFrame[varName] = val             ## Presun hodnoty do premennej v TF.

    elif frame == 'LF':
        lf = get_top_frame()
        if lf is None:                      ## Nedefinovany LF.
            write_err(ERR_NOT_EXISTS_FRAME)

        throwErr = True
        for var in lf:                      ## Kontrola ci premenna je definovana v danom ramci.
            if var == varName:
                throwErr = False
                break

        if throwErr:
            write_err(ERR_NOT_EXISTS_VAR)

        lf[varName] = val

    elif frame == 'GF':
        throwErr = True
        for var in gFrame:                  ## Kontrola ci premenna je definovana v danom ramci.
            if var == varName:
                throwErr = False
                break

        if throwErr:
            write_err(ERR_NOT_EXISTS_VAR)

        gFrame[varName] = val

    get_vars_number()               ## STATI


def exec_move(instrElem):
    """
    Vykona instrukciu 'MOVE' so zadanymi argumentami.
    :param instrElem:   Instrukcny element danej instrukcie.
    """
    opVal1 = instrElem.find("arg1").text
    opType2 = instrElem.find("arg2").get('type')    ## <symb>
    opVal2 = instrElem.find("arg2").text

    val = get_value_from_symb(opType2, opVal2)

    save_value_in_var(opVal1, val)                  ## Presun hodnoty do premennej.


def exec_aritmetic(instrElem):
    """
    Vykona prislusnu aritmeticku instrukciu 'ADD'/'SUB'/'MUL'/'IDIV' so zadanymi argumentami.
    :param instrElem:   Instrukcny element danej instrukcie.
    """
    opcode = instrElem.get('opcode').lower()
    opVal1 = instrElem.find("arg1").text
    opType2 = instrElem.find("arg2").get('type')  ## <symb>
    opVal2 = instrElem.find("arg2").text
    opType3 = instrElem.find("arg3").get('type')  ## <symb>
    opVal3 = instrElem.find("arg3").text

    val2 = get_value_from_symb(opType2, opVal2)
    val3 = get_value_from_symb(opType3, opVal3)

    val = None                                  ## Tu sa ulozi vysledok.

    if (isinstance(val2, int) and not isinstance(val2, bool)) \
            and (isinstance(val3, int) and not isinstance(val3, bool)):     ## Hodnoty su typu cele cislo.

        if opcode == 'add':
            val = val2 + val3

        elif opcode == 'sub':
            val = val2 - val3

        elif opcode == 'mul':
            val = val2 * val3

        elif opcode == 'idiv':
            if val3 == 0:                                                   ## Delenie nulou.
                write_err(ERR_WRONG_OP_VALUE)
            val = val2 // val3                                              ## Celociselne delenie.

    else:
        write_err(ERR_OPERANDS)

    save_value_in_var(opVal1, val)


def exec_relational(instrElem):
    """
    Vykona prislusnu relacnu instrukciu 'LT'/'GT'/'EQ' so zadanymi argumentami.
    :param instrElem:   Instrukcny element danej instrukcie.
    """
    opcode = instrElem.get('opcode').lower()
    opVal1 = instrElem.find("arg1").text
    opType2 = instrElem.find("arg2").get('type')  ## <symb>
    opVal2 = instrElem.find("arg2").text
    opType3 = instrElem.find("arg3").get('type')  ## <symb>
    opVal3 = instrElem.find("arg3").text

    val2 = get_value_from_symb(opType2, opVal2)
    val3 = get_value_from_symb(opType3, opVal3)

    val = None                                      ## Tu sa ulozi vysledok porovnania.

    ## Ide o operandy rovnakeho typu: 'int' alebo 'bool' alebo 'nil' alebo 'str'.
    if (isinstance(val2, int) and not isinstance(val2, bool)) \
            and (isinstance(val3, int) and not isinstance(val3, bool)):

        val = False                    ## Zmena v pripade ze plati relacny operator pre dane hodnoty.

        if opcode == 'lt':
            if val2 < val3:
                val = True

        elif opcode == 'gt':
            if val2 > val3:
                val = True

        elif opcode == 'eq':
            if val2 == val3:
                val = True

    elif (isinstance(val2, int) and isinstance(val2, bool)) \
            and (isinstance(val3, int) and isinstance(val3, bool)):

        val = False                   ## Zmena v pripade ze plati relacny operator pre dane hodnoty.

        if opcode == 'lt':
            if val2 is False and val3 is True:
                val = True

        elif opcode == 'gt':
            if val2 is True and val3 is False:
                val = True

        elif opcode == 'eq':
            if (val2 is True and val3 is True) or (val2 is False and val3 is False):
                val = True

    ## Aspon jeden z operandov je typu 'nil'.
    elif val2 == '\#n\#i\#l\#' and val3 == '\#n\#i\#l\#':

        if opcode == 'eq':
            val = True
        else:
            write_err(ERR_OPERANDS)

    elif (val2 == '\#n\#i\#l\#' and val3 != '\#n\#i\#l\#') or (val2 != '\#n\#i\#l\#' and val3 == '\#n\#i\#l\#'):

        if opcode == 'eq':
            val = False
        else:
            write_err(ERR_OPERANDS)

    elif isinstance(val2, str) and isinstance(val3, str):

        val = False

        if opcode == 'lt':
            if val2 < val3:
                val = True

        elif opcode == 'gt':
            if val2 > val3:
                val = True

        elif opcode == 'eq':
            if val2 == val3:
                val = True

    else:
        write_err(ERR_OPERANDS)

    save_value_in_var(opVal1, val)


def exec_rel_bool(instrElem):
    """
    Vykona prislusnu instrukciu s booleovskymi operandami ('AND'/'OR'/'NOT').
    :param instrElem:   Instrukcny element danej instrukcie.
    """
    opcode = instrElem.get('opcode').lower()
    opVal1 = instrElem.find("arg1").text
    opType2 = instrElem.find("arg2").get('type')  ## <symb>
    opVal2 = instrElem.find("arg2").text

    val2 = get_value_from_symb(opType2, opVal2)

    val3 = None                                         ## Inicializacia kvoli kontrole IDE.
    if opcode != 'not':                                 ## Instrukcia s operacnym kodom 'NOT' nema treti argument.
        opType3 = instrElem.find("arg3").get('type')    ## <symb>
        opVal3 = instrElem.find("arg3").text

        val3 = get_value_from_symb(opType3, opVal3)

    val = None                                          ## Tu sa ulozi vysledok porovnania.

    ## Ide o operandy rovnakeho typu 'bool'.
    if opcode != 'not':
        if (isinstance(val2, int) and isinstance(val2, bool)) \
                and (isinstance(val3, int) and isinstance(val3, bool)):

            if opcode == 'and':

                val = False
                if val2 is True and val3 is True:
                    val = True

            elif opcode == 'or':

                val = True
                if val2 is False and val3 is False:
                    val = False

        else:
            write_err(ERR_OPERANDS)

    else:
        if isinstance(val2, int) and isinstance(val2, bool):

            val = True
            if val2 is True:
                val = False

        else:
            write_err(ERR_OPERANDS)

    save_value_in_var(opVal1, val)


def convert_escape_seq(str):
    """
    Vyhladanie 'escape' sekvencii v retazci a ich nahradenie prislusnym UNICODE znakom.
    V pripade, ze sa tieto sekvencie v retazci nenachadzaju, vracia sa povodny retazec.
    :param str: Retazec obsahujuci 'escape' sekvencie.
    :return:    Retazec s konvertovanymi 'escape' sekvenciami.
    """
    try:
        if len(str) != 0 and re.search(r'\\[0-9]{3}', str, re.UNICODE):

            escPatt = re.compile(r'\\[0-9]{3}', re.UNICODE)
            escSeqs = escPatt.finditer(str)                     ## Najdenie vsetkych 'escape' sekvencii.

            if escSeqs is not None:                             ## Ak 'None', nenasli sa ziadne.

                originLen = len(str)

                for escSeq in escSeqs:                          ## Vymena 'escape' sekvencii jednotlivo.

                    offset = originLen - len(str)
                    (begin, end) = escSeq.span()                ## Index prveho a posledneho znaku sekvencie v retazci.
                    char = chr(int(escSeq.group()[1:]))
                    str = str[:begin - offset] + char + str[end - offset:]      ## Nahradenie 'escape' sekvencie.
    except TypeError:
        str = ''

    return str


def exec_write(instrElem):
    """
    Vykonanie instrukcie write.
    :param instrElem:   Referencia na instrukcny element z XML stromu.
    """
    opType = instrElem.find("arg1").get('type')     ## <symb>
    opVal = instrElem.find("arg1").text

    ## Vypis hodnot typu 'bool' a 'nil' je specialny.
    val = get_value_from_symb(opType, opVal)

    if val is True:
        print("true", end='', file=sys.stdout)

    elif val is False:
        print("false", end='', file=sys.stdout)

    elif val == '\#n\#i\#l\#':
        print("", end='', file=sys.stdout)

    else:
        print(val, end='', file=sys.stdout)


def exec_read(instrElem):
    """
    Vykona instrukciu 'READ' so zadanymi argumentami.
    Nacita vstup zo zadaneho suboru alebo z STDIN v pripade chybajuceho suboru.
    :param instrElem:   Instrukcny element danej instrukcie.
    """
    opVal1 = instrElem.find("arg1").text
    opVal2 = instrElem.find("arg2").text
    val = None

    if opVal2 == 'int':
        try:
            val = input()
            val = int(val)
        except EOFError:
            val = '\#n\#i\#l\#'

    elif opVal2 == 'bool':
        try:
            val = input()
            if re.fullmatch(r'^true$', val, re.IGNORECASE):
                val = True
            else:
                val = False
        except EOFError:
            val = '\#n\#i\#l\#'

    elif opVal2 == 'string':
        try:
            val = input()
            val = str(val)
        except EOFError:
            val = '\#n\#i\#l\#'

    save_value_in_var(opVal1, val)


def get_var_type_from_frame(varName, frame):
    """
    Zisti typ zadanej premennej definovanej v zadanom ramci.
    :param varName: Nazov premennej.
    :param frame:   Ramec, v ktorom sa premenna nachadza.
    :return:        Typ prislusnej premennej daneho ramca.
    """
    typeResult = None

    throwErr = True
    for var in frame:                               ## Kontrola ci premenna je definovana v danom ramci.
        if var == varName:
            if frame[varName] is None:              ## Pristup k neinicializovanej premennej.
                typeResult = ''
            throwErr = False
            break

    if throwErr:
        write_err(ERR_NOT_EXISTS_VAR)

    if typeResult is None:                          ## Typ sa este nezistil.
        if isinstance(frame[varName], int) and not isinstance(frame[varName], bool):
            typeResult = 'int'

        elif isinstance(frame[varName], int) and isinstance(frame[varName], bool):
            typeResult = 'bool'

        elif frame[varName] == '\#n\#i\#l\#':
            typeResult = 'nil'

        elif isinstance(frame[varName], str):
            typeResult = 'string'

    return typeResult


def exec_type(instrElem):
    """
    Vykonanie instrukcie 'TYPE'.
    :param instrElem:   Referencia na instrukcny element.
    """
    opVal1 = instrElem.find("arg1").text          ## var
    opType2 = instrElem.find("arg2").get('type')  ## <symb>
    opVal2 = instrElem.find("arg2").text

    global tmpFrameDef, tmpFrame, stackFrame, gFrame
    typeResult = None                                   ## Vysledok - typ hodnoty <symb>.

    if opType2 == 'var':
        parts = opVal2.split('@')
        frame = parts[0]
        varName = parts[1]

        if frame == 'TF':
            if not tmpFrameDef:                         ## Ramec nie je definovany - nie je mozne pouzivat.
                write_err(ERR_NOT_EXISTS_FRAME)

            typeResult = get_var_type_from_frame(varName, tmpFrame)

        elif frame == 'LF':
            lf = get_top_frame()
            if lf is None:                              ## Nedefinovany LF.
                write_err(ERR_NOT_EXISTS_FRAME)

            typeResult = get_var_type_from_frame(varName, lf)

        elif frame == 'GF':
            typeResult = get_var_type_from_frame(varName, gFrame)

    elif opType2 == 'int':
        if isinstance(opVal2, int) and not isinstance(opVal2, bool):
            typeResult = 'int'
        else:
            write_err(ERR_OPERANDS)

    elif opType2 == 'bool':
        if opVal2 == 'false' or opVal2 == 'true':
            typeResult = 'bool'
        else:
            write_err(ERR_OPERANDS)

    elif opType2 == 'string':
        if isinstance(opVal2, str):
            typeResult = 'string'
        else:
            write_err(ERR_OPERANDS)

    elif opType2 == 'nil':
        if opVal2 == 'nil':
            typeResult = 'nil'
        else:
            write_err(ERR_OPERANDS)

    save_value_in_var(opVal1, typeResult)               ## Ulozi typ do premennej.


def exec_equal(instrElem):
    """
    Pomocna funkcia pre instrukcie 'JUMPIFEQ' a 'JUMPINEQ' - zistuje rovnost operandov.
    :param instrElem:   Referencia na instrukcny element.
    :return:            Booleovska hodnota rovnosti operandov pre zadanu instrukciu 'JUMPIFEQ' alebo 'JUMPINEQ'.
    """
    opType2 = instrElem.find("arg2").get('type')  ## <symb>
    opVal2 = instrElem.find("arg2").text
    opType3 = instrElem.find("arg3").get('type')  ## <symb>
    opVal3 = instrElem.find("arg3").text

    val2 = get_value_from_symb(opType2, opVal2)
    val3 = get_value_from_symb(opType3, opVal3)

    if (isinstance(val2, int) and not isinstance(val2, bool)) \
            and (isinstance(val3, int) and not isinstance(val3, bool)):     ## Ide o 'int' hodnoty!!!
        if val2 == val3:
            return True

    elif (isinstance(val2, int) and isinstance(val2, bool)) \
            and (isinstance(val3, int) and isinstance(val3, bool)):         ## Ide o 'bool' hodnoty!!!
        if val2 == val3:
            return True

    elif val2 == '\#n\#i\#l\#' and val3 == '\#n\#i\#l\#':                   ## Ide o 'nil' hodnoty!!!
        return True

    elif (isinstance(val2, str) and val3 != '\#n\#i\#l\#') \
            and (isinstance(val3, str) and val2 != '\#n\#i\#l\#'):                   ## Ide o 'string' hodnoty!!!
        if val2 == val3:
            return True

    else:                                                                   ## Hodnoty su odlisneho typu.
        write_err(ERR_OPERANDS)

    return False


def exec_exit(instrElem):
    """
    Vykona instrukciu 'EXIT' (ukoncenie behu programu so zadanym navratovym kodom).
    :param instrElem:   Referencia na objekt instrukcny element v strome XML.
    """
    opType = instrElem.find("arg1").get('type')  ## <symb>
    opVal = instrElem.find("arg1").text

    val = get_value_from_symb(opType, opVal)

    if isinstance(val, int) and not isinstance(val, bool):
        if 0 <= val <= 49:
            if val == 0:
                make_stati()            ## STATI
            exit(val)

        else:
            write_err(ERR_WRONG_OP_VALUE)

    else:
        write_err(ERR_OPERANDS)


def exec_stri2int_or_concat(instrElem):
    """
    Spojena funkcia vykonavajuca instrukcie 'STRI2INT' a 'CONCAT'
      podla zadaneho operacneho kodu v instrukcnom elemente.
    :param instrElem:   Referencia na objekt instrukcny element v strome XML.
    """
    opcode = instrElem.get('opcode').lower()
    opVal1 = instrElem.find("arg1").text            ## <var>
    opType2 = instrElem.find("arg2").get('type')    ## <symb>
    opVal2 = instrElem.find("arg2").text
    opType3 = instrElem.find("arg3").get('type')    ## <symb>
    opVal3 = instrElem.find("arg3").text

    val2 = get_value_from_symb(opType2, opVal2)
    val3 = get_value_from_symb(opType3, opVal3)

    val = None

    if opcode == 'stri2int' and (isinstance(val2, str) and val2 != '\#n\#i\#l\#') \
                                and (isinstance(val3, int) and not isinstance(val3, bool)):
        try:
            if len(val2) - 1 < val3:
                write_err(ERR_STRING)
            val = ord(val2[val3])
        except ValueError or IndexError:
            write_err(ERR_STRING)
        except Exception:
            write_err(ERR_INTERNAL)

    elif opcode == 'concat' and (isinstance(val2, str) and val2 != '\#n\#i\#l\#') \
                                and (isinstance(val3, str) and val3 != '\#n\#i\#l\#'):
        try:
            val = val2 + val3
        except ValueError:
            write_err(ERR_STRING)
        except Exception:
            write_err(ERR_INTERNAL)

    else:
        write_err(ERR_OPERANDS)

    save_value_in_var(opVal1, val)


def exec_int2char_or_strlen(instrElem):
    """
    Spojena funkcia vykonavajuca instrukcie 'INT2CHAR' a 'STRLEN'
      podla zadaneho operacneho kodu v instrukcnom elemente.
    :param instrElem:   Referencia na objekt instrukcny element v strome XML.
    """
    opcode = instrElem.get('opcode').lower()
    opVal1 = instrElem.find("arg1").text            ## <var>
    opType2 = instrElem.find("arg2").get('type')    ## <symb>
    opVal2 = instrElem.find("arg2").text

    val2 = get_value_from_symb(opType2, opVal2)

    val = None

    if opcode == 'int2char' and isinstance(val2, int) and not isinstance(val2, bool):
        try:
            val = chr(val2)
        except ValueError:
            write_err(ERR_STRING)
        except Exception:
            write_err(ERR_INTERNAL)

    elif opcode == 'strlen' and isinstance(val2, str) and val2 != '\#n\#i\#l\#':
        try:
            val = len(val2)
        except ValueError:
            write_err(ERR_STRING)
        except Exception:
            write_err(ERR_INTERNAL)

    else:
        write_err(ERR_OPERANDS)

    save_value_in_var(opVal1, val)


def exec_set_or_get_char(instrElem):
    """
    Spojena funkcia vykonavajuca instrukcie 'SETCHAR' a 'GETCHAR'
      podla zadaneho operacneho kodu v instrukcnom elemente.
    :param instrElem:   Referencia na objekt instrukcny element v strome XML.
    """
    opcode = instrElem.get('opcode').lower()
    opType1 = instrElem.find("arg1").get('type')    ## <symb>
    opVal1 = instrElem.find("arg1").text            ## <var>
    opType2 = instrElem.find("arg2").get('type')    ## <symb>
    opVal2 = instrElem.find("arg2").text
    opType3 = instrElem.find("arg3").get('type')    ## <symb>
    opVal3 = instrElem.find("arg3").text

    val1 = None
    if opcode == 'setchar':
        val1 = get_value_from_symb(opType1, opVal1)

    val2 = get_value_from_symb(opType2, opVal2)
    val3 = get_value_from_symb(opType3, opVal3)

    val = None

    if opcode == 'getchar' and (isinstance(val2, str) and val2 != '\#n\#i\#l\#') \
                            and (isinstance(val3, int) and not isinstance(val3, bool)):
        try:
            if len(val2) - 1 < val3:
                write_err(ERR_STRING)
            val = val2[val3]
        except ValueError:
            write_err(ERR_STRING)
        except Exception:
            write_err(ERR_INTERNAL)

    elif opcode == 'setchar' and (isinstance(val1, str) and val1 != '\#n\#i\#l\#') \
                                and (isinstance(val2, int) and not isinstance(val2, bool)) \
                                    and isinstance(val3, str):
        try:
            if len(val1) - 1 < val2 or len(val3) == 0:
                write_err(ERR_STRING)
            val = val1[:val2]
            val = val + val3[:1]
            val = val + val1[val2 + 1:]
        except ValueError or IndexError:
            write_err(ERR_STRING)
        except Exception:
            write_err(ERR_INTERNAL)

    else:
        write_err(ERR_OPERANDS)

    save_value_in_var(opVal1, val)


def make_stati():
    """
    **ROZSIRENIE STATI**
    Vypis statistik do suboru.
    """
    global fstats, stati, maxvars, insts
    ## Vypis statistik do suboru (STATI).
    if fstats is not None:
        try:
            file = open(fstats, "w")
            for i in stati:
                if i in ('-v', '--vars'):
                    print(maxvars, file=file)
                elif i in ('-n', '--insts'):
                    print(insts, file=file)
            file.close()
        except FileNotFoundError or PermissionError or IOError:
            write_err(ERR_OUTPUT_FOPEN)


def main():
    """Hlavna funkcia prevadzajuca vsetky ukony."""

    global labels
    labels = []                                 ## Pole navesti naplnene pocas XML analyzy.
    global fstats, insts, maxvars, vars, stati  ## Rozsirenie STATI - pocet instrukcii a incializovanych premennych.
    stati = []

    tree = options_parsing()                    ## Analyza zadanych prepinacov, vracia XML strom.
    root = tree.getroot()                       ## Ziskanie ukazatela na korenovy uzol stromu.
    xml_parsing(root)                           ## Analyza vstupneho XML kodu.

    check_redef_label()                         ## Kontrola redefinicie navestia (chyba 52).
    sort_instructions(root)                     ## Zoradenie instrukcii vzostupne.

    global gFrame, stackFrame, tmpFrameDef, tmpFrame, stackData
    gFrame = {}                     ## Inicializovany slovnik globalnych premennych (nazov premennej, hodnota).
    stackFrame = []                 ## Zasobnik lokalnych ramcov. LF je na zaciatku nedefinovany => prazdny zasobnik.
    tmpFrameDef = False             ## Docasny ramec je na zaciatku nedefinovany.
    tmpFrame = {}                   ## Slovnik premennych na docasnom ramci.
    pc = 1                          ## Interny citac instrukcii.
    stackCall = []                  ## Zasobnik volani.
    stackData = []                  ## Datovy zasobnik.

    lastInstr = root.find("./instruction[last()]")      ## Referencia na poslednu instrukciu v strome XML.
    if lastInstr is None:                       ## Ide o prazdny XML kod.
        exit(0)

    instElem = None                 ## Inicializacia instrukcneho elementu.
    jumpTo = ""                     ## Navestie, na ktore sa bude skakat.
    jumping = False                 ## Predikat ze sa bude skakat.
    insts = 0
    vars = 0
    maxvars = 0

    while True:

        ## Bola vykonana posledna instrukcia; Koniec len ak nejde o skok.
        if instElem == lastInstr \
                and re.fullmatch(r'^CALL|RETURN|JUMP|JUMPIFEQ|JUMPIFNEQ$', instElem.get('opcode'), re.IGNORECASE) is None:
            break

        ## Dojde k prepisu 'instElem', ak nasleduje skok.
        xpathToInst = "./instruction[" + str(pc) + "]"      ## Retazec pre vyhladanie dalsej instrukcie v strome.
        instElem = root.find(xpathToInst)                   ## Ziskany instrukcny element podla citaca instrukcii.

        insts += 1                  ## Pocet vykonanych instrukcii.

        ## PREVEDENIE SKOKU; Ziskanie instrukcie s cielom skoku (dany 'LABEL').
        if jumping:
            instElem, pc = get_instElem_and_pos(root, jumpTo)

        instr = instElem.get('opcode')                      ## Ziskanie operacneho kodu instrukcie.

        ## ******************** PRACA S RAMCAMI, VOLANIE FUNKCII ******************** ##
        if re.fullmatch(r'^MOVE$', instr, re.IGNORECASE):
            exec_move(instElem)
            pc += 1

        elif re.fullmatch(r'^CREATEFRAME$', instr, re.IGNORECASE):
            exec_createframe()
            pc += 1

        elif re.fullmatch(r'^PUSHFRAME$', instr, re.IGNORECASE):
            exec_pushframe()
            pc += 1

        elif re.fullmatch(r'^POPFRAME$', instr, re.IGNORECASE):
            exec_popframe()
            pc += 1

        elif re.fullmatch(r'^DEFVAR$', instr, re.IGNORECASE):
            exec_defvar(instElem)
            pc += 1

        elif re.fullmatch(r'^CALL$', instr, re.IGNORECASE):
            pc += 1                                     ## 'RETURN' sa vrati na dalsiu instrukciu za 'CALL'.
            stackCall.append(pc)

            jumpTo = instElem.find('arg1').text         ## Navestie, na ktore sa bude skakat.
            jumping = True

        elif re.fullmatch(r'^RETURN$', instr, re.IGNORECASE):
            if len(stackCall) == 0:                     ## Prazdny zasobnik volani.
                write_err(ERR_MISSING_VALUE)

            pc = stackCall.pop(len(stackCall) - 1)

        ## *********************** PRACA S DATOVYM ZASOBNIKOM *********************** ##
        elif re.fullmatch(r'^PUSHS$', instr, re.IGNORECASE):

            val = get_value_from_symb(instElem.find("arg1").get('type'), instElem.find("arg1").text)
            stackData.append(val)
            pc += 1

        elif re.fullmatch(r'^POPS$', instr, re.IGNORECASE):

            if len(stackData) == 0:                         ## Prazdny datovy zasobnik.
                write_err(ERR_MISSING_VALUE)
            opVal = instElem.find("arg1").text

            ## Ulozenie hodnoty z vrcholu datoveho zasobnika do premennej.
            save_value_in_var(opVal, stackData.pop(len(stackData) - 1))
            pc += 1

        ## ************************* ARITMETICKE INSTRUKCIE ************************* ##
        elif re.fullmatch(r'^ADD$', instr, re.IGNORECASE):
            exec_aritmetic(instElem)
            pc += 1

        elif re.fullmatch(r'^SUB$', instr, re.IGNORECASE):
            exec_aritmetic(instElem)
            pc += 1

        elif re.fullmatch(r'^MUL$', instr, re.IGNORECASE):
            exec_aritmetic(instElem)
            pc += 1

        elif re.fullmatch(r'^IDIV$', instr, re.IGNORECASE):
            exec_aritmetic(instElem)
            pc += 1

        elif re.fullmatch(r'^LT$', instr, re.IGNORECASE):
            exec_relational(instElem)
            pc += 1

        elif re.fullmatch(r'^GT$', instr, re.IGNORECASE):
            exec_relational(instElem)
            pc += 1

        elif re.fullmatch(r'^EQ$', instr, re.IGNORECASE):
            exec_relational(instElem)
            pc += 1

        elif re.fullmatch(r'^AND$', instr, re.IGNORECASE):
            exec_rel_bool(instElem)
            pc += 1

        elif re.fullmatch(r'^OR$', instr, re.IGNORECASE):
            exec_rel_bool(instElem)
            pc += 1

        elif re.fullmatch(r'^NOT$', instr, re.IGNORECASE):
            exec_rel_bool(instElem)
            pc += 1

        elif re.fullmatch(r'^INT2CHAR$', instr, re.IGNORECASE):
            exec_int2char_or_strlen(instElem)
            pc += 1

        elif re.fullmatch(r'^STRI2INT$', instr, re.IGNORECASE):
            exec_stri2int_or_concat(instElem)
            pc += 1

        ## ********************** VSTUPNO-VYSTUPNE INSTRUKCIE *********************** ##
        elif re.fullmatch(r'^READ$', instr, re.IGNORECASE):
            exec_read(instElem)
            pc += 1

        elif re.fullmatch(r'^WRITE$', instr, re.IGNORECASE):
            exec_write(instElem)
            pc += 1

        ## *************************** PRACA S RETAZCAMI **************************** ##
        elif re.fullmatch(r'^CONCAT$', instr, re.IGNORECASE):
            exec_stri2int_or_concat(instElem)
            pc += 1

        elif re.fullmatch(r'^STRLEN$', instr, re.IGNORECASE):
            exec_int2char_or_strlen(instElem)
            pc += 1

        elif re.fullmatch(r'^GETCHAR|SETCHAR$', instr, re.IGNORECASE):
            exec_set_or_get_char(instElem)
            pc += 1

        ## ***************************** PRACA S TYPMI ****************************** ##
        elif re.fullmatch(r'^TYPE$', instr, re.IGNORECASE):
            exec_type(instElem)
            pc += 1

        ## ***************** INSTRUKCIE PRE RIADENIE TOKU PROGRAMU ****************** ##
        elif re.fullmatch(r'^LABEL$', instr, re.IGNORECASE):
            jumping = False                                     ## Vynulovanie 'jumping' po skoku.
            pc += 1

        elif re.fullmatch(r'^JUMP$', instr, re.IGNORECASE):
            jumpTo = instElem.find('arg1').text                 ## Navestie, na ktore sa bude skakat.
            jumping = True

        elif re.fullmatch(r'^JUMPIFEQ$', instr, re.IGNORECASE):

            isEQ = exec_equal(instElem)
            if isEQ is True:
                jumpTo = instElem.find("arg1").text
                jumping = True

            pc += 1

        elif re.fullmatch(r'^JUMPIFNEQ$', instr, re.IGNORECASE):

            isEQ = exec_equal(instElem)
            if isEQ is False:
                jumpTo = instElem.find("arg1").text
                jumping = True

            pc += 1

        elif re.fullmatch(r'^EXIT$', instr, re.IGNORECASE):
            exec_exit(instElem)
            pc += 1

        ## *************************** LADIACE INSTRUKCIE *************************** ##
        elif re.fullmatch(r'^DPRINT$', instr, re.IGNORECASE):
            val = get_value_from_symb(instElem.find('arg1').get('type'), instElem.find("arg1").text)
            print(val, end='', file=sys.stderr)
            pc += 1

        elif re.fullmatch(r'^BREAK$', instr, re.IGNORECASE):
            print("Aktualna pozicia kodu (hodnota instrukcneho citaca): {}", format(pc), file=sys.stderr)
            print("\nGlobalny Ramec:", file=sys.stderr)
            print("\t", gFrame, file=sys.stderr)
            print("\nZasobnik Lokalnych Ramcov:", file=sys.stderr)
            print("\t", stackFrame, file=sys.stderr)
            print("\nDocasny Ramec (definovany: {}):", format(tmpFrameDef), file=sys.stderr)
            print("\t", tmpFrame, file=sys.stderr)
            print("\nDatovy Zasobnik:", file=sys.stderr)
            print("\t", stackData, file=sys.stderr)
            print("\nMaximalny pocet definovanych premennych: {}", format(maxvars), file=sys.stderr)
            pc += 1

    make_stati()            ## STATI

if __name__ == '__main__':
    main()
