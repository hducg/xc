def VtkLoadNodos(setName, nmbContndr):
  nmbContndr= vtk.vtkPoints() # Definimos el conjunto de puntos a dibujar
  nSet= preprocessor.getSets.getSet(setName)
  nSet.numerate()
  print "nombre set: ",nSet.nombre
  print "num. nodos: ",nSet.getNumNodes
  nodos= nSet.getNodes
  for n in nodos:
    nmbContndr.InsertPoint(n.getIdx,coord[0],coord[1],coord[2])
  ugrid.SetPoints(nmbContndr)
