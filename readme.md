# SelfishCA
*Cellular Automaton (CA) viewer for 2d totalistic CA.*

## Key Map
key|command
---:|:---
**ctrl-q**|quit
**space**|start / stop
**ctrl-r**|restart (randomize values)
**ctrl-n**|new CA (random rule)

## CA String Definition
Key to the CA is embedded in a string of five characters.
**position**|**character**|**options**
---:|---|---
1|grid shape code|'Q' = square, 'X' = hexagon
2|neighborhood code|'V' = Von Neuman (adjacent neighbors), 'M' = Moore (adjacent and diagonal neighbors)
3|neighborhood size|integer in range(1, 10)
4|CA type code|'T' = totalistic, 'S' = self-totalistic
5|cell value range|integer in range(2, 10)

> ex: QV1T3
> Square grid, Von Neuman neighborhood (size 1), totalistic CA with cells having values of 0 | 1 | 2
> neighborhood:
> [0 1 0]
> [1 1 1]
> [0 1 0]