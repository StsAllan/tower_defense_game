import math
from OpenGL.GL import *
from utils import desenhar_circulo, desenhar_retangulo, desenhar_sprite, desenhar_texto, TEXTURAS
from config import CAMINHO, TIPOS_TORRES


class TextoFlutuante:
    """Texto que sobe e desaparece"""

    def __init__(self, x, y, texto, cor=(0.2, 1.0, 0.2)):
        self.x, self.y = x, y
        self.texto = texto
        self.cor = cor
        self.timer = 60
        self.ativo = True

    def atualizar(self):
        self.y += 0.5
        self.timer -= 1
        if self.timer <= 0:
            self.ativo = False

    def desenhar(self, fonte):
        alpha = 255
        if self.timer < 20:
            alpha = int((self.timer / 20.0) * 255)

        r = int(self.cor[0] * 255)
        g = int(self.cor[1] * 255)
        b = int(self.cor[2] * 255)
        desenhar_texto(self.texto, self.x, self.y, fonte, (r, g, b, alpha))


class Projetil:
    """Projétil disparado por torres"""

    def __init__(self, x, y, alvo, dano, cor, slow_factor=1.0, slow_time=0):
        self.x, self.y = x, y
        self.alvo = alvo
        self.dano = dano
        self.cor = cor
        self.velocidade = 12
        self.ativo = True
        self.raio = 4
        self.slow_factor = slow_factor
        self.slow_time = slow_time

    def atualizar(self):
        if not self.alvo.ativo:
            self.ativo = False
            return

        dx = self.alvo.x - self.x
        dy = self.alvo.y - self.y
        dist = math.hypot(dx, dy)

        if dist < self.velocidade + self.alvo.raio:
            self.alvo.vida -= self.dano
            if self.slow_time > 0:
                self.alvo.aplicar_lentidao(self.slow_time, self.slow_factor)
            self.ativo = False
        else:
            self.x += (dx / dist) * self.velocidade
            self.y += (dy / dist) * self.velocidade

    def desenhar(self):
        glColor3f(*self.cor)
        desenhar_circulo(self.x, self.y, self.raio)


class Inimigo:
    """Inimigo que segue o caminho"""

    def __init__(self, nivel_onda, tipo_inimigo='normal'):
        self.indice_caminho = 0
        self.x, self.y = CAMINHO[0]
        self.ativo = True
        self.tipo_inimigo = tipo_inimigo

        vida_base = 50 + (nivel_onda * 25)
        vel_base = 1.5 + (nivel_onda * 0.1)

        if self.tipo_inimigo == 'tank':
            self.vida_max = vida_base * 3
            self.velocidade_base = vel_base * 0.6
            self.raio = 18
            self.recompensa = (15 + (nivel_onda * 2)) * 2
        elif self.tipo_inimigo == 'speed':
            self.vida_max = vida_base * 0.6
            self.velocidade_base = vel_base * 2.0
            self.raio = 12
            self.recompensa = 15 + (nivel_onda * 2)
        else:
            self.vida_max = vida_base
            self.velocidade_base = vel_base
            self.raio = 15
            self.recompensa = 15 + (nivel_onda * 2)

        self.vida = self.vida_max
        self.timer_lento = 0
        self.fator_lento_atual = 1.0
        self.indice_frame = 0.0
        self.vel_animacao = 0.15

    def aplicar_lentidao(self, duracao, fator):
        self.timer_lento = duracao
        self.fator_lento_atual = fator

    def mover(self):
        vel_efetiva = self.velocidade_base

        if self.timer_lento > 0:
            self.timer_lento -= 1
            vel_efetiva *= self.fator_lento_atual
        else:
            self.fator_lento_atual = 1.0

        self.indice_frame += self.vel_animacao

        if self.indice_caminho < len(CAMINHO) - 1:
            alvo_x, alvo_y = CAMINHO[self.indice_caminho + 1]
            dx = alvo_x - self.x
            dy = alvo_y - self.y
            dist = math.hypot(dx, dy)

            if dist < vel_efetiva:
                self.x, self.y = alvo_x, alvo_y
                self.indice_caminho += 1
            else:
                self.x += (dx / dist) * vel_efetiva
                self.y += (dy / dist) * vel_efetiva
        else:
            return True  # Chegou ao fim

        return False

    def desenhar(self):
        # Define frames e cor de fallback
        if self.tipo_inimigo == 'tank':
            frames_key = 'enemy_hp_frames'
            cor_fallback = (1, 0.5, 0)
        elif self.tipo_inimigo == 'speed':
            frames_key = 'enemy_speed_frames'
            cor_fallback = (1, 1, 0)
        else:
            frames_key = 'enemy_frames'
            cor_fallback = (1, 1, 1)

        frames_inimigo = TEXTURAS.get(frames_key, [])
        cor = (1, 1, 1)

        if self.timer_lento > 0:
            cor = (0.3, 0.3, 1.0)

        # Desenha sprite ou círculo
        if frames_inimigo:
            idx = int(self.indice_frame) % len(frames_inimigo)
            tamanho = 30
            if self.tipo_inimigo == 'tank':
                tamanho = 36
            elif self.tipo_inimigo == 'speed':
                tamanho = 24

            desenhar_sprite(frames_inimigo[idx], self.x, self.y, tamanho, tamanho, cor=cor)
        else:
            cor_desenho = cor if self.timer_lento > 0 else cor_fallback
            glColor3f(*cor_desenho)
            desenhar_circulo(self.x, self.y, self.raio)

        # Barra de vida
        glColor3f(1, 0, 0)
        razao = max(0, self.vida / self.vida_max)
        desenhar_retangulo(self.x - 10, self.y - 20, 20 * razao, 4)


