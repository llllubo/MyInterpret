<?php
/** ******************** HLAVICKA SKRIPTU ******************** **/
/** PROJEKT 2a:     Testovaci ramec                            **/
/** VERZIA:         1.0                                        **/
/** AUTOR:          Lubos Vajcovec, xvajco00@stud.fit.vutbr.cz **/
/** DATUM:          05.04.2020                                 **/
/** PREDMET:        Principy programovacich jazykov a OOP      **/
/** ********************************************************** **/

/** Definovanie konstant **/
const ERR_OPTS = 10;
const ERR_PATH = 11;
const ERR_FINPUT = 110;
const ERR_INTERNAL = 99;

/** ------------------------------------ DEFINICIE FUNKCII ------------------------------------ **/
/**
 * Vypis napovedy HELP.
 */
function write_help() {
    fwrite(STDOUT, "POUZITIE: php7.4 test.php [--help | [--directory=path | --recursive | \n");
    fwrite(STDOUT, "\t[[--parse-script=file | --parse-only] | [--int-script=file | --int-only]] | --jexamxml=file]]\n");
    fwrite(STDOUT, "POUZITIE: php7.4 test.php [-h | [-d path | -r | [[-P file | -p] | [-I file | -i]] | -j file]]\n\n");

    fwrite(STDOUT, "MOZNE PREPINACE:\n");
    fwrite(STDOUT, "\t-h,        --help\t\tVypis napovedy HELP (ZAKAZ kombinacie s akymkolvek prepinacom).\n");

    fwrite(STDOUT, "\t-d path,   --directory=path\tExplicitne zadany adresar lokalizacii testov, inak \n");
    fwrite(STDOUT, "\t\t\t\t\tsa implicitne prechadza aktualny adresar.\n");

    fwrite(STDOUT, "\t-r,        --recursive\t\tRekurzivne vyhladavanie testov v podadresaroch daneho adresara.\n");

    fwrite(STDOUT, "\t-P file,   --parse-script=file\tSubor 'file' so skriptom pre analyzu zdrojoveho kodu v IPPcode20 \n");
    fwrite(STDOUT, "\t\t\t\t\t(implicitne je parse.php ulozeny v aktualnom adresari).\n");

    fwrite(STDOUT, "\t-I file,   --int-script=file\tSubor 'file' so skriptom pre interpret XML reprezentacie kodu v \n");
    fwrite(STDOUT, "\t\t\t\t\tIPPcode20 (implicitne je skript interpret.py ulozeny v aktualnom adresari).\n");

    fwrite(STDOUT, "\t-p,        --parse-only,\tTestovanie len skriptu parse.php (ZAKAZ kombinovat s --int-only a \n");
    fwrite(STDOUT, "\t\t\t\t\t--int-script=file), porovnanie s referencnym vystupom pomocou A7Soft JExamXML.\n");

    fwrite(STDOUT, "\t-i,        --int-only\t\tTestovanie len skriptu interpret.py (ZAKAZ kombinacie s --parse-only a \n");
    fwrite(STDOUT, "\t\t\t\t\t--parse-script=file), pricom vstupny program vo forme XML bude v subore *.src.\n");

    fwrite(STDOUT, "\t-j file,   --jexamxml=file\tCesta k JAR balicku s nastrojom A7Soft JExamXML pre porovnanie (implicitne \n");
    fwrite(STDOUT, "\t\t\t\t\tje v ceste '/pub/courses/ipp/jexamxml/jexamxml.jar' na serveri Merlin).\n\n");

    fwrite(STDOUT, "Skript test.php sluzi ako testovaci ramec skriptov parse.php a interpret.py.\n");
    fwrite(STDOUT, "Skript vyuziva poskytnuty, resp. aktualny adresar s testami pre automaticke\n");
    fwrite(STDOUT, "otestovanie spravnej funkcnosti skriptov. Vystup tohto skriptu je vygenerovany prehlad\n");
    fwrite(STDOUT, "vysledkov testov v HTML 5. Spustanie skriptu je doporucene 'php7.4' interpretom.\n\n");

    fwrite(STDOUT, "PRIKLADY (ROVNAKO PRE KRATKE VERZIE):\n");
    fwrite(STDOUT, "php7.4 test.php --help\n");
    fwrite(STDOUT, "php7.4 test.php --directory=path --recursive --parse-script=file --parse-only --jexamxml=file\n");
    fwrite(STDOUT, "php7.4 test.php --directory=path --recursive --int-script=file --int-only --jexamxml=file\n\n");

    fwrite(STDOUT, "CHYBOVE NAVRATOVE KODY:\n");
    fwrite(STDOUT, "10 - Zakazana kombinacia prepinacov alebo chybajuci parameter skriptu.\n");
    fwrite(STDOUT, "11 - Chyba pri otvarani vstupnych suborov (napr. nedostatocne opravnenie) alebo pri zadani\n");
    fwrite(STDOUT, "     neexistujuceho adresara/suboru.\n");
    fwrite(STDOUT, "99 - Interna chyba programu, napr. pri alokacii pamati.\n");
    exit(0);
}

