# 🏰 Tower Defense OpenGL (Python)

Um jogo de Tower Defense desenvolvido em **Python** combinando a performance da biblioteca **OpenGL** (via PyOpenGL) com a facilidade do **Pygame** para gerenciamento de janelas e interfaces.

Este projeto foca em mecânicas estratégicas, renderização de sprites com sistema de "fallback" (formas geométricas caso falte a imagem) e um sistema de progressão de dificuldade exponencial.

## 🎮 Funcionalidades

### 🛠️ Core Gameplay
* **Renderização Híbrida:** Utiliza OpenGL para desenhar o mapa/entidades e Pygame para UI e carregamento de texturas.
* **Sistema de Ondas Progressivo:** A dificuldade aumenta exponencialmente. A cada **3 ondas**, a quantidade de inimigos é multiplicada por **1.7x**.
* **Economia:** Dinheiro obtido ao derrotar inimigos ou gerado passivamente via **Fazendas**.
* **Animação:** Suporte para sprites de inimigos animados (4 frames).

### 🧱 Torres e Defesas
O jogo possui um sistema de interface por Abas (**Dano** e **Suporte**):

#### ⚔️ Aba de Dano
| Torre | Descrição |
| :--- | :--- |
| **Básica** | Custo baixo. Dano e alcance equilibrados. |
| **Rápida** | Atira muito rápido com dano baixo. Ideal para início de jogo. |
| **Sniper** | Alcance e dano altíssimos, mas recarga lenta. |

#### ❤️ Aba de Suporte
| Torre | Descrição |
| :--- | :--- |
| **Gelinho** | Aplica efeito de **Lentidão (Slow)** nos inimigos, reduzindo a velocidade em 50%. |
| **Estimulante** | Não ataca. Aumenta a **Velocidade de Ataque** das torres vizinhas em **30%** (acumulativo com upgrades). |
| **Fazenda** | Não ataca. Gera **$10 de dinheiro a cada 5 segundos**. Upgrades aumentam a renda. |

### ⚙️ Mecânicas Avançadas
* **Upgrades:** Clique direito para evoluir torres.
    * *Dano:* Aumenta Dano, Alcance e Velocidade.
    * *Estimulante:* Aumenta a potência do Buff (+15%).
    * *Fazenda:* Aumenta a renda gerada (+10).
* **Venda:** Venda torres estratégicas recuperando 75% do investimento total.
* **Ghost Mode:** Visualização translúcida da torre e do alcance antes de confirmar a construção.
* **Visual Feedback:** Textos flutuantes (ex: ganho de dinheiro) e ícones de status (buff).

---

## 🚀 Como Executar

### Pré-requisitos
Certifique-se de ter o [Python 3.x](https://www.python.org/) instalado.

### 1. Instalar Dependências
Abra o terminal na pasta do projeto e execute:

```bash
pip install pygame PyOpenGL PyOpenGL_accelerate