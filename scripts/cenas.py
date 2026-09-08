import pygame
import random
import time
from scripts.jogador import Jogador
from scripts.inimigos import Inimigo
from scripts.boss import Boss
from scripts.mapas import MAPAS, LARGURA_BLOCO, ALTURA_BLOCO
from scripts.bolhas import BolhaAtaque, InimigoBolha, ItemFruta
from scripts.api import enviar_pontuacao, buscar_ranking

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
        
        # Controle de Tempo de Jogo
        self.tempo_inicio = time.time()
        self.tempo_decorrido = 0
        
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
            if not self.boss:
                self.boss = Boss(220, 100)
                self.jogador.vidas = 1
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
        self.tempo_decorrido = time.time() - self.tempo_inicio
        obstaculos = self.plataformas + self.paredes
        self.jogador.atualizar(self.plataformas, self.paredes)
        
        # Projéteis do Jogador vs Obstáculos e Inimigos
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

        # Boss
        if self.boss:
            self.boss.atualizar(obstaculos)
            novos_projeteis = self.boss.tentar_disparar()
            self.projeteis_boss.extend(novos_projeteis)

            if self.jogador.rect.colliderect(self.boss.rect):
                self.jogador.vidas -= 1
                if self.jogador.vidas > 0:
                    self.projeteis_boss.clear()
                    self.reiniciar_fase()
                else:
                    return "game_over"

        # Projéteis do Boss
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
                    self.projeteis_boss.clear()
                    self.reiniciar_fase()
                else:
                    return "game_over"

        # Inimigos na Bolha
        for bolha in self.inimigos_bolha[:]:
            bolha.atualizar(obstaculos)
            if self.jogador.rect.colliderect(bolha.rect):
                self.itens.append(ItemFruta(bolha.rect.x, bolha.rect.y))
                self.inimigos_bolha.remove(bolha)

        # Coleta de Frutas
        for item in self.itens[:]:
            if self.jogador.rect.colliderect(item.rect):
                self.jogador.pontos += 600
                self.itens.remove(item)

        # Jogador vs Inimigos Padrão
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

        # HUD com Tempo
        txt_vidas = self.fonte_hud.render(f"Vidas: {self.jogador.vidas}", True, (255, 255, 255))
        fase_nome = "BOSS" if self.fase_atual == len(MAPAS) - 1 else f"Fase: {self.fase_atual + 1}"
        txt_fase = self.fonte_hud.render(fase_nome, True, (255, 255, 0))
        txt_pontos = self.fonte_hud.render(f"Pts: {self.jogador.pontos}", True, (255, 255, 255))
        txt_tempo = self.fonte_hud.render(f"{self.tempo_decorrido:.1f}s", True, (0, 255, 255))
        
        self.tela.blit(txt_vidas, (15, 10))
        self.tela.blit(txt_fase, (150, 10))
        self.tela.blit(txt_pontos, (270, 10))
        self.tela.blit(txt_tempo, (480, 10))