/**
 * Vypis chyboveho hlasenia na zaklade typu chyby a ukoncenie skriptu s navratovym kodom prislusnym danej chybe.
 * @param int $errno    Unikatne cislo chyby.
 */
function write_err(int $errno) {
    switch ($errno) {
        case 10:
            fwrite(STDERR, "CHYBA! Zakazana kombinacia prepinacov.\n");
            exit(10);
        case 11:
            fwrite(STDERR, "CHYBA! Zadany adresar/skript neexistuje.\n");
            exit(11);
        case 110:
            fwrite(STDERR, "CHYBA! Nepodarilo sa otvorit vstupny subor na citanie.\n");
            exit(11);
        case 99:
            fwrite(STDERR, "CHYBA! Interna chyba programu.\n");
            exit(99);
    }
}

/**
 * Generovanie HTML kodu na uvod, zahrna vsetky dolezite znacky vratane CSS kodu.
 * HTML znacka <h1> sluzi pre vypis nadpisu v uvode stranky.
 * HTML znacka <h2> sluzi pre vypis prehladu uspesnych testov k ich celkovemu poctu.
 * HTML znacka <p> sluzi pre vypis popisu k tabulke s testami, vratane uspesnosti v danom adresari (tabulke).
 * HTML znacka <table> sluzi pre tabulku, ktorej obsahom su 2 zlozky: nazov testu a uspesnost testu.
 * Uspesne testy su zafarbene na zeleno (OK), neuspesne na cerveno (X).
 */
function start_html() {
    $GLOBALS['htmlCode'] .= "<!DOCTYPE html>\n" .
                            "<html lang=\"sk\">\n" .
                            "<head>\n" .
                            "  <meta charset=\"UTF-8\">\n" .
                            "  <meta name=\"author\" content=\"Ľuboš Vajčovec\">\n" .
                            "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n" .
                            "  <title>Výsledky testov</title>\n" .
                            "  <style>\n" .
                            "    body {\n" .
                            "      background-color: rgb(57, 19, 39);\n" .
                            "      font-family: \"Lucida Console\", Monaco, monospace;\n" .
                            "      font-size: 12px;\n" .
                            "      color: white;\n" .
                            "    }\n" .
                            "    h1 {\n" .
                            "      font-size: 32px;\n" .
                            "      text-align: center;\n" .
                            "      letter-spacing: 1px;\n" .
                            "    }\n" .
                            "    h2 {\n" .
                            "      color: rgb(255, 179, 102);\n" .
                            "      font-size: 25px;\n" .
                            "      padding: 2%;\n" .
                            "    }\n" .
                            "    p {\n" .
                            "      color: rgb(255, 255, 128);\n" .
                            "      font-size: 18px;\n" .
                            "    }\n" .
                            "    table {\n" .
                            "      border-collapse: collapse;\n" .
                            "      width: 50%;\n" .
                            "      text-align: center;\n" .
                            "      margin-left: 9%;\n" .
                            "    }\n" .
                            "    th {\n" .
                            "      background-color: rgb(41, 41, 61);\n" .
                            "      padding: 10px;\n" .
                            "    }\n" .
                            "    tr {\n" .
                            "      font-size: 15px;\n" .
                            "      height: 20px;\n" .
                            "    }\n" .
                            "    tr:hover {\n" .
                            "      background-color: rgb(41, 41, 61);\n" .
                            "    }\n" .
                            "    .DIR {\n" .
                            "      color: white;\n" .
                            "    }\n" .
                            "    .OK {\n" .
                            "      color: rgb(0, 153, 0);\n" .
                            "    }\n" .
                            "    .X {\n" .
                            "      color: rgb(230, 0, 0);\n" .
                            "    }\n" .
                            "  </style>\n" .
                            "</head>\n" .
                            "<body>\n" .
                            "  <h1>Súhrnný prehľad nájdených testov</h1>\n" .
                            "  <div style=\"text-align:center\">Ľuboš Vajčovec | xvajco00 | IPP | VUT FIT 2020</div>\n";
}

