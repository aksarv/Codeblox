import pygame
from app import App


def main():
    pygame.init()
    app = App()
    app.exec()
    pygame.quit()


if __name__ == "__main__":
    main()
