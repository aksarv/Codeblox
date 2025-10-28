import pygame
import copy
import datetime
import time
import math
import os
import numpy as np
import threading

pygame.init()

globals = {}

FONT_SIZE = 20
FONT = pygame.font.SysFont("SF Mono", FONT_SIZE)
BOLD_FONT = pygame.font.SysFont("SF Mono", FONT_SIZE, bold=True)
# use this to work out how many characters we can fit with a set number of pixels
# only one character needed as the font is monospaced
char_width, char_height = FONT.size("n")

magnifyPlus = pygame.transform.scale(pygame.image.load("magnifyPlus.png"), (30, 30))
magnifyMinus = pygame.transform.scale(pygame.image.load("magnifyMinus.png"), (30, 30))
loading = pygame.transform.scale(pygame.image.load("loading.png"), (150, 150))

ops = os.listdir(os.path.join(os.getcwd(), "operations"))
comps = os.listdir(os.path.join(os.getcwd(), "comparisons"))
t2Ds = os.listdir(os.path.join(os.getcwd(), "turtle2D"))
operations = [pygame.image.load(os.path.join(os.path.join(os.getcwd(), "operations"), o)) for o in ops if
              o.endswith(".png")]
comparisons = [pygame.image.load(os.path.join(os.path.join(os.getcwd(), "comparisons"), o)) for o in comps if
               o.endswith(".png")]
turtle2Ds = [pygame.image.load(os.path.join(os.path.join(os.getcwd(), "turtle2D"), o)) for o in t2Ds if
             o.endswith(".png")]