/**
 * Generovanie celkoveho prehladu testov, pocet_uspesnych_testov/pocet_spustenych_testov a percentualne vyjadrenie.
 * @param int $numofOKs     Celkovy pocet uspesnych testov.
 * @param int $numofTests   Celkovy pocet spustenych testov.
 */
function summary_html(int $numofOKs, int $numofTests) {
    if ($numofTests == 0)
        $per = 100;
    else
        $per = round(($numofOKs/$numofTests)*100, 2);

    $GLOBALS['htmlCode'] .= "  <h2>SPOLU: $numofOKs/$numofTests \n" .
                            "    <span style=\"font-size:small\">($per%)</span>\n" .
                            "  </h2>\n";
}

/**
 * Generovanie (HTML kodu) popisu k tabulke s testami, ktory obsahuje nazvov adresara a celkove vyhodnotenie testov v ramci adresara.
 * @param string $dirPath       Cesta K adresaru, v ktorom sa budu hladat testy.
 * @param int    $okTests       Pocet uspesnych testov v ramci adresara.
 * @param int    $foundTests    Pocet najdenych testov v ramci adresara.
 */
function caption_html(string $dirPath, int $okTests, int $foundTests) {
    $per = round(($okTests/$foundTests)*100, 2);
    $GLOBALS['htmlTables'] .= "  <p>\n" .
                              "    Adresár:&emsp;\n" .
                              "    <span class=\"DIR\">$dirPath</span>\n" .
                              "    &emsp;&emsp;$okTests/$foundTests \n" .
                              "    <span style=\"font-size:12px\">($per%)</span>\n" .
                              "  </p>\n" .
                              "  <table>\n" .
                              "    <tr>\n" .
                              "      <th>Názov testu</th>\n" .
                              "      <th>Výsledok testu</th>\n" .
                              "    </tr>\n";
}

/**
 * Generovanie (HTML kodu) riadku v tabulke testov na zaklade vysledku testu.
 * @param string $testName  Nazov testu (testovacieho suboru).
 * @param string $result    Vysledok testu (OK | X).
 */
function test_html(string $testName, string $result) {
    $GLOBALS['htmlTables'] .= "    <tr>\n" .
                              "      <td>$testName</td>\n" .
                              "      <td class=\"$result\">$result</td>\n" .
                              "    </tr>\n";
}

/**
 * Generovanie konca tabulky s testami pre dany adresar, pouzite po poslednom volani funkcie 'test_html()' pre dany adresar.
 */
function end_table_html() {
    $GLOBALS['htmlTables'] .= "  </table>\n";
}

/**
 * Generovanie tabuliek s vysledkami testov k prislusnym adresarom a celkovou uspesnostou v nich.
 * @param array $arrTests   Pole s adresarmi (DIR_PATH => DIR) a testami (TEST_PATH => OK | X).
 */
