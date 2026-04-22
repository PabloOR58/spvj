class Tripulantes:
    def __init__ (self,nombre,rango_militar):
        if nombre is None or nombre.strip()== "":
            raise TypeError("se necesita poner un nombre")
        self.nombre = nombre
        self.rango = rango_militar
class Naves:
    def __init__ (self,numero_matricula):
        if numero_matricula is None or numero_matricula.strip()== "":
            raise TypeError("se necesita poner una matricula")
        self.numero_matricula = numero_matricula
        self.lista_tripulantes = []
    def generar_registro(self, nuevo_tripulante):
            self.lista_tripulantes.append(nuevo_tripulante)
class Nave_Carga(Naves):
    def __init__(self, numero_matricula,limite_peso,peso_actual):
        super().__init__(numero_matricula)
        self.limite_peso = limite_peso
        self.peso_actual = peso_actual
    def calcular_carga(self,nuevo_peso):
            self.peso_actual += nuevo_peso
            if self.limite_peso < self.peso_actual:
                raise ValueError ("Error critico, la nave collapsa!!")
class Nave_Combate(Naves):
    def __init__ (self,numero_matricula,poder_combate,escudos):
        super().__init__(numero_matricula)
        self.poder_combate = poder_combate
        self.escudos = escudos
    def recepcion_danno(self, danno_producido):
        self.escudos -= danno_producido
        if self.escudos < 0:
            self.escudos = 0 
            print(f"¡Alerta! La nave {self.numero_matricula} ha perdido los escudos!")
class Flota():
    def __init__ (self,nombre):
        self.nombre = nombre
        self.lista_naves = []
    def agregar_nave(self,nueva_nave):
        self.lista_naves.append(nueva_nave)
    def informe_radar(self):
        for nave in self.lista_naves:
            if isinstance (nave,Nave_Carga):
                print(f"la nave de carga: {nave.numero_matricula} tiene un peso actual de: {nave.peso_actual}")
            elif isinstance(nave,Nave_Combate):
                print(f"la nave de combate: {nave.numero_matricula} tiene unos escudos restantes de : {nave.escudos}")
            print("Tripulacion de la nave : ")
            for tripulante in nave.lista_tripulantes:
                print (f"nombre: {tripulante.nombre} rango: {tripulante.rango}")
def main():
    flota = Flota("Sector Alfa")
    tripulante1 = Tripulantes("Spock","Oficial Cientifico")   
    tripulante2 = Tripulantes("Han Solo","Piloto")    
    nave_carga = Nave_Carga("USC-Nostromo",2000,0)
    try:
        nave_carga.calcular_carga(2500)
    except ValueError as e:
        print(f"ATENCIÓN: {e}")
        nave_carga.peso_actual=2000
    nave_combate = Nave_Combate("X-Wing-01",200,500)
    nave_combate.recepcion_danno(600)
    nave_carga.generar_registro(tripulante1)
    nave_combate.generar_registro(tripulante2)
    flota.agregar_nave(nave_carga)
    flota.agregar_nave(nave_combate)
    flota.informe_radar()       
if __name__ == "__main__":
    main()