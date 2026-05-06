from OpenGL.GL import *
from OpenGL.GLU import * 
from OpenGL.GLUT import * 
from OpenGL.GLUT import GLUT_BITMAP_9_BY_15, GLUT_BITMAP_8_BY_13
import sys
import numpy as np
from clases import *
import random
import time

class SpaceInvaders:
    def __init__(self):
        # Configuración global
        self.ventana = 800
        self.mitad_ventana = self.ventana // 2
        self.divisiones = 2
        
        # Variables del juego
        self.pos_x = 0
        self.direccion = 1
        self.velocidad = 2
        self.limite_derecho = self.mitad_ventana//self.divisiones - ((self.mitad_ventana//self.divisiones)// 13) -13
        self.limite_izquierdo = 0
        self.mostrar_primero = True
        
        # Nave jugador
        self.nave_dispara_x = 0
        self.velocidad_nave_dispara = 10
        self.vidas = 3
        self.puntaje = 0
        
        # Disparos
        self.disparos_jugador = []
        self.disparos_enemigos = []
        self.velocidad_disparo = 10
        self.frecuencia_disparo_enemigo = 0.002
        
        # Naves enemigas
        self.naves_enemigas = []
        self.filas_enemigas = 5
        self.columnas_enemigas = 10
        self.espaciado_enemigos = 15
        
        # Nave nodriza
        self.nodriza_activa = False
        self.nodriza_x = -100
        self.velocidad_nodriza = 5
        self.frecuencia_nodriza = 0.001
        
        # Escudos
        self.escudos = []
        self.inicializar_escudos()
        
        # Estados del juego
        self.juego_pausado = False
        self.game_over = False

        self.nivel = 1

        self.ultimo_disparo = 0
        self.intervalo_disparo = 1.0  # un segundo entre disparos

    def inicializar_escudos(self):
        """Inicializa los escudos con sus píxeles"""
        vertices_escudo_base = [(0,0), (5,0), (5,2), (6,2), (6,3), (7,3), (7,4), 
                               (14,4), (15,4), (15,3), (16,3), (16,2), (17,2), (17,0), (22,0), 
                               (22,12), (21,12), (21,13),(20,13), (20,14), (19,14), (19,15), (18,15), (18,16), 
                               (4,16),(4,15), (3,15), (3,14), (2,14),(2,13),(1,13), (1,12), (0,12)]
        
        self.escudos = []
        for i in range(4):
            x_base = -80 + i * 45
            y_base = -50
            
            # Crear un conjunto de píxeles para cada escudo
            pixeles_escudo = set()
            
            # Escalar y trasladar los vértices
            poligono_escudo = Poligono(vertices_escudo_base, True)
            poligono_escudo = poligono_escudo.escalar_poligono(2, 2)
            poligono_escudo = poligono_escudo.trasladar_poligono(x_base, y_base)
            
            # Convertir el polígono a píxeles individuales
            # Aproximación simple: crear píxeles en una cuadrícula dentro del polígono
            min_x = min(v[0] for v in poligono_escudo.vertices)
            max_x = max(v[0] for v in poligono_escudo.vertices)
            min_y = min(v[1] for v in poligono_escudo.vertices)
            max_y = max(v[1] for v in poligono_escudo.vertices)
            
            # Crear píxeles para representar el escudo
            for x in range(int(min_x), int(max_x) + 1):
                for y in range(int(min_y), int(max_y) + 1):
                    # Verificar si el punto está dentro del polígono (aproximación simple)
                    if self.punto_en_poligono(x, y, poligono_escudo.vertices):
                        pixeles_escudo.add((x, y))
            
            self.escudos.append({
                'pixeles': pixeles_escudo,
                'x_base': x_base,
                'y_base': y_base
            })

    def punto_en_poligono(self, x, y, vertices):
        """Determina si un punto está dentro de un polígono usando ray casting"""
        n = len(vertices)
        inside = False
        
        p1x, p1y = vertices[0]
        for i in range(1, n + 1):
            p2x, p2y = vertices[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside

    def verificar_colision_escudo(self, disparo_x, disparo_y):
        """Verifica si un disparo colisiona con algún escudo y lo daña"""
        for escudo in self.escudos:
            pixeles_a_remover = set()
            
            # Verificar colisión con píxeles del escudo
            for pixel_x, pixel_y in escudo['pixeles']:
                if abs(disparo_x - pixel_x) < 3 and abs(disparo_y - pixel_y) < 3:
                    # Crear un área de daño alrededor del impacto
                    for dx in range(-2, 3):
                        for dy in range(-2, 3):
                            pixel_dañado = (pixel_x + dx, pixel_y + dy)
                            if pixel_dañado in escudo['pixeles']:
                                pixeles_a_remover.add(pixel_dañado)
                    
                    # Remover píxeles dañados
                    escudo['pixeles'] -= pixeles_a_remover
                    return True
        
        return False

    def inicializar_enemigos(self): 
        self.naves_enemigas = []
        altura_inicial = (self.mitad_ventana // self.divisiones) - 50
        
        for fila in range(self.filas_enemigas):
            for col in range(self.columnas_enemigas):
                x = -self.mitad_ventana//self.divisiones + col * self.espaciado_enemigos + 30
                y = altura_inicial - fila * 20
                tipo = 1 if fila < 2 else 2
                self.naves_enemigas.append({'x': x, 'y': y, 'tipo': tipo, 'viva': True})

    def reiniciar_juego(self):
        self.vidas = 3
        self.puntaje = 0
        self.nivel = 1
        self.pos_x = 0
        self.direccion = 1
        self.game_over = False
        self.disparos_jugador = []
        self.disparos_enemigos = []
        self.nodriza_activa = False
        self.inicializar_enemigos()
        self.inicializar_escudos()


    def actualizar_disparos(self):
        '''Actualiza la posición de los disparos y verifica colisiones'''
        # Mover disparos del jugador
        for disparo in self.disparos_jugador[:]:
            disparo['y'] += self.velocidad_disparo / self.divisiones
            
            # Verificar colisión con escudos
            if self.verificar_colision_escudo(disparo['x'], disparo['y']):
                self.disparos_jugador.remove(disparo)
                continue
            
            # Verificar colisión con naves enemigas
            for enemigo in self.naves_enemigas:
                if enemigo['viva'] and abs(disparo['x'] - enemigo['x'] - self.pos_x) < 10 and abs(disparo['y'] - enemigo['y']) < 10:
                    enemigo['viva'] = False
                    self.disparos_jugador.remove(disparo)
                    self.puntaje += 100 if enemigo['tipo'] == 1 else 200
                    break
            
            # Verificar colisión con nave nodriza
            if self.nodriza_activa and abs(disparo['x'] - self.nodriza_x) < 30 and abs(disparo['y'] - ((self.mitad_ventana // self.divisiones) - 20)) < 15:
                self.disparos_jugador.remove(disparo)
                self.puntaje += 500
                self.nodriza_activa = False
                break
            
            # Eliminar disparos que salen de la pantalla
            if disparo['y'] > self.mitad_ventana // self.divisiones:
                self.disparos_jugador.remove(disparo)
        
        # Mover disparos enemigos
        for disparo in self.disparos_enemigos[:]:
            disparo['y'] -= self.velocidad_disparo / self.divisiones
            
            # Verificar colisión con escudos
            if self.verificar_colision_escudo(disparo['x'], disparo['y']):
                self.disparos_enemigos.remove(disparo)
                continue
            
            # Verificar colisión con nave jugador
            if abs(disparo['x'] - (-(self.mitad_ventana//self.divisiones) + self.nave_dispara_x)) < 10 and abs(disparo['y'] - (-(self.mitad_ventana//self.divisiones) + 50)) < 10:
                self.disparos_enemigos.remove(disparo)
                self.vidas -= 1
                if self.vidas <= 0:
                    self.game_over = True
                break
            
            # Eliminar disparos que salen de la pantalla
            if disparo['y'] < -self.mitad_ventana // self.divisiones:
                self.disparos_enemigos.remove(disparo)

        self.verificar_colision_balas() # Verifica colisiones entre balas

    def verificar_colision_balas(self):
        """
        Verifica si las balas del jugador colisionan con las balas enemigas
        y elimina ambas balas cuando esto ocurre
        """
        balas_jugador_a_eliminar = []
        balas_enemigos_a_eliminar = []
        
        for i, bala_jugador in enumerate(self.disparos_jugador):
            for j, bala_enemigo in enumerate(self.disparos_enemigos):
                # Calcular distancia entre las dos balas
                distancia_x = abs(bala_jugador['x'] - bala_enemigo['x'])
                distancia_y = abs(bala_jugador['y'] - bala_enemigo['y'])
                
                # Si están lo suficientemente cerca, han colisionado
                if distancia_x < 5 and distancia_y < 5:
                    # Marcar ambas balas para eliminación
                    if i not in balas_jugador_a_eliminar:
                        balas_jugador_a_eliminar.append(i)
                    if j not in balas_enemigos_a_eliminar:
                        balas_enemigos_a_eliminar.append(j)
                    
                    # Opcional: añadir puntos por interceptar balas enemigas
                    self.puntaje += 10
        
        # Eliminar balas en orden inverso para no alterar los índices
        for i in sorted(balas_jugador_a_eliminar, reverse=True):
            if i < len(self.disparos_jugador):
                self.disparos_jugador.pop(i)
        
        for i in sorted(balas_enemigos_a_eliminar, reverse=True):
            if i < len(self.disparos_enemigos):
                self.disparos_enemigos.pop(i)

    def disparar_enemigos(self):
        for enemigo in self.naves_enemigas:
            if enemigo['viva'] and random.random() < self.frecuencia_disparo_enemigo:
                self.disparos_enemigos.append({'x': enemigo['x'] + self.pos_x, 'y': enemigo['y']})

    def actualizar_nodriza(self):
        '''Actualiza la posición de la nave nodriza y su activación'''
        if not self.nodriza_activa and random.random() < self.frecuencia_nodriza:
            self.nodriza_activa = True
            self.nodriza_x = -self.mitad_ventana // self.divisiones - 50
        
        if self.nodriza_activa:
            self.nodriza_x += self.velocidad_nodriza
            if self.nodriza_x > self.mitad_ventana // self.divisiones + 50:
                self.nodriza_activa = False

    def verificar_fin_nivel(self):
        """Verifica si todas las naves enemigas han sido destruidas y sube de nivel"""
        enemigos_vivos = [e for e in self.naves_enemigas if e['viva']]
        if not enemigos_vivos:
            self.nivel += 1
            print(f"¡Subiste al nivel {self.nivel}!")
            self.velocidad += 0.5
            self.frecuencia_disparo_enemigo += 0.0005
            self.inicializar_enemigos()
            self.inicializar_escudos()
            self.disparos_jugador = []
            self.disparos_enemigos = []

    def actualizar(self, valor):
        """Actualiza la lógica del juego, mueve las naves y gestiona disparos"""
        if self.game_over or self.juego_pausado:
            glutTimerFunc(30, lambda v: self.actualizar(v), 0)
            return
        
        self.mostrar_primero = not self.mostrar_primero
        
        # Mover naves enemigas
        self.pos_x += self.velocidad * self.direccion
        if self.pos_x > self.limite_derecho:
            self.direccion = -1
            # Bajar todas las naves
            for enemigo in self.naves_enemigas:
                enemigo['y'] -= 5
        elif self.pos_x < self.limite_izquierdo:
            self.direccion = 1
            # Bajar todas las naves
            for enemigo in self.naves_enemigas:
                enemigo['y'] -= 5
        
        # Actualizar elementos del juego
        self.actualizar_disparos()
        self.disparar_enemigos()
        self.actualizar_nodriza()
        self.verificar_fin_nivel()
        glutPostRedisplay()
        glutTimerFunc(30, lambda v: self.actualizar(v), 0)

    def disparar_jugador(self):
        """Función para disparar del jugador, respetando un intervalo mínimo"""
        if not self.juego_pausado and not self.game_over:
            tiempo_actual = time.time()
            if tiempo_actual - self.ultimo_disparo >= self.intervalo_disparo:
                self.disparos_jugador.append({
                    'x': -(self.mitad_ventana//self.divisiones) + self.nave_dispara_x + 6, 
                    'y': -(self.mitad_ventana//self.divisiones) + 50 + 8
                })
                self.ultimo_disparo = tiempo_actual


    def manejar_teclado_especial(self, key, x, y):
        if self.game_over:
            return
        
        if key == GLUT_KEY_LEFT:
            if self.nave_dispara_x - self.velocidad_nave_dispara > self.limite_izquierdo:
                self.nave_dispara_x -= self.velocidad_nave_dispara
        elif key == GLUT_KEY_RIGHT:
            if self.nave_dispara_x + self.velocidad_nave_dispara < self.mitad_ventana - 15:
                self.nave_dispara_x += self.velocidad_nave_dispara
        elif key == GLUT_KEY_F1:
            self.juego_pausado = not self.juego_pausado
        
        glutPostRedisplay()

    def manejar_teclado(self, key, x, y):
        if key == b'r' and self.game_over:
            self.reiniciar_juego()
        elif key == b' ':  # Tecla espacio para disparar
            self.disparar_jugador()
        glutPostRedisplay()


class Renderer:
    def __init__(self, juego):
        self.juego = juego
        self.poligono_enemigo_1a = Poligono([
            (1,0), (2,0), (2,1), (3,1), (3,2), (8,2), (8,1), (9,1), (9,0),
            (10,0), (10,1), (9,1), (9,2), (10,2), (10,3), (11,3), (11,7), (10,7),
            (10,5), (9,5), (9,6), (8,6), (8,7), (9,7), (9,8), (8,8), (8,7),
            (7,7), (7,6), (4,6), (4,7), (3,7), (3,8), (2,8), (2,7), (3,7),
            (3,6), (2,6), (2,5), (1,5), (1,7), (0,7), (0,3), (1,3), (1,2),
            (2,2), (2,1), (1,1)
        ], True)

        self.poligono_enemigo_1b = Poligono([
            (1,1), (1,3), (2,3), (2,1), (3,1), (3,0), (5,0), (5,1), (3,1),
            (3,2), (8,2), (8,1), (6,1), (6,0), (8,0), (8,1), (9,1), (9,3),
            (10,3), (10,1), (11,1), (11,4), (10,4), (10,5), (9,5), (9,6),
            (8,6), (8,7), (9,7), (9,8), (8,8), (8,7), (7,7), (7,6), (4,6),
            (4,7), (3,7), (3,8), (2,8), (2,7), (3,7), (3,6), (2,6), (2,5),
            (1,5), (1,4), (0,4), (0,1)
        ], True)

        self.poligono_enemigo_2a = Poligono([
            (1,0), (2,0), (2,1), (1,1), (1,2), (2,2), (2,3), (3,3), (3,2),
            (5,2), (5,3), (6,3), (6,2), (7,2), (7,1), (6,1), (6,0), (7,0),
            (7,1), (8,1), (8,2), (7,2), (7,3), (8,3), (8,5), (7,5), (7,6),
            (6,6), (6,7), (5,7), (5,8), (3,8), (3,7), (2,7), (2,6), (1,6),
            (1,5), (0,5), (0,3), (1,3), (1,2), (0,2), (0,1), (1,1)
        ], True)

        self.poligono_enemigo_2b = Poligono([
            (0,0), (1,0), (1,1), (2,1), (2,0), (3,0), (3,1), (5,1), (5,0),
            (6,0), (6,1), (7,1), (7,0), (8,0), (8,1), (7,1), (7,2), (6,2),
            (6,3), (8,3), (8,5), (7,5), (7,6), (6,6), (6,7), (5,7), (5,8),
            (3,8), (3,7), (2,7), (2,6), (1,6), (1,5), (0,5), (0,3), (2,3),
            (2,2), (1,2), (1,1), (0,1)
        ], True)

        self.poligono_jugador_base = Poligono([
            (0,0), (12,0), (12,4), (11,4), (11,5), (7,5), (7,7), (6,7),
            (6,8), (5,7), (5,5), (1,5), (1,4), (0,4)
        ], True)

    def nave_enemiga_1(self, x, y):
        base = self.poligono_enemigo_1a if self.juego.mostrar_primero else self.poligono_enemigo_1b
        poligono = base.trasladar_poligono(x//divisiones, y//divisiones)
        poligono.graficar()
        return poligono.vertices

    def nave_enemiga_2(self, x, y):
        base = self.poligono_enemigo_2a if self.juego.mostrar_primero else self.poligono_enemigo_2b
        poligono = base.trasladar_poligono(x//divisiones, y//divisiones)
        poligono.graficar()
        return poligono.vertices

        
    def nave_dispara(self, x, y):
        poligono = self.poligono_jugador_base.trasladar_poligono(x//divisiones, y//divisiones)
        poligono.graficar()
        return poligono.vertices

    def nave_nodriza(self, x, y):
        vertices1 = [(x+vx, y+vy) for vx, vy in [
                (0,6), (3,6), (4,5), (4,4), (5,4), (6,3), (6,2), (7,2), 
                (7,3),(8,4), (9,4), (9,5), (10,6), (13,6), (14,5),
                (14,4), (17,4), (17,6), (22,6), (22,4), (24,4), (24,2), 
                (25,2), (25,4), (27,4), (27,6), (31,6), (31,7), 
                (29,7), (29,9), (27,9), (27,11), (25,11), (25,13), 
                (21,13), (21,15), (10,15), (10,13), (6,13), (6,11), 
                (4,11), (4,9), (2,9), (2,7), (0,7)
        ]]
        poligono = Poligono(vertices1, True)
        poligono.graficar()
        return vertices1

    def dibujar_escudos(self):
        """Dibuja los escudos píxel por píxel"""
        glColor3f(0, 1, 0)
        glPointSize(1.5)
        glBegin(GL_POINTS)
        
        for escudo in self.juego.escudos:
            for pixel_x, pixel_y in escudo['pixeles']:
                # Convertir coordenadas del juego a coordenadas de pantalla
                screen_x = self.juego.mitad_ventana + self.juego.divisiones * pixel_x
                screen_y = self.juego.mitad_ventana + self.juego.divisiones * pixel_y
                glVertex2f(screen_x, screen_y)
        
        glEnd()
        glPointSize(1.0)

    def dibujar_naves(self):
        # Dibujar naves enemigas
        for enemigo in self.juego.naves_enemigas:
            if enemigo['viva']:
                x = enemigo['x'] + self.juego.pos_x
                y = enemigo['y']
                if enemigo['tipo'] == 1:
                    glColor3f(1, 0, 0)  # Rojo
                    self.nave_enemiga_1(x, y)
                else:
                    glColor3f(0, 0, 1)  # Azul
                    self.nave_enemiga_2(x, y)
        
        # Dibujar nave nodriza si está activa
        if self.juego.nodriza_activa:
            glColor3f(0, 1, 1)  # Cyan
            self.nave_nodriza(self.juego.nodriza_x, (self.juego.mitad_ventana // self.juego.divisiones) - 20)
        
        # Dibujar nave jugador
        glColor3f(0, 1, 0)  # Verde
        self.nave_dispara(-(self.juego.mitad_ventana//self.juego.divisiones) + self.juego.nave_dispara_x, 
                         -(self.juego.mitad_ventana//self.juego.divisiones) + 50)

    def dibujar_disparos(self):
        glColor3f(1, 1, 1)  # Blanco para los disparos
        
        # Dibujar disparos del jugador
        for disparo in self.juego.disparos_jugador[:]:
            x, y = disparo['x'], disparo['y']
            # Convertir coordenadas a enteros
            ix = int(self.juego.mitad_ventana + self.juego.divisiones * x)
            iy = int(self.juego.mitad_ventana + self.juego.divisiones * y)
                 
            plot(ix, iy + self.juego.divisiones)  # Arriba
            plot(ix, iy)               # Centro
            plot(ix - self.juego.divisiones, iy)  # Izquierda
            plot(ix + self.juego.divisiones, iy)  # Derecha
                    
        # Dibujar disparos enemigos
        glColor3f(0, 1, 0)  # Verde para los disparos enemigos
        for disparo in self.juego.disparos_enemigos[:]:
            x, y = disparo['x'], disparo['y']
            ix = int(self.juego.mitad_ventana + self.juego.divisiones * x)
            iy = int(self.juego.mitad_ventana + self.juego.divisiones * y)

            # Usar la función plot para dibujar cada punto del disparo
            plot(ix, iy - self.juego.divisiones)  # Abajo
            plot(ix, iy)                          # Centro
            plot(ix - self.juego.divisiones, iy)  # Izquierda
            plot(ix + self.juego.divisiones, iy)  # Derecha


    def dibujar_hud(self):
        # Dibujar puntaje
        glColor3f(1, 1, 1)
        punto1, punto2 = Punto((self.juego.mitad_ventana)//self.juego.divisiones - 70, 
                              (-self.juego.mitad_ventana)//self.juego.divisiones + 40).ubicar()
        
        glRasterPos2f(punto1, punto2)
        for char in f"Puntaje: {self.juego.puntaje}":
            
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))
        
        # Dibujar vidas
        punto3, punto4 = Punto((-self.juego.mitad_ventana)//self.juego.divisiones + 40, 
                              (-self.juego.mitad_ventana)//self.juego.divisiones + 40).ubicar()
        glRasterPos2f(punto3, punto4)
        for char in f"Vidas: {self.juego.vidas}":
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))

        # Mostrar Nivel centrado entre Vidas y Puntaje, en la misma línea
        x_nivel = (((-self.juego.mitad_ventana)//self.juego.divisiones + 40) + 
                ((self.juego.mitad_ventana)//self.juego.divisiones - 70)) // 2
        y_nivel = (-self.juego.mitad_ventana)//self.juego.divisiones + 40

        punto5, punto6 = Punto(x_nivel, y_nivel).ubicar()
        glRasterPos2f(punto5, punto6)
        for char in f"Nivel: {self.juego.nivel}":
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))



    def dibujar_instrucciones(self):
        # Dibujar instrucciones de control
        glColor3f(0.7, 0.7, 0.7)
        punto1, punto2 = Punto((-self.juego.mitad_ventana)//self.juego.divisiones + 10, 
                              (self.juego.mitad_ventana)//self.juego.divisiones - 20).ubicar()
        glRasterPos2f(punto1, punto2)
        for char in "Controles: Flechas = Mover, Espacio = Disparar, F1 = Pausa":
            glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ord(char))

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT) 
        glClearColor(0.0, 0.0, 0.0, 1.0)
        
        if self.juego.game_over:
            glColor3f(1, 0, 0)
            glRasterPos2f(self.juego.ventana // 2 - 150, self.juego.ventana // 2)
            for char in "GAME OVER - Presiona R para reiniciar":
                glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))
            
            glRasterPos2f(self.juego.ventana // 2 - 80, self.juego.ventana // 2 - 30)
            for char in f"Puntaje final: {self.juego.puntaje}":
                glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))

        else:
            self.dibujar_naves()
            self.dibujar_escudos()
            self.dibujar_disparos()
            self.dibujar_hud()
            self.dibujar_instrucciones()
            
            if self.juego.juego_pausado:
                glColor3f(1, 1, 0)
                glRasterPos2f(-30, 0)
                for char in "PAUSA - F1 para continuar":
                    glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))
        
        glFlush()

class GameManager:
    def __init__(self):
        self.juego = SpaceInvaders()
        self.renderer = Renderer(self.juego)
        
    def myinit(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glPointSize(1.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0.0, self.juego.ventana - 1, 0.0, self.juego.ventana - 1)

    def iniciar(self):
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
        glutInitWindowSize(self.juego.ventana, self.juego.ventana)
        glutInitWindowPosition(0, 0)
        glutCreateWindow(b"Space Invaders")
        glutDisplayFunc(self.renderer.display)
        glutSpecialFunc(self.juego.manejar_teclado_especial)
        glutKeyboardFunc(self.juego.manejar_teclado)
        self.myinit()
        self.juego.inicializar_enemigos()
        glutTimerFunc(0, self.juego.actualizar, 0)
        glutMainLoop()

def main():
    game_manager = GameManager()
    game_manager.iniciar()

if __name__ == "__main__":
    main()
    