function captions_tables_html(array $arrTests) {
    $dir = '';                                      /// Aktualny adresar, v ktorom sa nachadzaju testy.
    $OKdirTestsCnt = 0;                             /// Pocitadlo OK testov v adresari.
    $dirTestsCnt = 0;                               /// Pocitadlo testov v ramci adresara.
    $arrDirTests = array();                         /// Pole pre testy v ramci adresara.
    foreach ($arrTests as $testPath => $value) {
        if ($value == 'OK' || $value == 'X') {
            $GLOBALS['testsCnt'] += 1;              /// Celkovy pocet testov.
            $dirTestsCnt += 1;
            if ($value == 'OK') {
                $OKdirTestsCnt += 1;
                $GLOBALS['OKtestsCnt'] += 1;        /// Celkovy pocet OK testov.
            }
            $arrDirTests[mb_substr(mb_strrchr($testPath, "/"), 1)] = $value;     /// Do pola pridava len nazov testu, bez cesty k nemu.
        }
        elseif ($value == 'DIR') {
            if (count($arrDirTests) != 0) {
                ksort($arrDirTests);                /// Radenie abecedne vzostupne podla kluca v poli.
                caption_html($dir, $OKdirTestsCnt, $dirTestsCnt);
                foreach ($arrDirTests as $test => $res) {
                    test_html($test, $res);
                }
                end_table_html();

                $OKdirTestsCnt = 0;
                $dirTestsCnt = 0;
                $arrDirTests = array();             /// Premazanie pola s testami pre adresar.
            }
            $dir = $testPath;
        }
    }
    /// Vypis posledneho prejdeneho adresara.
    if (count($arrDirTests) != 0) {
        ksort($arrDirTests);
        caption_html($dir, $OKdirTestsCnt, $dirTestsCnt);
        foreach ($arrDirTests as $test => $res) {
            test_html($test, $res);
        }
        end_table_html();
    }
}

/**
 * Generovanie ukoncujucich HTML znaciek do retazca pre HTML kod.
 */
function end_html() {
    $GLOBALS['htmlCode'] .= "</body>\n" .
                            "</html>\n";
}

/**
 * Automaticke dogenerovanie chybajucich suborov k danemu testu.
 * @param string $dirPath   Cesta adresara.
 * @param string $fileName  Nazov suboru bez jeho pripony (nazov testu).
 */
function gen_missing_files(string $dirPath, string $fileName) {
    /// Vstupny subor *.in je nutny len pre 'interpret.py'.
    if (!$GLOBALS['parseOnly'] && !is_file("$dirPath/$fileName.in")) {
        if (($file = fopen("$dirPath/$fileName.in", "w+")) === false)
            write_err(ERR_INTERNAL);
        fclose($file);
    }
    if(!is_file("$dirPath/$fileName.out")) {
        if (($file = fopen("$dirPath/$fileName.out", "w+")) === false)
            write_err(ERR_INTERNAL);
        fclose($file);
    }
    if (!is_file("$dirPath/$fileName.rc")) {
        if (($file = fopen("$dirPath/$fileName.rc", "w+")) === false)
            write_err(ERR_INTERNAL);
        fwrite($file, "0");
        fclose($file);
    }
}

/**
 * Ziskanie ocakavaneho navratoveho kodu zo suboru '*.rc' k danemu testu.
 * @param  string $dirPath   Cesta aktualneho adresara.
 * @param  string $fileName  Nazov aktualneho testu.
 * @return string            Ciselna hodnota zo suboru, ocakavany navratovy kod pre dany test.
 */
function get_rc(string $dirPath, string $fileName) {
    if (($rcExpected = file_get_contents("$dirPath/$fileName.rc")) === false)
        write_err(ERR_FINPUT);
    $rcExpected = trim($rcExpected);        /// Odstranenie neziaducich bielych znakov.
    return $rcExpected;
}

/**
 * Kontrola vystupu z analyzatora pomocou nastroja A7Soft JExamXML, v pripade Parse-Only testovania.
 * @param string $dirPath       Cesta aktualneho adresara.
 * @param string $fileName      Nazov aktualneho testu.
 * @param int    $rcParse       Navratovy kod z analyzatora.
 * @param string $rcExpected    Navratovy kod zo suboru '*.rc' k danemu testu.
 * @param string $fileMyOut     Unikatny nazov docasneho suboru k aktualnemu testu.
 */