class Torre:
    """Torre que ataca inimigos"""

    def __init__(self, x, y, chave_tipo):
        self.x, self.y = x, y
        self.tipo = chave_tipo
        self.stats = TIPOS_TORRES[chave_tipo].copy()
        self.timer_cooldown = 0
        self.nivel = 1
        self.investimento_total = self.stats['custo']
        self.cooldown_base = self.stats['speed']
        self.esta_buffada = False
        self.estrategia = 'PRIMEIRO'  # PRIMEIRO, ÚLTIMO, MAIS VIDA

    def melhorar(self):
        """Faz upgrade da torre"""
        custo = self.nivel * 50
        self.nivel += 1

        if self.stats['nome'] == 'Estimulante':
            self.stats['buff_factor'] += 0.15
            self.stats['range'] *= 1.1
        elif self.stats['nome'] == 'Fazenda':
            self.stats['income'] += 10
        else:
            self.stats['dano'] *= 1.3
            self.stats['range'] *= 1.1
            self.cooldown_base *= 0.9
            self.stats['speed'] = self.cooldown_base

        self.investimento_total += custo
        return custo

    def resetar_buffs(self):
        if self.stats['role'] == 'DANO':
            self.stats['speed'] = self.cooldown_base
        self.esta_buffada = False

    def aplicar_buff(self, fator):
        if self.stats['role'] == 'DANO':
            nova_speed = self.cooldown_base / fator
            if nova_speed < self.stats['speed']:
                self.stats['speed'] = nova_speed
                self.esta_buffada = True

    def atualizar(self, inimigos, lista_projeteis, ref_jogo):
        if self.timer_cooldown > 0:
            self.timer_cooldown -= 1
            return

        # Torre de renda
        if self.stats.get('income', 0) > 0:
            if ref_jogo.onda_ativa:
                quantidade = self.stats['income']
                ref_jogo.dinheiro += quantidade
                self.timer_cooldown = self.stats['speed']
                ref_jogo.textos_flutuantes.append(
                    TextoFlutuante(self.x, self.y + 20, f"+${quantidade}")
                )
            return

        # Filtra inimigos no alcance
        inimigos_no_alcance = []
        for inimigo in inimigos:
            dist = math.hypot(inimigo.x - self.x, inimigo.y - self.y)
            if dist <= self.stats['range']:
                inimigos_no_alcance.append(inimigo)

        if inimigos_no_alcance:
            alvo = None

            if self.estrategia == 'PRIMEIRO':
                alvo = inimigos_no_alcance[0]
            elif self.estrategia == 'ÚLTIMO':
                alvo = inimigos_no_alcance[-1]
            elif self.estrategia == 'MAIS VIDA':
                alvo = max(inimigos_no_alcance, key=lambda e: e.vida)

            if alvo:
                self.atirar(alvo, lista_projeteis)

    def atirar(self, inimigo, lista_projeteis):
        proj = Projetil(
            self.x, self.y, inimigo,
            self.stats['dano'],
            self.stats['cor'],
            self.stats['slow_factor'],
            self.stats['slow_time']
        )
        lista_projeteis.append(proj)
        self.timer_cooldown = self.stats['speed']

    def desenhar(self, selecionada=False):
        from utils import desenhar_circulo_contorno

        chave_tex = self.stats['img_name']
        desenhado = desenhar_sprite(TEXTURAS.get(chave_tex), self.x, self.y, 40, 40)

        if not desenhado:
            glColor3f(*self.stats['cor'])
            desenhar_retangulo(self.x - 15, self.y - 15, 30, 30)

        # Ícone de buff
        if self.esta_buffada:
            icone_ok = desenhar_sprite(TEXTURAS.get('buff_icon'), self.x, self.y - 30, 20, 20)
            if not icone_ok:
                glColor3f(1, 1, 0)
                desenhar_retangulo(self.x - 5, self.y - 35, 10, 10)

        # Contorno se selecionada
        if selecionada:
            glColor3f(0, 0, 0)
            desenhar_circulo_contorno(self.x, self.y, self.stats['range'])

            if self.stats.get('buff_factor', 1.0) > 1.0:
                glColor3f(1, 1, 0)
                desenhar_circulo_contorno(self.x, self.y, self.stats['range'] + 2)