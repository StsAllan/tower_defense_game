import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import os

# --- Configurações Lógicas ---
LOGICAL_WIDTH = 800
LOGICAL_HEIGHT = 600
UI_HEIGHT = 150 
PLAY_AREA_HEIGHT = LOGICAL_HEIGHT - UI_HEIGHT

# --- Variáveis de Viewport ---
viewport_x = 0
viewport_y = 0
viewport_w = LOGICAL_WIDTH
viewport_h = LOGICAL_HEIGHT
scale_ratio = 1.0

# --- Dicionário de Texturas ---
TEXTURES = {}

# --- Definição das Torres ---
TOWER_TYPES = {
    'BASICA': {'nome': 'Basica', 'role': 'DANO', 'range': 100, 'dano': 20, 'speed': 30, 'custo': 100, 'cor': (0, 1, 1), 'img_name': 'basica.png', 'slow_factor': 1.0, 'slow_time': 0, 'buff_factor': 1.0, 'income': 0}, 
    'RAPIDA': {'nome': 'Rapida', 'role': 'DANO', 'range': 70, 'dano': 8, 'speed': 10, 'custo': 150, 'cor': (1, 1, 0), 'img_name': 'rapida.png', 'slow_factor': 1.0, 'slow_time': 0, 'buff_factor': 1.0, 'income': 0}, 
    'SNIPER': {'nome': 'Sniper', 'role': 'DANO', 'range': 200, 'dano': 100, 'speed': 80, 'custo': 200, 'cor': (1, 0, 1), 'img_name': 'sniper.png', 'slow_factor': 1.0, 'slow_time': 0, 'buff_factor': 1.0, 'income': 0},
    'GELINHO': {'nome': 'Gelinho', 'role': 'SUPORTE', 'range': 110, 'dano': 5, 'speed': 40, 'custo': 120, 'cor': (0.5, 0.8, 1), 'img_name': 'gelinho.png', 'slow_factor': 0.5, 'slow_time': 120, 'buff_factor': 1.0, 'income': 0},
    'ESTIMULANTE': {'nome': 'Estimulante', 'role': 'SUPORTE', 'range': 80, 'dano': 2, 'speed': 45, 'custo': 250, 'cor': (1, 0.5, 0), 'img_name': 'estimulante.png', 'slow_factor': 1.0, 'slow_time': 0, 'buff_factor': 1.3, 'income': 0},
    'FAZENDA': {'nome': 'Fazenda', 'role': 'SUPORTE', 'range': 40, 'dano': 0, 'speed': 300, 'custo': 300, 'cor': (0, 0.8, 0), 'img_name': 'fazenda.png', 'slow_factor': 1.0, 'slow_time': 0, 'buff_factor': 1.0, 'income': 10},
}

PATH = [(0, 100), (200, 100), (200, 300), (500, 300), (500, 100), (700, 100), (700, 450), (800, 450)]

# --- Funções de Tela ---
def update_viewport(window_w, window_h):
    global viewport_x, viewport_y, viewport_w, viewport_h, scale_ratio
    target_aspect = LOGICAL_WIDTH / LOGICAL_HEIGHT
    window_aspect = window_w / window_h
    
    if window_aspect > target_aspect:
        viewport_h = window_h
        viewport_w = int(window_h * target_aspect)
        viewport_y = 0
        viewport_x = int((window_w - viewport_w) / 2)
    else:
        viewport_w = window_w
        viewport_h = int(window_w / target_aspect)
        viewport_x = 0
        viewport_y = int((window_h - viewport_h) / 2)
        
    scale_ratio = LOGICAL_WIDTH / viewport_w
    glViewport(viewport_x, viewport_y, viewport_w, viewport_h)

def get_logical_mouse():
    raw_x, raw_y = pygame.mouse.get_pos()
    window_h = pygame.display.get_surface().get_height()
    margin_top = (window_h - viewport_h) / 2
    game_x = (raw_x - viewport_x) * scale_ratio
    game_y = (raw_y - margin_top) * scale_ratio
    return game_x, game_y

def dist_point_to_segment(px, py, x1, y1, x2, y2):
    l2 = (x1 - x2)**2 + (y1 - y2)**2
    if l2 == 0: return math.hypot(px - x1, py - y1)
    t = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / l2
    t = max(0, min(1, t))
    proj_x = x1 + t * (x2 - x1)
    proj_y = y1 + t * (y2 - y1)
    return math.hypot(px - proj_x, py - proj_y)

