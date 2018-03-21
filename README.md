# GML filer til Tinglysningen

Dette plugin kan bruges til at generere de nødvendige filer og kortbilag til Tinglysning.dk. Plugin'et kan generere en gml fil med de attributter, der bliver valgt, samt et kortbilag i enten pdf, jpg eller png format.

Der er to faneblad - *Data* og *Kortbilag*

## Data

I dette faneblad indtaster/vælger brugeren de attributter, der passer til den pågældende tinglysning.

Under *Producent info*, skal man indtaster CVR nummer og navnet på din organisation. Disse Informationer bliver gemt i settings, så næste gang plugin'et åbnes, så husker den, hvad der skal stå der.

Under *Gem GML fil* skal brugeren foretage nogle valg, før plugin'et kan bruges.

1. *Vælg lag til konvertering*
..- Her skal man vælge det lag fra lagpanelet, som indeholder den geometri, der skal tinglyses.

2. *Vælg matrikellag*
..- Her skal man vælge, hvilket lag fra lagpanelet indeholder matriklerne. 

**Hvis indeholdet af drop down menuerne ikke afspejler det, der bliver vist i lagvinduet, så kan man klikke på _efresh lister_**

3. *Vælg kolonner*
  - Her skal man angive, hvilke kolonner i matrikellaget indeholder matrikelnumre og ejerlavsnavn. De værdier bliver brugt til navngivning af kortbilag.

Til sidst skal man vælge placering af sin GML fil. Det er også den sti, hvor evt. kortbilag bliver gemt.

## Kortbilag

Her kan man lave et kortbilag, som skal følge med gml filen.

Under *Info* skal man udfylde tre værdier. Disse værdier kommer med på kortbilaget.

1. *Vedrørende*
  - Kort fortalt hvad tinglysningen drejer sig om. Skal ikke være en lang fortælling, men et enkelt ord eller to.
2. *Matrikelnumre*
  - Hvilke matrikler geometrien berører. Bliver automatisk udfyldt efter brugeren gemmer en GML fil.
3. *Ejerlav*
  - Hvilket ejerlav matriklen tilhører. Bliver også autmatisk udfyldt.

Under *Vælg format* skal man vælge, hvilket format man ønsker sit kortbilag. Der er sat kryds ved *PDF*, fordi det er det format, man kan uploade til tinglysning.dk.

Under *Målestok* kan man angive et målestoksforhold for sit kortbilag. Hvis man ikke angiver et målestoksforhold, så bruger plugin'et det målestoksforhold, der er angivet for kortvinduet i QGIS.
