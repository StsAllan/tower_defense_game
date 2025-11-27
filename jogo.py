import math
import os
import random
from pygame.locals import Rect
from entidades import Inimigo, Torre, TextoFlutuante
from utils import carregar_textura, TEXTURAS, dist_ponto_segmento
from config import *


class GerenciadorMusica:
    def __init__(self, pygame_mixer):
        self.mixer = pygame_mixer
        self.atual = None
        self.caminhos = {
            'normal': os.path.join("assets", "trilha-sonora.wav"),
            'onda': os.path.join("assets", "wave-song.wav")
        }
        self.mudando = False
        self.contador_fade = 0

    def iniciar(self):
        if os.path.exists(self.caminhos['normal']):
            try:
                self.mixer.music.load(self.caminhos['normal'])
                self.mixer.music.set_volume(0.5)
                self.mixer.music.play(loops=-1)
                self.atual = 'normal'
            except Exception as e:
                print(f"Erro ao carregar música: {e}")

    def trocar(self, tipo_musica):
        if self.atual != tipo_musica and not self.mudando:
            caminho = self.caminhos.get(tipo_musica)
            if caminho and os.path.exists(caminho):
                try:
                    self.mixer.music.fadeout(400)
                    self.mudando = True
                    self.contador_fade = 30
                    self.proximo_tipo = tipo_musica
                except Exception as e:
                    print(f"Erro ao trocar música: {e}")

    def atualizar(self):
        if self.mudando:
            self.contador_fade -= 1
            if self.contador_fade <= 0:
                try:
                    caminho = self.caminhos[self.proximo_tipo]
                    self.mixer.music.load(caminho)
                    self.mixer.music.set_volume(0.5)
                    self.mixer.music.play(loops=-1)
                    self.atual = self.proximo_tipo
                except Exception as e:
                    print(f"Erro ao carregar música: {e}")
                finally:
                    self.mudando = False


