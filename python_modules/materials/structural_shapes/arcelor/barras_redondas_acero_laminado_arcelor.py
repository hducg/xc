
import math

redondos={}

redondos['R10']= {'nmb': "R10", 'd': 10e-3, 'r': 5e-3, 'P': 0.617, 'A': 0.785e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R12']= {'nmb': "R12", 'd': 12e-3, 'r': 6e-3, 'P': 0.888, 'A': 1.13e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R14']= {'nmb': "R14", 'd': 14e-3, 'r': 7e-3, 'P': 1.21, 'A': 1.54e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R16']= {'nmb': "R16", 'd': 16e-3, 'r': 8e-3, 'P': 1.58, 'A': 2.01e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R18']= {'nmb': "R18", 'd': 18e-3, 'r': 9e-3, 'P': 2, 'A': 2.54e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R20']= {'nmb': "R20", 'd': 20e-3, 'r': 10e-3, 'P': 2.47, 'A': 3.14e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R22']= {'nmb': "R22", 'd': 22e-3, 'r': 11e-3, 'P': 2.98, 'A': 3.8e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R22_25']= {'nmb': "R22_25", 'd': 22.25e-3, 'r': 11.125e-3, 'P': 3.05, 'A': 3.89e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R23_6']= {'nmb': "R23_6", 'd': 23.6e-3, 'r': 11.8e-3, 'P': 3.43, 'A': 4.37e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R24']= {'nmb': "R24", 'd': 24e-3, 'r': 12e-3, 'P': 3.55, 'A': 4.52e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R24_5']= {'nmb': "R24_5", 'd': 24.5e-3, 'r': 12.25e-3, 'P': 3.7, 'A': 4.71e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R25']= {'nmb': "R25", 'd': 25e-3, 'r': 12.5e-3, 'P': 3.85, 'A': 4.91e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R26']= {'nmb': "R26", 'd': 26e-3, 'r': 13e-3, 'P': 4.17, 'A': 5.31e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R26_7']= {'nmb': "R26_7", 'd': 26.7e-3, 'r': 13.35e-3, 'P': 4.4, 'A': 5.6e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R27']= {'nmb': "R27", 'd': 27e-3, 'r': 13.5e-3, 'P': 4.49, 'A': 5.73e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R28']= {'nmb': "R28", 'd': 28e-3, 'r': 14e-3, 'P': 4.83, 'A': 6.16e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R29']= {'nmb': "R29", 'd': 29e-3, 'r': 14.5e-3, 'P': 5.19, 'A': 6.61e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R29_5']= {'nmb': "R29_5", 'd': 29.5e-3, 'r': 14.75e-3, 'P': 5.37, 'A': 6.83e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R29_7']= {'nmb': "R29_7", 'd': 29.7e-3, 'r': 14.85e-3, 'P': 5.44, 'A': 6.93e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R30']= {'nmb': "R30", 'd': 30e-3, 'r': 15e-3, 'P': 5.55, 'A': 7.07e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R31']= {'nmb': "R31", 'd': 31e-3, 'r': 15.5e-3, 'P': 5.92, 'A': 7.55e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R32']= {'nmb': "R32", 'd': 32e-3, 'r': 16e-3, 'P': 6.31, 'A': 8.04e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R34']= {'nmb': "R34", 'd': 34e-3, 'r': 17e-3, 'P': 7.13, 'A': 9.08e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R34_4']= {'nmb': "R34_4", 'd': 34.4e-3, 'r': 17.2e-3, 'P': 7.3, 'A': 9.29e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R35']= {'nmb': "R35", 'd': 35e-3, 'r': 17.5e-3, 'P': 7.55, 'A': 9.62e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R35_7']= {'nmb': "R35_7", 'd': 35.7e-3, 'r': 17.85e-3, 'P': 7.86, 'A': 10e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R36']= {'nmb': "R36", 'd': 36e-3, 'r': 18e-3, 'P': 7.99, 'A': 10.2e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R37']= {'nmb': "R37", 'd': 37e-3, 'r': 18.5e-3, 'P': 8.44, 'A': 10.8e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R38']= {'nmb': "R38", 'd': 38e-3, 'r': 19e-3, 'P': 8.9, 'A': 11.3e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R39']= {'nmb': "R39", 'd': 39e-3, 'r': 19.5e-3, 'P': 9.38, 'A': 11.9e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R39_2']= {'nmb': "R39_2", 'd': 39.2e-3, 'r': 19.6e-3, 'P': 9.47, 'A': 12.1e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R40']= {'nmb': "R40", 'd': 40e-3, 'r': 20e-3, 'P': 9.86, 'A': 12.6e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R42']= {'nmb': "R42", 'd': 42e-3, 'r': 21e-3, 'P': 10.9, 'A': 13.9e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R44']= {'nmb': "R44", 'd': 44e-3, 'r': 22e-3, 'P': 11.9, 'A': 15.2e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R45']= {'nmb': "R45", 'd': 45e-3, 'r': 22.5e-3, 'P': 12.5, 'A': 15.9e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R46']= {'nmb': "R46", 'd': 46e-3, 'r': 23e-3, 'P': 13, 'A': 16.6e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R47']= {'nmb': "R47", 'd': 47e-3, 'r': 23.5e-3, 'P': 13.6, 'A': 17.3e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R48']= {'nmb': "R48", 'd': 48e-3, 'r': 24e-3, 'P': 14.2, 'A': 18.1e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R49_2']= {'nmb': "R49_2", 'd': 49.2e-3, 'r': 24.6e-3, 'P': 14.9, 'A': 19e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R50']= {'nmb': "R50", 'd': 50e-3, 'r': 25e-3, 'P': 15.4, 'A': 19.6e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R51']= {'nmb': "R51", 'd': 51e-3, 'r': 25.5e-3, 'P': 16, 'A': 20.4e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R52']= {'nmb': "R52", 'd': 52e-3, 'r': 26e-3, 'P': 16.7, 'A': 21.2e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R53']= {'nmb': "R53", 'd': 53e-3, 'r': 26.5e-3, 'P': 17.3, 'A': 22.1e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R54']= {'nmb': "R54", 'd': 54e-3, 'r': 27e-3, 'P': 18, 'A': 22.9e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R55']= {'nmb': "R55", 'd': 55e-3, 'r': 27.5e-3, 'P': 18.7, 'A': 23.8e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R55_8']= {'nmb': "R55_8", 'd': 55.8e-3, 'r': 27.9e-3, 'P': 19.2, 'A': 24.5e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R56']= {'nmb': "R56", 'd': 56e-3, 'r': 28e-3, 'P': 19.3, 'A': 24.6e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R57']= {'nmb': "R57", 'd': 57e-3, 'r': 28.5e-3, 'P': 20, 'A': 25.5e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R58']= {'nmb': "R58", 'd': 58e-3, 'r': 29e-3, 'P': 20.7, 'A': 26.4e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R59']= {'nmb': "R59", 'd': 59e-3, 'r': 29.5e-3, 'P': 21.5, 'A': 27.3e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R60']= {'nmb': "R60", 'd': 60e-3, 'r': 30e-3, 'P': 22.2, 'A': 28.3e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R62']= {'nmb': "R62", 'd': 62e-3, 'r': 31e-3, 'P': 23.7, 'A': 30.2e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R63']= {'nmb': "R63", 'd': 63e-3, 'r': 31.5e-3, 'P': 24.5, 'A': 31.2e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R65']= {'nmb': "R65", 'd': 65e-3, 'r': 32.5e-3, 'P': 26, 'A': 33.2e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R70']= {'nmb': "R70", 'd': 70e-3, 'r': 35e-3, 'P': 30.2, 'A': 38.5e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R75']= {'nmb': "R75", 'd': 75e-3, 'r': 37.5e-3, 'P': 34.7, 'A': 44.2e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R80']= {'nmb': "R80", 'd': 80e-3, 'r': 40e-3, 'P': 39.5, 'A': 50.3e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R85']= {'nmb': "R85", 'd': 85e-3, 'r': 42.5e-3, 'P': 44.5, 'A': 56.7e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R90']= {'nmb': "R90", 'd': 90e-3, 'r': 45e-3, 'P': 49.9, 'A': 63.6e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R95']= {'nmb': "R95", 'd': 95e-3, 'r': 47.5e-3, 'P': 55.6, 'A': 70.9e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R100']= {'nmb': "R100", 'd': 100e-3, 'r': 50e-3, 'P': 61.7, 'A': 78.5e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R105']= {'nmb': "R105", 'd': 105e-3, 'r': 52.5e-3, 'P': 68, 'A': 86.6e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R110']= {'nmb': "R110", 'd': 110e-3, 'r': 55e-3, 'P': 74.6, 'A': 95e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R120']= {'nmb': "R120", 'd': 120e-3, 'r': 60e-3, 'P': 88.8, 'A': 113e-4, 'E': 210000e6, 'nu': 0.3}
redondos['R130']= {'nmb': "R130", 'd': 130e-3, 'r': 65e-3, 'P': 104, 'A': 133e-4, 'E': 210000e6, 'nu': 0.3}

for item in redondos:
  profile= redondos[item]
  A= profile['A']
  E= profile['E']
  nu= profile['nu']
  r= profile['r']
  Iz= math.pi*r**4/4.0
  Iy= Iz
  profile['alpha']= 0.5*5/6.0
  profile['G']= E/(2*(1+nu))
  profile['AreaQy']=  9/10*A
  profile['AreaQz']=  9/10*A
  profile['Iz']= Iz
  profile['Iy']= Iy
  profile['iz']= Iz/r
  profile['iy']= Iy/r
  profile['Wzel']= Iz/r
  profile['Wyel']= Iy/r
  profile['Wypl']= 4.0*r**3/3.0
  profile['Wzpl']= 4.0*r**3/3.0
  profile['J']= math.pi*r**4/2.0

