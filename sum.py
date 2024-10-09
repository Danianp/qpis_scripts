from qgis.core import *
from qgis.gui import *

# Pobieranie aktywnej warstwy
warstwa = iface.activeLayer()

# Inicjalizacja zmiennej przechowującej sumę długości
suma_dlugosci = 0 #Zaczynamy od wartosci zero w celu przyszłej interacji po warstwie

# Iteracja po obiektach w warstwie i sumowanie długości
for f in warstwa.getFeatures():
    suma_dlugosci += f['dlugosc'] #Wybór kolumny o nazwie 'dlugosc', można zamienić pod swoją wartosc

# Dodanie wartości sumy długości do nowej kolumny
if 'suma_dlugosci' not in warstwa.fields().names():
    pv = warstwa.dataProvider()
    pv.addAttributes([QgsField('suma_dlugosci', QVariant.Double)])
    warstwa.updateFields()

idx = warstwa.fields().indexFromName('suma_dlugosci')
with edit(warstwa):
    for f in warstwa.getFeatures():
        f['suma_dlugosci'] = suma_dlugosci
        warstwa.updateFeature(f)

print("Suma dlugosci:", suma_dlugosci)