function check_parseOnly_output(string $dirPath, string $fileName, int $rcParse, string $rcExpected, string $fileMyOut) {
    /// Ziskany ocakavany 'rc' a zaroven spravne ukoncenie 'parse.php'.
    if ($rcParse == $rcExpected && $rcParse == 0) {
        exec("java -jar " . $GLOBALS['jexamPath'] . " $dirPath/$fileName.out $fileMyOut diffs.xml /D /pub/courses/ipp/jexamxml/options", $arrOutJExam, $rcJExam);
        exec("rm -f diffs.xml");             /// Nie je potreba suboru 'diffs.xml', no pre spustenie je nutne ho uvadzat.

        /// Vystup sa zhoduje s referencnym vystupom.
        if ($rcJExam == 0) {
            $GLOBALS['arrTests']["$dirPath/$fileName"] = "OK";
        }
        /// Vystup sa nezhoduje s referencnym.
        else {
            $GLOBALS['arrTests']["$dirPath/$fileName"] = "X";
        }
    }
    /// Ziskany ocakavany 'rc', no nie je to nula.
    elseif ($rcParse == $rcExpected) {
        $GLOBALS['arrTests']["$dirPath/$fileName"] = "OK";
    }
    /// Nebol ziskany ocakavany 'rc'.
    else {
        $GLOBALS['arrTests']["$dirPath/$fileName"] = "X";
    }
}

/**
 * Kontrola vystupu Interpretu pomocou Shell nastroja diff, v pripade testovania Int-Only alebo oboch skriptov.
 * @param string $dirPath   Cesta aktualneho adresara.
 * @param string $fileName  Nazov aktualneho testu.
 * @param int    $rcInt     Navratovy kod z Interpretu.
 * @param string $fileMyOut Unikatny nazov docasneho suboru k aktualnemu testu.
 */
function check_int_output(string $dirPath, string $fileName, int $rcInt, string $fileMyOut) {
    $rcExpected = get_rc($dirPath, $fileName);

    /// Interpret sa ukoncil spravne s ocakavanym 'rc' => porovnanie vystupu s referencnym.
    if ($rcExpected == $rcInt && $rcInt == 0) {
        exec("diff $dirPath/$fileName.out $fileMyOut", $arrOutDiff, $rcDiff);
        if ($rcDiff == 0) {
            $GLOBALS['arrTests']["$dirPath/$fileName"] = "OK";
        }
        else {
            $GLOBALS['arrTests']["$dirPath/$fileName"] = "X";
        }
    }
    /// 'rc' je ocakavany, no nie je nula - uspech.
    elseif ($rcExpected == $rcInt) {
        $GLOBALS['arrTests']["$dirPath/$fileName"] = "OK";
    }
    /// Bol ziskany neocakavany 'rc' - neuspech.
    else {
        $GLOBALS['arrTests']["$dirPath/$fileName"] = "X";
    }
}

/**
 * Hlavna cinnost skriptu. Najdenie a spustenie testov, porovnanie vysledkov testov.
 * Ak potrebne, tak rekurzivne prehladavanie podadresarov zadaneho adresara.
 * Po skonceni funkcie je pole 'arrTests' naplnene hodnotami: cesta_k_testu => vysledok_testu,
 * v pripade, ze ide o adresar, tak cesta_k_adresaru => DIR.
 * @param string $dirPath   Cesta prehladavaneho adresara.
 */
