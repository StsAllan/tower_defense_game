# === CONFIGURAÇÕES DE TELA ===
LARGURA_LOGICA = 800
ALTURA_LOGICA = 600
ALTURA_UI = 150
ALTURA_AREA_JOGO = ALTURA_LOGICA - ALTURA_UI

# === TIPOS DE TORRES ===
TIPOS_TORRES = {
    'BASICA': {
        'nome': 'Basica',
        'role': 'DANO',
        'range': 100,
        'dano': 20,
        'speed': 30,
        'custo': 100,
        'cor': (0, 1, 1),
        'img_name': 'basica.png',
        'slow_factor': 1.0,
        'slow_time': 0,
        'buff_factor': 1.0,
        'income': 0
    },
    'RAPIDA': {
        'nome': 'Rapida',
        'role': 'DANO',
        'range': 70,
        'dano': 8,
        'speed': 10,
        'custo': 150,
        'cor': (1, 1, 0),
        'img_name': 'rapida.png',
        'slow_factor': 1.0,
        'slow_time': 0,
        'buff_factor': 1.0,
        'income': 0
    },
    'SNIPER': {
        'nome': 'Sniper',
        'role': 'DANO',
        'range': 200,
        'dano': 100,
        'speed': 80,
        'custo': 200,
        'cor': (1, 0, 1),
        'img_name': 'sniper.png',
        'slow_factor': 1.0,
        'slow_time': 0,
        'buff_factor': 1.0,
        'income': 0
    },
    'GELINHO': {
        'nome': 'Gelinho',
        'role': 'SUPORTE',
        'range': 110,
        'dano': 5,
        'speed': 40,
        'custo': 120,
        'cor': (0.5, 0.8, 1),
        'img_name': 'gelinho.png',
        'slow_factor': 0.5,
        'slow_time': 120,
        'buff_factor': 1.0,
        'income': 0
    },
    'ESTIMULANTE': {
        'nome': 'Estimulante',
        'role': 'SUPORTE',
        'range': 80,
        'dano': 2,
        'speed': 45,
        'custo': 250,
        'cor': (1, 0.5, 0),
        'img_name': 'estimulante.png',
        'slow_factor': 1.0,
        'slow_time': 0,
        'buff_factor': 1.3,
        'income': 0
    },
    'FAZENDA': {
        'nome': 'Fazenda',
        'role': 'SUPORTE',
        'range': 40,
        'dano': 0,
        'speed': 300,
        'custo': 300,
        'cor': (0, 0.8, 0),
        'img_name': 'fazenda.png',
        'slow_factor': 1.0,
        'slow_time': 0,
        'buff_factor': 1.0,
        'income': 10
    },
}

# === CAMINHO DOS INIMIGOS ===
CAMINHO = [
    (0, 100),
    (200, 100),
    (200, 300),
    (500, 300),
    (500, 100),
    (700, 100),
    (700, 450),
    (800, 450)
]

# === CONFIGURAÇÕES DE GAMEPLAY ===
DINHEIRO_INICIAL = 400
VIDAS_INICIAL = 10
RAIO_BLOQUEIO_CAMINHO = 25
DISTANCIA_MIN_TORRES = 40