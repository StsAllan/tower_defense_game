import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import os

# --- Configurações Globais ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
UI_HEIGHT = 180 
GAME_HEIGHT = WINDOW_HEIGHT - UI_HEIGHT

# --- Dicionário de Texturas Global ---
TEXTURES = {}

# --- Definição das Torres ---
TOWER_TYPES = {
    # --- TORRES DE DANO ---
    'BASICA': {
        'nome': 'Basica', 'role': 'DANO', 
        'range': 100, 'dano': 20, 'speed': 30, 'custo': 100, 
        'cor': (0, 1, 1), 'img_name': 'basica.png',
        'slow_factor': 1.0, 'slow_time': 0, 'buff_factor': 1.0, 'income': 0
    }, 
    'RAPIDA': {
        'nome': 'Rapida', 'role': 'DANO',
        'range': 70, 'dano': 8, 'speed': 10, 'custo': 150, 
        'cor': (1, 1, 0), 'img_name': 'rapida.png',
        'slow_factor': 1.0, 'slow_time': 0, 'buff_factor': 1.0, 'income': 0
    }, 
    'SNIPER': {
        'nome': 'Sniper', 'role': 'DANO',
        'range': 200, 'dano': 100, 'speed': 80, 'custo': 200, 
        'cor': (1, 0, 1), 'img_name': 'sniper.png',
        'slow_factor': 1.0, 'slow_time': 0, 'buff_factor': 1.0, 'income': 0
    },

    # --- TORRES DE SUPORTE ---
    'GELINHO': {
        'nome': 'Gelinho', 'role': 'SUPORTE',
        'range': 110, 'dano': 5, 'speed': 40, 'custo': 120, 
        'cor': (0.5, 0.8, 1), 'img_name': 'gelinho.png',
        'slow_factor': 0.5, 'slow_time': 120, 'buff_factor': 1.0, 'income': 0
    },
    
    'ESTIMULANTE': {
        'nome': 'Estimulante', 'role': 'SUPORTE',
        'range': 80, 'dano': 2, 'speed': 45, 'custo': 250, 
        'cor': (1, 0.5, 0), 'img_name': 'estimulante.png',
        'slow_factor': 1.0, 'slow_time': 0, 'buff_factor': 1.3, 'income': 0
    },

    'FAZENDA': {
        'nome': 'Fazenda', 'role': 'SUPORTE',
        'range': 40, 
        'dano': 0,   
        'speed': 300, # 5 segundos
        'custo': 300, 
        'cor': (0, 0.8, 0), 'img_name': 'fazenda.png',
        'slow_factor': 1.0, 'slow_time': 0, 'buff_factor': 1.0,
        'income': 10 # 10 de dinheiro a cada 5s
    },
}

PATH = [(0, 100), (200, 100), (200, 300), (500, 300), (500, 100), (700, 100), (700, 450), (800, 450)]