function make_tests(string $dirPath) {
    $dirFiles = scandir($dirPath);
    $dirFiles = array_diff($dirFiles, array('.', '..'));
    $GLOBALS['arrTests']["$dirPath"] = "DIR";                   /// Pridanie adresara do pola testov, aby k nim bolo mozne zaradit testy spravne.

    foreach ($dirFiles as $file) {
        if ($GLOBALS['recurs'] && is_dir("$dirPath/$file")) {   /// Rekurzivne prehladavanie adresara, zadany prepinac --recursive.
            make_tests("$dirPath/$file");
        }
        elseif (mb_ereg_match('^.*\.src$', $file) !== false) {   /// Nasiel sa subor '*.src', moze sa spustit dany test.

            if (($fileName = mb_ereg_replace('\.src$', '', $file)) === false)    /// Ziskanie nazvu testu kvoli dalsej kontrole.
                write_err(ERR_INTERNAL);
            gen_missing_files($dirPath, $fileName);             /// Automaticke vygenerovanie chybajucich suborov pre jednotlivy test.

            $fileMyOut = tempnam("$dirPath", "$fileName.out."); /// Vygenerovanie docasneho suboru pre vystup zo skriptu s unikatnym nazvom k danemu testu.

            /// Testuje sa len 'interpret.py'.
            if ($GLOBALS['intOnly']) {
                exec("python3.8 " . $GLOBALS['intPath'] . " --source=$dirPath/$fileName.src --input=$dirPath/$fileName.in >$fileMyOut" , $arrOutInt, $rcInt);
            }
            /// Analyzator sa spusta v pripade, ze sa netestuje LEN 'interpret.py'.
            else {
                exec("php7.4 " . $GLOBALS['parsePath'] . " <$dirPath/$fileName.src >$fileMyOut", $arrOutParse, $rcParse);

                $rcExpected = get_rc($dirPath, $fileName);   /// Ziskanie ocakavaneho 'rc' zo suboru '*.rc', pri neuspechu chyba (11).

                if ($GLOBALS['parseOnly']) {
                    check_parseOnly_output($dirPath, $fileName, $rcParse, $rcExpected, $fileMyOut);
                    exec("rm -f $fileMyOut");                /// Odstranenie docasneho suboru.
                    continue;                                /// Koniec testu --parse-only.
                }
                /// Ide o testovanie oboch skriptov - vystup z 'parse.php' na vstupe pre 'interpret.py'.
                elseif ($rcParse == 0) {
                    exec("python3.8 " . $GLOBALS['intPath'] . " --source=$fileMyOut --input=$dirPath/$file.in >$fileMyOut", $arrOutInt, $rcInt);
                }
                /// Ide o testovanie oboch skriptov, 'parse.php' sa neukoncil s 'rc' nula, ale s inym, no ocakavanym 'rc'.
                elseif ($rcParse == $rcExpected) {
                    $GLOBALS['arrTests']["$dirPath/$fileName"] = "OK";
                    exec("rm -f $fileMyOut");                /// Odstranenie docasneho suboru.
                    continue;                                /// Koniec testu oboch skriptov, uspesne uz pri 'parse.php'.
                }
                /// Analyzator zlyhal.
                else {
                    $GLOBALS['arrTests']["$dirPath/$fileName"] = "X";
                    exec("rm -f $fileMyOut");                /// Odstranenie docasneho suboru.
                    continue;                                /// Koniec testu oboch skriptov, neuspesne.
                }
            }
            check_int_output($dirPath, $fileName, $rcInt, $fileMyOut);  /// Porovnanie vystupu interpretu pre test oboch skriptov alebo '--int-only'.
            exec("rm -f $fileMyOut");                                   /// Odstranenie docasneho suboru.
        }
    }
}

/** -------------------------------------- HLAVNY PROGRAM -------------------------------------- **/

/*
 * Pociatocna inicializacia globalnych premennych.
 */
$arrOpt = array();                      /// Pole obsahujuce ziskane prepinace z prikazoveho riadku.
$numofOpts = 0;                         /// Pocet ziskanych argumentov prikazoveho riadku.
$dirPath = getcwd();                    /// => Implicitna hodnota - aktualny adresar; Cesta adresara s testami.
$recurs = false;                        /// Poziadavka na rekurzivne prehladavanie testov.
$parsePath = '';                        /// Cesta k skriptu 'parse.php'.
$intPath = '';                          /// Cesta k skriptu 'interpret.py'.
$parseOnly = false;                     /// Testovanie len parser-u.
$intOnly = false;                       /// Testovanie len interpreter-u.
$jexamPath = '';                        /// Cesta k JAR balicku s nastrojom A7Soft JExamXML.
$htmlCode = '';                         /// HTML kod pre vygenerovanie vystupnej HTML stranky.
$htmlTables = '';                       /// Docasny retazec, ukladaju sa nazvy adresarov a tabulka s testami v HTML kvoli vypisu 'SPOLU' na zaciatku stranky.
$arrTests = array();                    /// Asociativne pole obsahujuce testy s ich vysledkami (DIRPATH/TEST => OK|X, ...).
$testsCnt = 0;                          /// Pocitadlo testov v ramci vsetkych testovanych adresarov.
$OKtestsCnt = 0;                        /// Pocitadlo uspesnych testov v ramci vsetkych testovanych adresarov.