class Jogo:

    def __init__(self):
        self.dinheiro = DINHEIRO_INICIAL
        self.vidas = VIDAS_INICIAL
        self.onda = 0
        self.inimigos = []
        self.projeteis = []
        self.torres = []
        self.textos_flutuantes = []
        self.torre_selecionada = None
        self.onda_ativa = False
        self.inimigos_para_spawnar = 0
        self.timer_spawn = 0
        self.modo_construcao = None

        self.btn_vender = Rect(650, ALTURA_LOGICA - 60, 120, 40)
        self.btn_onda = Rect(650, ALTURA_LOGICA - 130, 120, 40)

        self.btn_primeiro = Rect(350, ALTURA_AREA_JOGO + 80, 60, 25)
        self.btn_mais_vida = Rect(415, ALTURA_AREA_JOGO + 80, 70, 25)
        self.btn_ultimo = Rect(490, ALTURA_AREA_JOGO + 80, 60, 25)

        self.aba_ativa = 'DANO'
        self.abas = {
            'DANO': Rect(10, ALTURA_AREA_JOGO + 10, 100, 30),
            'SUPORTE': Rect(120, ALTURA_AREA_JOGO + 10, 100, 30)
        }

        self.carregar_assets()

    def carregar_assets(self):
        frames_normal = []
        frames_tank = []
        frames_speed = []

        # Inimigos normais
        for i in range(4):
            tex = carregar_textura(f'enemy_{i}.png')
            if tex:
                frames_normal.append(tex)
            elif i == 0:
                fb = carregar_textura('enemy.png')
                if fb:
                    frames_normal.append(fb)

        TEXTURAS['enemy_frames'] = frames_normal

        # Inimigos tank
        for i in range(4):
            tex = carregar_textura(f'enemy_hp_{i}.png')
            if tex:
                frames_tank.append(tex)
        TEXTURAS['enemy_hp_frames'] = frames_tank

        # Inimigos speed
        for i in range(4):
            tex = carregar_textura(f'enemy_speed_{i}.png')
            if tex:
                frames_speed.append(tex)
        TEXTURAS['enemy_speed_frames'] = frames_speed

        # Torres
        for chave, dados in TIPOS_TORRES.items():
            TEXTURAS[dados['img_name']] = carregar_textura(dados['img_name'])

        # UI
        TEXTURAS['background'] = carregar_textura('background.png')
        TEXTURAS['buff_icon'] = carregar_textura('buff_icon.png')
        TEXTURAS['heart'] = carregar_textura('heart.png')
        TEXTURAS['coin'] = carregar_textura('coin.png')
        TEXTURAS['menu_bottom'] = carregar_textura('menu.png')

    def pode_construir(self, x, y):
        """Verifica se pode construir torre na posição"""
        # Checa distância do caminho
        for i in range(len(CAMINHO) - 1):
            p1 = CAMINHO[i]
            p2 = CAMINHO[i + 1]
            dist = dist_ponto_segmento(x, y, p1[0], p1[1], p2[0], p2[1])
            if dist < RAIO_BLOQUEIO_CAMINHO:
                return False

        # Checa distância de outras torres
        for torre in self.torres:
            dist = math.hypot(x - torre.x, y - torre.y)
            if dist < DISTANCIA_MIN_TORRES:
                return False

        return True

    def iniciar_onda(self):
        """Inicia próxima onda"""
        if not self.onda_ativa:
            self.onda += 1
            quantidade_base = 5 + self.onda
            ciclo = self.onda // 3
            multiplicador = 1.7 ** ciclo
            self.inimigos_para_spawnar = int(quantidade_base * multiplicador)
            self.onda_ativa = True

    def atualizar(self):
        """Atualiza lógica do jogo"""
        # Spawn de inimigos
        if self.onda_ativa and self.inimigos_para_spawnar > 0:
            self.timer_spawn += 1
            delay_spawn = max(10, 40 - (self.onda * 2))

            if self.timer_spawn > delay_spawn:
                tipo_inimigo = 'normal'

                if self.onda >= 3:
                    ciclos = (self.onda - 3) // 3
                    chance_especial = 0.05 + (ciclos * 0.05)
                    chance_especial = min(chance_especial, 0.80)

                    if random.random() < chance_especial:
                        tipo_inimigo = 'tank' if random.random() < 0.5 else 'speed'

                self.inimigos.append(Inimigo(self.onda, tipo_inimigo))
                self.inimigos_para_spawnar -= 1
                self.timer_spawn = 0

        elif self.onda_ativa and len(self.inimigos) == 0 and self.inimigos_para_spawnar == 0:
            self.onda_ativa = False

        # Move inimigos
        for inimigo in self.inimigos[:]:
            if inimigo.mover():
                self.vidas -= 1
                inimigo.ativo = False
                self.inimigos.remove(inimigo)
            elif inimigo.vida <= 0:
                self.dinheiro += int(inimigo.recompensa)
                inimigo.ativo = False
                self.inimigos.remove(inimigo)

        # Atualiza buffs
        for torre in self.torres:
            torre.resetar_buffs()

        for torre in self.torres:
            fator_buff = torre.stats.get('buff_factor', 1.0)
            if fator_buff > 1.0:
                for alvo in self.torres:
                    if alvo != torre:
                        dist = math.hypot(alvo.x - torre.x, alvo.y - torre.y)
                        if dist <= torre.stats['range']:
                            alvo.aplicar_buff(fator_buff)

        # Atualiza torres
        for torre in self.torres:
            torre.atualizar(self.inimigos, self.projeteis, self)

        # Atualiza projéteis
        for proj in self.projeteis[:]:
            proj.atualizar()
            if not proj.ativo:
                self.projeteis.remove(proj)

        # Atualiza textos flutuantes
        for texto in self.textos_flutuantes[:]:
            texto.atualizar()
            if not texto.ativo:
                self.textos_flutuantes.remove(texto)