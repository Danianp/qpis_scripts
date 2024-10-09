from qgis.core import *
from qgis.gui import *

# Wybieranie aktywnej warstwy
warstwa = iface.activeLayer()

# Sprawdzanie, czy istnieje kolumna 'dlugosc', i dodawanie jej, jeśli nie istnieje
if 'dlugosc' not in warstwa.fields().names():
    pv = warstwa.dataProvider()
    pv.addAttributes([QgsField('dlugosc', QVariant.Double)])
    warstwa.updateFields()

# Tworzenie wyrażenia do obliczania długości
expression = QgsExpression('round($length, 4)') #Obliczenie dlugosci do 4 miejsc po przecinku
print(expression)
context = QgsExpressionContext() 
context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(warstwa))

# Edytowanie warstwy i obliczanie dlugosci
with edit(warstwa):
    for f in warstwa.getFeatures():
        context.setFeature(f)
        dlugosc_m = expression.evaluate(context)
        f['dlugosc'] = dlugosc_m
        print(dlugosc_m) #Wyswietlenie dlugosci
        warstwa.updateFeature(f) #Zaktualizowanie wartosci
