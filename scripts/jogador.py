import pygame

class Jogador:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.vel_x = 0
        self.vel_y = 0
        self.no_chao = False
        self.direcao_olhar = 1
        self.vidas = 24
        self.pontos = 0

        self.sprites = [
            pygame.transform.scale(pygame.image.load("assets/furao-0.png").convert_alpha(), (32, 32)),
            pygame.transform.scale(pygame.image.load("assets/furao-1.png").convert_alpha(), (32, 32))
        ]
        self.frame_atual = 0
        self.tempo_animacao = 0

    def processar_eventos(self, eventos):
        for evento in eventos:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_LEFT:
                    self.vel_x = -4
                    self.direcao_olhar = -1
                elif evento.key == pygame.K_RIGHT:
                    self.vel_x = 4
                    self.direcao_olhar = 1
                elif evento.key == pygame.K_UP and self.no_chao:
                    self.vel_y = -10
                    self.no_chao = False

            elif evento.type == pygame.KEYUP:
                if evento.key == pygame.K_LEFT and self.vel_x < 0:
                    self.vel_x = 0
                elif evento.key == pygame.K_RIGHT and self.vel_x > 0:
                    self.vel_x = 0

    def atualizar(self, plataformas, paredes):
        self.vel_y += 0.5
        if self.vel_y > 8:
            self.vel_y = 8

        # 1. Movimento Horizontal e Colisão apenas com PAREDES
        self.rect.x += self.vel_x
        for parede in paredes:
            if self.rect.colliderect(parede):
                if self.vel_x > 0:
                    self.rect.right = parede.left
                elif self.vel_x < 0:
                    self.rect.left = parede.right

        # 2. Movimento Vertical e Colisão One-Way com PLATAFORMAS
        pos_anterior_bottom = self.rect.bottom
        self.rect.y += self.vel_y
        self.no_chao = False

        # Paredes físicas bloqueiam movimento vertical em ambos os sentidos
        for parede in paredes:
            if self.rect.colliderect(parede):
                if self.vel_y > 0:
                    self.rect.bottom = parede.top
                    self.vel_y = 0
                    self.no_chao = True
                elif self.vel_y < 0:
                    self.rect.top = parede.bottom
                    self.vel_y = 0

        # Plataformas One-Way (atravessa por baixo, pousa vindo de cima)
        for plat in plataformas:
            if self.rect.colliderect(plat):
                if self.vel_y > 0 and pos_anterior_bottom <= plat.top + 2:
                    self.rect.bottom = plat.top
                    self.vel_y = 0
                    self.no_chao = True

        # 3. Screen Wrapping (Envolver a tela)
        # Vertical: ao cair no buraco do fundo da tela, reaparece no topo
        if self.rect.top >= 600:
            self.rect.bottom = 0
        elif self.rect.bottom <= 0 and self.vel_y < 0:
            self.rect.top = 600

        # Horizontal: travessia lateral se sair dos limites da tela
        if self.rect.left >= 600:
            self.rect.right = 0
        elif self.rect.right <= 0:
            self.rect.left = 600

        # Animação
        if self.vel_x != 0:
            self.tempo_animacao += 1
            if self.tempo_animacao >= 10:
                self.tempo_animacao = 0
                self.frame_atual = (self.frame_atual + 1) % len(self.sprites)

    def resetar_posicao(self):
        self.rect.x = 280
        self.rect.y = 400
        self.vel_x = 0
        self.vel_y = 0

    def desenhar(self, tela):
        imagem = self.sprites[self.frame_atual]
        if self.direcao_olhar == -1:
            imagem = pygame.transform.flip(imagem, True, False)
        tela.blit(imagem, self.rect)
