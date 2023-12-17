# Projekt z Algorytmów Geometrycznych 2023/2024
> Należy zaimplementować algorytmy konstrukcji triangulacji dla dowolnego wielokąta protego dwoma metodami. <br><br>
> W obu przypadkach triangulacja ma się opierać jedynie na wierzchołkach wielokąta (bez dodawania wierzchołków wewnątrz wielokąta). <br><br>
> Pierwsza metoda to podział wielokąta na wielokąty monotoniczne (zgodnie z algorytmem podanym na wykładzie), a następnie triangulacja wynikłych z podziału wielokątów monotonicznych także metodą podaną na wykładzie (i realizowaną na ćwiczeniach). <br><br>
> Drugi algorytm to triangulacja Delaunay’a z ograniczeniami (z procedurami odzyskania krawędzi i usunięcia trójkątów zewnętrznych). W tej metodzie wybrać odpowiedni sposób poszukiwania trójkąta w istniejącej triangulacji (i go omówić). <br><br> 
> Program powinien pozwolić na wizualizację działania obu metod. <br><br>
> Przeanalizować i porównać obie metody pod kątem efektywności oraz jakości otrzymanej triangulacji (wybrać odpowiednie kryterium oceny trójkątów).

## Setup
```
conda env create -f environment.yml
conda activate alg-geo-proj
pip install -e .
```


## Remove
```
conda remove --name alg-geo-proj --all
```