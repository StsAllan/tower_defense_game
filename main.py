from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

from config import *
from utils import *
from jogo import Jogo, GerenciadorMusica
from entidades import Torre


def processar_eventos(jogo, evento, mx, my):
    if my > ALTURA_AREA_JOGO:
        if evento.button == 1:
            for nome_aba, rect in jogo.abas.items():
                if rect.collidepoint(mx, my):
                    jogo.aba_ativa = nome_aba
                    jogo.modo_construcao = None

            botoes_torres = {}
            x_offset = 10
            for chave, dados in TIPOS_TORRES.items():
                if dados['role'] == jogo.aba_ativa:
                    rect = Rect(x_offset, ALTURA_AREA_JOGO + 60, 100, 40)
                    botoes_torres[chave] = rect
                    x_offset += 110

            for chave, rect in botoes_torres.items():
                if rect.collidepoint(mx, my):
                    if jogo.dinheiro >= TIPOS_TORRES[chave]['custo']:
                        jogo.modo_construcao = chave
                        jogo.torre_selecionada = None

            if jogo.btn_onda.collidepoint(mx, my):
                jogo.iniciar_onda()

            if jogo.torre_selecionada:
                if jogo.btn_vender.collidepoint(mx, my):
                    reembolso = int(jogo.torre_selecionada.investimento_total * 0.75)
                    jogo.dinheiro += reembolso
                    jogo.torres.remove(jogo.torre_selecionada)
                    jogo.torre_selecionada = None

                # Botões de estratégia
                elif jogo.btn_primeiro.collidepoint(mx, my):
                    jogo.torre_selecionada.estrategia = 'PRIMEIRO'
                elif jogo.btn_mais_vida.collidepoint(mx, my):
                    jogo.torre_selecionada.estrategia = 'MAIS VIDA'
                elif jogo.btn_ultimo.collidepoint(mx, my):
                    jogo.torre_selecionada.estrategia = 'ÚLTIMO'

    else:
        if evento.button == 1:
            if jogo.modo_construcao:
                if jogo.pode_construir(mx, my):
                    jogo.torres.append(Torre(mx, my, jogo.modo_construcao))
                    jogo.dinheiro -= TIPOS_TORRES[jogo.modo_construcao]['custo']
                    jogo.modo_construcao = None
            else:
                clicou = False
                for torre in jogo.torres:
                    if math.hypot(torre.x - mx, torre.y - my) < 20:
                        jogo.torre_selecionada = torre
                        clicou = True
                        break
                if not clicou:
                    jogo.torre_selecionada = None

        elif evento.button == 3:
            if jogo.modo_construcao:
                jogo.modo_construcao = None
            elif jogo.torre_selecionada:
                dist = math.hypot(jogo.torre_selecionada.x - mx, jogo.torre_selecionada.y - my)
                if dist < 20 and jogo.dinheiro >= jogo.torre_selecionada.nivel * 50:
                    jogo.dinheiro -= jogo.torre_selecionada.nivel * 50
                    jogo.torre_selecionada.melhorar()


