import pygame
import random
from scripts.jogador import Jogador
from scripts.inimigos import Inimigo
from scripts.boss import Boss
from scripts.mapas import MAPAS, LARGURA_BLOCO, ALTURA_BLOCO
from scripts.bolhas import BolhaAtaque, InimigoBolha, ItemFruta

class Partida:
    def __init__(self, tela):
        self.tela = tela
        self.jogador = Jogador(280, 400)
        self.fase_atual = 0
        
        self.plataformas = []
        self.paredes = []
        self.inimigos = []
        self.projeteis = []
        self.inimigos_bolha = []
        self.itens = []
        
        self.boss = None
        self.projeteis_boss = []
        
        pygame.font.init()
        self.fonte_hud = pygame.font.Font(None, 36)
        
        self.carregar_mapa(self.fase_atual)

    def carregar_mapa(self, indice_fase):
        self.plataformas.clear()
        self.paredes.clear()
        self.projeteis.clear()
        self.inimigos_bolha.clear()
        self.itens.clear()
        self.projeteis_boss.clear()
        self.jogador.resetar_posicao()
        
        mapa = MAPAS[indice_fase]
        posicoes_validas = []

        for linha_idx, linha in enumerate(mapa):
            for col_idx, caractere in enumerate(linha):
                x = col_idx * LARGURA_BLOCO
                y = linha_idx * ALTURA_BLOCO
                if caractere == '#':
                    self.plataformas.append(pygame.Rect(x, y, LARGURA_BLOCO, ALTURA_BLOCO))
                    if linha_idx > 2:
                        posicoes_validas.append((x, y - 32))
                elif caractere == '@':
                    self.paredes.append(pygame.Rect(x, y, LARGURA_BLOCO, ALTURA_BLOCO))

        if indice_fase == len(MAPAS) - 1:
            self.inimigos.clear()
            self.boss = Boss(220, 100)
            self.jogador.vidas = 5
        else:
            self.boss = None
            qtd_inimigos = 2 + indice_fase
            self.inimigos.clear()
            for i in range(qtd_inimigos):
                if posicoes_validas:
                    pos = random.choice(posicoes_validas)
                    self.inimigos.append(Inimigo(pos[0], pos[1]))
                else:
                    self.inimigos.append(Inimigo(100 + (i * 60), 100))

    def reiniciar_fase(self):
        self.carregar_mapa(self.fase_atual)

    def processar_eventos(self, eventos):
        self.jogador.processar_eventos(eventos)
        for evento in eventos:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    pos_x = self.jogador.rect.right if self.jogador.direcao_olhar == 1 else self.jogador.rect.left - 16
                    pos_y = self.jogador.rect.centery - 8
                    self.projeteis.append(BolhaAtaque(pos_x, pos_y, self.jogador.direcao_olhar))

    def atualizar(self):
        obstaculos = self.plataformas + self.paredes
        self.jogador.atualizar(self.plataformas, self.paredes)
        
        # 1. Projéteis do Jogador vs Obstáculos e Inimigos
        for projeteil in self.projeteis[:]:
            ativo = projeteil.atualizar(obstaculos)
            if not ativo:
                self.projeteis.remove(projeteil)
                continue

            if self.boss and projeteil.rect.colliderect(self.boss.rect):
                self.boss.vida -= 1
                if projeteil in self.projeteis:
                    self.projeteis.remove(projeteil)
                if self.boss.vida <= 0:
                    self.boss = None
                    return "vitoria"
                continue

            for inimigo in self.inimigos[:]:
                if projeteil.rect.colliderect(inimigo.rect):
                    self.inimigos_bolha.append(InimigoBolha(inimigo.rect.x, inimigo.rect.y))
                    if inimigo in self.inimigos:
                        self.inimigos.remove(inimigo)
                    if projeteil in self.projeteis:
                        self.projeteis.remove(projeteil)
                    break

        # 2. Boss
        if self.boss:
            self.boss.atualizar(obstaculos)
            novos_projeteis = self.boss.tentar_disparar()
            self.projeteis_boss.extend(novos_projeteis)

            if self.jogador.rect.colliderect(self.boss.rect):
                self.jogador.vidas -= 1
                if self.jogador.vidas > 0:
                    self.reiniciar_fase()
                else:
                    return "game_over"

        # 3. Projéteis do Boss
        for p_boss in self.projeteis_boss[:]:
            ativo = p_boss.atualizar(obstaculos)
            if not ativo:
                self.projeteis_boss.remove(p_boss)
                continue

            if self.jogador.rect.colliderect(p_boss.rect):
                self.jogador.vidas -= 1
                if p_boss in self.projeteis_boss:
                    self.projeteis_boss.remove(p_boss)
                if self.jogador.vidas > 0:
                    self.reiniciar_fase()
                else:
                    return "game_over"

        # 4. Inimigos na Bolha
        for bolha in self.inimigos_bolha[:]:
            bolha.atualizar(obstaculos)
            if self.jogador.rect.colliderect(bolha.rect):
                self.itens.append(ItemFruta(bolha.rect.x, bolha.rect.y))
                self.inimigos_bolha.remove(bolha)

        # 5. Coleta de Frutas
        for item in self.itens[:]:
            if self.jogador.rect.colliderect(item.rect):
                self.jogador.pontos += 600
                self.itens.remove(item)

        # 6. Jogador vs Inimigos Padrão
        for inimigo in self.inimigos:
            inimigo.atualizar(self.plataformas, self.paredes)
            if self.jogador.rect.colliderect(inimigo.rect):
                self.jogador.vidas -= 1
                if self.jogador.vidas > 0:
                    self.reiniciar_fase()
                else:
                    return "game_over"

        if not self.boss and not self.inimigos and not self.inimigos_bolha and not self.itens:
            if self.fase_atual + 1 < len(MAPAS):
                self.fase_atual += 1
                self.carregar_mapa(self.fase_atual)
            else:
                return "vitoria"

        return "partida"
    
    def desenhar(self):
        for plat in self.plataformas:
            pygame.draw.rect(self.tela, (40, 160, 80), plat)

        for parede in self.paredes:
            pygame.draw.rect(self.tela, (100, 100, 120), parede)

        for projeteil in self.projeteis:
            projeteil.desenhar(self.tela)

        for p_boss in self.projeteis_boss:
            p_boss.desenhar(self.tela)

        for bolha in self.inimigos_bolha:
            bolha.desenhar(self.tela)

        for item in self.itens:
            item.desenhar(self.tela)

        self.jogador.desenhar(self.tela)
        
        for inimigo in self.inimigos:
            inimigo.desenhar(self.tela)

        if self.boss:
            self.boss.desenhar(self.tela)

        # HUD
        txt_vidas = self.fonte_hud.render(f"Vidas: {self.jogador.vidas}", True, (255, 255, 255))
        fase_nome = "BOSS" if self.fase_atual == len(MAPAS) - 1 else f"Fase: {self.fase_atual + 1}"
        txt_fase = self.fonte_hud.render(fase_nome, True, (255, 255, 0))
        txt_pontos = self.fonte_hud.render(f"Pontos: {self.jogador.pontos}", True, (255, 255, 255))
        
        self.tela.blit(txt_vidas, (20, 10))
        self.tela.blit(txt_fase, (250, 10))
        self.tela.blit(txt_pontos, (440, 10))


