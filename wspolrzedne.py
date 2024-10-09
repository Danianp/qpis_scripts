# Importowanie niezbędnych modułów
from qgis.core import QgsProject, QgsField, QgsFeature, QgsGeometry
from PyQt5.QtCore import QVariant

# Pobranie aktywnej warstwy z interfejsu QGIS
warstwa = iface.activeLayer()

# Sprawdzenie, czy warstwa została poprawnie pobrana
if warstwa:
    # Nazwa nowego pola atrybutowego
    nazwa_pola = 'Współrzędne'

    # Sprawdzenie, czy pole już istnieje
    if warstwa.fields().indexFromName(nazwa_pola) == -1:
        # Jeśli pole nie istnieje, dodajemy je jako nowe pole typu tekstowego
        pole = QgsField(nazwa_pola, QVariant.String)
        warstwa.dataProvider().addAttributes([pole])
        warstwa.updateFields()
    else:
        # Jeśli pole już istnieje, pobierz jego indeks
        idx = warstwa.fields().indexFromName(nazwa_pola)

    # Rozpoczęcie edycji warstwy
    warstwa.startEditing()

    # Pętla po obiektach (cechach) w warstwie
    for cecha in warstwa.getFeatures():
        geometria = cecha.geometry()
        
        # Pobranie typu geometrii i współrzędnych
        typ_geometrii = geometria.wkbType()
        x = geometria.asPoint().x()
        y = geometria.asPoint().y()

        # Utworzenie tekstu współrzędnych z typem geometrii
        if typ_geometrii == QgsWkbTypes.Point:
            tekst_wspolrzednych = f'POINT({x} {y})'
        elif typ_geometrii == QgsWkbTypes.LineString:
            tekst_wspolrzednych = f'LINESTRING({x} {y})'
        # Dodaj tutaj inne typy geometrii, jeśli są potrzebne

        # Ustawienie wartości pola atrybutowego
        if 'idx' in locals():
            cecha[idx] = tekst_wspolrzednych
        else:
            cecha.setAttribute(nazwa_pola, tekst_wspolrzednych)

        # Zapisanie zmian do warstwy
        warstwa.updateFeature(cecha)

    # Zakończenie edycji warstwy
    warstwa.commitChanges()

    # Aktualizacja warstwy
    warstwa.updateExtents()
    warstwa.triggerRepaint()

    # Wyświetlenie komunikatu po zakończeniu
    print('Współrzędne z typem geometrii zostały dodane do tabeli atrybutów warstwy.')

else:
    print('Aktywna warstwa nie została znaleziona.')
