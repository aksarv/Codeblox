import math
import pygame
from constants import *
from helpers import *


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


# operations and comparisons are binary, taking a sign representing the operation/comparison and the left and right
# arguments, and these are blocks themselves which may be of type operation/comparison. here Python is allowed to
# interpret the use of boolean arithmetic (e.g., if left and right evaluate to true in an addition operation, the
# result would be 2)
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


# if else block takes a conditional statement to decide which of the true or false set of statements should be executed
# the conditional statement is of type operation or comparison
class IfElse:
    def __init__(self, cond, true, false):
        self.cond = cond
        self.true = true + [None]
        self.false = false + [None]


class While:
    def __init__(self, cond, stats):
        self.cond = cond
        self.stats = stats + [None]


class Turtle2D:
    def __init__(self):
        self.x = 0
        self.y = 0
        # angle is from horizontal - pi/2 rad or 90 deg ensures it's pointing up initially
        self.angle = math.pi / 2
        self.pixels_per_unit = 20
        self.lines = []

    def move(self, dist):
        # use trig to move by a certain distance in the direction of the angle the turtle currently is in
        self.x += math.cos(self.angle) * dist
        self.y += math.sin(self.angle) * dist

    def relocate(self, x, y):
        # set turtle's x and y to that provided
        self.x = x
        self.y = y


# next three classes are for the turtle action blocks. Turtle2DMovement is for moving the turtle to the start_x and
# start_y, angling it towards dest_x and dest_y, and then moving it there. Turtle2DMoveForward is for moving the turtle
# a certain distance in the direction of its current angle. Turtle2DRotate is for rotating the turtle by a certain
# number of degrees
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


# stores information about the menu from which new blocks can be chosen and added. stores each icon to be displayed for
# adding, and the offset of each category of icons.
class Menu:
    def __init__(self, items, item_names, start_x, start_y):
        self.items = items
        self.item_names = item_names
        self.offsets = [0 for _ in range(len(items))]
        self.start_x = start_x
        self.start_y = start_y


# combines an expression/block tree with its associated x and y to draw it at
class Block:
    def __init__(self, block, x, y):
        self.block = block
        self.x = x
        self.y = y


