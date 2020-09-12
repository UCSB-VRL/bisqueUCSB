function [genus, specie, commonName, url] = get_specie(tag)

genus='Unknown';
specie='Unknown';
commonName='Unknown';
url='Unknown';

switch tag
    case 1
        genus='Lupinus';
        specie='arboreus';
        commonName='BushLupine';
        url='http://en.wikipedia.org/wiki/Lupinus_arboreus';
    case 2
        genus='Artemisia';
        specie='californica';
        commonName='CA Coastal Sage';
        url='http://en.wikipedia.org/wiki/Artemisia_californica';
    case 3
        genus='Ambrosia';
        specie='chamissonis';
        commonName='Beach Burr';
        url='http://en.wikipedia.org/wiki/Ambrosia_chamissonis';
    case 4
        genus='Eriogonum';
        specie='fasciculatum';
        commonName='Buckwheat';
        url='http://en.wikipedia.org/wiki/Eriogonum_fasciculatum';
    case 5
        genus='Malacothamnus';
        specie='fasciculatus';
        commonName='Chaparral Mallow';
        url='http://en.wikipedia.org/wiki/Malacothamnus_fasciculatus';
    case 6
        genus='Rhus';
        specie='integrifolia';
        commonName='Lemonade Berry';
        url='http://en.wikipedia.org/wiki/Rhus_integrifolia';
    case 7
        genus='Atriplex';
        specie='lentiformis';
        commonName='Quail Bush';
        url='http://en.wikipedia.org/wiki/Atriplex_lentiformis';
    case 8
        genus='Isocoma';
        specie='menziesii';
        commonName='CA Coastal Golden Bush';
        url='http://en.wikipedia.org/wiki/Isocoma_menziesii';
    case 9
        genus='Baccharis';
        specie='pilularis';
        commonName='Coyote Bush';
        url='http://en.wikipedia.org/wiki/Baccharis_pilularis';
    case 10
        genus='Abronia';
        specie='umbellata';
        commonName='Pink sand verbena';
        url='http://en.wikipedia.org/wiki/Abronia_umbellata';
    case 11
        genus='Foeniculum';
        specie='vulgare';
        commonName='Fennel';
        url='http://en.wikipedia.org/wiki/Foeniculum_vulgare';          
end