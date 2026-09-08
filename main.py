import pygame
# Inicialização
pygame.init()
LARGURA_TELA = 600
ALTURA_TELA = 600

tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Gloob Gloobers!")
relogio = pygame.time.Clock()

from scripts.cenas import CenasGerenciador

gerenciador_cenas = CenasGerenciador(tela)

rodando = True
while rodando:
    eventos = pygame.event.get()
    for e in eventos:
        if e.type == pygame.QUIT:
            rodando = False

    # Processamento de Eventos e Atualização
    gerenciador_cenas.processar_eventos(eventos)
    gerenciador_cenas.atualizar()

    # Renderização
    tela.fill((0, 0, 0)) # Fundo escuro estilo arcade
    gerenciador_cenas.desenhar()

    pygame.display.flip()
    relogio.tick(60)

pygame.quit()