def desenhar_ui(jogo, fonte, fonte_hud, fonte_pequena):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0, 0, 0, 0.5)
    desenhar_retangulo(0, 0, LARGURA_LOGICA, 40)
    glDisable(GL_BLEND)

    desenhar_texto(f"ONDA {jogo.onda}", LARGURA_LOGICA - 140, 25, fonte_hud)

    if desenhar_sprite(TEXTURAS.get('heart'), 30, 20, 24, 24):
        pass
    else:
        glColor3f(1, 0, 0)
        desenhar_retangulo(18, 8, 24, 24)
    desenhar_texto(f"{jogo.vidas}", 60, 28, fonte_hud)

    if desenhar_sprite(TEXTURAS.get('coin'), 130, 20, 24, 24):
        pass
    else:
        glColor3f(1, 1, 0)
        desenhar_retangulo(118, 8, 24, 24)
    desenhar_texto(f"${jogo.dinheiro}", 160, 28, fonte_hud)

    if TEXTURAS.get('menu_bottom'):
        desenhar_sprite(
            TEXTURAS['menu_bottom'],
            LARGURA_LOGICA / 2,
            ALTURA_AREA_JOGO + ALTURA_UI / 2,
            800, 150
        )
    else:
        glColor3f(0.2, 0.2, 0.2)
        desenhar_retangulo(0, ALTURA_AREA_JOGO, LARGURA_LOGICA, ALTURA_UI)

    # Abas
    for nome_aba, rect in jogo.abas.items():
        if nome_aba == jogo.aba_ativa:
            glColor3f(0.5, 0.5, 0.8)
        else:
            glColor3f(0.3, 0.3, 0.3)
        desenhar_retangulo(rect.x, rect.y, rect.w, rect.h)

        text_w, text_h = fonte.size(nome_aba)
        center_x = rect.x + (rect.w - text_w) / 2
        center_y = rect.y + (rect.h / 2) + (text_h / 4)
        desenhar_texto(nome_aba, center_x, center_y, fonte)

    x_offset = 10
    for chave, dados in TIPOS_TORRES.items():
        if dados['role'] == jogo.aba_ativa:
            rect = Rect(x_offset, ALTURA_AREA_JOGO + 60, 100, 40)

            if chave == jogo.modo_construcao:
                glColor3f(0.8, 0.8, 0.8)
            else:
                glColor3f(0.5, 0.5, 0.5)
            desenhar_retangulo(rect.x, rect.y, rect.w, rect.h)

            nome_txt = f"{dados['nome']}"
            custo_txt = f"${dados['custo']}"

            nw, nh = fonte.size(nome_txt)
            cw, ch = fonte.size(custo_txt)

            desenhar_texto(nome_txt, rect.x + (rect.w - nw) / 2, rect.y + 12, fonte)
            desenhar_texto(custo_txt, rect.x + (rect.w - cw) / 2, rect.y + 28, fonte)

            x_offset += 110

    glColor3f(0, 0.8, 0)
    desenhar_retangulo(jogo.btn_onda.x, jogo.btn_onda.y, jogo.btn_onda.w, jogo.btn_onda.h)
    onda_txt = "Prox Onda"
    ww, wh = fonte.size(onda_txt)
    desenhar_texto(
        onda_txt,
        jogo.btn_onda.x + (jogo.btn_onda.w - ww) / 2,
        jogo.btn_onda.y + 20,
        fonte,
        (0, 0, 0, 255)
    )

    if jogo.torre_selecionada:
        t = jogo.torre_selecionada

        if t.stats['nome'] == 'Estimulante':
            info = f"{t.stats['nome']} (Lv {t.nivel}) | Buff: {t.stats['buff_factor']:.2f}x"
        elif t.stats['nome'] == 'Fazenda':
            info = f"{t.stats['nome']} (Lv {t.nivel}) | Renda: ${t.stats['income']}/5s"
        else:
            info = f"{t.stats['nome']} (Lv {t.nivel}) | Dano: {int(t.stats['dano'])}"

        desenhar_texto(info, 350, ALTURA_AREA_JOGO + 30, fonte, (255, 255, 255, 255))
        desenhar_texto(f"Upgrade: ${t.nivel * 50} (Dir.)", 350, ALTURA_AREA_JOGO + 50, fonte)

        valor_venda = int(t.investimento_total * 0.75)
        glColor3f(0.8, 0.2, 0.2)
        desenhar_retangulo(jogo.btn_vender.x, jogo.btn_vender.y, jogo.btn_vender.w, jogo.btn_vender.h)

        vender_txt = f"VENDER ${valor_venda}"
        sw, sh = fonte.size(vender_txt)
        desenhar_texto(vender_txt, jogo.btn_vender.x + (jogo.btn_vender.w - sw) / 2, jogo.btn_vender.y + 20, fonte)

        if t.stats['nome'] != 'Fazenda':
            c1 = (0, 0.8, 0) if t.estrategia == 'PRIMEIRO' else (0.4, 0.4, 0.4)
            c2 = (0, 0.8, 0) if t.estrategia == 'MAIS VIDA' else (0.4, 0.4, 0.4)
            c3 = (0, 0.8, 0) if t.estrategia == 'ÚLTIMO' else (0.4, 0.4, 0.4)

            glColor3f(*c1)
            desenhar_retangulo(jogo.btn_primeiro.x, jogo.btn_primeiro.y, jogo.btn_primeiro.w, jogo.btn_primeiro.h)
            tw, th = fonte_pequena.size("Primeiro")
            desenhar_texto("Primeiro", jogo.btn_primeiro.x + (60 - tw) / 2, jogo.btn_primeiro.y + 12, fonte_pequena)

            glColor3f(*c2)
            desenhar_retangulo(jogo.btn_mais_vida.x, jogo.btn_mais_vida.y, jogo.btn_mais_vida.w, jogo.btn_mais_vida.h)
            tw, th = fonte_pequena.size("Mais Vida")
            desenhar_texto("Mais Vida", jogo.btn_mais_vida.x + (70 - tw) / 2, jogo.btn_mais_vida.y + 12, fonte_pequena)

            glColor3f(*c3)
            desenhar_retangulo(jogo.btn_ultimo.x, jogo.btn_ultimo.y, jogo.btn_ultimo.w, jogo.btn_ultimo.h)
            tw, th = fonte_pequena.size("Último")
            desenhar_texto("Último", jogo.btn_ultimo.x + (60 - tw) / 2, jogo.btn_ultimo.y + 12, fonte_pequena)


