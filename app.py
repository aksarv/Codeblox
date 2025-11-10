import pygame
import datetime
import os
import math
import numpy as np
from helpers import *
from blocks import *
from constants import *
from trace import *
from globalsStack import GlobalsStack


class App:
    def __init__(self):
        self.scr_width, self.scr_height = 1280, 720
        self.scr = pygame.display.set_mode((self.scr_width, self.scr_height), pygame.RESIZABLE)

        # code in AST representation is stored as a list of blocks here, initially empty
        self.code = []
        self.prev_mouse_x, self.prev_mouse_y = None, None
        self.selected_new_block = None
        self.join_new_block = None
        self.sensitivity = 1
        self.enteredText = ""
        self.current_outputs = []
        self.globals = GlobalsStack()

        self.FONT_SIZE = 20
        self.FONT = pygame.font.Font(os.path.join(os.getcwd(), "SFMono-Regular.otf"), self.FONT_SIZE)
        self.BOLD_FONT = pygame.font.Font(os.path.join(os.getcwd(), "SFMono-Bold.otf"), self.FONT_SIZE)
        # use this to work out how many characters we can fit with a set number of pixels
        # only one character needed as the font is monospaced
        self.char_width, self.char_height = self.FONT.size("n")

        self.turtle = Turtle2D()
        self.menu = Menu(
            [operations, comparisons, turtle2Ds],
            [ops, comps, t2Ds],
            self.scr_width // 2 - self.scr_width // 12.8 + 10,
            10
        )
        self.trace = TraceTable()

        self.output_offset = 0
        self.frames = 0

    def draw_turtle(self):
        # draw the turtle's trail
        for line in self.turtle.lines:
            pygame.draw.line(self.scr, (0, 0, 0),
                             (self.scr_width // 4 * 3 + line[0][0] * self.turtle.pixels_per_unit,
                              self.scr_height // 4 - line[0][1] * self.turtle.pixels_per_unit), (
                                 self.scr_width // 4 * 3 + line[1][0] * self.turtle.pixels_per_unit,
                                 self.scr_height // 4 - line[1][1] * self.turtle.pixels_per_unit))

        # draw the turtle
        # the turtle is made of an equilateral triangle with a 'hole' in the bottom (a circle is drawn at the bottom centre
        # of the triangle to represent this hole)
        # the turtle's x and y attributes represent the coordinates of the 'centre' of the equilateral triangle (i.e.,
        # halfway down the mast of the triangle)
        # we set the height of the triangle to be 10 pixels, so from the centre to the top and bottom it is 5 units each
        # we use the angle and trigonometry to extend from the centre out 5 pixels in the direction of the angle to draw the
        # top of the triangle
        # we can draw both base points through rotating the equivalent of 60 degrees in radians from the angle, and
        # similarly extending out from the centre by 5 pixels
        # we can draw the white circle last by calculating the midpoint of both base points and drawing the circle centered
        # at there
        centre_x = self.scr_width // 4 * 3
        centre_y = self.scr_height // 4
        pygame.draw.polygon(self.scr, (0, 0, 0),
                            [(centre_x + self.turtle.x * self.turtle.pixels_per_unit + 10 * math.cos(
                                self.turtle.angle),
                              centre_y - self.turtle.y * self.turtle.pixels_per_unit - 10 * math.sin(
                                  self.turtle.angle)), (
                                 centre_x + self.turtle.x * self.turtle.pixels_per_unit + 10 * math.cos(
                                     self.turtle.angle + math.pi / 1.5),
                                 centre_y - self.turtle.y * self.turtle.pixels_per_unit - 10 * math.sin(
                                     self.turtle.angle + math.pi / 1.5)), (
                                 centre_x + self.turtle.x * self.turtle.pixels_per_unit + 10 * math.cos(
                                     self.turtle.angle + math.pi / 1.5 * 2),
                                 centre_y - self.turtle.y * self.turtle.pixels_per_unit - 10 * math.sin(
                                     self.turtle.angle + math.pi / 1.5 * 2))])
        point1, point2 = (
            centre_x + self.turtle.x * self.turtle.pixels_per_unit + 10 * math.cos(
                self.turtle.angle + math.pi / 1.5),
            centre_y - self.turtle.y * self.turtle.pixels_per_unit - 10 * math.sin(
                self.turtle.angle + math.pi / 1.5)), (
            centre_x + self.turtle.x * self.turtle.pixels_per_unit + 10 * math.cos(
                self.turtle.angle + math.pi / 1.5 * 2),
            centre_y - self.turtle.y * self.turtle.pixels_per_unit - 10 * math.sin(
                self.turtle.angle + math.pi / 1.5 * 2))
        pygame.draw.circle(self.scr, (255, 255, 255), ((point1[0] + point2[0]) / 2, (point1[1] + point2[1]) / 2), 3)

    def set_mouse_hand(self):
        # determining when to display the different types of cursors depending on actions being performed
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if (
                self.scr_width // 4 - 50 - self.scr_width // 12.8 // 2 <= mouse_x <= self.scr_width // 4 - self.scr_width // 12.8 // 2 + 50 and 20 <= mouse_y <= 70):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif self.selected_new_block is not None or self.join_new_block is not None:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEALL)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def draw_icons_borders(self):
        # draw the block adding bar at the bottom
        pygame.draw.rect(self.scr, (255, 255, 255),
                         [0, self.scr_height - 50, self.scr_width // 2 - self.scr_width // 12.8, 50])
        draw_text_center(self.scr, self.enteredText, (self.scr_width / 2 - self.scr_width / 12.8) // 2,
                         self.scr_height - 25, self.FONT,
                         (0, 0, 0))

        # draw all borders
        pygame.draw.line(self.scr, (0, 0, 0), (self.scr_width // 2, 0), (self.scr_width // 2, self.scr_height), 10)
        pygame.draw.line(self.scr, (0, 0, 0), (self.scr_width // 2 - self.scr_width // 12.8, 0),
                         (self.scr_width // 2 - self.scr_width // 12.8, self.scr_height), 10)

        pygame.draw.line(self.scr, (0, 0, 0), (self.scr_width // 2, self.scr_height // 2),
                         (self.scr_width, self.scr_height // 2), 10)
        pygame.draw.line(self.scr, (0, 0, 0), (0, self.scr_height - 50),
                         (self.scr_width // 2 - self.scr_width // 12.8, self.scr_height - 50), 10)

    def draw_menu_icons(self):
        # draw all menu icons
        # note: we multiply by 100 to account for the 100 pixels spacing between adjacent menu categories, and add 86 pixels
        # padding (over the block height of 72) to ensure the scroll bar appears below the menu icons for that category
        for i, row in enumerate(self.menu.items):
            running_width = 0
            for icon in row:
                self.scr.blit(icon, (
                    self.menu.start_x + running_width - self.menu.offsets[i], self.menu.start_y + (i * 100)))
                running_width += icon.get_width()
            bar_width = self.scr_width // 2 - 10 - self.menu.start_x
            pygame.draw.line(self.scr, (0, 0, 0), (self.menu.start_x, self.menu.start_y + (i * 100) + 86),
                             (self.scr_width // 2 - 10, self.menu.start_y + (i * 100) + 86), 5)
            pygame.draw.circle(self.scr, (255, 0, 0), (
                self.menu.start_x + (self.menu.offsets[i] / running_width) * bar_width,
                self.menu.start_y + (i * 100) + 86), 5)

        pygame.draw.rect(self.scr, (255, 255, 255),
                         [self.scr_width // 2, 0, self.scr_width // 2, self.scr_height // 2])

    def draw_terminal_output(self):
        # draw the trace table
        self.trace.length += 1

        containsError = False
        for k, line in enumerate(flatten(self.current_outputs)):
            self.scr.blit(self.FONT.render(line, True, (0, 0, 0)),
                          (self.scr_width // 2 + 10,
                           self.scr_height // 2 + 6 + k * (self.char_height + 5) + self.output_offset))
            if "Error" in line or "error" in line:
                containsError = True

        if self.trace.get_num_vars() > 0 and not containsError:
            # top left coordinates of the trace table
            trace_x, trace_y = self.scr_width // 2 + 10, self.scr_height // 2 + 6 + len(flatten(self.current_outputs)) * (self.char_height + 5) + self.output_offset
            # draw horizontal separating lines between rows of the table
            for i in np.linspace(trace_y, trace_y + self.trace.height(self.char_height), self.trace.length + 1):
                pygame.draw.line(self.scr, (0, 0, 0), (trace_x, i), (trace_x + self.trace.width(self.FONT), i))

            # draw vertical lines which are aligned to fit to the column headers
            running_width = trace_x
            for i in self.trace.get_vars():
                pygame.draw.line(self.scr, (0, 0, 0), (running_width, trace_y),
                                 (running_width, trace_y + self.trace.height(self.char_height)))
                running_width += self.FONT.size(i)[0] + 10
            pygame.draw.line(self.scr, (0, 0, 0), (running_width, trace_y),
                             (running_width, trace_y + self.trace.height(self.char_height)))

            # draw the headers and the values themselves
            running_width = trace_x
            for key in self.trace.get_vars():
                lst = [key] + [str(x) for x in self.trace.get_column(key)]
                for j, i in enumerate(
                        np.linspace(trace_y, trace_y + self.trace.height(self.char_height), self.trace.length + 1)):
                    if j == 0:
                        self.scr.blit(self.BOLD_FONT.render(lst[j], True, (0, 0, 0)), (running_width + 5, i + 5))
                    elif j < len(lst):
                        self.scr.blit(self.FONT.render((lst[j] if lst[j] != "None" else ""), True, (0, 0, 0)),
                                      (running_width + 5, i + 5))
                running_width += self.FONT.size(key)[0] + 10

        self.trace.length -= 1

    def set_menu_offsets(self):
        # scroll bars for menu items
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # for the x, we check if the mouse is between the left and right boundaries of the block adding environment
        # for the y, we check the y against each scroll bar's rectangle and find the minimum such difference
        # this is then compared to the height of the scroll bar (10 pixels) so if we are less than that we are in bounds
        # 'fraction' below finds, as a float from 0 to 1, what proportion of the way we are through the scroll bar
        if self.scr_width // 2 - self.scr_width // 12.8 + 5 <= mouse_x <= self.scr_width // 2 - 5 and min(
                abs(mouse_y - ((x + 1) * 100)) for x in range(int(self.scr_height // 100) + 1)) < 10:
            mouse_y -= self.menu.start_y
            fraction = (mouse_x - (self.scr_width // 2 - self.scr_width // 12.8 + 5)) / (
                    (self.scr_width // 2 - 5) - (self.scr_width // 2 - self.scr_width // 12.8 + 5))
            try:
                ind = mouse_y // 100
                total_width = sum(x.get_width() for x in self.menu.items[ind])
                self.menu.offsets[ind] = total_width * fraction
            except IndexError:
                pass

    def on_keydown(self, event):
        # on detecting KEYDOWN events, most of the following code is for updating the textarea in the block
        # adding bar at the bottom and performing appropriate actions depending on what has been entered into it.
        # we record the unicode character represented by the KEYDOWN event to add it to the textarea, in the
        # 'key' variable through the 'unicode' attribute of 'event'
        key = event.unicode
        if event.key == pygame.K_BACKSPACE:
            self.enteredText = self.enteredText[:-1]
        elif event.key == pygame.K_r and (
                pygame.key.get_pressed()[pygame.K_LALT] or pygame.key.get_pressed()[pygame.K_RALT]):
            self.trace = TraceTable()
        elif event.key == pygame.K_RETURN:
            k = pygame.key.get_pressed()
            if self.enteredText == "if":
                self.code.append(Block(IfElse(None, [], []), 100, 100))
            elif self.enteredText == "while":
                self.code.append(Block(While(None, []), 100, 100))
            elif isNumeric(self.enteredText) and self.enteredText:
                self.code.append(Block(Number(numerify(self.enteredText)), 100, 100))
            elif self.enteredText.isalnum() and not self.enteredText[0].isnumeric() and self.enteredText:
                if not (k[pygame.K_LSHIFT] or k[pygame.K_RSHIFT]):
                    self.code.append(Block(Variable(self.enteredText), 100, 100))
                else:
                    self.code.append(Block(Assignment(self.enteredText, None), 100, 100))
        # note: event.key takes the value 45 when the KEYDOWN event was pressing the hyphen key (to allow for
        # minus signs)
        elif any(x == event.key for x in numberKeys) or event.key == pygame.K_PERIOD or any(
                x == event.key for x in alphaKeys) or event.key == 45:
            self.enteredText += key

    def display_blocks(self):
        # order blocks by y and then x to ensure the order the blocks are labelled is the same as the running order (which
        # orders by y and then x)
        order = sorted(self.code, key=lambda l: (l.y, l.x))
        for block in self.code:
            draw_text_center(self.scr, f"Block {order.index(block) + 1}", block.x, block.y - 20, self.FONT,
                             (0, 0, 0))
            if isinstance(block, Block):
                BlockFunctions.drawBlock(self.scr, self.FONT, block.block, block.x, block.y)

    def on_mouse_button_up(self):
        # handling dragging logic to pan around in the code development environment
        # if the mouse button was released and self.selected_new_block is not None, it means it was the end of a drag
        # of a block into the code development environment. as such the appropriate block is added to the code
        # otherwise, we need to further check if this was part of a drag of a block into a space in another block.
        # we check if we are in the overall bounding rectangle of each block. if so, we can call addBlock() on it.
        # however, if we made to do this drag but didn't end up within any bounding rectangles, we just readd the block
        # back to the code development environment.
        self.prev_mouse_x, self.prev_mouse_y = None, None
        if self.selected_new_block is not None:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.code.append(Block(self.selected_new_block, mouse_x, mouse_y))
            self.selected_new_block = None
        if self.join_new_block is not None:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            for block in self.code:
                if block.x <= mouse_x <= block.x + BlockFunctions.get_width(
                        block.block,
                        self.FONT) and block.y <= mouse_y <= block.y + 50 + 10 * BlockFunctions.get_max_depth(
                    block.block):
                    BlockFunctions.addBlock(self.FONT, block.block, self.join_new_block, mouse_x, mouse_y,
                                            block.x,
                                            block.y)
                    break
            else:
                self.code.append(Block(self.join_new_block, mouse_x, mouse_y))
            self.join_new_block = None

    def on_mouse_button_down(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.scr_width // 4 - 50 - self.scr_width // 12.8 // 2 <= mouse_x <= self.scr_width // 4 - self.scr_width // 12.8 // 2 + 50 and 20 <= mouse_y <= 70:
            # sort blocks by their y position, and in rare instances of y positions being equal, their x
            run_order = sorted(self.code, key=lambda l: (l.y, l.x))
            now = datetime.datetime.now().strftime("Run time: %d/%m/%Y %H:%M:%S")
            line_length = self.scr_width // 2 // self.char_width - 1
            self.current_outputs = BlockFunctions.executeBlocks(run_order, line_length, self.turtle, self.trace,
                                                                self.globals,
                                                                now)
        # if the user presses down on a block in the menu to add (as part of dragging it into the code
        # development environment) we store it so later when they release the mouse in the CDE we can add the
        # correct block
        elif self.scr_width // 2 - self.scr_width // 12.8 <= mouse_x <= self.scr_width // 2 and not (
                self.scr_width // 2 - self.scr_width // 12.8 + 5 <= mouse_x <= self.scr_width // 2 - 5 and min(
            abs(mouse_y - ((x + 1) * 100)) for x in range(int(self.scr_height // 100) + 1)) < 10):
            ind = (mouse_y - self.menu.start_y) // 100
            # we only need to account for three categories
            if ind < 3:
                running_width = self.menu.start_x - self.menu.offsets[ind]
                for i, icon in enumerate(self.menu.items[ind]):
                    if running_width <= mouse_x <= running_width + icon.get_width():
                        item_name = self.menu.item_names[ind][i]
                        break
                    running_width += icon.get_width()
                if item_name in ops:
                    self.selected_new_block = Operation(item_name[-5], None, None)
                elif item_name in comps:
                    self.selected_new_block = Comparison(item_name[-5], None, None)
                elif item_name == "turtle2Dmovement.png":
                    self.selected_new_block = Turtle2DMovement(None, None, None, None)
                elif item_name == "turtle2DmoveForward.png":
                    self.selected_new_block = Turtle2DMoveForward(None)
                elif item_name == "turtle2Drotate.png":
                    self.selected_new_block = Turtle2DRotate(None)
        else:
            # we check if we made to drag any blocks. if so, we will either add it into an empty space in another block
            # or just readd it back into the code development environment. as such we copy that block to self.join_new
            # _block.
            for b, block in enumerate(self.code):
                if block.x <= mouse_x <= block.x + BlockFunctions.get_width(
                        block.block,
                        self.FONT) and block.y <= mouse_y <= block.y + 50 + 10 * BlockFunctions.get_max_depth(
                    block.block):
                    self.join_new_block = block.block
                    del self.code[b]
                    break

    def change_screen_size(self):
        # change the size of the screen
        self.scr_width, self.scr_height = self.scr.get_size()
        self.menu.start_x = self.scr_width // 2 - self.scr_width // 12.8 + 10

    def on_pan(self):
        # logic to deal with updating the offset of the code development environment as the mouse is being held during a pan
        # (in which its position may change, which is what this code accounts for)
        mouse = pygame.mouse.get_pressed()
        if mouse[0]:
            if self.prev_mouse_x is None and self.prev_mouse_y is None and self.selected_new_block is None and self.join_new_block is None:
                self.prev_mouse_x, self.prev_mouse_y = pygame.mouse.get_pos()
                if self.prev_mouse_x > self.scr_width // 2 - self.scr_width // 12.8:
                    self.prev_mouse_x, self.prev_mouse_y = None, None
            elif self.selected_new_block is None and self.join_new_block is None:
                new_mouse_x, new_mouse_y = pygame.mouse.get_pos()
                for block in self.code:
                    block.x += self.sensitivity * (new_mouse_x - self.prev_mouse_x)
                    block.y += self.sensitivity * (new_mouse_y - self.prev_mouse_y)
                self.prev_mouse_x = new_mouse_x
                self.prev_mouse_y = new_mouse_y

    def draw_run_button(self):
        pygame.draw.rect(self.scr, (0, 255, 0),
                         [self.scr_width // 4 - 50 - self.scr_width // 12.8 // 2, 20, 100, 50],
                         border_radius=20)
        draw_text_center(self.scr, "▶ Run", self.scr_width // 4 - self.scr_width // 12.8 // 2, 45, self.FONT,
                         (0, 0, 0))

    def frame_to_disp(self, f):
        # log is undefined at 0 so just set displacement as 0
        if f == 0:
            return 0
        # scaled logarithm - the longer the arrows are held, the more displacement that's needed
        return math.log(f, 1.5) * 0.1

    def set_output_offset(self):
        # calculate the displacements needed and add one to the frame counter to allow for next displacement to be
        # accurately calculated
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN] and self.current_outputs:
            self.output_offset -= self.frame_to_disp(self.frames)
            self.frames += 1
        if keys[pygame.K_UP] and self.current_outputs:
            self.output_offset += self.frame_to_disp(self.frames)
            self.frames += 1

    def exec(self):
        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    self.on_mouse_button_up()
                if event.type == pygame.VIDEORESIZE:
                    self.change_screen_size()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.on_mouse_button_down()
                if event.type == pygame.KEYDOWN:
                    self.on_keydown(event)
                if event.type == pygame.KEYUP:
                    if self.frames and (event.key == pygame.K_DOWN or event.key == pygame.K_UP):
                        self.frames = 0

            self.scr.fill((255, 255, 255))

            self.on_pan()

            if pygame.mouse.get_pressed()[0]:
                self.set_menu_offsets()

            self.set_output_offset()

            self.display_blocks()
            self.draw_run_button()

            pygame.draw.rect(self.scr, (255, 255, 255),
                             [self.scr_width // 2 - self.scr_width // 12.8, 0,
                              self.scr_width // 2 + self.scr_width // 12.8, self.scr_height])

            self.draw_terminal_output()
            self.draw_menu_icons()
            self.draw_turtle()
            self.draw_icons_borders()
            self.set_mouse_hand()

            pygame.display.update()

