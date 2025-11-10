# subroutine to draw text centered at an x and y
def draw_text_center(surf, text, x, y, font, color):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surf.blit(text_surface, text_rect)


# if the string is a float then convert it to a float. else convert it to an int. the input will only be those
def numerify(string):
    if "." in string:
        return float(string)
    return int(string)


# check if a string represents a valid decimal or integer
def isNumeric(string):
    initial = all(c in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", "-"] for c in string) and string.count(
        ".") < 2 and string.count("-") < 2 and not string.endswith(".") and not string.startswith(".")
    if initial:
        try:
            return string.index("-") == 0
        except ValueError:
            return True


# wrap an 'output' string given a fixed line length
def wrap(output, line_length):
    return [output[i: i + line_length] for i in range(0, len(output), line_length)]


# flatten a multidimensional list into a 1D list
def flattenHelper(lst):
    for i in lst:
        if not isinstance(i, list):
            yield i
        else:
            yield from flattenHelper(i)


def flatten(lst):
    return list(flattenHelper(lst))

