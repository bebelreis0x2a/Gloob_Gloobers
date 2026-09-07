import pygame

class Jogador:
    def __init__(self, x, y):
        self.posicao_inicial = (x, y)
        self.largura = 32
        self.altura = 32
        self.rect = pygame.Rect(x, y, self.largura, self.altura)
        
        # Atributos de Jogo
        self.vidas = 3
        self.pontos = 0
        self.direcao_olhar = 1  # 1: Direita, -1: Esquerda
        
        # Movimentação e Física
        self.vel_x = 0
        self.vel_y = 0
        self.velocidade_movimento = 4
        self.forca_pulo = -12
        self.gravidade = 0.6
        self.no_chao = False

    def resetar_posicao(self):
        self.rect.x = self.posicao_inicial[0]
        self.rect.y = self.posicao_inicial[1]
        self.vel_x = 0
        self.vel_y = 0

    def processar_eventos(self, eventos):
        teclas = pygame.key.get_pressed()
        
        self.vel_x = 0
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.vel_x = -self.velocidade_movimento
            self.direcao_olhar = -1
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.vel_x = self.velocidade_movimento
            self.direcao_olhar = 1

        for evento in eventos:
            if evento.type == pygame.KEYDOWN:
                # Alterado: Pulo agora aceita apenas W ou Seta para Cima (sem ESPAÇO)
                if (evento.key == pygame.K_UP or evento.key == pygame.K_w) and self.no_chao:
                    self.vel_y = self.forca_pulo
                    self.no_chao = False

    def aplicar_gravidade(self):
        self.vel_y += self.gravidade
        if self.vel_y > 10:
            self.vel_y = 10

    def atualizar(self, plataformas, paredes):
        # 1. Movimento Horizontal e Colisão com Paredes (@)
        self.rect.x += self.vel_x
        for parede in paredes:
            if self.rect.colliderect(parede):
                if self.vel_x > 0:
                    self.rect.right = parede.left
                elif self.vel_x < 0:
                    self.rect.left = parede.right

        # 2. Movimento Vertical e Gravidade
        self.aplicar_gravidade()
        pos_y_anterior = self.rect.y
        self.rect.y += self.vel_y

        self.no_chao = False

        for parede in paredes:
            if self.rect.colliderect(parede):
                if self.vel_y > 0:
                    self.rect.bottom = parede.top
                    self.vel_y = 0
                    self.no_chao = True
                elif self.vel_y < 0:
                    self.rect.top = parede.bottom
                    self.vel_y = 0

        if self.vel_y > 0:
            for plat in plataformas:
                if self.rect.colliderect(plat):
                    if (pos_y_anterior + self.altura) <= plat.top + 8:
                        self.rect.bottom = plat.top
                        self.vel_y = 0
                        self.no_chao = True
                        break

        # 3. Screen-Wrapping
        ALTURA_TELA = 600
        if self.rect.top > ALTURA_TELA:
            self.rect.bottom = 0

    def desenhar(self, tela):
        pygame.draw.rect(tela, (50, 150, 255), self.rect)
