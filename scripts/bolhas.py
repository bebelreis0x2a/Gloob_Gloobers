import pygame

class BolhaAtaque:
    def __init__(self, x, y, direcao):
        self.rect = pygame.Rect(x, y, 16, 16)
        self.direcao = direcao  # 1 para direita, -1 para esquerda
        self.velocidade = 8
        self.alcance_maximo = 200  # Distância máxima que voa antes de sumir
        self.distancia_percorrida = 0

    def atualizar(self, paredes):
        deslocamento = self.velocidade * self.direcao
        self.rect.x += deslocamento
        self.distancia_percorrida += abs(deslocamento)

        # Destrói a bolha de tiro se bater em uma parede
        for parede in paredes:
            if self.rect.colliderect(parede):
                return False

        # Destrói se ultrapassar o alcance máximo
        if self.distancia_percorrida >= self.alcance_maximo:
            return False

        return True

    def desenhar(self, tela):
        # Projétil temporário: Retângulo ciano/azul claro
        pygame.draw.rect(tela, (100, 230, 255), self.rect)


class InimigoBolha:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.vel_x = 1
        self.vel_y = -1  # Flutua suavemente para cima

    def atualizar(self, paredes):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Colisão com paredes para quicar suavemente
        for parede in paredes:
            if self.rect.colliderect(parede):
                if self.rect.right >= parede.left or self.rect.left <= parede.right:
                    self.vel_x *= -1
                if self.rect.bottom >= parede.top or self.rect.top <= parede.bottom:
                    self.vel_y *= -1

        # Screen-wrapping simples se subir até o teto
        if self.rect.bottom < 0:
            self.rect.top = 600

    def desenhar(self, tela):
        # Inimigo capturado: Retângulo Roxo
        pygame.draw.rect(tela, (160, 32, 240), self.rect)


class ItemFruta:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)

    def desenhar(self, tela):
        # Item/Fruta: Retângulo Amarelo brilhante
        pygame.draw.rect(tela, (255, 215, 0), self.rect)