# --- Carregamento ---
def load_texture(filename):
    path = os.path.join("assets", filename)
    if not os.path.exists(path): return None
    try:
        texture_surface = pygame.image.load(path).convert_alpha()
        texture_surface = pygame.transform.flip(texture_surface, False, True)
        texture_data = pygame.image.tostring(texture_surface, "RGBA", 1)
        width, height = texture_surface.get_width(), texture_surface.get_height()
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        return tex_id
    except: return None

def draw_sprite(texture_id, x, y, width, height, color=(1,1,1), alpha=1.0):
    if texture_id is None: return False 
    glEnable(GL_TEXTURE_2D); glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glColor4f(color[0], color[1], color[2], alpha)
    half_w, half_h = width / 2, height / 2
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(x - half_w, y - half_h)
    glTexCoord2f(1, 0); glVertex2f(x + half_w, y - half_h)
    glTexCoord2f(1, 1); glVertex2f(x + half_w, y + half_h)
    glTexCoord2f(0, 1); glVertex2f(x - half_w, y + half_h)
    glEnd()
    glDisable(GL_TEXTURE_2D); glDisable(GL_BLEND)
    return True

# --- NOVA FUNÇÃO DE TEXTO (Desenha como Sprite) ---
def draw_text(text, x, y, font, color=(255, 255, 255, 255)):
    # Renderiza no Pygame
    text_surface = font.render(text, True, color)
    # Inverte igual as texturas para ficar correto no OpenGL
    text_surface = pygame.transform.flip(text_surface, False, True)
    
    text_data = pygame.image.tostring(text_surface, "RGBA", 1)
    w, h = text_surface.get_width(), text_surface.get_height()

    # Gera textura temporária
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    # Desenha usando a lógica de sprite (centrado)
    # Como o X passado geralmente é "Esquerda", compensamos somando w/2
    draw_sprite(tex_id, x + w/2, y, w, h)
    
    # Limpa memória da textura
    glDeleteTextures(1, [tex_id])

# --- Classes ---
class FloatingText:
    def __init__(self, x, y, text, color=(0.2, 1.0, 0.2)): 
        self.x, self.y = x, y
        self.text = text
        self.color = color
        self.timer = 60 
        self.active = True
    def update(self):
        self.y += 0.5 
        self.timer -= 1
        if self.timer <= 0: self.active = False
    def draw(self, font):
        # Floating text desenha um pouco diferente (transparência dinâmica), 
        # mas vamos usar a nova draw_text com cor modificada se possível, 
        # ou manter lógica simplificada para performance. 
        # Mantendo simplificado com draw_text para consistência:
        alpha = 255
        if self.timer < 20: alpha = int((self.timer / 20.0) * 255)
        r = int(self.color[0]*255)
        g = int(self.color[1]*255)
        b = int(self.color[2]*255)
        draw_text(self.text, self.x, self.y, font, (r, g, b, alpha))

class Projectile:
    def __init__(self, x, y, target, damage, color, slow_factor=1.0, slow_time=0):
        self.x, self.y = x, y
        self.target = target
        self.damage = damage
        self.color = color
        self.speed = 12 
        self.active = True
        self.radius = 4
        self.slow_factor = slow_factor
        self.slow_time = slow_time
    def update(self):
        if not self.target.active: self.active = False; return
        dx, dy = self.target.x - self.x, self.target.y - self.y
        dist = math.hypot(dx, dy)
        if dist < self.speed + self.target.radius:
            self.target.health -= self.damage
            if self.slow_time > 0: self.target.apply_slow(self.slow_time, self.slow_factor)
            self.active = False 
        else:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
    def draw(self):
        glColor3f(*self.color)
        draw_circle(self.x, self.y, self.radius)

