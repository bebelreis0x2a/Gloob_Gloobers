import pygame
import math

class ProjetilBoss:
    def __init__(self, x, y, vel_x, vel_y):
        self.rect = pygame.Rect(x, y, 16, 16)
        self.vel_x = vel_x
        self.vel_y = vel_y

    def atualizar(self, paredes):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Destrói projétil se colidir com parede
        for parede in paredes:
            if self.rect.colliderect(parede):
                return False
        return True

    def desenhar(self, tela):
        pygame.draw.rect(tela, (255, 100, 0), self.rect)


class Boss:
    def __init__(self, x, y):
        # 5x o tamanho normal de 32px (160x160)
        self.largura = 160
        self.altura = 160
        self.rect = pygame.Rect(x, y, self.largura, self.altura)
        
        # Movimentação diagonal rápida
        self.vel_x = 5
        self.vel_y = 5
        self.vida = 20
        
        # Controle de disparos
        self.tempo_ultimo_disparo = pygame.time.get_ticks()
        self.cooldown_disparo = 2000  # Dispara a cada 2 segundos

    def atualizar(self, paredes):
        # Movimentação diagonal
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Quica ao rebater em paredes
        for parede in paredes:
            if self.rect.colliderect(parede):
                if self.rect.right >= parede.left or self.rect.left <= parede.right:
                    self.vel_x *= -1
                if self.rect.bottom >= parede.top or self.rect.top <= parede.bottom:
                    self.vel_y *= -1

        # Limites da arena
        if self.rect.left <= 40 or self.rect.right >= 560:
            self.vel_x *= -1
        if self.rect.top <= 40 or self.rect.bottom >= 560:
            self.vel_y *= -1

    def tentar_disparar(self):
        agora = pygame.time.get_ticks()
        projeteis = []
        if agora - self.tempo_ultimo_disparo >= self.cooldown_disparo:
            self.tempo_ultimo_disparo = agora
            
            # Gera 6 projéteis espaçados a cada 60 graus
            centro_x = self.rect.centerx
            centro_y = self.rect.centery
            velocidade_projetil = 6
            
            for i in range(6):
                angulo = math.radians(i * 60)
                vx = math.cos(angulo) * velocidade_projetil
                vy = math.sin(angulo) * velocidade_projetil
                projeteis.append(ProjetilBoss(centro_x, centro_y, vx, vy))
                
        return projeteis

    def desenhar(self, tela):
        # Retângulo Laranja Gigante
        pygame.draw.rect(tela, (220, 20, 60), self.rect)
