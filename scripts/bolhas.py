import pygame

class BolhaAtaque:
    def __init__(self, x, y, direcao):
        self.rect = pygame.Rect(x, y, 16, 16)
        self.vel_x = direcao * 7
        self.imagem = pygame.transform.scale(pygame.image.load("assets/bolha.png").convert_alpha(), (16, 16))

    def atualizar(self, paredes):
        self.rect.x += self.vel_x
        for parede in paredes:
            if self.rect.colliderect(parede):
                return False
        return True

    def desenhar(self, tela):
        tela.blit(self.imagem, self.rect)


class InimigoBolha:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.vel_y = -1.5
        
        self.sprite_inimigo = pygame.transform.scale(pygame.image.load("assets/monstro-0.png").convert_alpha(), (24, 24))
        self.sprite_bolha = pygame.transform.scale(pygame.image.load("assets/bolha.png").convert_alpha(), (32, 32))
        
        self.angulo_rotacao = 0

    def atualizar(self, paredes):
        self.rect.y += self.vel_y
        self.angulo_rotacao = (self.angulo_rotacao - 5) % 360
        
        for parede in paredes:
            if self.rect.colliderect(parede):
                self.vel_y = 0

    def desenhar(self, tela):
        tela.blit(self.sprite_bolha, self.rect)
        
        # Rotação sem alterar o Rect de colisão principal
        inimigo_rotacionado = pygame.transform.rotate(self.sprite_inimigo, self.angulo_rotacao)
        rect_rot = inimigo_rotacionado.get_rect(center=self.rect.center)
        tela.blit(inimigo_rotacionado, rect_rot)


class ItemFruta:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 24, 24)

    def desenhar(self, tela):
        pygame.draw.circle(tela, (255, 50, 50), self.rect.center, 12)