class Enemy:
    def __init__(self, wave_level):
        self.path_index = 0
        self.x, self.y = PATH[0]
        self.max_health = 50 + (wave_level * 25)
        self.health = self.max_health
        self.base_speed = 1.5 + (wave_level * 0.1)
        self.slow_timer = 0
        self.current_slow_factor = 1.0
        self.radius = 15 
        self.reward = 15 + (wave_level * 2)
        self.active = True
        self.frame_index = 0.0
        self.animation_speed = 0.15
    def apply_slow(self, duration, factor):
        self.slow_timer = duration
        self.current_slow_factor = factor
    def move(self):
        effective_speed = self.base_speed
        if self.slow_timer > 0:
            self.slow_timer -= 1
            effective_speed *= self.current_slow_factor
        else: self.current_slow_factor = 1.0
        self.frame_index += self.animation_speed
        if self.path_index < len(PATH) - 1:
            target_x, target_y = PATH[self.path_index + 1]
            dx, dy = target_x - self.x, target_y - self.y
            dist = math.hypot(dx, dy)
            if dist < effective_speed:
                self.x, self.y = target_x, target_y
                self.path_index += 1
            else:
                self.x += (dx / dist) * effective_speed
                self.y += (dy / dist) * effective_speed
        else: return True 
        return False
    def draw(self):
        enemy_frames = TEXTURES.get('enemy_frames', [])
        color = (1, 1, 1)
        if self.slow_timer > 0: color = (0.3, 0.3, 1.0) 
        if enemy_frames:
            idx = int(self.frame_index) % len(enemy_frames)
            draw_sprite(enemy_frames[idx], self.x, self.y, 30, 30, color=color)
        else:
            glColor3f(*color); draw_circle(self.x, self.y, self.radius)
        glColor3f(1, 0, 0) 
        ratio = max(0, self.health / self.max_health)
        draw_rect(self.x - 10, self.y - 20, 20 * ratio, 4)

class Tower:
    def __init__(self, x, y, type_key):
        self.x, self.y = x, y
        self.type = type_key
        self.stats = TOWER_TYPES[type_key].copy()
        self.cooldown_timer = 0
        self.level = 1
        self.total_investment = self.stats['custo']
        self.base_cooldown = self.stats['speed']
        self.is_buffed = False
    def upgrade(self):
        cost = self.level * 50
        self.level += 1
        if self.stats['nome'] == 'Estimulante':
            self.stats['buff_factor'] += 0.15
            self.stats['range'] *= 1.1 
        elif self.stats['nome'] == 'Fazenda':
            self.stats['income'] += 10 
        else:
            self.stats['dano'] *= 1.3
            self.stats['range'] *= 1.1
            self.base_cooldown *= 0.9 
            self.stats['speed'] = self.base_cooldown
        self.total_investment += cost
        return cost
    def reset_buffs(self):
        if self.stats['role'] == 'DANO':
            self.stats['speed'] = self.base_cooldown
        self.is_buffed = False
    def apply_buff(self, factor):
        if self.stats['role'] == 'DANO':
            new_speed = self.base_cooldown / factor
            if new_speed < self.stats['speed']:
                self.stats['speed'] = new_speed
                self.is_buffed = True
    def update(self, enemies, projectiles_list, game_ref):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
            return
        if self.stats.get('income', 0) > 0:
            if game_ref.wave_active:
                if self.cooldown_timer <= 0:
                    amount = self.stats['income']
                    game_ref.money += amount
                    self.cooldown_timer = self.stats['speed'] 
                    game_ref.floating_texts.append(FloatingText(self.x, self.y + 20, f"+${amount}"))
            return 
        for enemy in enemies:
            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist <= self.stats['range']:
                self.shoot(enemy, projectiles_list)
                break
    def shoot(self, enemy, projectiles_list):
        proj = Projectile(self.x, self.y, enemy, self.stats['dano'], self.stats['cor'], self.stats['slow_factor'], self.stats['slow_time'])
        projectiles_list.append(proj)
        self.cooldown_timer = self.stats['speed']
    def draw(self, selected=False):
        tex_key = self.stats['img_name']
        drawn = draw_sprite(TEXTURES.get(tex_key), self.x, self.y, 40, 40)
        if not drawn:
            glColor3f(*self.stats['cor'])
            draw_rect(self.x - 15, self.y - 15, 30, 30)
        if self.is_buffed:
            icon_drawn = draw_sprite(TEXTURES.get('buff_icon'), self.x, self.y - 30, 20, 20)
            if not icon_drawn:
                glColor3f(1, 1, 0); draw_rect(self.x - 5, self.y - 35, 10, 10)
        if selected:
            glColor3f(0, 0, 0)
            draw_circle_outline(self.x, self.y, self.stats['range'])
            if self.stats.get('buff_factor', 1.0) > 1.0:
                glColor3f(1, 1, 0); draw_circle_outline(self.x, self.y, self.stats['range'] + 2)

