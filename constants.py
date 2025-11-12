import pygame
import os

# list all the pictures' file names in each of the directories for the icons of each of the block categories
ops = os.listdir(os.path.join(os.getcwd(), "operations"))
comps = os.listdir(os.path.join(os.getcwd(), "comparisons"))
t2Ds = os.listdir(os.path.join(os.getcwd(), "turtle2D"))

# get the absolute paths of all the icons and store their images in lists for each category
operations = [pygame.image.load(os.path.join(os.path.join(os.getcwd(), "operations"), o)) for o in ops if
              o.endswith(".png")]
comparisons = [pygame.image.load(os.path.join(os.path.join(os.getcwd(), "comparisons"), o)) for o in comps if
               o.endswith(".png")]
turtle2Ds = [pygame.image.load(os.path.join(os.path.join(os.getcwd(), "turtle2D"), o)) for o in t2Ds if
             o.endswith(".png")]

# resize icon images so their height is 72 pixels, since operation/comparison blocks have same width and height they
# are directly resized to 72 by 72. but proportional scaling is applied to other blocks as they do not
operations = [pygame.transform.scale(o, (72, 72)) for o in operations]
comparisons = [pygame.transform.scale(o, (72, 72)) for o in comparisons]
turtle2Ds = [pygame.transform.scale(o, (o.get_width() // (o.get_height() / 72), 72)) for o in turtle2Ds]

# store lists of all the number keys and alphabet keys for identifying key presses
numberKeys = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7,
              pygame.K_8, pygame.K_9]

alphaKeys = [pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d, pygame.K_e, pygame.K_f, pygame.K_g, pygame.K_h, pygame.K_i,
             pygame.K_j, pygame.K_k, pygame.K_l, pygame.K_m, pygame.K_n, pygame.K_o, pygame.K_p, pygame.K_q, pygame.K_r,
             pygame.K_s, pygame.K_t, pygame.K_u, pygame.K_v, pygame.K_w, pygame.K_x, pygame.K_y, pygame.K_z]