class CenasGerenciador:
    def __init__(self, tela):
        self.tela = tela
        self.estado = "menu"
        self.partida = None
        
        pygame.font.init()
        self.fonte_titulo = pygame.font.Font(None, 60)
        self.fonte_menu = pygame.font.Font(None, 36)
        self.fonte_subtitulo = pygame.font.Font(None, 26)

        self.btn_jogar = pygame.Rect(200, 260, 200, 50)
        self.btn_ranking = pygame.Rect(200, 330, 200, 50)

        # Controle do Ranking e Iniciais
        self.nome_jogador = ""
        self.ranking_dados = []
        self.enviado = False

    def processar_eventos(self, eventos):
        for evento in eventos:
            if self.estado == "menu":
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    if self.btn_jogar.collidepoint(evento.pos):
                        self.partida = Partida(self.tela)
                        self.estado = "partida"
                        self.nome_jogador = ""
                        self.enviado = False
                    elif self.btn_ranking.collidepoint(evento.pos):
                        self.ranking_dados = buscar_ranking()
                        self.estado = "ranking"

            elif self.estado == "ranking":
                if (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE) or evento.type == pygame.MOUSEBUTTONDOWN:
                    self.estado = "menu"

            elif self.estado in ["partida", "pause"]:
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    self.estado = "pause" if self.estado == "partida" else "partida"
                
                if self.estado == "partida" and self.partida:
                    self.partida.processar_eventos([evento])

            elif self.estado in ["game_over", "vitoria"]:
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_RETURN and len(self.nome_jogador) > 0:
                        if not self.enviado:
                            fase_final = self.partida.fase_atual + 1
                            enviar_pontuacao(
                                self.nome_jogador.upper(),
                                self.partida.jogador.pontos,
                                fase_final,
                                round(self.partida.tempo_decorrido, 2)
                            )
                            self.enviado = True
                        self.estado = "menu"
                    elif evento.key == pygame.K_BACKSPACE:
                        self.nome_jogador = self.nome_jogador[:-1]
                    elif len(self.nome_jogador) < 3 and evento.unicode.isalpha():
                        self.nome_jogador += evento.unicode.upper()

    def atualizar(self):
        if self.estado == "partida" and self.partida:
            resultado = self.partida.atualizar()
            if resultado in ["game_over", "vitoria"]:
                self.estado = resultado

    def desenhar(self):
        if self.estado == "menu":
            self.desenhar_menu()
        elif self.estado == "ranking":
            self.desenhar_ranking()
        elif self.estado in ["partida", "pause", "game_over", "vitoria"]:
            if self.partida:
                self.partida.desenhar()
            
            if self.estado == "pause":
                overlay = pygame.Surface(self.tela.get_size(), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                self.tela.blit(overlay, (0, 0))
                texto = self.fonte_titulo.render("PAUSADO", True, (255, 255, 255))
                self.tela.blit(texto, texto.get_rect(center=(300, 300)))

            elif self.estado in ["game_over", "vitoria"]:
                cor_fundo = (150, 0, 0, 200) if self.estado == "game_over" else (0, 150, 0, 200)
                overlay = pygame.Surface(self.tela.get_size(), pygame.SRCALPHA)
                overlay.fill(cor_fundo)
                self.tela.blit(overlay, (0, 0))

                titulo_txt = "GAME OVER" if self.estado == "game_over" else "VITÓRIA!"
                txt_titulo = self.fonte_titulo.render(titulo_txt, True, (255, 255, 255))
                self.tela.blit(txt_titulo, txt_titulo.get_rect(center=(300, 130)))

                fase = self.partida.fase_atual + 1
                pts = self.partida.jogador.pontos
                tempo = round(self.partida.tempo_decorrido, 1)
                txt_resumo = self.fonte_subtitulo.render(f"Fase: {fase} | Pontos: {pts} | Tempo: {tempo}s", True, (255, 255, 200))
                self.tela.blit(txt_resumo, txt_resumo.get_rect(center=(300, 200)))

                # Entrada estilo Arcade
                txt_instrucao = self.fonte_subtitulo.render("DIGITE SUAS INICIAIS (3 LETRAS):", True, (255, 255, 255))
                self.tela.blit(txt_instrucao, txt_instrucao.get_rect(center=(300, 280)))

                nome_display = self.nome_jogador.ljust(3, '_')
                txt_nome = self.fonte_titulo.render(f"[ {nome_display} ]", True, (0, 255, 255))
                self.tela.blit(txt_nome, txt_nome.get_rect(center=(300, 340)))

                txt_enter = self.fonte_subtitulo.render("Pressione ENTER para salvar", True, (200, 200, 200))
                self.tela.blit(txt_enter, txt_enter.get_rect(center=(300, 420)))

    def desenhar_menu(self):
        pos_mouse = pygame.mouse.get_pos()

        txt_titulo = self.fonte_titulo.render("Gloob Gloobers!", True, (255, 0, 255))
        self.tela.blit(txt_titulo, txt_titulo.get_rect(center=(300, 140)))

        cor_btn_jogar = (80, 200, 80) if self.btn_jogar.collidepoint(pos_mouse) else (50, 150, 50)
        pygame.draw.rect(self.tela, cor_btn_jogar, self.btn_jogar, border_radius=8)
        pygame.draw.rect(self.tela, (255, 255, 255), self.btn_jogar, width=2, border_radius=8)
        txt_jogar = self.fonte_menu.render("JOGAR", True, (255, 255, 255))
        self.tela.blit(txt_jogar, txt_jogar.get_rect(center=self.btn_jogar.center))

        cor_btn_ranking = (80, 120, 200) if self.btn_ranking.collidepoint(pos_mouse) else (50, 80, 150)
        pygame.draw.rect(self.tela, cor_btn_ranking, self.btn_ranking, border_radius=8)
        pygame.draw.rect(self.tela, (255, 255, 255), self.btn_ranking, width=2, border_radius=8)
        txt_ranking = self.fonte_menu.render("RANKING", True, (255, 255, 255))
        self.tela.blit(txt_ranking, txt_ranking.get_rect(center=self.btn_ranking.center))

    def desenhar_ranking(self):
        txt_titulo = self.fonte_titulo.render("TOP 10 RANKING", True, (255, 255, 0))
        self.tela.blit(txt_titulo, txt_titulo.get_rect(center=(300, 70)))

        if not self.ranking_dados:
            txt_vazio = self.fonte_subtitulo.render("Nenhum registro encontrado.", True, (200, 200, 200))
            self.tela.blit(txt_vazio, txt_vazio.get_rect(center=(300, 280)))
        else:
            txt_header = self.fonte_subtitulo.render("POS  NOME   PTS   FASE   TEMPO", True, (0, 255, 255))
            self.tela.blit(txt_header, (100, 130))

            y = 170
            for idx, r in enumerate(self.ranking_dados):
                linha = f"{idx+1:02d}.   {r['nome']:<6} {r['pontos']:<5}  F{r['fase']}     {r['tempo']}s"
                txt_linha = self.fonte_subtitulo.render(linha, True, (255, 255, 255))
                self.tela.blit(txt_linha, (100, y))
                y += 30

        txt_voltar = self.fonte_subtitulo.render("Clique ou pressione ESC para voltar", True, (150, 150, 150))
        self.tela.blit(txt_voltar, txt_voltar.get_rect(center=(300, 540)))