# static class for block functions
class BlockFunctions:
    # get the max depth of a tree - we want the height of a block to account for the deepest subblock
    # if it is a leaf node, its max depth is inherently 1. otherwise, take each of the subtrees, and find their max depth.
    # the depth of the tree is just this plus the root node which adds 1 to the depth.
    @staticmethod
    def get_max_depth(block):
        if isinstance(block, Number) or block is None or isinstance(block, Variable):
            return 1
        elif isinstance(block, Comparison) or isinstance(block, Operation):
            return 1 + max(BlockFunctions.get_max_depth(block.left), BlockFunctions.get_max_depth(block.right))
        elif isinstance(block, Turtle2DMovement):
            return 1 + max(BlockFunctions.get_max_depth(block.start_x), BlockFunctions.get_max_depth(block.start_y),
                           BlockFunctions.get_max_depth(block.dest_x),
                           BlockFunctions.get_max_depth(block.dest_y))
        elif isinstance(block, Turtle2DMoveForward):
            return 1 + BlockFunctions.get_max_depth(block.dist)
        elif isinstance(block, Turtle2DRotate):
            return 1 + BlockFunctions.get_max_depth(block.angle)
        elif isinstance(block, Assignment):
            return 1 + BlockFunctions.get_max_depth(block.expr)
        elif isinstance(block, IfElse):
            return 1 + max(BlockFunctions.get_max_depth(block.cond), max(BlockFunctions.get_max_depth(x) for x in block.true),
                           max(BlockFunctions.get_max_depth(x) for x in block.false))
        elif isinstance(block, While):
            return 1 + max(BlockFunctions.get_max_depth(block.cond), max(BlockFunctions.get_max_depth(x) for x in block.stats))

    # get the width a block needs to be. this is used to find the left offset to draw blocks in the drawing functions, and
    # get a block's overall width
    @staticmethod
    def get_width(block, font):
        if block is None:
            return 20
        if isinstance(block, Number):
            return font.size(str(block.n))[0] + 20
        elif isinstance(block, Variable):
            return font.size(str(block.name))[0] + 20
        elif isinstance(block, Operation) or isinstance(block, Comparison):
            return BlockFunctions.get_width(block.left, font) + BlockFunctions.get_width(block.right, font) + 30
        elif isinstance(block, Turtle2DMovement):
            return BlockFunctions.get_width(block.start_x, font) + BlockFunctions.get_width(block.start_y, font) + BlockFunctions.get_width(
                block.dest_x, font) + BlockFunctions.get_width(
                block.dest_y, font) + 25 + font.size("move")[0]
        elif isinstance(block, Turtle2DMoveForward):
            return BlockFunctions.get_width(block.dist, font) + 20 + font.size("moveForward")[0]
        elif isinstance(block, Turtle2DRotate):
            return BlockFunctions.get_width(block.angle, font) + 20 + font.size("rotate")[0]
        elif isinstance(block, Assignment):
            return BlockFunctions.get_width(block.expr, font) + 20 + font.size(block.varName + " <- ")[0]
        elif isinstance(block, IfElse):
            return BlockFunctions.get_width(block.cond, font) + 30 + font.size("if")[0] + font.size("then")[0] + font.size("else")[
                0] + 5 * (
                    len(block.true) + len(block.false)) + sum(BlockFunctions.get_width(x, font) for x in block.true) + sum(
                BlockFunctions.get_width(x, font) for x in block.false)
        elif isinstance(block, While):
            return 5 + font.size("while")[0] + 5 + BlockFunctions.get_width(block.cond, font) + 5 + font.size("do")[0] + 5 + 5 * len(block.stats) + sum(BlockFunctions.get_width(x, font) for x in block.stats) + 5

    # recursive drawing subroutine
    # input the block (and on recursive calls the subblock) and the x y to draw it at
    # in general, for a block, first calculate its overall width and height to determine the size of the bounding box to
    # draw. from get_width(), this accounts for all separations in width/height due to padding/text.
    # then, from the widths of all the subblocks which are its parameters, again using get_width(), we can find the
    # respective x values to draw the blocks at. for the y values, for each depth we simply add one more layer of padding.
    @staticmethod
    def drawBlock(surf, font, block, x, y, last_height=None):
        overall_width = BlockFunctions.get_width(block, font)
        max_depth = BlockFunctions.get_max_depth(block)
        overall_height = 50 + 10 * max_depth
        if isinstance(block, Number) or isinstance(block, Variable):
            content = block.n if isinstance(block, Number) else block.name if isinstance(block, Variable) else None
            termColour = (0, 128, 25) if isinstance(block, Number) else (255, 128, 128) if isinstance(block,
                                                                                                      Variable) else None
            termOutlineColour = (0, 64, 12) if isinstance(block, Number) else (128, 64, 64) if isinstance(block,
                                                                                                          Variable) else None
            if last_height is not None:
                pygame.draw.rect(surf, termColour,
                                 [x, y, font.size(str(content))[0] + 20, 50])
                draw_text_center(surf, str(content), x + font.size(str(content))[0] // 2 + 10,
                                 y + 25,
                                 font, (0, 0, 0))
                pygame.draw.rect(surf, termOutlineColour,
                                 [x, y, font.size(str(content))[0] + 20, 50], 2)
                return
            else:
                pygame.draw.rect(surf, termColour, [x, y, font.size(str(content))[0] + 20, 50])
                draw_text_center(surf, str(content), x + font.size(str(content))[0] // 2 + 10, y + 25, font, (0, 0, 0))
                pygame.draw.rect(surf, termOutlineColour, [x, y, font.size(str(content))[0] + 20, 50], 2)
                return
        elif block is None:
            pygame.draw.rect(surf, (255, 255, 255), [x, y, 20, 50])
            pygame.draw.rect(surf, (0, 0, 0), [x, y, 20, 50], 2)
            return
        elif isinstance(block, Operation) or isinstance(block, Comparison):
            left_width = BlockFunctions.get_width(block.left, font)
            if last_height is not None:
                pygame.draw.rect(surf, (
                    (124, 193, 215) if isinstance(block, Operation) else (222, 80, 34) if isinstance(block,
                                                                                                     Comparison) else (
                        0, 0, 0)), [x, y, overall_width, overall_height])
                pygame.draw.rect(surf, (
                    (62, 97, 107) if isinstance(block, Operation) else (111, 40, 17) if isinstance(block,
                                                                                                   Comparison) else (
                        0, 0, 0)), [x, y, overall_width, overall_height],
                                 2)
            else:
                pygame.draw.rect(surf, (
                    (124, 193, 215) if isinstance(block, Operation) else (222, 80, 34) if isinstance(block,
                                                                                                     Comparison) else (
                        0, 0, 0)), [x, y, overall_width, overall_height])
                pygame.draw.rect(surf, (
                    (62, 97, 107) if isinstance(block, Operation) else (111, 40, 17) if isinstance(block,
                                                                                                   Comparison) else (
                        0, 0, 0)), [x, y, overall_width, overall_height], 2)

            draw_text_center(surf, block.sign, x + left_width + 15, (2 * y + overall_height) // 2, font, (0, 0, 0))
            BlockFunctions.drawBlock(surf, font, block.left, x + 5, y + 5, last_height=overall_height)
            BlockFunctions.drawBlock(surf, font, block.right, x + left_width + 25, y + 5, last_height=overall_height)
        elif isinstance(block, Turtle2DMovement):
            pygame.draw.rect(surf, (152, 59, 191), [x, y, overall_width, overall_height])
            pygame.draw.rect(surf, (71, 29, 96), [x, y, overall_width, overall_height], 2)
            draw_text_center(surf, "move", x + 5 + font.size("move")[0] // 2, (2 * y + overall_height) // 2, font,
                             (0, 0, 0))
            BlockFunctions.drawBlock(surf, font, block.start_x, x + 5 + font.size("move")[0], y + 5,
                                     last_height=overall_height)
            BlockFunctions.drawBlock(surf, font, block.start_y,
                                     x + font.size("move")[0] + 10 + BlockFunctions.get_width(block.start_x, font),
                                     y + 5,
                                     last_height=overall_height)
            BlockFunctions.drawBlock(surf, font, block.dest_x,
                                     x + font.size("move")[0] + 15 + BlockFunctions.get_width(block.start_x,
                                                                                              font) + BlockFunctions.get_width(
                                         block.start_y, font),
                                     y + 5, last_height=overall_height)
            BlockFunctions.drawBlock(surf, font, block.dest_y,
                                     x + font.size("move")[0] + 20 + BlockFunctions.get_width(block.start_x,
                                                                                              font) + BlockFunctions.get_width(
                                         block.start_y, font) + BlockFunctions.get_width(
                                         block.dest_x, font), y + 5, last_height=overall_height)
        elif isinstance(block, Turtle2DMoveForward):
            pygame.draw.rect(surf, (152, 59, 191), [x, y, overall_width, overall_height])
            pygame.draw.rect(surf, (71, 29, 96), [x, y, overall_width, overall_height], 2)
            draw_text_center(surf, "moveForward", x + 5 + font.size("moveForward")[0] // 2,
                             (2 * y + overall_height) // 2,
                             font, (0, 0, 0))
            BlockFunctions.drawBlock(surf, font, block.dist, x + 5 + font.size("moveForward")[0], y + 5,
                                     last_height=overall_height)
        elif isinstance(block, Turtle2DRotate):
            pygame.draw.rect(surf, (152, 59, 191), [x, y, overall_width, overall_height])
            pygame.draw.rect(surf, (71, 29, 96), [x, y, overall_width, overall_height], 2)
            draw_text_center(surf, "rotate", x + 5 + font.size("rotate")[0] // 2, (2 * y + overall_height) // 2, font,
                             (0, 0, 0))
            BlockFunctions.drawBlock(surf, font, block.angle, x + 5 + font.size("rotate")[0], y + 5,
                                     last_height=overall_height)
        elif isinstance(block, Assignment):
            pygame.draw.rect(surf, (255, 128, 128), [x, y, overall_width, overall_height])
            pygame.draw.rect(surf, (128, 64, 64), [x, y, overall_width, overall_height], 2)
            draw_text_center(surf, block.varName + " <- ", x + 5 + font.size(block.varName + " <- ")[0] // 2,
                             (2 * y + overall_height) // 2, font,
                             (0, 0, 0))
            BlockFunctions.drawBlock(surf, font, block.expr, x + 5 + font.size(block.varName + " <- ")[0], y + 5,
                                     last_height=overall_height)
        elif isinstance(block, IfElse):
            pygame.draw.rect(surf, (255, 255, 0), [x, y, overall_width, overall_height])
            pygame.draw.rect(surf, (128, 128, 0), [x, y, overall_width, overall_height], 2)
            draw_text_center(surf, "if", x + 5 + font.size("if")[0] // 2, (2 * y + overall_height) // 2, font,
                             (0, 0, 0))
            BlockFunctions.drawBlock(surf, font, block.cond, x + 5 + font.size("if")[0], y + 5,
                                     last_height=overall_height)
            draw_text_center(surf, "then",
                             x + 5 + font.size("if")[0] + BlockFunctions.get_width(block.cond, font) +
                             font.size("then")[0] // 2,
                             (2 * y + overall_height) // 2, font, (0, 0, 0))
            start_x = x + 10 + font.size("if")[0] + BlockFunctions.get_width(block.cond, font) + font.size("then")[0]
            for statement in block.true:
                BlockFunctions.drawBlock(surf, font, statement, start_x, y + 5, last_height=overall_height)
                start_x += 5 + BlockFunctions.get_width(statement, font)
            start_x += 20
            draw_text_center(surf, "else", start_x, (2 * y + overall_height) // 2, font, (0, 0, 0))
            draw_text_center(surf, "else", start_x, (2 * y + overall_height) // 2, font, (0, 0, 0))
            start_x += font.size("else")[0] - 20
            for statement in block.false:
                BlockFunctions.drawBlock(surf, font, statement, start_x, y + 5, last_height=overall_height)
                start_x += 5 + BlockFunctions.get_width(statement, font)
        elif isinstance(block, While):
            pygame.draw.rect(surf, (255, 0, 255), [x, y, overall_width, overall_height])
            pygame.draw.rect(surf, (128, 0, 128), [x, y, overall_width, overall_height], 2)
            draw_text_center(surf, "while", x + 5 + font.size("while")[0] // 2, (2 * y + overall_height) // 2, font, (0, 0, 0))
            BlockFunctions.drawBlock(surf, font, block.cond, x + 5 + font.size("while")[0], y + 5, last_height=overall_height)
            draw_text_center(surf, "do",
                             x + 5 + font.size("while")[0] + BlockFunctions.get_width(block.cond, font) +
                             font.size("do")[0] // 2 + 2,
                             (2 * y + overall_height) // 2, font, (0, 0, 0))
            start_x = x + 10 + font.size("while")[0] + BlockFunctions.get_width(block.cond, font) + font.size("do")[0]
            for statement in block.stats:
                BlockFunctions.drawBlock(surf, font, statement, start_x, y + 5, last_height=overall_height)
                start_x += 5 + BlockFunctions.get_width(statement, font)

    # Evaluate expressions (can include some boolean arithmetic edge cases - like True + True evaluates to 2)
    # The 'prev' parameter displays appropriate error messages about missing arguments if a None is found
    @staticmethod
    def evaluateExpr(block, globals, prev=""):
        # base case if it is a number or a variable - just appropriately retrieve the value from the object/globals dict
        # or just provide that value
        if isinstance(block, Number):
            return block.n
        if isinstance(block, Variable):
            return globals[block.name]
        if not (isinstance(block, Operation) or isinstance(block, Comparison)):
            raise SyntaxError(prev)

        # evaluate left and right subtrees recursively then apply the operator to the results
        evalLeft = BlockFunctions.evaluateExpr(block.left, globals, prev=(
            "arithmetic operation" if isinstance(block, Operation) else "comparison" if isinstance(block,
                                                                                                   Comparison) else ""))
        evalRight = BlockFunctions.evaluateExpr(block.right, globals, prev=(
            "arithmetic operation" if isinstance(block, Operation) else "comparison" if isinstance(block,
                                                                                                   Comparison) else ""))

        match block.sign:
            case "+":
                return evalLeft + evalRight
            case "-":
                return evalLeft - evalRight
            case "×":
                return evalLeft * evalRight
            case "÷":
                return evalLeft / evalRight
            case "^":
                return evalLeft ** evalRight
            case ">":
                return evalLeft > evalRight
            case "<":
                return evalLeft < evalRight
            case "=":
                return evalLeft == evalRight

    # evaluate if statements, which contain two sets of statements to execute, one if the condition expression is true
    # and the other if the condition expression is false. each statement can either be an if statement itself or a normal
    # operation, turtle instruction or comparison type statement.
    # note that between the following four methods for block execution, many parameters are passed by reference so they
    # are modified in place, e.g., the globals, turtle and trace
    @staticmethod
    def evaluateIfElse(block, num, turtle, trace, globals, run_order, line_length):
        globals.push()
        try:
            if BlockFunctions.evaluateExpr(block.cond, globals):
                for statement in block.true:
                    if isinstance(statement, IfElse):
                        yield from BlockFunctions.evaluateIfElse(statement, num, turtle, trace, globals, run_order, line_length)
                    elif isinstance(statement, While):
                        yield from BlockFunctions.evaluateWhile(statement, num, turtle, trace, globals, run_order, line_length)
                    else:
                        yield from BlockFunctions.execute(statement, num, turtle, trace, globals, run_order, line_length)
            else:
                for statement in block.false:
                    if isinstance(statement, IfElse):
                        yield from BlockFunctions.evaluateIfElse(statement, num, turtle, trace, globals, run_order, line_length)
                    elif isinstance(statement, While):
                        yield from BlockFunctions.evaluateWhile(statement, num, turtle, trace, globals, run_order, line_length)
                    else:
                        yield from BlockFunctions.execute(statement, num, turtle, trace, globals, run_order, line_length)
        except SyntaxError:
            output = f"Error running block {num}: missing or invalid condition provided to if statement"
            yield wrap(output, line_length)
        except OverflowError:
            output = f"Error running block {num}: result too large"
            yield wrap(output, line_length)
        except ZeroDivisionError:
            output = f"Error running block {num}: cannot divide by zero"
            yield wrap(output, line_length)
        except KeyError as e:
            output = f"Error running block {num}: variable {e} not defined in this scope"
            yield wrap(output, line_length)
        except:
            output = f"Error running block {num}: unexpected error while parsing"
            yield wrap(output, line_length)
        # regardless of what happens we need to exit the current scope when done with the if, so a finally block is used
        finally:
            globals.pop()

    @staticmethod
    def evaluateWhile(block, num, turtle, trace, globals, run_order, line_length):
        globals.push()
        try:
            while BlockFunctions.evaluateExpr(block.cond, globals):
                for statement in block.stats:
                    if isinstance(statement, IfElse):
                        yield from BlockFunctions.evaluateIfElse(statement, num, turtle, trace, globals, run_order, line_length)
                    elif isinstance(statement, While):
                        yield from BlockFunctions.evaluateWhile(statement, num, turtle, trace, globals, run_order,
                                                                 line_length)
                    else:
                        yield from BlockFunctions.execute(statement, num, turtle, trace, globals, run_order, line_length)
        except SyntaxError:
            output = f"Error running block {num}: missing or invalid condition provided to while statement"
            yield wrap(output, line_length)
        except OverflowError:
            output = f"Error running block {num}: result too large"
            yield wrap(output, line_length)
        except ZeroDivisionError:
            output = f"Error running block {num}: cannot divide by zero"
            yield wrap(output, line_length)
        except KeyError as e:
            output = f"Error running block {num}: variable {e} not defined in this scope"
            yield wrap(output, line_length)
        except:
            output = f"Error running block {num}: unexpected error while parsing"
            yield wrap(output, line_length)
        finally:
            globals.pop()

    @staticmethod
    def execute(block, num, turtle, trace, globals, run_order, line_length):
        if isinstance(block, Comparison) or isinstance(block, Operation) or isinstance(
                block, Number) or isinstance(block, Variable):
            try:
                output = f"Ran block {num}: " + str(BlockFunctions.evaluateExpr(block, globals))
            except SyntaxError as e:
                output = f"Error running block {num}: missing or invalid argument provided to {e}"
            except OverflowError:
                output = f"Error running block {num}: result too large"
            except ZeroDivisionError:
                output = f"Error running block {num}: cannot divide by zero"
            except KeyError as e:
                output = f"Error running block {num}: variable {e} not defined in this scope"
            except:
                output = f"Error running block {num}: unexpected error while parsing"
            yield wrap(output, line_length)
        elif isinstance(block, Turtle2DMovement):
            try:
                s_x, s_y = BlockFunctions.evaluateExpr(block.start_x, globals), BlockFunctions.evaluateExpr(block.start_y, globals)
                d_x, d_y = BlockFunctions.evaluateExpr(block.dest_x, globals), BlockFunctions.evaluateExpr(block.dest_y, globals)
                output = f"Ran block {num}"
                turtle.relocate(s_x, s_y)
                delta_x = d_x - s_x
                delta_y = d_y - s_y
                # find hypotenuse - so distance to move by - through pythagorean theorem
                dist = math.hypot(delta_x, delta_y)
                # boundary conditions - note delta_x being 0 would have made the argument to arctan undefined since
                # you cannot divide by 0 so it must be separately dealt with
                if delta_x == 0:
                    if d_y < s_y:
                        angle = math.pi * 1.5
                    elif d_y >= s_y:
                        angle = math.pi * 0.5
                elif delta_y == 0 and d_x < s_x:
                    angle = math.pi
                else:
                    # given a delta_y and a delta_x, arctan will give the angle it subtends with the horizontal axis
                    angle = math.atan(delta_y / delta_x)
                    # note: in two specific cases, arctan's output will be wrong by itself since it can only take values from 0
                    # to 90 but in reality the angles formed are greater. this specifically occurs in the second and third quadrants
                    if delta_x < 0 < delta_y or (delta_x < 0 and delta_y < 0):
                        angle += math.pi
                turtle.angle = angle
                turtle.move(dist)
                if [(s_x, s_y), (d_x, d_y)] not in turtle.lines:
                    turtle.lines.append([(s_x, s_y), (d_x, d_y)])
            except SyntaxError:
                output = f"Error running block {num}: missing or invalid argument provided to turtle movement"
            except OverflowError:
                output = f"Error running block {num}: result too large"
            except ZeroDivisionError:
                output = f"Error running block {num}: cannot divide by zero"
            except KeyError as e:
                output = f"Error running block {num}: variable {e} not defined in this scope"
            except:
                output = f"Error running block {num}: unexpected error while parsing"
            yield wrap(output, line_length)
        elif isinstance(block, Turtle2DMoveForward):
            output = f"Ran block {num}"
            s_x, s_y = turtle.x, turtle.y
            try:
                turtle.move(BlockFunctions.evaluateExpr(block.dist, globals))
                d_x, d_y = turtle.x, turtle.y
                turtle.lines.append([(s_x, s_y), (d_x, d_y)])
            except SyntaxError:
                output = f"Error running block {num}: missing or invalid argument provided to turtle move forward"
            except OverflowError:
                output = f"Error running block {num}: result too large"
            except ZeroDivisionError:
                output = f"Error running block {num}: cannot divide by zero"
            except KeyError as e:
                output = f"Error running block {num}: variable {e} not defined in this scope"
            except:
                output = f"Error running block {num}: unexpected error while parsing"
            yield wrap(output, line_length)
        elif isinstance(block, Turtle2DRotate):
            output = f"Ran block {num}"
            try:
                turtle.angle += math.radians(BlockFunctions.evaluateExpr(block.angle, globals))
            except SyntaxError:
                output = f"Error running block {num}: missing or invalid argument provided to turtle rotation"
            except OverflowError:
                output = f"Error running block {num}: result too large"
            except ZeroDivisionError:
                output = f"Error running block {num}: cannot divide by zero"
            except KeyError as e:
                output = f"Error running block {num}: variable {e} not defined in this scope"
            except:
                output = f"Error running block {num}: unexpected error while parsing"
            yield wrap(output, line_length)
        elif isinstance(block, Assignment):
            output = f"Ran block {num}"
            try:
                trace.update(block.varName, BlockFunctions.evaluateExpr(block.expr, globals))
                globals[block.varName] = BlockFunctions.evaluateExpr(block.expr, globals)
            except SyntaxError:
                output = f"Error running block {num}: missing or invalid argument provided to assignment"
            except OverflowError:
                output = f"Error running block {num}: result too large"
            except ZeroDivisionError:
                output = f"Error running block {num}: cannot divide by zero"
            except KeyError as e:
                output = f"Error running block {num}: variable {e} not defined in this scope"
            except:
                output = f"Error running block {num}: unexpected error while parsing"
            yield wrap(output, line_length)

    @staticmethod
    def executeBlocks(run_order, line_length, turtle, trace, globals, now):
        outputs = []
        try:
            for block in run_order:
                if isinstance(block.block, IfElse):
                    outputs.append(list(
                        BlockFunctions.evaluateIfElse(block.block, run_order.index(block) + 1, turtle, trace, globals,
                                                      run_order, line_length)))
                elif isinstance(block.block, While):
                    outputs.append(list(
                        BlockFunctions.evaluateWhile(block.block, run_order.index(block) + 1, turtle, trace, globals,
                                                      run_order, line_length)))
                else:
                    outputs.append(list(
                        BlockFunctions.execute(block.block, run_order.index(block) + 1, turtle, trace, globals, run_order,
                                               line_length)))
        except RecursionError:
            # an excessively long program may result in too many recursive calls for evaluation
            # additionally, there may be too many nested if/while blocks which cause the same issue
            msg = "There was an error, which may be due to too many nested if/while blocks or the program being too long."
            outputs.append(wrap(msg, line_length))
        finally:
            # this should be executed no matter what
            # add on the run time to the output regardless, and reset the globals
            outputs.insert(0, wrap(now, line_length))
            globals.reset()
            return outputs

    # subroutine to add a block to another block after it has been dragged into it. it starts at the overall block and
    # determines which subblock contains the point. it then repeats on that subblock, until an atomic block is
    # reached (i.e., empty space, number, variable instance). we further keep track of the block immediately before in each
    # recursive call to ensure the block to be added is 'added' by assigning it as child of that parent block. to determine
    # which attribute to set it as the child of, we also keep track of that parent's attribute associated with the subblock
    # the setattr() builtin function allows for this attribute to be set from a string representation of its name
    @staticmethod
    def addBlock(font, block, toAdd, x, y, pos_x, pos_y, par=None, attr=None):
        if block is None:
            if attr == "true":
                par.true[-1] = toAdd
                par.true = par.true + [None]
                return
            if attr == "false":
                par.false[-1] = toAdd
                par.false = par.false + [None]
                return
            if attr == "stats":
                par.stats[-1] = toAdd
                par.stats = par.stats + [None]
                return
            setattr(par, attr, toAdd)
        if isinstance(block, Comparison) or isinstance(block, Operation):
            if pos_x + 5 <= x <= pos_x + 5 + BlockFunctions.get_width(
                    block.left, font) and pos_y + 5 <= y <= pos_y + 55 + 10 * BlockFunctions.get_max_depth(
                    block.left):
                BlockFunctions.addBlock(font, block.left, toAdd, x, y, pos_x + 5, pos_y + 5, par=block, attr="left")
            elif pos_x + BlockFunctions.get_width(block.left, font) + 25 <= x <= pos_x + BlockFunctions.get_width(block.left, font) + 25 + BlockFunctions.get_width(
                    block.right, font) and pos_y + 5 <= y <= pos_y + 55 + 10 * BlockFunctions.get_max_depth(block.right):
                BlockFunctions.addBlock(font, block.right, toAdd, x, y, pos_x + BlockFunctions.get_width(block.left, font) + 25, pos_y + 5, par=block,
                         attr="right")
        elif isinstance(block, Turtle2DMoveForward):
            if pos_x + 5 + font.size("moveForward")[0] <= x <= pos_x + 5 + font.size("moveForward")[0] + BlockFunctions.get_width(
                    block.dist, font) and pos_y + 5 <= y <= pos_y + 55 + 10 * BlockFunctions.get_max_depth(block.dist):
                BlockFunctions.addBlock(font, block.dist, toAdd, x, y, pos_x + 5 + font.size("moveForward")[0], pos_y + 5, par=block,
                         attr="dist")
        elif isinstance(block, Turtle2DRotate):
            if pos_x + 5 + font.size("rotate")[0] <= x <= pos_x + 5 + font.size("rotate")[0] + BlockFunctions.get_width(
                    block.angle, font) and pos_y + 5 <= y <= pos_y + 55 + 10 * BlockFunctions.get_max_depth(block.angle):
                BlockFunctions.addBlock(font, block.angle, toAdd, x, y, pos_x + 5 + font.size("rotate")[0], pos_y + 5, par=block,
                         attr="angle")
        elif isinstance(block, Turtle2DMovement):
            if pos_x + 5 + font.size("move")[0] <= x <= pos_x + 5 + font.size("move")[0] + BlockFunctions.get_width(
                    block.start_x, font) and pos_y + 5 <= y <= pos_y + 55 + 10 * BlockFunctions.get_max_depth(block.start_x):
                BlockFunctions.addBlock(font, block.start_x, toAdd, x, y, pos_x + 5 + font.size("move")[0], pos_y + 5, par=block,
                         attr="start_x")
            elif pos_x + 10 + font.size("move")[0] + BlockFunctions.get_width(block.start_x, font) <= x <= pos_x + 10 + font.size("move")[
                0] + BlockFunctions.get_width(block.start_x, font) + BlockFunctions.get_width(
                block.start_y, font) and pos_y + 5 <= y <= pos_y + 55 + 10 * BlockFunctions.get_max_depth(block.start_y):
                BlockFunctions.addBlock(font, block.start_y, toAdd, x, y, pos_x + font.size("move")[0] + 10 + BlockFunctions.get_width(block.start_x, font),
                         pos_y + 5, par=block, attr="start_y")
            elif pos_x + 15 + font.size("move")[0] + BlockFunctions.get_width(block.start_x, font) + BlockFunctions.get_width(
                    block.start_y, font) <= x <= pos_x + 15 + font.size("move")[0] + BlockFunctions.get_width(block.start_x, font) + BlockFunctions.get_width(
                block.start_y, font) + BlockFunctions.get_width(block.dest_x, font) and pos_y + 5 <= y <= pos_y + 55 + 10 * BlockFunctions.get_max_depth(
                block.dest_x):
                BlockFunctions.addBlock(font, block.dest_x, toAdd, x, y,
                         pos_x + font.size("move")[0] + 15 + BlockFunctions.get_width(block.start_x, font) + BlockFunctions.get_width(block.start_y, font),
                         pos_y + 5, par=block, attr="dest_x")
            elif pos_x + 20 + font.size("move")[0] + BlockFunctions.get_width(block.start_x, font) + BlockFunctions.get_width(block.start_y, font) + BlockFunctions.get_width(
                    block.dest_x, font) <= x <= pos_x + 20 + font.size("move")[0] + BlockFunctions.get_width(block.start_x, font) + BlockFunctions.get_width(
                block.start_y, font) + BlockFunctions.get_width(block.dest_x, font) + BlockFunctions.get_width(
                block.dest_y, font) and pos_y + 5 <= y <= pos_y + 55 + 10 * BlockFunctions.get_max_depth(block.dest_y):
                BlockFunctions.addBlock(font, block.dest_y, toAdd, x, y,
                         pos_x + font.size("move")[0] + 20 + BlockFunctions.get_width(block.start_x, font) + BlockFunctions.get_width(
                             block.start_y, font) + BlockFunctions.get_width(
                             block.dest_x, font), pos_y + 5, par=block, attr="dest_y")
        elif isinstance(block, IfElse):
            if pos_x + 5 + font.size("if")[0] <= x <= pos_x + 5 + font.size("if")[0] + BlockFunctions.get_width(
                    block.cond, font) and pos_y + 5 <= y <= pos_y + 55 + 10 * BlockFunctions.get_max_depth(block.cond):
                BlockFunctions.addBlock(font, block.cond, toAdd, x, y, pos_x + 5 + font.size("if")[0], pos_y + 5, par=block,
                         attr="cond")
            start_x = pos_x + 10 + font.size("if")[0] + BlockFunctions.get_width(block.cond, font) + font.size("then")[0]
            for statement in block.true:
                if start_x <= x <= start_x + BlockFunctions.get_width(statement, font) and pos_y + 5 <= y <= pos_y + 55 + 10 * BlockFunctions.get_max_depth(
                        statement):
                    BlockFunctions.addBlock(font, statement, toAdd, x, y, start_x, pos_y + 5, par=block, attr="true")
                    break
                start_x += 5 + BlockFunctions.get_width(statement, font)
            else:
                start_x += font.size("else")[0]
                for statement in block.false:
                    if start_x <= x <= start_x + BlockFunctions.get_width(statement, font) and pos_y + 5 <= y <= pos_y + 55 + 10 * BlockFunctions.get_max_depth(
                            statement):
                        BlockFunctions.addBlock(font, statement, toAdd, x, y, start_x, pos_y + 5, par=block, attr="false")
                        break
                    start_x += 5 + BlockFunctions.get_width(statement, font)
        elif isinstance(block, While):
            if pos_x + 5 + font.size("while")[0] <= x <= pos_x + 5 + font.size("while")[0] + BlockFunctions.get_width(block.cond, font) and pos_y + 5 <= y <= pos_y + 55 + 10 * BlockFunctions.get_max_depth(block.cond):
                BlockFunctions.addBlock(font, block.cond, toAdd, x, y, pos_x + 5 + font.size("while")[0], pos_y + 5, par=block, attr="cond")
            start_x = pos_x + 10 + font.size("while")[0] + BlockFunctions.get_width(block.cond, font) + font.size("do")[0]
            for statement in block.stats:
                if start_x <= x <= start_x + BlockFunctions.get_width(statement, font) and pos_y + 5 <= y <= pos_y + 55 + 10 * BlockFunctions.get_max_depth(statement):
                    BlockFunctions.addBlock(font, statement, toAdd, x, y, start_x, pos_y + 5, par=block, attr="stats")
                    break
                start_x += 5 + BlockFunctions.get_width(statement, font)
        elif isinstance(block, Assignment):
            if pos_x + 5 + font.size(block.varName + " <- ")[0] <= x <= pos_x + 5 + font.size(block.varName + " <- ")[
                0] + BlockFunctions.get_width(block.expr, font) and pos_y + 5 <= y <= pos_y + 55 + 10 * BlockFunctions.get_max_depth(block.expr):
                BlockFunctions.addBlock(font, block.expr, toAdd, x, y, pos_x + 5 + font.size(block.varName + " <- ")[0], pos_y + 5,
                         par=block,
                         attr="expr")