class Game:
    def __init__(self):
        self.money = 400
        self.lives = 10
        self.wave = 0
        self.enemies = []
        self.projectiles = [] 
        self.towers = []
        self.floating_texts = [] 
        self.selected_tower = None
        self.wave_active = False
        self.enemies_to_spawn = 0
        self.spawn_timer = 0
        self.build_mode = None 
        
        self.sell_button_rect = Rect(650, LOGICAL_HEIGHT - 60, 120, 40)
        self.wave_button_rect = Rect(650, LOGICAL_HEIGHT - 130, 120, 40)
        self.active_tab = 'DANO'
        self.tabs = {
            'DANO': Rect(10, PLAY_AREA_HEIGHT + 10, 100, 30),
            'SUPORTE': Rect(120, PLAY_AREA_HEIGHT + 10, 100, 30)
        }
        self.load_assets()

    def load_assets(self):
        enemy_frames = []
        for i in range(4): 
            tex = load_texture(f'enemy_{i}.png')
            if tex: enemy_frames.append(tex)
            elif i == 0: 
                fb = load_texture('enemy.png')
                if fb: enemy_frames.append(fb)
        TEXTURES['enemy_frames'] = enemy_frames
        for key, data in TOWER_TYPES.items():
            TEXTURES[data['img_name']] = load_texture(data['img_name'])
        TEXTURES['background'] = load_texture('background.png')
        TEXTURES['buff_icon'] = load_texture('buff_icon.png') 
        TEXTURES['heart'] = load_texture('heart.png')
        TEXTURES['coin'] = load_texture('coin.png')
    
    def can_build(self, x, y):
        path_radius = 25
        for i in range(len(PATH) - 1):
            p1 = PATH[i]
            p2 = PATH[i+1]
            dist = dist_point_to_segment(x, y, p1[0], p1[1], p2[0], p2[1])
            if dist < path_radius: return False
        min_tower_dist = 40
        for t in self.towers:
            dist = math.hypot(x - t.x, y - t.y)
            if dist < min_tower_dist: return False
        return True

    def start_wave(self):
        if not self.wave_active:
            self.wave += 1
            base_amount = 5 + self.wave
            cycle = self.wave // 3 
            multiplier = 1.7 ** cycle
            self.enemies_to_spawn = int(base_amount * multiplier)
            print(f"Iniciando Onda {self.wave}: {self.enemies_to_spawn} inimigos (Mult: {multiplier:.2f}x)")
            self.wave_active = True

    def update(self):
        if self.wave_active and self.enemies_to_spawn > 0:
            self.spawn_timer += 1
            if self.spawn_timer > 60:
                self.enemies.append(Enemy(self.wave))
                self.enemies_to_spawn -= 1
                self.spawn_timer = 0
        elif self.wave_active and len(self.enemies) == 0 and self.enemies_to_spawn == 0:
            self.wave_active = False 
        for e in self.enemies[:]:
            if e.move():
                self.lives -= 1
                e.active = False
                self.enemies.remove(e)
            elif e.health <= 0:
                self.money += int(e.reward)
                e.active = False
                self.enemies.remove(e)
        for t in self.towers: t.reset_buffs()
        for t in self.towers:
            buff_factor = t.stats.get('buff_factor', 1.0)
            if buff_factor > 1.0: 
                for target in self.towers:
                    if target != t: 
                        dist = math.hypot(target.x - t.x, target.y - t.y)
                        if dist <= t.stats['range']: target.apply_buff(buff_factor)
        for t in self.towers: t.update(self.enemies, self.projectiles, self)
        for p in self.projectiles[:]:
            p.update()
            if not p.active: self.projectiles.remove(p)
        for ft in self.floating_texts[:]:
            ft.update()
            if not ft.active: self.floating_texts.remove(ft)

# --- Desenho Auxiliar ---
def draw_rect(x, y, width, height):
    glBegin(GL_QUADS)
    glVertex2f(x, y); glVertex2f(x + width, y); 
    glVertex2f(x + width, y + height); glVertex2f(x, y + height)
    glEnd()
def draw_circle(x, y, radius):
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x, y)
    for i in range(361):
        angle = math.radians(i)
        glVertex2f(x + math.cos(angle) * radius, y + math.sin(angle) * radius)
    glEnd()
