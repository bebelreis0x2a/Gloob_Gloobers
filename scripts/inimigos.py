import pygame

class Inimigo:
    def __init__(self, x, y):
        self.largura = 32
        self.altura = 32
        self.rect = pygame.Rect(x, y, self.largura, self.altura)
        self.vel_x = 2
        self.vel_y = 0
        self.gravidade = 0.6

    def atualizar(self, plataformas, paredes):
        # --- 1. Movimento e Colisão Horizontal com Paredes Sólidas (@) ---
        self.rect.x += self.vel_x

        for parede in paredes:
            if self.rect.colliderect(parede):
                if self.vel_x > 0:
                    self.rect.right = parede.left
                    self.vel_x *= -1
                elif self.vel_x < 0:
                    self.rect.left = parede.right
                    self.vel_x *= -1

        # --- 2. Movimento Vertical e Gravidade ---
        self.vel_y += self.gravidade
        if self.vel_y > 10:
            self.vel_y = 10

        pos_y_anterior = self.rect.y
        self.rect.y += self.vel_y

        # Colisão vertical com Paredes (@)
        for parede in paredes:
            if self.rect.colliderect(parede):
                if self.vel_y > 0:
                    self.rect.bottom = parede.top
                    self.vel_y = 0
                elif self.vel_y < 0:
                    self.rect.top = parede.bottom
                    self.vel_y = 0

        # Colisão vertical One-Way com Plataformas (#)
        if self.vel_y > 0:
            for plat in plataformas:
                if self.rect.colliderect(plat):
                    if (pos_y_anterior + self.altura) <= plat.top + 8:
                        self.rect.bottom = plat.top
                        self.vel_y = 0
                        break

        # --- 3. Screen-Wrapping ---
        ALTURA_TELA = 600
        if self.rect.top > ALTURA_TELA:
            self.rect.bottom = 0

    def desenhar(self, tela):
        # Retângulo Vermelho para o Inimigo
        pygame.draw.rect(tela, (230, 50, 50), self.rect)
