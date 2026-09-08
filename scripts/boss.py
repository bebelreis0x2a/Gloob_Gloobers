import pygame
import math

class ProjetilBoss:
    def __init__(self, x, y, vel_x, vel_y):
        self.rect = pygame.Rect(x, y, 16, 16)
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.imagem = pygame.transform.scale(pygame.image.load("assets/bolha.png").convert_alpha(), (16, 16))

    def atualizar(self, paredes):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        for parede in paredes:
            if self.rect.colliderect(parede):
                return False
        return True

    def desenhar(self, tela):
        tela.blit(self.imagem, self.rect)


class Boss:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 160, 160)
        self.vel_x = 5
        self.vel_y = 5
        
        # Vida do Boss
        self.vida_maxima = 50
        self.vida = self.vida_maxima
        
        self.tempo_ultimo_disparo = pygame.time.get_ticks()
        self.cooldown_disparo = 2000

        # Scale para 160x160px
        self.sprites = [
            pygame.transform.scale(pygame.image.load("assets/chefe-0.png").convert_alpha(), (160, 160)),
            pygame.transform.scale(pygame.image.load("assets/chefe-1.png").convert_alpha(), (160, 160)),
            pygame.transform.scale(pygame.image.load("assets/chefe-2.png").convert_alpha(), (160, 160)),
            pygame.transform.scale(pygame.image.load("assets/chefe-3.png").convert_alpha(), (160, 160))
        ]
        self.frame_atual = 0
        self.tempo_animacao = 0

    def atualizar(self, paredes):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        for parede in paredes:
            if self.rect.colliderect(parede):
                if self.rect.right >= parede.left or self.rect.left <= parede.right:
                    self.vel_x *= -1
                if self.rect.bottom >= parede.top or self.rect.top <= parede.bottom:
                    self.vel_y *= -1

        if self.rect.left <= 40 or self.rect.right >= 560:
            self.vel_x *= -1
        if self.rect.top <= 40 or self.rect.bottom >= 560:
            self.vel_y *= -1

        self.tempo_animacao += 1
        if self.tempo_animacao >= 8:
            self.tempo_animacao = 0
            self.frame_atual = (self.frame_atual + 1) % len(self.sprites)

    def tentar_disparar(self):
        agora = pygame.time.get_ticks()
        projeteis = []
        if agora - self.tempo_ultimo_disparo >= self.cooldown_disparo:
            self.tempo_ultimo_disparo = agora
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
        # 1. Desenha o sprite do Boss
        tela.blit(self.sprites[self.frame_atual], self.rect)

        # 2. Configurações da Barra de Vida
        largura_barra = 120  # Largura total da barra em pixels
        altura_barra = 12    # Altura da barra em pixels
        
        # Centraliza a barra horizontalmente em relação ao Boss e coloca 15px acima dele
        pos_x = self.rect.centerx - (largura_barra // 2)
        pos_y = self.rect.top - 15

        # Evita divisão por zero ou proporção negativa
        porcentagem_vida = max(0, self.vida / self.vida_maxima)
        largura_atual = int(largura_barra * porcentagem_vida)

        # Retângulos da barra
        rect_fundo = pygame.Rect(pos_x, pos_y, largura_barra, altura_barra)
        rect_vida = pygame.Rect(pos_x, pos_y, largura_atual, altura_barra)

        # 3. Desenho dos elementos
        # Fundo vermelho/escuro
        pygame.draw.rect(tela, (200, 30, 30), rect_fundo)
        # Vida atual em verde
        pygame.draw.rect(tela, (50, 220, 50), rect_vida)
        # Borda preta em volta da barra para acabamento
        pygame.draw.rect(tela, (0, 0, 0), rect_fundo, 2)

        pygame.draw.rect(tela, (255, 0, 0), self.rect, 2)
