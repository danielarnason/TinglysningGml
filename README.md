# GML filer til Tinglysningen

Dette plugin kan bruges til at generere de n�dvendige filer og kortbilag til Tinglysning.dk. Plugin'et kan generere en gml fil med de attributter, der bliver valgt, samt et kortbilag i enten pdf, jpg eller png format.

Der er to faneblad - *Data* og *Kortbilag*

## Data

I dette faneblad indtaster/v�lger brugeren de attributter, der passer til den p�g�ldende tinglysning.

Under *Producent info*, skal man indtaster CVR nummer og navnet p� din organisation. Disse Informationer bliver gemt i settings, s� n�ste gang plugin'et �bnes, s� husker den, hvad der skal st� der.

Under *Gem GML fil* skal brugeren foretage nogle valg, f�r plugin'et kan bruges.

1. *V�lg lag til konvertering*
..- Her skal man v�lge det lag fra lagpanelet, som indeholder den geometri, der skal tinglyses.

2. *V�lg matrikellag*
..- Her skal man v�lge, hvilket lag fra lagpanelet indeholder matriklerne. 

**Hvis indeholdet af drop down menuerne ikke afspejler det, der bliver vist i lagvinduet, s� kan man klikke p� _efresh lister_**

3. *V�lg kolonner*
  - Her skal man angive, hvilke kolonner i matrikellaget indeholder matrikelnumre og ejerlavsnavn. De v�rdier bliver brugt til navngivning af kortbilag.

Til sidst skal man v�lge placering af sin GML fil. Det er ogs� den sti, hvor evt. kortbilag bliver gemt.

## Kortbilag

Her kan man lave et kortbilag, som skal f�lge med gml filen.

Under *Info* skal man udfylde tre v�rdier. Disse v�rdier kommer med p� kortbilaget.

1. *Vedr�rende*
  - Kort fortalt hvad tinglysningen drejer sig om. Skal ikke v�re en lang fort�lling, men et enkelt ord eller to.
2. *Matrikelnumre*
  - Hvilke matrikler geometrien ber�rer. Bliver automatisk udfyldt efter brugeren gemmer en GML fil.
3. *Ejerlav*
  - Hvilket ejerlav matriklen tilh�rer. Bliver ogs� autmatisk udfyldt.

Under *V�lg format* skal man v�lge, hvilket format man �nsker sit kortbilag. Der er sat kryds ved *PDF*, fordi det er det format, man kan uploade til tinglysning.dk.

Under *M�lestok* kan man angive et m�lestoksforhold for sit kortbilag. Hvis man ikke angiver et m�lestoksforhold, s� bruger plugin'et det m�lestoksforhold, der er angivet for kortvinduet i QGIS.
