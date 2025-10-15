#!/usr/bin/awk -f

# Script awk pour découper les lignes à 23 champs après le premier caractère du 12ème champ

BEGIN {
    FS = ",";
}

{
    if (NF == 23) {
        # Découpe le 12ème champ après le premier caractère
        first_char = substr($12, 1, 1);  # Premier caractère du 12ème champ
        rest_of_field = substr($12, 2);   # Le reste du 12ème champ

        # Construit la première ligne : champs 1 à 11 + premier caractère du 12ème champ
        line1 = $1;
        for (i = 2; i <= 11; i++) line1 = line1 "," $i;
        line1 = line1 "," first_char;
        print line1;

        # Construit la deuxième ligne : reste du 12ème champ + champs 13 à 23
        line2 = rest_of_field;
        for (i = 13; i <= NF; i++) line2 = line2 "," $i;
        print line2;
    } else {
        # Ligne normale, pas de découpage
        print $0;
    }
}
