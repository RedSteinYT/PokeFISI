import pygame
import pokemones

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720


def main():
    pygame.init()

    pantalla = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    reloj = pygame.time.Clock()
    pokemones.load_all_pokemon_sprites()

    mio = pokemones.garchomp
    rival = pokemones.infernape

    ejecutando = True
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_a:
                    mio.activar_animacion("espalda")
                elif evento.key == pygame.K_d:
                    rival.activar_animacion("frente")
                elif evento.key == pygame.K_s:
                    rival.activar_animacion("frente")
                    mio.activar_animacion("espalda")

        mio.actualizar()
        rival.actualizar()
        pantalla.fill((0, 0, 0))

        rival.dibujar(pantalla, (100, 100), vista="frente")
        mio.dibujar(pantalla, (600, 100), vista="espalda")

        pygame.display.flip()
        reloj.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