def draw_circle_outline(x, y, radius):
    glBegin(GL_LINE_LOOP)
    for i in range(360):
        angle = math.radians(i)
        glVertex2f(x + math.cos(angle) * radius, y + math.sin(angle) * radius)
    glEnd()

# --- Main ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((LOGICAL_WIDTH, LOGICAL_HEIGHT), DOUBLEBUF | OPENGL | RESIZABLE)
    pygame.display.set_caption("Tower Defense OpenGL")
    
    update_viewport(LOGICAL_WIDTH, LOGICAL_HEIGHT)
    glMatrixMode(GL_PROJECTION); glLoadIdentity()
    gluOrtho2D(0, LOGICAL_WIDTH, LOGICAL_HEIGHT, 0)
    glMatrixMode(GL_MODELVIEW)

    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Arial', 16)
    font_hud = pygame.font.SysFont('Arial', 24, bold=True) 
    font_float = pygame.font.SysFont('Arial', 14, bold=True)
    game = Game()

    running = True
    while running:
        current_tower_buttons = {}
        x_offset = 10
        for key, data in TOWER_TYPES.items():
            if data['role'] == game.active_tab:
                rect = Rect(x_offset, PLAY_AREA_HEIGHT + 60, 100, 40)
                current_tower_buttons[key] = rect
                x_offset += 110

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            
            if event.type == VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), DOUBLEBUF | OPENGL | RESIZABLE)
                update_viewport(event.w, event.h)
                glMatrixMode(GL_PROJECTION); glLoadIdentity()
                gluOrtho2D(0, LOGICAL_WIDTH, LOGICAL_HEIGHT, 0)
                glMatrixMode(GL_MODELVIEW)
                game.load_assets()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = get_logical_mouse()
                if my > PLAY_AREA_HEIGHT: 
                    if event.button == 1:
                        for tab_name, rect in game.tabs.items():
                            if rect.collidepoint(mx, my):
                                game.active_tab = tab_name; game.build_mode = None 
                        for key, rect in current_tower_buttons.items():
                            if rect.collidepoint(mx, my):
                                if game.money >= TOWER_TYPES[key]['custo']:
                                    game.build_mode = key; game.selected_tower = None
                        if game.wave_button_rect.collidepoint(mx, my): game.start_wave()
                        if game.selected_tower and game.sell_button_rect.collidepoint(mx, my):
                            refund = int(game.selected_tower.total_investment * 0.75)
                            game.money += refund
                            game.towers.remove(game.selected_tower)
                            game.selected_tower = None
                else: 
                    if event.button == 1: 
                        if game.build_mode:
                            if game.can_build(mx, my):
                                game.towers.append(Tower(mx, my, game.build_mode))
                                game.money -= TOWER_TYPES[game.build_mode]['custo']
                                game.build_mode = None
                            else: print("Lugar inválido!")
                        else:
                            clicked = False
                            for t in game.towers:
                                if math.hypot(t.x - mx, t.y - my) < 20:
                                    game.selected_tower = t; clicked = True; break
                            if not clicked: game.selected_tower = None
                    elif event.button == 3:
                        if game.build_mode: game.build_mode = None 
                        elif game.selected_tower:
                            dist = math.hypot(game.selected_tower.x - mx, game.selected_tower.y - my)
                            if dist < 20 and game.money >= game.selected_tower.level * 50:
                                game.money -= game.selected_tower.level * 50
                                game.selected_tower.upgrade()

        if game.lives > 0: game.update()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        if TEXTURES.get('background'): 
            draw_sprite(TEXTURES['background'], LOGICAL_WIDTH/2, 225, 800, 450)
        else: glColor3f(0.1, 0.1, 0.1); draw_rect(0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT)
        
        for e in game.enemies: e.draw()
        for t in game.towers: t.draw(selected=(t == game.selected_tower))
        for p in game.projectiles: p.draw()
        for ft in game.floating_texts: ft.draw(font_float)

        if game.build_mode:
            mx, my = get_logical_mouse()
            if my < PLAY_AREA_HEIGHT:
                stats = TOWER_TYPES[game.build_mode]
                is_valid = game.can_build(mx, my)
                drawn = draw_sprite(TEXTURES.get(stats['img_name']), mx, my, 40, 40, alpha=0.5)
                if not drawn:
                    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                    glColor4f(*stats['cor'], 0.5); draw_rect(mx - 15, my - 15, 30, 30); glDisable(GL_BLEND)
                glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                if is_valid: glColor4f(0, 0, 0, 0.3) 
                else: glColor4f(1, 0, 0, 0.5) 
                draw_circle_outline(mx, my, stats['range']); glDisable(GL_BLEND)

        # --- HUD Topo (Com textos como textura para alinhamento correto) ---
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0, 0, 0, 0.5); draw_rect(0, 0, LOGICAL_WIDTH, 40); glDisable(GL_BLEND)
        
        # Texto Onda
        draw_text(f"ONDA {game.wave}", LOGICAL_WIDTH - 140, 20, font_hud) # Y=20 (centro)
        
        # Vida
        icon_drawn = draw_sprite(TEXTURES.get('heart'), 30, 20, 24, 24)
        if not icon_drawn: glColor3f(1, 0, 0); draw_rect(18, 8, 24, 24)
        draw_text(f"{game.lives}", 55, 20, font_hud) # Y=20 (centro)

        # Dinheiro
        icon_drawn = draw_sprite(TEXTURES.get('coin'), 130, 20, 24, 24)
        if not icon_drawn: glColor3f(1, 1, 0); draw_rect(118, 8, 24, 24)
        draw_text(f"${game.money}", 155, 20, font_hud) # Y=20 (centro)

        glColor3f(0.2, 0.2, 0.2); draw_rect(0, PLAY_AREA_HEIGHT, LOGICAL_WIDTH, UI_HEIGHT)
        for tab_name, rect in game.tabs.items():
            if tab_name == game.active_tab: glColor3f(0.5, 0.5, 0.8)
            else: glColor3f(0.3, 0.3, 0.3)
            draw_rect(rect.x, rect.y, rect.w, rect.h)
            draw_text(tab_name, rect.x, rect.y + rect.h/2, font) # Texto centralizado no botão

        for key, rect in current_tower_buttons.items():
            if key == game.build_mode: glColor3f(0.8, 0.8, 0.8)
            else: glColor3f(0.5, 0.5, 0.5)
            draw_rect(rect.x, rect.y, rect.w, rect.h)
            cost_txt = f"${TOWER_TYPES[key]['custo']}"
            # Ajuste de texto dos botões
            draw_text(f"{TOWER_TYPES[key]['nome']}", rect.x, rect.y + 12, font)
            draw_text(cost_txt, rect.x, rect.y + 28, font)

        glColor3f(0, 0.8, 0)
        draw_rect(game.wave_button_rect.x, game.wave_button_rect.y, game.wave_button_rect.w, game.wave_button_rect.h)
        draw_text("Prox Onda", game.wave_button_rect.x, game.wave_button_rect.y + 20, font)

        if game.selected_tower:
            t = game.selected_tower
            if t.stats['nome'] == 'Estimulante':
                info = f"{t.stats['nome']} (Lv {t.level}) | Buff: {t.stats['buff_factor']:.2f}x"
            elif t.stats['nome'] == 'Fazenda':
                info = f"{t.stats['nome']} (Lv {t.level}) | Renda: ${t.stats['income']}/5s"
            else:
                info = f"{t.stats['nome']} (Lv {t.level}) | Dano: {int(t.stats['dano'])}"
            
            draw_text(info, 350, PLAY_AREA_HEIGHT + 30, font, (255,255,255,255))
            
            # Botão de Upgrade
            upgrade_text = f"Upgrade: ${t.level * 50} (Dir.)"
            draw_text(upgrade_text, 350, PLAY_AREA_HEIGHT + 50, font)

            sell_val = int(t.total_investment * 0.75)
            glColor3f(0.8, 0.2, 0.2)
            draw_rect(game.sell_button_rect.x, game.sell_button_rect.y, game.sell_button_rect.w, game.sell_button_rect.h)
            draw_text(f"VENDER ${sell_val}", game.sell_button_rect.x, game.sell_button_rect.y + 20, font)

        if game.lives <= 0: draw_text("GAME OVER", LOGICAL_WIDTH/2, LOGICAL_HEIGHT/2, font)
        pygame.display.flip(); clock.tick(60)
    pygame.quit()

if __name__ == "__main__": main()