def main():
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    tela = pygame.display.set_mode((LARGURA_LOGICA, ALTURA_LOGICA), DOUBLEBUF | OPENGL | RESIZABLE)
    pygame.display.set_caption("Tower Defense OpenGL")

    atualizar_viewport(LARGURA_LOGICA, ALTURA_LOGICA)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, LARGURA_LOGICA, ALTURA_LOGICA, 0)
    glMatrixMode(GL_MODELVIEW)

    fonte = pygame.font.SysFont('Arial', 16)
    fonte_hud = pygame.font.SysFont('Arial', 24, bold=True)
    fonte_float = pygame.font.SysFont('Arial', 14, bold=True)
    fonte_pequena = pygame.font.SysFont('Arial', 12, bold=True)

    jogo = Jogo()
    musica = GerenciadorMusica(pygame.mixer)
    musica.iniciar()

    relogio = pygame.time.Clock()
    rodando = True

    while rodando:
        if pygame.mixer.get_init():
            if jogo.onda_ativa:
                musica.trocar('onda')
            else:
                musica.trocar('normal')
            musica.atualizar()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            if evento.type == VIDEORESIZE:
                tela = pygame.display.set_mode((evento.w, evento.h), DOUBLEBUF | OPENGL | RESIZABLE)
                atualizar_viewport(evento.w, evento.h)
                glMatrixMode(GL_PROJECTION)
                glLoadIdentity()
                gluOrtho2D(0, LARGURA_LOGICA, ALTURA_LOGICA, 0)
                glMatrixMode(GL_MODELVIEW)
                jogo.carregar_assets()

            if evento.type == pygame.MOUSEBUTTONDOWN:
                mx, my = obter_mouse_logico()
                processar_eventos(jogo, evento, mx, my)

        if jogo.vidas > 0:
            jogo.atualizar()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if TEXTURAS.get('background'):
            desenhar_sprite(TEXTURAS['background'], LARGURA_LOGICA / 2, 225, 800, 450)
        else:
            glColor3f(0.1, 0.1, 0.1)
            desenhar_retangulo(0, 0, LARGURA_LOGICA, ALTURA_LOGICA)

        for inimigo in jogo.inimigos:
            inimigo.desenhar()

        for torre in jogo.torres:
            torre.desenhar(selecionada=(torre == jogo.torre_selecionada))

        for proj in jogo.projeteis:
            proj.desenhar()

        for texto in jogo.textos_flutuantes:
            texto.desenhar(fonte_float)

        if jogo.modo_construcao:
            mx, my = obter_mouse_logico()
            if my < ALTURA_AREA_JOGO:
                stats = TIPOS_TORRES[jogo.modo_construcao]
                valido = jogo.pode_construir(mx, my)

                if not desenhar_sprite(TEXTURAS.get(stats['img_name']), mx, my, 40, 40, alpha=0.5):
                    glEnable(GL_BLEND)
                    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                    glColor4f(*stats['cor'], 0.5)
                    desenhar_retangulo(mx - 15, my - 15, 30, 30)
                    glDisable(GL_BLEND)

                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                if valido:
                    glColor4f(0, 0, 0, 0.3)
                else:
                    glColor4f(1, 0, 0, 0.5)
                desenhar_circulo_contorno(mx, my, stats['range'])
                glDisable(GL_BLEND)

        desenhar_ui(jogo, fonte, fonte_hud, fonte_pequena)

        if jogo.vidas <= 0:
            desenhar_texto("GAME OVER", LARGURA_LOGICA / 2, ALTURA_LOGICA / 2, fonte_hud)

        pygame.display.flip()
        relogio.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()