"""
Skrypt do przypisywania wartości Well-Known Binary, do kolumny 'WKB' na podstawie identyfikatora obiektu w warstwie QGIS.

Autor: [DP]
Data: [10-02-2024]

Opis:
Ten skrypt pobiera geometrię obiektów z wybranej warstwy w QGIS, generuje ich reprezentację w formie Well-Known Binary,
a następnie przypisuje te wartości do nowej kolumny 'WKB' na podstawie identyfikatora obiektu (np. 'id').

Wymagane biblioteki:
- PyQt5.QtCore
- qgis.core

Instrukcja użytkowania:
1. Uruchom QGIS.
2. Wybierz warstwę, na której chcesz przeprowadzić operację.
3. Uruchom ten skrypt w Pythonie w środowisku QGIS.

Uwagi:
- Przed uruchomieniem upewnij się, że wybrana warstwa zawiera kolumnę 'id' lub inną unikalną kolumnę identyfikacyjną.
"""

from PyQt5.QtCore import QVariant  # Importowanie niezbędnych modułów
from qgis.core import QgsField, QgsFeature, QgsGeometry


warstwa = iface.activeLayer()  # Wybór aktywnej warstwy: Pobieramy aktywną warstwę z interfejsu QGIS.
zadanie = [f for f in warstwa.getFeatures()]  # Pobranie geometrii obiektów z warstwy: Przechodzimy przez wszystkie obiekty w warstwie i pobieramy ich geometrię.

# Sprawdzenie, czy kolumna WKB już istnieje, jeśli nie, dodaj ją
if not 'WKB' in [field.name() for field in warstwa.fields()]:
    warstwa.startEditing()
    warstwa.addAttribute(QgsField('WKB', QVariant.String))
    warstwa.updateFields()

# Sprawdzenie dostępnych kolumn po próbie dodania
print("Dostępne kolumny po próbie dodania kolumny 'WKB':")
fields_after_adding = warstwa.fields()
for field in fields_after_adding:
    print(field.name())
    
#Definiowanie funkcji generatora:
def generator(lista):
    # Iteracja po obiektach
    for feature in lista:
        obj_id = feature['id']  # Pobranie wartości z kolumny 'id'
        wkb = feature.geometry().asWkb()
        test = QByteArray.toHex(wkb)  # Konwersja QByteArray do ciągu znaków
        
        # Aktualizacja wartości w kolumnie 'WKB' na podstawie 'id'
        warstwa.startEditing()
        for feat in warstwa.getFeatures():
            if feat['id'] == obj_id:
                feat['WKB'] = test
                if warstwa.updateFeature(feat):
                    print("Zaktualizowano obiekt w warstwie.")
                else:
                    print("Nie udało się zaktualizować obiektu w warstwie.")
        warstwa.commitChanges()

# Wywołanie generatora
generator(zadanie)