operations = [pygame.transform.scale(o, (72, 72)) for o in operations]
comparisons = [pygame.transform.scale(o, (72, 72)) for o in comparisons]
turtle2Ds = [pygame.transform.scale(o, (o.get_width() // (o.get_height() / 72), 72)) for o in turtle2Ds]

numberKeys = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]

alphaKeys = [pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d, pygame.K_e, pygame.K_f, pygame.K_g, pygame.K_h, pygame.K_i, pygame.K_j, pygame.K_k, pygame.K_l, pygame.K_m, pygame.K_n, pygame.K_o, pygame.K_p, pygame.K_q, pygame.K_r, pygame.K_s, pygame.K_t, pygame.K_u, pygame.K_v, pygame.K_w, pygame.K_x, pygame.K_y, pygame.K_z]

isProgramRunning = False


# subroutine to draw text centered at an x and y
def draw_text_center(surf, text, x, y, font, color):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surf.blit(text_surface, text_rect)


# if the string is a float then convert it to a float. else convert it to an int. assuming input can only be those
def numerify(string):
    if "." in string:
        return float(string)
    return int(string)


# classes - numbers, variables, assignments and operations. 'expr' means any block of type comparison or operation
# i.e., an expression that may evaluate to an integer or a boolean
class Number:
    def __init__(self, n):
        self.n = n


class Variable:
    def __init__(self, name):
        self.name = name


class Assignment:
    def __init__(self, varName, expr):
        self.varName = varName
        self.expr = expr


class Operation:
    def __init__(self, sign, left, right):
        self.sign = sign
        self.left = left
        self.right = right


class Comparison:
    def __init__(self, sign, left, right):
        self.sign = sign
        self.left = left
        self.right = right


class IfElse:
    def __init__(self, cond, true, false):
        self.cond = cond
        self.true = true + [None]
        self.false = false + [None]


class Turtle2D:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.angle = math.pi / 2
        self.pixels_per_unit = 20
        self.lines = []

    def move(self, dist):
        self.x += math.cos(self.angle) * dist
        self.y += math.sin(self.angle) * dist

    def relocate(self, x, y):
        self.x = x
        self.y = y


class Turtle2DMovement:
    def __init__(self, start_x, start_y, dest_x, dest_y):
        self.dest_x = dest_x
        self.dest_y = dest_y
        self.start_x = start_x
        self.start_y = start_y


class Turtle2DMoveForward:
    def __init__(self, dist):
        self.dist = dist


class Turtle2DRotate:
    def __init__(self, angle):
        self.angle = angle


class TurtleWait:
    def __init__(self, time):
        self.time = time
        self.elapsed = 0


class Menu:
    def __init__(self, items, item_names, start_x, start_y):
        self.items = items
        self.item_names = item_names
        self.offsets = [0 for _ in range(len(items))]
        self.start_x = start_x
        self.start_y = start_y


class TraceTable:
    def __init__(self):
        self.traceDict = {}
        self.length = 1

    def update(self, varName, value):
        if varName not in self.traceDict:
            self.traceDict[varName] = [None for _ in range(self.length)]
            self.traceDict[varName][-1] = value
        else:
            if self.traceDict[varName][-1] is not None:
                for key in self.traceDict.keys():
                    self.traceDict[key].append(None)
                self.traceDict[varName][-1] = value
                self.length += 1
            else:
                self.traceDict[varName][-1] = value

    def width(self):
        return sum(FONT.size(x)[0] for x in self.traceDict.keys()) + 10 * len(self.traceDict.keys())

    def height(self):
        return (char_height + 10) * self.length


# get the max depth of a tree - we want the height of a block to account for the deepest subblock
def get_max_depth(block):
    if isinstance(block, Number) or block is None or isinstance(block, Variable):
        return 1
    elif isinstance(block, Comparison) or isinstance(block, Operation):
        return 1 + max(get_max_depth(block.left), get_max_depth(block.right))
    elif isinstance(block, TurtleWait):
        return 1 + get_max_depth(block.time)
    elif isinstance(block, Turtle2DMovement):
        return 1 + max(get_max_depth(block.start_x), get_max_depth(block.start_y), get_max_depth(block.dest_x),
                       get_max_depth(block.dest_y))
    elif isinstance(block, Turtle2DMoveForward):
        return 1 + get_max_depth(block.dist)
    elif isinstance(block, Turtle2DRotate):
        return 1 + get_max_depth(block.angle)
    elif isinstance(block, Assignment):
        return 1 + get_max_depth(block.expr)
    elif isinstance(block, IfElse):
        return 1 + max(get_max_depth(block.cond), max(get_max_depth(x) for x in block.true),
                       max(get_max_depth(x) for x in block.false))


# get the width a block needs to be - to find the left offset to draw the right block in drawing functions
def get_width(block):
    if block is None:
        return 20
    if isinstance(block, Number):
        return FONT.size(str(block.n))[0] + 20
    elif isinstance(block, Variable):
        return FONT.size(str(block.name))[0] + 20
    elif isinstance(block, Operation) or isinstance(block, Comparison):
        return get_width(block.left) + get_width(block.right) + 30
    elif isinstance(block, TurtleWait):
        return get_width(block.time) + 20 + FONT.size("wait")[0]
    elif isinstance(block, Turtle2DMovement):
        return get_width(block.start_x) + get_width(block.start_y) + get_width(block.dest_x) + get_width(
            block.dest_y) + 25 + FONT.size("move")[0]
    elif isinstance(block, Turtle2DMoveForward):
        return get_width(block.dist) + 20 + FONT.size("moveForward")[0]
    elif isinstance(block, Turtle2DRotate):
        return get_width(block.angle) + 20 + FONT.size("rotate")[0]
    elif isinstance(block, Assignment):
        return get_width(block.expr) + 20 + FONT.size(block.varName + " <- ")[0]
    elif isinstance(block, IfElse):
        return get_width(block.cond) + 30 + FONT.size("if")[0] + FONT.size("then")[0] + FONT.size("else")[0] + 5 * (
                    len(block.true) + len(block.false)) + sum(get_width(x) for x in block.true) + sum(
            get_width(x) for x in block.false)


# recursive drawing subroutine
# input the block (and on recursive calls the subblock) and the x y to draw it at
# an additional parameter gives context of the height of the containing parent block to correctly y-center the child
def drawBlock(block, x, y, last_height=None):
    overall_width = get_width(block)
    max_depth = get_max_depth(block)
    overall_height = 50 + 10 * max_depth
    if isinstance(block, Number) or isinstance(block, Variable):
        content = block.n if isinstance(block, Number) else block.name if isinstance(block, Variable) else None
        termColour = (0, 128, 25) if isinstance(block, Number) else (255, 128, 128) if isinstance(block,
                                                                                                  Variable) else None
        termOutlineColour = (0, 64, 12) if isinstance(block, Number) else (128, 64, 64) if isinstance(block,
                                                                                                      Variable) else None
        if last_height is not None:
            pygame.draw.rect(scr, termColour, [x, y + (last_height // 2 - 30), FONT.size(str(content))[0] + 20, 50])
            draw_text_center(scr, str(content), x + FONT.size(str(content))[0] // 2 + 10,
                             y + (last_height // 2 - 30) + 25,
                             FONT, (0, 0, 0))
            pygame.draw.rect(scr, termOutlineColour,
                             [x, y + (last_height // 2 - 30), FONT.size(str(content))[0] + 20, 50], 2)
            return
        else:
            pygame.draw.rect(scr, termColour, [x, y, FONT.size(str(content))[0] + 20, 50])
            draw_text_center(scr, str(content), x + FONT.size(str(content))[0] // 2 + 10, y + 25, FONT, (0, 0, 0))
            pygame.draw.rect(scr, termOutlineColour, [x, y, FONT.size(str(content))[0] + 20, 50], 2)
            return
    elif block is None:
        pygame.draw.rect(scr, (255, 255, 255), [x, y + (last_height // 2 - 30), 20, 50])
        pygame.draw.rect(scr, (0, 0, 0), [x, y + (last_height // 2 - 30), 20, 50], 2)
        return
    elif isinstance(block, Operation) or isinstance(block, Comparison):
        left_width = get_width(block.left)
        if last_height is not None:
            pygame.draw.rect(scr, (
                (124, 193, 215) if isinstance(block, Operation) else (222, 80, 34) if isinstance(block,
                                                                                                 Comparison) else (
                    0, 0, 0)), [x, y + (last_height // 2 - overall_height // 2 - 5), overall_width, overall_height])
            pygame.draw.rect(scr, (
                (62, 97, 107) if isinstance(block, Operation) else (111, 40, 17) if isinstance(block, Comparison) else (
                    0, 0, 0)), [x, y + (last_height // 2 - overall_height // 2 - 5), overall_width, overall_height], 2)
        else:
            pygame.draw.rect(scr, (
                (124, 193, 215) if isinstance(block, Operation) else (222, 80, 34) if isinstance(block,
                                                                                                 Comparison) else (
                    0, 0, 0)), [x, y, overall_width, overall_height])
            pygame.draw.rect(scr, (
                (62, 97, 107) if isinstance(block, Operation) else (111, 40, 17) if isinstance(block, Comparison) else (
                    0, 0, 0)), [x, y, overall_width, overall_height], 2)

        # draw operator/comparator, then left subtree, then right subtree
        draw_text_center(scr, block.sign, x + left_width + 15, (2 * y + overall_height) // 2, FONT, (0, 0, 0))
        drawBlock(block.left, x + 5, y + 5, last_height=overall_height)
        drawBlock(block.right, x + left_width + 25, y + 5, last_height=overall_height)
    elif isinstance(block, TurtleWait):
        pygame.draw.rect(scr, (152, 59, 191), [x, y, overall_width, overall_height])
        pygame.draw.rect(scr, (71, 29, 96), [x, y, overall_width, overall_height], 2)
        draw_text_center(scr, "wait", x + 5 + FONT.size("wait")[0] // 2, (2 * y + overall_height) // 2, FONT, (0, 0, 0))
        drawBlock(block.time, x + 5 + FONT.size("wait")[0], y + 5, last_height=overall_height)
    elif isinstance(block, Turtle2DMovement):
        pygame.draw.rect(scr, (152, 59, 191), [x, y, overall_width, overall_height])
        pygame.draw.rect(scr, (71, 29, 96), [x, y, overall_width, overall_height], 2)
        draw_text_center(scr, "move", x + 5 + FONT.size("move")[0] // 2, (2 * y + overall_height) // 2, FONT, (0, 0, 0))
        drawBlock(block.start_x, x + 5 + FONT.size("move")[0], y + 5, last_height=overall_height)
        drawBlock(block.start_y, x + FONT.size("move")[0] + 10 + get_width(block.start_x), y + 5,
                  last_height=overall_height)
        drawBlock(block.dest_x, x + FONT.size("move")[0] + 15 + get_width(block.start_x) + get_width(block.start_y),
                  y + 5, last_height=overall_height)
        drawBlock(block.dest_y,
                  x + FONT.size("move")[0] + 20 + get_width(block.start_x) + get_width(block.start_y) + get_width(
                      block.dest_x), y + 5, last_height=overall_height)
    elif isinstance(block, Turtle2DMoveForward):
        pygame.draw.rect(scr, (152, 59, 191), [x, y, overall_width, overall_height])
        pygame.draw.rect(scr, (71, 29, 96), [x, y, overall_width, overall_height], 2)
        draw_text_center(scr, "moveForward", x + 5 + FONT.size("moveForward")[0] // 2, (2 * y + overall_height) // 2,
                         FONT, (0, 0, 0))
        drawBlock(block.dist, x + 5 + FONT.size("moveForward")[0], y + 5, last_height=overall_height)
    elif isinstance(block, Turtle2DRotate):
        pygame.draw.rect(scr, (152, 59, 191), [x, y, overall_width, overall_height])
        pygame.draw.rect(scr, (71, 29, 96), [x, y, overall_width, overall_height], 2)
        draw_text_center(scr, "rotate", x + 5 + FONT.size("rotate")[0] // 2, (2 * y + overall_height) // 2, FONT,
                         (0, 0, 0))
        drawBlock(block.angle, x + 5 + FONT.size("rotate")[0], y + 5, last_height=overall_height)
    elif isinstance(block, Assignment):
        pygame.draw.rect(scr, (255, 128, 128), [x, y, overall_width, overall_height])
        pygame.draw.rect(scr, (128, 64, 64), [x, y, overall_width, overall_height], 2)
        draw_text_center(scr, block.varName + " <- ", x + 5 + FONT.size(block.varName + " <- ")[0] // 2,
                         (2 * y + overall_height) // 2, FONT,
                         (0, 0, 0))
        drawBlock(block.expr, x + 5 + FONT.size(block.varName + " <- ")[0], y + 5, last_height=overall_height)
    elif isinstance(block, IfElse):
        pygame.draw.rect(scr, (255, 255, 0), [x, y, overall_width, overall_height])
        pygame.draw.rect(scr, (128, 128, 0), [x, y, overall_width, overall_height], 2)
        draw_text_center(scr, "if", x + 5 + FONT.size("if")[0] // 2, (2 * y + overall_height) // 2, FONT, (0, 0, 0))
        drawBlock(block.cond, x + 5 + FONT.size("if")[0], y + 5, last_height=overall_height)
        draw_text_center(scr, "then", x + 5 + FONT.size("if")[0] + get_width(block.cond) + FONT.size("then")[0] // 2,
                         (2 * y + overall_height) // 2, FONT, (0, 0, 0))
        start_x = x + 10 + FONT.size("if")[0] + get_width(block.cond) + FONT.size("then")[0]
        for statement in block.true:
            drawBlock(statement, start_x, y + 5, last_height=overall_height)
            start_x += 5 + get_width(statement)
        start_x += 20
        draw_text_center(scr, "else", start_x, (2 * y + overall_height) // 2, FONT, (0, 0, 0))
        start_x += FONT.size("else")[0] - 20
        for statement in block.false:
            drawBlock(statement, start_x, y + 5, last_height=overall_height)
            start_x += 5 + get_width(statement)


# combines an expression/block tree with its associated x and y
class Block:
    def __init__(self, block, x, y):
        self.block = block
        self.x = x
        self.y = y


# Evaluate expressions (can include some boolean arithmetic edge cases - like True + True evaluates to 2)
# The 'prev' parameter displays appropriate error messages about missing arguments if a None is found
def evaluateExpr(block, prev=""):
    # base case if it is a number or a variable - just appropriately retrieve the value from the object/globals dict
    if isinstance(block, Number):
        return block.n
    if isinstance(block, Variable):
        return globals[block.name]
    if not (isinstance(block, Operation) or isinstance(block, Comparison)):
        raise SyntaxError(prev)

    # evaluate left and right subtrees then apply the operator to the results
    evalLeft = evaluateExpr(block.left, prev=(
        "arithmetic operation" if isinstance(block, Operation) else "comparison" if isinstance(block,
                                                                                               Comparison) else ""))
    evalRight = evaluateExpr(block.right, prev=(
        "arithmetic operation" if isinstance(block, Operation) else "comparison" if isinstance(block,
                                                                                               Comparison) else ""))
    return evalLeft + evalRight if block.sign == "+" else evalLeft - evalRight if block.sign == "-" else evalLeft * evalRight if block.sign == "×" else evalLeft / evalRight if block.sign == "÷" else evalLeft ** evalRight if block.sign == "^" else evalLeft > evalRight if block.sign == ">" else evalLeft < evalRight if block.sign == "<" else evalLeft == evalRight if block.sign == "=" else 0


def evaluateIfElse(block, num):
    global run_order, outputs
    try:
        if evaluateExpr(block.cond):
            for statement in block.true:
                if not isinstance(statement, IfElse):
                    execute(statement, num)
                else:
                    evaluateIfElse(statement, num)
        else:
            for statement in block.false:
                if not isinstance(statement, IfElse):
                    execute(statement, num)
                else:
                    evaluateIfElse(statement, num)
    except SyntaxError:
        output = f"Error running block {num}: missing or invalid condition provided to if statement"
        wrapped = [output[i: i + line_length] for i in range(0, len(output), line_length)]
        outputs.append(wrapped)


def execute(block, num):
    global run_order, outputs
    if isinstance(block, Comparison) or isinstance(block, Operation) or isinstance(
            block, Number):
        try:
            output = f"Ran block {num}: " + str(evaluateExpr(block))
        except SyntaxError as e:
            output = f"Error running block {num}: missing or invalid argument provided to {e}"
        except OverflowError:
            output = f"Error running block {num}: division result too large"
        wrapped = [output[i: i + line_length] for i in range(0, len(output), line_length)]
        outputs.append(wrapped)
    elif isinstance(block, Turtle2DMovement):
        s_x, s_y = evaluateExpr(block.start_x), evaluateExpr(block.start_y)
        d_x, d_y = evaluateExpr(block.dest_x), evaluateExpr(block.dest_y)
        output = f"Ran block {num}"
        turtle.relocate(s_x, s_y)
        delta_x = d_x - s_x
        delta_y = d_y - s_y
        dist = math.hypot(delta_x, delta_y)
        angle = math.atan(delta_y / delta_x)
        # second quadrant
        if delta_x < 0 < delta_y:
            angle += math.pi / 2
        # third quadrant
        elif delta_x < 0 and delta_y < 0:
            angle += math.pi
        # fourth quadrant
        elif delta_y < 0 < delta_x:
            angle += math.pi / 2 * 3
        turtle.angle = angle
        turtle.move(dist)
        if [(s_x, s_y), (d_x, d_y)] not in turtle.lines:
            turtle.lines.append([(s_x, s_y), (d_x, d_y)])
        wrapped = [output[i: i + line_length] for i in range(0, len(output), line_length)]
        outputs.append(wrapped)
    elif isinstance(block, Turtle2DMoveForward):
        output = f"Ran block {num}"
        s_x, s_y = turtle.x, turtle.y
        try:
            turtle.move(evaluateExpr(block.dist))
            d_x, d_y = turtle.x, turtle.y
            turtle.lines.append([(s_x, s_y), (d_x, d_y)])
        except SyntaxError as e:
            if not e:
                output = f"Error running block {num}: turtle move forward missing argument"
            else:
                output = f"Error running block {num}: {e} missing argument"
        wrapped = [output[i: i + line_length] for i in range(0, len(output), line_length)]
        outputs.append(wrapped)
    elif isinstance(block, Turtle2DRotate):
        output = f"Ran block {num}"
        try:
            turtle.angle += math.radians(evaluateExpr(block.angle))
        except SyntaxError as e:
            if not e:
                output = f"Error running block {num}: turtle rotation missing argument"
            else:
                output = f"Error running block {num}: {e} missing argument"
        wrapped = [output[i: i + line_length] for i in range(0, len(output), line_length)]
        outputs.append(wrapped)
    elif isinstance(block, Assignment):
        output = f"Ran block {num}"
        globals[block.varName] = evaluateExpr(block.expr)
        trace.update(block.varName, evaluateExpr(block.expr))
        wrapped = [output[i: i + line_length] for i in range(0, len(output), line_length)]
        outputs.append(wrapped)


def executeBlocks():
    global isProgramRunning, run_order, outputs, current_outputs
    isProgramRunning = True
    for block in run_order:
        if not isinstance(block.block, IfElse):
            execute(block.block, run_order.index(block) + 1)
        else:
            evaluateIfElse(block.block, run_order.index(block) + 1)
    isProgramRunning = False
    outputs.insert(0, [now[i: i + line_length] for i in range(0, len(now), line_length)])
    current_outputs = copy.deepcopy(outputs)


def loadingScreen():
    surf = pygame.Surface((scr_width, scr_height))
    surf.set_alpha(128)
    surf.fill((0, 0, 0))
    scr.blit(surf, (0, 0))
    scr.blit(loading, (scr_width // 2 - 75, scr_height // 2 - 75))


def addBlock(block, toAdd, x, y, pos_x, pos_y, par=None, attr=None):
    if block is None:
        if attr == "true":
            par.true[-1] = toAdd
            par.true = par.true + [None]
            return
        if attr == "false":
            par.false[-1] = toAdd
            par.false = par.false + [None]
            return
        setattr(par, attr, toAdd)
    if isinstance(block, Comparison) or isinstance(block, Operation):
        if pos_x + 5 <= x <= pos_x + 5 + get_width(block.left) and pos_y + 5 <= y <= pos_y + 55 + 10 * get_max_depth(
                block.left):
            addBlock(block.left, toAdd, x, y, pos_x + 5, pos_y + 5, par=block, attr="left")
        elif pos_x + get_width(block.left) + 25 <= x <= pos_x + get_width(block.left) + 25 + get_width(
                block.right) and pos_y + 5 <= y <= pos_y + 55 + 10 * get_max_depth(block.right):
            addBlock(block.right, toAdd, x, y, pos_x + get_width(block.left) + 25, pos_y + 5, par=block, attr="right")
    elif isinstance(block, TurtleWait):
        if pos_x + 5 + FONT.size("wait")[0] <= x <= pos_x + 5 + FONT.size("wait")[0] + get_width(
                block.time) and pos_y + 5 <= y <= pos_y + 55 + 10 * get_max_depth(block.time):
            addBlock(block.time, toAdd, x, y, pos_x + 5 + FONT.size("wait")[0], pos_y + 5, par=block, attr="time")
    elif isinstance(block, Turtle2DMoveForward):
        if pos_x + 5 + FONT.size("moveForward")[0] <= x <= pos_x + 5 + FONT.size("moveForward")[0] + get_width(
                block.dist) and pos_y + 5 <= y <= pos_y + 55 + 10 * get_max_depth(block.dist):
            addBlock(block.dist, toAdd, x, y, pos_x + 5 + FONT.size("moveForward")[0], pos_y + 5, par=block,
                     attr="dist")
    elif isinstance(block, Turtle2DRotate):
        if pos_x + 5 + FONT.size("rotate")[0] <= x <= pos_x + 5 + FONT.size("rotate")[0] + get_width(
                block.angle) and pos_y + 5 <= y <= pos_y + 55 + 10 * get_max_depth(block.angle):
            addBlock(block.angle, toAdd, x, y, pos_x + 5 + FONT.size("rotate")[0], pos_y + 5, par=block, attr="angle")
    elif isinstance(block, Turtle2DMovement):
        if pos_x + 5 + FONT.size("move")[0] <= x <= pos_x + 5 + FONT.size("move")[0] + get_width(
                block.start_x) and pos_y + 5 <= y <= pos_y + 55 + 10 * get_max_depth(block.start_x):
            addBlock(block.start_x, toAdd, x, y, pos_x + 5 + FONT.size("move")[0], pos_y + 5, par=block, attr="start_x")
        elif pos_x + 10 + FONT.size("move")[0] + get_width(block.start_x) <= x <= pos_x + 10 + FONT.size("move")[
            0] + get_width(block.start_x) + get_width(
            block.start_y) and pos_y + 5 <= y <= pos_y + 55 + 10 * get_max_depth(block.start_y):
            addBlock(block.start_y, toAdd, x, y, pos_x + FONT.size("move")[0] + 10 + get_width(block.start_x),
                     pos_y + 5, par=block, attr="start_y")
        elif pos_x + 15 + FONT.size("move")[0] + get_width(block.start_x) + get_width(
                block.start_y) <= x <= pos_x + 15 + FONT.size("move")[0] + get_width(block.start_x) + get_width(
            block.start_y) + get_width(block.dest_x) and pos_y + 5 <= y <= pos_y + 55 + 10 * get_max_depth(
            block.dest_x):
            addBlock(block.dest_x, toAdd, x, y,
                     pos_x + FONT.size("move")[0] + 15 + get_width(block.start_x) + get_width(block.start_y),
                     pos_y + 5, par=block, attr="dest_x")
        elif pos_x + 20 + FONT.size("move")[0] + get_width(block.start_x) + get_width(block.start_y) + get_width(
                block.dest_x) <= x <= pos_x + 20 + FONT.size("move")[0] + get_width(block.start_x) + get_width(
            block.start_y) + get_width(block.dest_x) + get_width(
            block.dest_y) and pos_y + 5 <= y <= pos_y + 55 + 10 * get_max_depth(block.dest_y):
            addBlock(block.dest_y, toAdd, x, y,
                     pos_x + FONT.size("move")[0] + 20 + get_width(block.start_x) + get_width(
                         block.start_y) + get_width(
                         block.dest_x), pos_y + 5, par=block, attr="dest_y")
    elif isinstance(block, IfElse):
        if pos_x + 5 + FONT.size("if")[0] <= x <= pos_x + 5 + FONT.size("if")[0] + get_width(
                block.cond) and pos_y + 5 <= y <= pos_y + 55 + 10 * get_max_depth(block.cond):
            addBlock(block.cond, toAdd, x, y, pos_x + 5 + FONT.size("if")[0], pos_y + 5, par=block, attr="cond")
        start_x = pos_x + 10 + FONT.size("if")[0] + get_width(block.cond) + FONT.size("then")[0]
        for statement in block.true:
            if start_x <= x <= start_x + get_width(statement) and pos_y + 5 <= y <= pos_y + 55 + 10 * get_max_depth(
                    statement):
                addBlock(statement, toAdd, x, y, start_x, pos_y + 5, par=block, attr="true")
                break
            start_x += 5 + get_width(statement)
        start_x += FONT.size("else")[0]
        for statement in block.false:
            if start_x <= x <= start_x + get_width(statement) and pos_y + 5 <= y <= pos_y + 55 + 10 * get_max_depth(
                    statement):
                addBlock(statement, toAdd, x, y, start_x, pos_y + 5, par=block, attr="false")
                break
            start_x += 5 + get_width(statement)
    elif isinstance(block, Assignment):
        if pos_x + 5 + FONT.size(block.varName + " <- ")[0] <= x <= pos_x + 5 + FONT.size(block.varName + " <- ")[0] + get_width(block.expr) and pos_y + 5 <= y <= pos_y + 55 + 10 * get_max_depth(block.expr):
            addBlock(block.expr, toAdd, x, y, pos_x + 5 + FONT.size(block.varName + " <- ")[0], pos_y + 5, par=block, attr="expr")


scr_width, scr_height = 1280, 720
scr = pygame.display.set_mode((scr_width, scr_height), pygame.RESIZABLE)

code = []
prev_mouse_x, prev_mouse_y = None, None
selected_new_block = None
join_new_block = None
sensitivity = 1
enteredText = ""
homeScreen = False
current_outputs = []

turtle = Turtle2D()
menu = Menu(
    [operations, comparisons, turtle2Ds],
    [ops, comps, t2Ds],
    scr_width // 2 - scr_width // 12.8 + 10,
    10
)

trace = TraceTable()

start = time.time()

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if not homeScreen:
            if event.type == pygame.MOUSEBUTTONUP:
                prev_mouse_x, prev_mouse_y = None, None
                if selected_new_block is not None:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    code.append(Block(selected_new_block, mouse_x, mouse_y))
                    selected_new_block = None
                if join_new_block is not None:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    for block in code:
                        if block.x <= mouse_x <= block.x + get_width(block.block) and block.y <= mouse_y <= block.y + 50 + 10 * get_max_depth(block.block):
                            addBlock(block.block, join_new_block, mouse_x, mouse_y, block.x, block.y)
                            break
                    else:
                        code.append(Block(join_new_block, mouse_x, mouse_y))
                    join_new_block = None
            if event.type == pygame.VIDEORESIZE:
                scr_width, scr_height = scr.get_size()
                menu.start_x = scr_width // 2 - scr_width // 12.8 + 10
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if scr_width // 4 - 50 - scr_width // 12.8 // 2 <= mouse_x <= scr_width // 4 - scr_width // 12.8 // 2 + 50 and 20 <= mouse_y <= 70:
                    run_order = sorted(code, key=lambda l: (l.y, l.x))
                    now = datetime.datetime.now().strftime("Run time: %d/%m/%Y %H:%M:%S")
                    outputs = []
                    line_length = scr_width // 2 // char_width - 1
                    executeBlock = threading.Thread(target=executeBlocks)
                    executeBlock.start()
                elif 0 <= mouse_x <= 40 and 0 <= mouse_y <= 40:
                    FONT_SIZE += 3
                    FONT = pygame.font.SysFont("SF Mono", FONT_SIZE)
                    BOLD_FONT = pygame.font.SysFont("SF Mono", FONT_SIZE, bold=True)
                    char_width, char_height = FONT.size("n")
                elif 0 <= mouse_x <= 40 <= mouse_y <= 80:
                    FONT_SIZE -= 3
                    FONT = pygame.font.SysFont("SF Mono", FONT_SIZE)
                    BOLD_FONT = pygame.font.SysFont("SF Mono", FONT_SIZE, bold=True)
                    char_width, char_height = FONT.size("n")
                elif scr_width // 2 - scr_width // 12.8 <= mouse_x <= scr_width // 2 and not (
                        scr_width // 2 - scr_width // 12.8 + 5 <= mouse_x <= scr_width // 2 - 5 and min(
                    abs(mouse_y - ((x + 1) * 100)) for x in range(int(scr_height // 100) + 1)) < 10):
                    ind = (mouse_y - menu.start_y) // 100
                    try:
                        total_width = sum(x.get_width() for x in menu.items[ind])
                        item_name = menu.item_names[ind][int(menu.offsets[ind] / total_width * len(menu.items[ind]))]
                        if item_name in ops:
                            selected_new_block = Operation(item_name[-5], None, None)
                        elif item_name in comps:
                            selected_new_block = Comparison(item_name[-5], None, None)
                        elif item_name == "turtle2Dmovement.png":
                            selected_new_block = Turtle2DMovement(None, None, None, None)
                        elif item_name == "turtle2Dwait.png":
                            selected_new_block = TurtleWait(None)
                        elif item_name == "turtle2DmoveForward.png":
                            selected_new_block = Turtle2DMoveForward(None)
                        elif item_name == "turtle2Drotate.png":
                            selected_new_block = Turtle2DRotate(None)
                    except IndexError:
                        pass
                else:
                    for b, block in enumerate(code):
                        if block.x <= mouse_x <= block.x + get_width(
                                block.block) and block.y <= mouse_y <= block.y + 50 + 10 * get_max_depth(block.block):
                            join_new_block = block.block
                            del code[b]
                            break
            if event.type == pygame.KEYDOWN:
                key = event.unicode
                if event.key == pygame.K_BACKSPACE:
                    enteredText = enteredText[:-1]
                elif event.key == pygame.K_RETURN:
                    k = pygame.key.get_pressed()
                    if enteredText == "if":
                        code.append(Block(IfElse(None, [], []), 100, 100))
                    elif enteredText.isnumeric():
                        code.append(Block(Number(numerify(enteredText)), 100, 100))
                    elif enteredText.isalnum() and not enteredText[0].isnumeric():
                        if not (k[pygame.K_LSHIFT] or k[pygame.K_RSHIFT]):
                            code.append(Block(Variable(enteredText), 100, 100))
                        else:
                            code.append(Block(Assignment(enteredText, None), 100, 100))
                elif any(x == event.key for x in numberKeys) or event.key == pygame.K_PERIOD or any(x == event.key for x in alphaKeys):
                    enteredText += key
                elif event.key == pygame.K_r:
                    trace = TraceTable()

    scr.fill((255, 255, 255))

    mouse = pygame.mouse.get_pressed()
    if mouse[0]:
        if prev_mouse_x is None and prev_mouse_y is None and selected_new_block is None and join_new_block is None:
            prev_mouse_x, prev_mouse_y = pygame.mouse.get_pos()
            if prev_mouse_x > scr_width // 2 - scr_width // 12.8:
                prev_mouse_x, prev_mouse_y = None, None
        elif selected_new_block is None and join_new_block is None:
            new_mouse_x, new_mouse_y = pygame.mouse.get_pos()
            for block in code:
                block.x += sensitivity * (new_mouse_x - prev_mouse_x)
                block.y += sensitivity * (new_mouse_y - prev_mouse_y)
            prev_mouse_x = new_mouse_x
            prev_mouse_y = new_mouse_y

        # scroll bars for menu items
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if scr_width // 2 - scr_width // 12.8 + 5 <= mouse_x <= scr_width // 2 - 5 and min(
                abs(mouse_y - ((x + 1) * 100)) for x in range(int(scr_height // 100) + 1)) < 10:
            mouse_y -= menu.start_y
            fraction = (mouse_x - (scr_width // 2 - scr_width // 12.8 + 5)) / (
                    (scr_width // 2 - 5) - (scr_width // 2 - scr_width // 12.8 + 5))
            try:
                ind = mouse_y // 100
                total_width = sum(x.get_width() for x in menu.items[ind])
                menu.offsets[ind] = total_width * fraction
            except IndexError:
                pass

    order = sorted(code, key=lambda l: (l.y, l.x))
    for block in code:
        draw_text_center(scr, f"Block {order.index(block) + 1}", block.x, block.y - 20, FONT, (0, 0, 0))
        if isinstance(block, Block):
            drawBlock(block.block, block.x, block.y)

    pygame.draw.rect(scr, (0, 255, 0), [scr_width // 4 - 50 - scr_width // 12.8 // 2, 20, 100, 50], border_radius=20)
    draw_text_center(scr, "▶ Run", scr_width // 4 - scr_width // 12.8 // 2, 45, FONT, (0, 0, 0))

    pygame.draw.rect(scr, (255, 255, 255),
                     [scr_width // 2 - scr_width // 12.8, 0, scr_width // 2 + scr_width // 12.8, scr_height])

    trace.length += 1

    running_height = 0
    for message in current_outputs:
        for k, line in enumerate(message):
            scr.blit(FONT.render(line, True, (0, 0, 0)),
                     (scr_width // 2 + 10, scr_height // 2 + 6 + running_height + k * (char_height + 5)))
        running_height += (char_height + 5) * len(message)

    if len(trace.traceDict) > 0:
        trace_x, trace_y = scr_width // 2 + 10, running_height + scr_height // 2 + 6
        for i in np.linspace(trace_y, trace_y + trace.height(), trace.length + 1):
            pygame.draw.line(scr, (0, 0, 0), (trace_x, i), (trace_x + trace.width(), i))

        running_width = trace_x
        for i in trace.traceDict.keys():
            pygame.draw.line(scr, (0, 0, 0), (running_width, trace_y), (running_width, trace_y + trace.height()))
            running_width += FONT.size(i)[0] + 10
        pygame.draw.line(scr, (0, 0, 0), (running_width, trace_y), (running_width, trace_y + trace.height()))

        running_width = trace_x
        for key in trace.traceDict.keys():
            lst = [key] + [str(x) for x in trace.traceDict[key]]
            for j, i in enumerate(np.linspace(trace_y, trace_y + trace.height(), trace.length + 1)):
                if j == 0:
                    scr.blit(BOLD_FONT.render(lst[j], True, (0, 0, 0)), (running_width + 5, i + 5))
                elif j < len(lst):
                    scr.blit(FONT.render((lst[j] if lst[j] != "None" else ""), True, (0, 0, 0)),
                             (running_width + 5, i + 5))
            running_width += FONT.size(key)[0] + 10

    trace.length -= 1

    for i, row in enumerate(menu.items):
        running_width = 0
        for icon in row:
            scr.blit(icon, (menu.start_x + running_width - menu.offsets[i], menu.start_y + (i * 100)))
            running_width += icon.get_width()
        bar_width = scr_width // 2 - 10 - menu.start_x
        pygame.draw.line(scr, (0, 0, 0), (menu.start_x, menu.start_y + (i * 100) + 86),
                         (scr_width // 2 - 10, menu.start_y + (i * 100) + 86), 5)
        pygame.draw.circle(scr, (255, 0, 0), (
            menu.start_x + (menu.offsets[i] / running_width) * bar_width, menu.start_y + (i * 100) + 86), 5)

    pygame.draw.rect(scr, (255, 255, 255), [scr_width // 2, 0, scr_width // 2, scr_height // 2])

    for line in turtle.lines:
        pygame.draw.line(scr, (0, 0, 0), (scr_width // 4 * 3 + line[0][0] * turtle.pixels_per_unit,
                                          scr_height // 4 - line[0][1] * turtle.pixels_per_unit), (
                             scr_width // 4 * 3 + line[1][0] * turtle.pixels_per_unit,
                             scr_height // 4 - line[1][1] * turtle.pixels_per_unit))

    centre_x = scr_width // 4 * 3
    centre_y = scr_height // 4
    pygame.draw.polygon(scr, (0, 0, 0), [(centre_x + turtle.x * turtle.pixels_per_unit + 10 * math.cos(turtle.angle),
                                          centre_y - turtle.y * turtle.pixels_per_unit - 10 * math.sin(turtle.angle)), (
                                             centre_x + turtle.x * turtle.pixels_per_unit + 10 * math.cos(
                                                 turtle.angle + math.pi / 1.5),
                                             centre_y - turtle.y * turtle.pixels_per_unit - 10 * math.sin(
                                                 turtle.angle + math.pi / 1.5)), (
                                             centre_x + turtle.x * turtle.pixels_per_unit + 10 * math.cos(
                                                 turtle.angle + math.pi / 1.5 * 2),
                                             centre_y - turtle.y * turtle.pixels_per_unit - 10 * math.sin(
                                                 turtle.angle + math.pi / 1.5 * 2))])
    point1, point2 = (
        centre_x + turtle.x * turtle.pixels_per_unit + 10 * math.cos(
            turtle.angle + math.pi / 1.5),
        centre_y - turtle.y * turtle.pixels_per_unit - 10 * math.sin(
            turtle.angle + math.pi / 1.5)), (
        centre_x + turtle.x * turtle.pixels_per_unit + 10 * math.cos(
            turtle.angle + math.pi / 1.5 * 2),
        centre_y - turtle.y * turtle.pixels_per_unit - 10 * math.sin(
            turtle.angle + math.pi / 1.5 * 2))
    pygame.draw.circle(scr, (255, 255, 255), ((point1[0] + point2[0]) / 2, (point1[1] + point2[1]) / 2), 3)

    pygame.draw.rect(scr, (255, 255, 255), [0, scr_height - 50, scr_width // 2 - scr_width // 12.8, 50])
    draw_text_center(scr, enteredText, (scr_width / 2 - scr_width / 12.8) // 2, scr_height - 25, FONT, (0, 0, 0))

    pygame.draw.rect(scr, (255, 255, 255), [0, 0, 40, 40])
    pygame.draw.rect(scr, (255, 255, 255), [0, 40, 40, 40])
    scr.blit(magnifyPlus, (5, 5))
    scr.blit(magnifyMinus, (5, 45))
    pygame.draw.rect(scr, (0, 0, 0), [0, 0, 40, 40], 5)
    pygame.draw.rect(scr, (0, 0, 0), [0, 40, 40, 40], 5)

    pygame.draw.line(scr, (0, 0, 0), (scr_width // 2, 0), (scr_width // 2, scr_height), 10)
    pygame.draw.line(scr, (0, 0, 0), (scr_width // 2 - scr_width // 12.8, 0),
                     (scr_width // 2 - scr_width // 12.8, scr_height), 10)

    pygame.draw.line(scr, (0, 0, 0), (scr_width // 2, scr_height // 2), (scr_width, scr_height // 2), 10)
    pygame.draw.line(scr, (0, 0, 0), (0, scr_height - 50), (scr_width // 2 - scr_width // 12.8, scr_height - 50), 10)

    if isProgramRunning:
        loadingScreen()

    mouse_x, mouse_y = pygame.mouse.get_pos()
    if (scr_width // 4 - 50 - scr_width // 12.8 // 2 <= mouse_x <= scr_width // 4 - scr_width // 12.8 // 2 + 50 and 20 <= mouse_y <= 70) or (0 <= mouse_x <= 40 and 0 <= mouse_y <= 40) or (0 <= mouse_x <= 40 <= mouse_y <= 80):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    elif selected_new_block is not None or join_new_block is not None:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEALL)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    pygame.display.update()

pygame.quit()