class CenasGerenciador:
    def __init__(self, tela):
        self.tela = tela
        self.estado = "partida"
        self.partida = Partida(tela)
        pygame.font.init()
        self.fonte_menu = pygame.font.Font(None, 48)

    def processar_eventos(self, eventos):
        for evento in eventos:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE and self.estado not in ["game_over", "vitoria"]:
                    if self.estado == "partida":
                        self.estado = "pause"
                    elif self.estado == "pause":
                        self.estado = "partida"
                
                if evento.key == pygame.K_SPACE and self.estado in ["game_over", "vitoria"]:
                    self.partida = Partida(self.tela)
                    self.estado = "partida"

        if self.estado == "partida":
            self.partida.processar_eventos(eventos)

    def atualizar(self):
        if self.estado == "partida":
            resultado = self.partida.atualizar()
            if resultado in ["game_over", "vitoria"]:
                self.estado = resultado

    def desenhar(self):
        self.partida.desenhar()
        
        if self.estado == "pause":
            overlay = pygame.Surface(self.tela.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.tela.blit(overlay, (0, 0))
            texto = self.fonte_menu.render("JOGO PAUSADO", True, (255, 255, 255))
            self.tela.blit(texto, texto.get_rect(center=(300, 300)))

        elif self.estado == "game_over":
            overlay = pygame.Surface(self.tela.get_size(), pygame.SRCALPHA)
            overlay.fill((150, 0, 0, 180))
            self.tela.blit(overlay, (0, 0))
            txt_game_over = self.fonte_menu.render("GAME OVER", True, (255, 255, 255))
            txt_reiniciar = self.fonte_menu.render("Pressione ESPAÇO", True, (255, 255, 255))
            self.tela.blit(txt_game_over, txt_game_over.get_rect(center=(300, 260)))
            self.tela.blit(txt_reiniciar, txt_reiniciar.get_rect(center=(300, 320)))

        elif self.estado == "vitoria":
            overlay = pygame.Surface(self.tela.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 150, 0, 180))
            self.tela.blit(overlay, (0, 0))
            txt_vitoria = self.fonte_menu.render("VOCÊ VENCEU!", True, (255, 255, 255))
            txt_reiniciar = self.fonte_menu.render("Pressione ESPAÇO", True, (255, 255, 255))
            self.tela.blit(txt_vitoria, txt_vitoria.get_rect(center=(300, 260)))
            self.tela.blit(txt_reiniciar, txt_reiniciar.get_rect(center=(300, 320)))
