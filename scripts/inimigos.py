import pygame

class Inimigo:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.vel_x = 2
        self.vel_y = 0

        self.sprites = [
            pygame.transform.scale(pygame.image.load("assets/monstro-0.png").convert_alpha(), (32, 32)),
            pygame.transform.scale(pygame.image.load("assets/monstro-1.png").convert_alpha(), (32, 32))
        ]
        self.frame_atual = 0
        self.tempo_animacao = 0

    def atualizar(self, plataformas, paredes):
        # Gravidade
        self.vel_y += 0.5
        if self.vel_y > 8:
            self.vel_y = 8

        # 1. Movimento Horizontal e Colisão com Paredes
        self.rect.x += self.vel_x
        for parede in paredes:
            if self.rect.colliderect(parede):
                if self.vel_x > 0:
                    self.rect.right = parede.left
                    self.vel_x *= -1
                elif self.vel_x < 0:
                    self.rect.left = parede.right
                    self.vel_x *= -1

        # 2. Movimento Vertical e Pouso One-Way
        pos_anterior_bottom = self.rect.bottom
        self.rect.y += self.vel_y

        for parede in paredes:
            if self.rect.colliderect(parede):
                if self.vel_y > 0:
                    self.rect.bottom = parede.top
                    self.vel_y = 0
                elif self.vel_y < 0:
                    self.rect.top = parede.bottom
                    self.vel_y = 0

        for plat in plataformas:
            if self.rect.colliderect(plat):
                if self.vel_y > 0 and pos_anterior_bottom <= plat.top + 2:
                    self.rect.bottom = plat.top
                    self.vel_y = 0

        # 3. Screen Wrapping (Vertical e Horizontal)
        if self.rect.top >= 600:
            self.rect.bottom = 0
        elif self.rect.bottom <= 0 and self.vel_y < 0:
            self.rect.top = 600

        if self.rect.left >= 600:
            self.rect.right = 0
        elif self.rect.right <= 0:
            self.rect.left = 600

        # Animação
        self.tempo_animacao += 1
        if self.tempo_animacao >= 12:
            self.tempo_animacao = 0
            self.frame_atual = (self.frame_atual + 1) % len(self.sprites)

    def desenhar(self, tela):
        tela.blit(self.sprites[self.frame_atual], self.rect)