ini_set('display_errors', 'stderr');    /// Presmerovanie chybovych hlaseni na STDERR, namiesto STDOUT.
mb_internal_encoding("UTF-8");          /// Nastavenie kodovania pre regularne vyrazy na 'UTF-8'.

/*
 * Spracovanie argumentov prikazoveho riadku.
 */
if (($arrOpt = getopt('hd:rP:I:pij:', array('help', 'directory:', 'recursive', 'parse-script:',
                                          'int-script:', 'parse-only', 'int-only', 'jexamxml:'))) === false)
    write_err(ERR_INTERNAL);

$numofOpts = sizeof($arrOpt, COUNT_RECURSIVE);
foreach ($arrOpt as $opt) {                     /// Uprava poctu prepinacov v pripade ich opakovania.
    if (is_array($opt))
        $numofOpts -= 1;
}

/*
 * Kontrola jednotlivych parametrov a ziskanie pripadnych hodnot.
 */
foreach ($arrOpt as $opt => $optVal) {
    if ($opt == 'help' || $opt == 'h') {
        if ($numofOpts != 1)
            write_err(ERR_OPTS);
        write_help();
    }
    elseif ($opt == 'directory' || $opt == 'd') {
        if (!is_dir($optVal))                      /// Kontrola existencie zadaneho adresara s testami.
            write_err(ERR_PATH);
        $dirPath = realpath($optVal);              /// Doplnenie celej cesty k zadanemu adresaru.
    }
    elseif ($opt == 'recursive' || $opt == 'r') {
        $recurs = true;
    }
    elseif ($opt == 'parse-script' || $opt == 'P') {
        if ($intOnly == true)
            write_err(ERR_OPTS);

        if (is_file($optVal) === false)
            write_err(ERR_PATH);
        $parsePath = realpath($optVal);
    }
    elseif ($opt == 'int-script' || $opt == 'I') {
        if ($parseOnly == true)
            write_err(ERR_OPTS);

        if (is_file($optVal) === false)
            write_err(ERR_PATH);
        $intPath = realpath($optVal);
    }
    elseif ($opt == 'parse-only' || $opt == 'p') {
        if ($intOnly == true || $intPath != '')
            write_err(ERR_OPTS);
        $parseOnly = true;
    }
    elseif ($opt == 'int-only' || $opt == 'i') {
        if ($parseOnly == true || $parsePath != '')
            write_err(ERR_OPTS);
        $intOnly = true;
    }
    elseif ($opt == 'jexamxml' || $opt == 'j') {
        if (is_file($optVal) === false)
            write_err(ERR_PATH);
        $jexamPath = realpath($optVal);
    }
}

/// V pripade nezadanej cesty k skriptom explicitne, vezmu sa implicitne hodnoty.
if ($parsePath == '')
    $parsePath = getcwd() . '/parse.php';                   /// => Implicitna hodnota - aktualny adresar; Cesta k skriptu 'parse.php'.
if ($intPath == '')
    $intPath = getcwd() . '/interpret.py';                  /// => Implicitna hodnota - aktualny adresar; Cesta k skriptu 'interpret.py'.
if ($jexamPath == '')
    $jexamPath = '/pub/courses/ipp/jexamxml/jexamxml.jar';  /// => Implicitne umiestnenie; Cesta k JAR balicku s nastrojom A7Soft JExamXML.

start_html();                               /// Generovanie zaciatku HTML 5 kodu (DOCTYPE, html, head, ...).
make_tests($dirPath);                       /// Vykonanie testovania.
captions_tables_html($arrTests);            /// Tabulky s popismi sa ukladaju do docasneho retazca 'htmlTables', kvoli 'summary_html()'.
summary_html($OKtestsCnt, $testsCnt);
$htmlCode .= $htmlTables;                   /// Pripojenie tabuliek k celkovemu HTML kodu.
end_html();                                 /// Generovanie konca HTML 5 kodu (ukoncovacie tagy pre body, html).
echo "$htmlCode";                           /// Vypis HTML kodu na STDOUT.