# --- Funções de Carregamento ---

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
        if self.timer <= 0:
            self.active = False

    def draw(self, font):
        text_surface = font.render(self.text, True, (int(self.color[0]*255), int(self.color[1]*255), int(self.color[2]*255)), (0,0,0,0))
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        w, h = text_surface.get_width(), text_surface.get_height()
        alpha = 1.0
        if self.timer < 20: alpha = self.timer / 20.0
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(1, 1, 1, alpha) 
        glRasterPos2f(self.x, self.y)
        glDrawPixels(w, h, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        glDisable(GL_BLEND)

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
        self.last_int_frame = 0 
        self.animation_speed = 0.1 

    def apply_slow(self, duration, factor):
        self.slow_timer = duration
        self.current_slow_factor = factor

    def move(self):
        effective_speed = self.base_speed
        if self.slow_timer > 0:
            self.slow_timer -= 1
            effective_speed *= self.current_slow_factor
        else: self.current_slow_factor = 1.0
        step_distance = effective_speed / self.animation_speed
        self.frame_index += self.animation_speed
        current_int_frame = int(self.frame_index)
        if current_int_frame > self.last_int_frame:
            self.last_int_frame = current_int_frame
            if self.path_index < len(PATH) - 1:
                target_x, target_y = PATH[self.path_index + 1]
                dx, dy = target_x - self.x, target_y - self.y
                dist = math.hypot(dx, dy)
                if dist < step_distance:
                    self.x, self.y = target_x, target_y
                    self.path_index += 1
                else:
                    self.x += (dx / dist) * step_distance
                    self.y += (dy / dist) * step_distance
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
        glColor3f(0, 1, 0)
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
        # 1. Gerencia o Cooldown
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
            return # <--- CORREÇÃO AQUI: Para a execução se estiver em cooldown

        # 2. Se chegou aqui, cooldown é 0 (Pronto para agir)

        # --- LÓGICA DA FAZENDA ---
        if self.stats.get('income', 0) > 0:
            if game_ref.wave_active:
                amount = self.stats['income']
                game_ref.money += amount
                self.cooldown_timer = self.stats['speed'] # Reseta para 5s
                game_ref.floating_texts.append(FloatingText(self.x, self.y + 20, f"+${amount}"))
            return # Fazenda não atira
        # -------------------------

        # --- LÓGICA DE TIRO (Torres Normais) ---
        for enemy in enemies:
            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist <= self.stats['range']:
                self.shoot(enemy, projectiles_list)
                break

    def shoot(self, enemy, projectiles_list):
        proj = Projectile(
            self.x, self.y, enemy, 
            self.stats['dano'], self.stats['cor'],
            slow_factor=self.stats['slow_factor'],
            slow_time=self.stats['slow_time']
        )
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
            glColor3f(1, 1, 1)
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
        
        self.sell_button_rect = Rect(650, WINDOW_HEIGHT - 60, 120, 40)
        self.wave_button_rect = Rect(650, WINDOW_HEIGHT - 130, 120, 40)
        self.active_tab = 'DANO'
        self.tabs = {
            'DANO': Rect(10, GAME_HEIGHT + 10, 100, 30),
            'SUPORTE': Rect(120, GAME_HEIGHT + 10, 100, 30)
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

        for t in self.towers:
            t.update(self.enemies, self.projectiles, self)
            
        for p in self.projectiles[:]:
            p.update(); 
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

def draw_text(text, x, y, font, color=(255,255,255,255)):
    text_surface = font.render(text, True, color, (0,0,0,0)) 
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    w, h = text_surface.get_width(), text_surface.get_height()
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glRasterPos2f(x, y)
    glDrawPixels(w, h, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    glDisable(GL_BLEND)

# --- Main ---

def main():
    pygame.init()
    pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Tower Defense OpenGL")
    glMatrixMode(GL_PROJECTION); glLoadIdentity(); gluOrtho2D(0, WINDOW_WIDTH, WINDOW_HEIGHT, 0)
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
                rect = Rect(x_offset, GAME_HEIGHT + 60, 100, 40)
                current_tower_buttons[key] = rect
                x_offset += 110

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if my > GAME_HEIGHT: 
                    if event.button == 1:
                        for tab_name, rect in game.tabs.items():
                            if rect.collidepoint(mx, my):
                                game.active_tab = tab_name
                                game.build_mode = None 
                        for key, rect in current_tower_buttons.items():
                            if rect.collidepoint(mx, my):
                                if game.money >= TOWER_TYPES[key]['custo']:
                                    game.build_mode = key
                                    game.selected_tower = None
                        if game.wave_button_rect.collidepoint(mx, my): game.start_wave()
                        if game.selected_tower and game.sell_button_rect.collidepoint(mx, my):
                            refund = int(game.selected_tower.total_investment * 0.75)
                            game.money += refund
                            game.towers.remove(game.selected_tower)
                            game.selected_tower = None
                else: 
                    if event.button == 1: 
                        if game.build_mode:
                            game.towers.append(Tower(mx, my, game.build_mode))
                            game.money -= TOWER_TYPES[game.build_mode]['custo']
                            game.build_mode = None
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
            draw_sprite(TEXTURES['background'], WINDOW_WIDTH/2, GAME_HEIGHT/2, WINDOW_WIDTH, GAME_HEIGHT)
        else: glColor3f(0.1, 0.1, 0.1); draw_rect(0, 0, WINDOW_WIDTH, GAME_HEIGHT)
        # Desenha o caminho (opcional) apenas para visualização
        #glColor3f(0.3, 0.3, 0.3); glLineWidth(40)
        #glBegin(GL_LINE_STRIP); 
        #for p in PATH: glVertex2f(*p)
        #glEnd()

        for e in game.enemies: e.draw()
        for t in game.towers: t.draw(selected=(t == game.selected_tower))
        for p in game.projectiles: p.draw()
        for ft in game.floating_texts: ft.draw(font_float)

        if game.build_mode:
            mx, my = pygame.mouse.get_pos()
            if my < GAME_HEIGHT:
                stats = TOWER_TYPES[game.build_mode]
                drawn = draw_sprite(TEXTURES.get(stats['img_name']), mx, my, 40, 40, alpha=0.5)
                if not drawn:
                    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                    glColor4f(*stats['cor'], 0.5); draw_rect(mx - 15, my - 15, 30, 30); glDisable(GL_BLEND)
                glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                glColor4f(1, 1, 1, 0.3); draw_circle_outline(mx, my, stats['range']); glDisable(GL_BLEND)

        draw_text(f"ONDA {game.wave}", WINDOW_WIDTH - 130, 45, font_hud)

        glColor3f(0.2, 0.2, 0.2); draw_rect(0, GAME_HEIGHT, WINDOW_WIDTH, UI_HEIGHT)
        for tab_name, rect in game.tabs.items():
            if tab_name == game.active_tab: glColor3f(0.5, 0.5, 0.8)
            else: glColor3f(0.3, 0.3, 0.3)
            draw_rect(rect.x, rect.y, rect.w, rect.h)
            draw_text(tab_name, rect.x + 10, rect.y + 5, font)

        for key, rect in current_tower_buttons.items():
            if key == game.build_mode: glColor3f(0.8, 0.8, 0.8)
            else: glColor3f(0.5, 0.5, 0.5)
            draw_rect(rect.x, rect.y, rect.w, rect.h)
            cost_txt = f"${TOWER_TYPES[key]['custo']}"
            draw_text(f"{TOWER_TYPES[key]['nome']}", rect.x + 5, rect.y + 5, font)
            draw_text(cost_txt, rect.x + 5, rect.y + 20, font)

        glColor3f(0, 0.8, 0)
        draw_rect(game.wave_button_rect.x, game.wave_button_rect.y, game.wave_button_rect.w, game.wave_button_rect.h)
        draw_text("Prox Onda", game.wave_button_rect.x + 20, game.wave_button_rect.y + 10, font)

        draw_text(f"Dinheiro: ${game.money}", 10, GAME_HEIGHT + 120, font)
        draw_text(f"Vidas: {game.lives}", 150, GAME_HEIGHT + 120, font)

        if game.selected_tower:
            t = game.selected_tower
            if t.stats['nome'] == 'Estimulante':
                info = f"{t.stats['nome']} (Lv {t.level}) | Buff: {t.stats['buff_factor']:.2f}x"
            elif t.stats['nome'] == 'Fazenda':
                info = f"{t.stats['nome']} (Lv {t.level}) | Renda: ${t.stats['income']}/5s"
            else:
                info = f"{t.stats['nome']} (Lv {t.level}) | Dano: {int(t.stats['dano'])}"
            
            draw_text(info, 350, GAME_HEIGHT + 30, font)
            draw_text(f"Upgrade: ${t.level * 50} (Dir.)", 350, GAME_HEIGHT + 50, font)
            sell_val = int(t.total_investment * 0.75)
            glColor3f(0.8, 0.2, 0.2)
            draw_rect(game.sell_button_rect.x, game.sell_button_rect.y, game.sell_button_rect.w, game.sell_button_rect.h)
            draw_text(f"VENDER ${sell_val}", game.sell_button_rect.x + 10, game.sell_button_rect.y + 10, font)

        if game.lives <= 0: draw_text("GAME OVER", WINDOW_WIDTH//2 - 50, WINDOW_HEIGHT//2, font)
        pygame.display.flip(); clock.tick(60)
    pygame.quit()

if __name__ == "__main__": main()