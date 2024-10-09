# Pobieranie aktywnej warstwy
warstwa = iface.activeLayer()

# Sprawdzenie, czy wybrana warstwa jest warstwą liniową, poligonową lub punktową
geometry_type = warstwa.geometryType()
if geometry_type not in [QgsWkbTypes.LineGeometry, QgsWkbTypes.PolygonGeometry, QgsWkbTypes.PointGeometry]:
    print("Warstwa nie jest warstwą liniową, poligonową ani punktową.")
    quit()

# Utworzenie pustej listy do przechowywania unikalnych geometrii
unikalne_geom = []
usuniete_obiekty = []

# Pętla po wybranych obiektach warstwy
for obiekt in warstwa.selectedFeatures():
    geometria = obiekt.geometry()
    
    # Sprawdzenie, czy geometria jest już w liście unikalnych geometrii
    if geometria not in unikalne_geom:
        unikalne_geom.append(geometria)
    else:
        # Dodanie identyfikatora obiektu do listy usuwanych obiektów
        usuniete_obiekty.append(obiekt.id())
        # Usunięcie duplikatu
        warstwa.dataProvider().deleteFeatures([obiekt.id()])

# Aktualizacja warstwy
warstwa.triggerRepaint()

print("Duplikaty usunięte.")
print("Usunięte obiekty o identyfikatorach:", usuniete_obiekty)
