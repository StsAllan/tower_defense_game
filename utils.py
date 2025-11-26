import math
import pygame
import os
from OpenGL.GL import *
from OpenGL.GLU import *
from config import LARGURA_LOGICA, ALTURA_LOGICA

# === VARIÁVEIS GLOBAIS DE VIEWPORT ===
viewport_x = 0
viewport_y = 0
viewport_w = LARGURA_LOGICA
viewport_h = ALTURA_LOGICA
escala = 1.0

# === DICIONÁRIO DE TEXTURAS ===
TEXTURAS = {}


def atualizar_viewport(largura_janela, altura_janela):
    """Recalcula área de jogo quando janela muda"""
    global viewport_x, viewport_y, viewport_w, viewport_h, escala

    aspecto_alvo = LARGURA_LOGICA / ALTURA_LOGICA
    aspecto_janela = largura_janela / altura_janela

    if aspecto_janela > aspecto_alvo:
        viewport_h = altura_janela
        viewport_w = int(altura_janela * aspecto_alvo)
        viewport_y = 0
        viewport_x = int((largura_janela - viewport_w) / 2)
    else:
        viewport_w = largura_janela
        viewport_h = int(largura_janela / aspecto_alvo)
        viewport_x = 0
        viewport_y = int((altura_janela - viewport_h) / 2)

    escala = LARGURA_LOGICA / viewport_w
    glViewport(viewport_x, viewport_y, viewport_w, viewport_h)


def obter_mouse_logico():
    """Converte posição do mouse para coordenadas lógicas"""
    raw_x, raw_y = pygame.mouse.get_pos()
    jogo_x = (raw_x - viewport_x) * escala
    jogo_y = (raw_y - viewport_y) * escala
    return jogo_x, jogo_y


def dist_ponto_segmento(px, py, x1, y1, x2, y2):
    """Calcula distância de ponto até segmento de linha"""
    l2 = (x1 - x2) ** 2 + (y1 - y2) ** 2
    if l2 == 0:
        return math.hypot(px - x1, py - y1)

    t = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / l2
    t = max(0, min(1, t))

    proj_x = x1 + t * (x2 - x1)
    proj_y = y1 + t * (y2 - y1)

    return math.hypot(px - proj_x, py - proj_y)


def carregar_textura(nome_arquivo):
    """Carrega textura PNG e retorna ID OpenGL"""
    caminho = os.path.join("assets", nome_arquivo)
    if not os.path.exists(caminho):
        return None

    try:
        superficie = pygame.image.load(caminho).convert_alpha()
        superficie = pygame.transform.flip(superficie, False, True)
        dados = pygame.image.tostring(superficie, "RGBA", 1)
        largura, altura = superficie.get_width(), superficie.get_height()

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, largura, altura, 0, GL_RGBA, GL_UNSIGNED_BYTE, dados)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        return tex_id
    except:
        return None


def desenhar_sprite(tex_id, x, y, largura, altura, cor=(1, 1, 1), alpha=1.0):
    """Desenha sprite com textura"""
    if tex_id is None:
        return False

    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glColor4f(cor[0], cor[1], cor[2], alpha)

    metade_w = largura / 2
    metade_h = altura / 2

    glBegin(GL_QUADS)
    glTexCoord2f(0, 0);
    glVertex2f(x - metade_w, y - metade_h)
    glTexCoord2f(1, 0);
    glVertex2f(x + metade_w, y - metade_h)
    glTexCoord2f(1, 1);
    glVertex2f(x + metade_w, y + metade_h)
    glTexCoord2f(0, 1);
    glVertex2f(x - metade_w, y + metade_h)
    glEnd()

    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)
    return True


def desenhar_texto(texto, x, y, fonte, cor=(255, 255, 255, 255)):
    """Desenha texto usando pygame font"""
    superficie = fonte.render(texto, True, cor)
    superficie = pygame.transform.flip(superficie, False, True)
    dados = pygame.image.tostring(superficie, "RGBA", 1)
    w, h = superficie.get_width(), superficie.get_height()

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, dados)

    desenhar_sprite(tex_id, x + w / 2, y, w, h)
    glDeleteTextures(1, [tex_id])


def desenhar_retangulo(x, y, largura, altura):
    """Desenha retângulo preenchido"""
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + largura, y)
    glVertex2f(x + largura, y + altura)
    glVertex2f(x, y + altura)
    glEnd()


def desenhar_circulo(x, y, raio):
    """Desenha círculo preenchido"""
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x, y)
    for i in range(361):
        angulo = math.radians(i)
        glVertex2f(x + math.cos(angulo) * raio, y + math.sin(angulo) * raio)
    glEnd()


def desenhar_circulo_contorno(x, y, raio):
    """Desenha contorno de círculo"""
    glBegin(GL_LINE_LOOP)
    for i in range(360):
        angulo = math.radians(i)
        glVertex2f(x + math.cos(angulo) * raio, y + math.sin(angulo) * raio)
    glEnd()