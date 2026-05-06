from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# ========== Herramientas base ==========

# Dibuja un punto en la posición (x, y)
def set_pixel(x, y):
    glVertex2i(int(x), int(y))

# Algoritmo de Bresenham para dibujar líneas entre (x0, y0) y (x1, y1)
def bresenham_line(x0, y0, x1, y1):
    glBegin(GL_POINTS)
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        set_pixel(x0, y0)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    glEnd()

# ========== Clase Circunferencia ==========

class Circunferencia:
    """
    Clase que representa una circunferencia.
    """

    def __init__(self, cx, cy, radio, color=(0.2, 0.4, 1)):
        """
        Constructor de la circunferencia.

        Atributos:
        - cx, cy: Coordenadas del centro de la circunferencia.
        - radio: Radio de la circunferencia.
        - color: Color de relleno en formato RGB.
        """
        self.cx = cx  # Coordenada X del centro
        self.cy = cy  # Coordenada Y del centro
        self.r = radio  # Radio de la circunferencia
        self.color = color  # Color de relleno (RGB)

    def trasladar(self, traslaciones):
        """
        Aplica una lista de traslaciones (tx, ty) a la circunferencia.

        Parámetros:
        - traslaciones: Lista de tuplas con desplazamientos en X e Y.
        """
        for tx, ty in traslaciones:
            self.cx += tx
            self.cy += ty
    #usan el algortimo de punto medio
    def dibujar_contorno(self):
        """
        Dibuja el contorno de la circunferencia usando el algoritmo de los 8 puntos simétricos.
        """
        glColor3f(0, 0, 0)  # Color negro para el contorno
        x = 0
        y = self.r
        d = 1 - self.r
        glBegin(GL_POINTS)
        self._dibujar_simetrico(x, y)
        while x < y:
            x += 1
            if d < 0:
                d += 2 * x + 1
            else:
                y -= 1
                d += 2 * (x - y) + 1
            self._dibujar_simetrico(x, y)
        glEnd()

    def dibujar_scanline(self):
        """
        Rellena la circunferencia utilizando el algoritmo de Scan-Line adaptado a círculos.
        """
        glColor3f(*self.color)  # Color de relleno
        ymin = int(self.cy - self.r)
        ymax = int(self.cy + self.r)

        for y in range(ymin, ymax + 1):
            intersecciones = []
            # Calcula el desplazamiento horizontal (x) para el valor de y actual
            x_offset = int((self.r ** 2 - (y - self.cy) ** 2) ** 0.5)
            x1 = self.cx - x_offset
            x2 = self.cx + x_offset
            intersecciones.append(x1)
            intersecciones.append(x2)

            intersecciones.sort()

            # Dibuja la línea horizontal entre las intersecciones
            glBegin(GL_POINTS)
            for i in range(0, len(intersecciones), 2):
                if i + 1 < len(intersecciones):
                    x_start = int(intersecciones[i])
                    x_end = int(intersecciones[i + 1])
                    for x in range(x_start, x_end + 1):
                        set_pixel(x, y)
            glEnd()

    def _dibujar_simetrico(self, x, y):
        """
        Dibuja los 8 puntos simétricos de la circunferencia para el punto (x, y).
        """
        cx, cy = self.cx, self.cy
        for dx, dy in [(x, y), (-x, y), (x, -y), (-x, -y), (y, x), (-y, x), (y, -x), (-y, -x)]:
            set_pixel(cx + dx, cy + dy)

# ========== Clase Escena ==========

class Escena:
    """
    Clase que representa la escena completa con cuadrícula, ejes y las circunferencias.
    """

    def __init__(self):
        """
        Constructor que inicializa la escena con una circunferencia original
        y una trasladada con múltiples desplazamientos.
        """
        self.circulo_original = Circunferencia(0, 0, 40, color=(0, 1, 0))  # Círculo original verde
        
        # Lista de traslaciones a aplicar
        self.traslaciones = [(70, 80), (50, 30), (-30, -40)]

        # Circunferencia trasladada a partir de la original
        self.circulo_trasladado = Circunferencia(
            self.circulo_original.cx,
            self.circulo_original.cy,
            self.circulo_original.r,
            self.circulo_original.color
        )
        self.circulo_trasladado.trasladar(self.traslaciones)

    def dibujar_cuadricula(self):
        """
        Dibuja una cuadrícula de fondo para facilitar la visualización.
        """
        glColor3f(0.85, 0.85, 0.85)  # Gris claro
        for i in range(-150, 151, 15):
            bresenham_line(i, -150, i, 150)  # Líneas verticales
        for j in range(-150, 151, 15):
            bresenham_line(-150, j, 150, j)  # Líneas horizontales

    def dibujar_ejes(self):
        """
        Dibuja los ejes X e Y en el centro de la ventana.
        """
        glColor3f(0, 0, 0)  # Negro
        bresenham_line(-150, 0, 150, 0)  # Eje X
        bresenham_line(0, -150, 0, 150)  # Eje Y

    def mostrar(self):
        """
        Método principal que se encarga de dibujar toda la escena:
        cuadrícula, ejes, circunferencia original y trasladada.
        """
        glClear(GL_COLOR_BUFFER_BIT)
        self.dibujar_cuadricula()
        self.dibujar_ejes()

        # Dibuja la circunferencia original (solo contorno)
        self.circulo_original.dibujar_contorno()

        # Dibuja la circunferencia trasladada (relleno + contorno)
        self.circulo_trasladado.dibujar_scanline()
        self.circulo_trasladado.dibujar_contorno()

        glFlush()

# ========== Inicialización de OpenGL y ejecución ==========

def init():
    """
    Configura el entorno de OpenGL: color de fondo, sistema de coordenadas y tamaño de punto.
    """
    glClearColor(1, 1, 1, 1)  # Fondo blanco
    gluOrtho2D(-160, 160, -160, 160)  # Ventana de coordenadas
    glPointSize(2)  # Tamaño de los puntos

def main():
    """
    Función principal que lanza la ventana OpenGL y dibuja la escena.
    """
    escena = Escena()
    glutInit()
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowSize(640, 640)
    glutCreateWindow(b"Circulo con Traslaciones y Scan-Line (POO)")
    init()
    glutDisplayFunc(escena.mostrar)
    glutMainLoop()

# Punto de entrada del programa
if __name__ == "__main__":
    main()
