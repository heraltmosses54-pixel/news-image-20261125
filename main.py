"""THE WORLD - Wednesday 25 November 2026.
Sums up the day's world news in one 1024x1024 image.
Self-contained: Pillow only, no network, deterministic.
Writes entry.png to $MAKEFUN_OUTPUT_DIR (or cwd as fallback)."""
import base64
import os
import zlib

from PIL import Image, ImageDraw

PAPER = (247, 243, 234)
INK = (20, 20, 20)
NAVY = (20, 33, 61)
RED = (178, 34, 34)
GREY = (90, 86, 78)
CARD = (255, 255, 255)
LINEC = (198, 192, 180)
MAPDOT = (148, 163, 188)
MAPBG = (233, 236, 240)
WHITE = (255, 255, 255)

W = 1024
H = 1024

# Embedded font atlas: DejaVu glyphs rendered at build time, packed as
# 4-bit alpha (two pixels per byte), zlib-compressed, base64.
# table entries: char -> (sheet_x, sheet_y, w, h, bearing_l, bearing_t, advance)
ATLAS = {
    'B58': {
        'w': 512, 'h': 46, 'ascent': 54, 'descent': 14,
        'table': {' ': (1, 1, 20, 0, 0, 54, 20), 'D': (22, 1, 48, 42, 0, 12, 48), 'E': (71, 1, 40, 42, 0, 12, 40), 'H': (112, 1, 49, 42, 0, 12, 49), 'L': (162, 1, 37, 42, 0, 12, 37), 'O': (200, 1, 49, 44, 0, 11, 49), 'R': (250, 1, 45, 42, 0, 12, 45), 'T': (296, 1, 40, 42, 0, 12, 40), 'W': (337, 1, 64, 42, 0, 12, 64)},
        'b64': (
            'eNrtmrtv00AYwO082iTNa6gEAqFEArHG/AXkP2hXpiB1YGwlRoZ0YiTsDOl/0K4dUDoBnVIxwIKUCkQlhpK26btpjO5h3+fz+ewmn6tI9JacnfPd/ezvdd+dYdwVt+RsVv7+2HxrwT/WbViGoLHTrEMuBoo/QEm8+Ni39zeXFCPa9v72awP25S3HRo390DJD7y2yiwapH6Dy0/Klisx/r8ef/2OpR7y0NPxF8nPOGmTpvffsok3qW/j89rCOyv8AdGCpR7wqB/PnxMhGgd7bYRddUl+Ngd8eVhH5Zz1fuqwe8WcwP5N59lSF1g/ZBdQFXH77DI/f9EL9Uo84KgfyJ0GvDVsYgxStl2Pht9fQ+B9JPdfVI64F8rPvvCJUnhuDDKleG/HwX2Hxmz2p54F6xEEwP727IVSeTyNPqhcx8TsCMDH/nNwxk3TfiOfB/E3h5/hNWi+R2gkmv2WYT97wIU4B/0DdOBJ/k3X3/Zn5lNNteNvOv7NlQZYGfe5epqAO0dtHuPzEWffZGFUU/gTrbI/Uk13wZkVbriHB/CXXImc4/4r7ZnfR+R3J3EDhz0GZZ7owktsuhPBTRb90aj1nbh1opxH5jZYtJGtS/grw7o75eim1LcqOTBo04741IgkfHGMg+kLmZxcXKPwtzyxpKM9CVtC2EPL9U64+EpV/xf9LBi02JuY3+mJCk/L3PLYtIyTrBvziSxOVf8yNwaz8FB5/UxjZCfkT0Jc4l2dS2xII8JX8XUfTO0QPuDHIwTAFl59OiK0sJuSfgfG6Q3Klsn9nGv6WY+kpeocZg6L8FB7/nHAA64qgyB8sBfJnbe8atemaMtn/HWr4G7xBkspSixmDmuLLIPHPilXmhPx5uF53XV3ZE/+0QHyv5q/wSG+GGo8FZgyW8bIf8syZwT1A4C9KTqrimvKcer2h5C9wf5SjsyqxiazjZT/kmSfR+Etwyee5zqnXm0r+LHciRaqVeSabfbzshzzzhLBaKPyWdL3o62TP0PGnudbUqJ5k6NxM6c1OJ38FLCWEPvj4Pxla/gR/apn2nqLGII3p/mOT/4j83/T8jqy3KbFJjUEWMfshzzyNrP/h8v9Vz89tXY+FST0CXkDMfoT5v/Hjn6j2b1TV8jNfZ/I0CRGDcgUx+xEW/4zPH9n/7Wj52RZImqc+SThUb8hB01TGv+Hxz3zb9kmyb1C2BZLlSkle4mrL99amcf2TC49/E33fU75BqUAO87wrovpbXcTsR3zr3yjrn5otR3K+QZlBqnBRInJwiJn9iC//Ia1/TdX6l72jEx0/c8gt7jrIA+eSY53W/FeU/Ec3JP/rZED63HSQlzoSmURs/oeY+U9V/mtHmf9c1PE7GwPXQD95TnS689+1CPnPvGwA/IPyXQSolIjZjxj3P6Lkv1NgUzNg0AXPrJa9W2m3t//l+3Qqfreciv2P35r9Dy4WQx1/iXd5BIQKL/sRef/z5vzh+1/u161r+PO8y10QVTo93eL+9xj8+v1Py1AZAD9/xjOtObgNFgt/wPmHMfj1+98WWG8ea/hTcHz3REk9Lv6g8y9j8OvPP1ggShhq+E3+sAXCIbzsR+TzT+Pwa8+/WCDBLT6nwun0PMTwNAI+/+eqgcivPf9kgQSvMAAK/rbHKnfAMRhU/pH+/ONY/Lrzb5ahMgAK/obHLDXliGG6y33F+cf/qrDzr9tLxl2ZmvIPQvRKOA=='
        ),
    },
    'B36': {
        'w': 512, 'h': 55, 'ascent': 34, 'descent': 9,
        'table': {' ': (1, 1, 13, 0, 0, 34, 13), "'": (15, 1, 11, 26, 0, 8, 11), ',': (27, 1, 14, 12, 0, 27, 14), '0': (42, 1, 25, 26, 0, 8, 25), '1': (68, 1, 25, 26, 0, 8, 25), '2': (94, 1, 25, 26, 0, 8, 25), '3': (120, 1, 25, 26, 0, 8, 25), '4': (146, 1, 25, 26, 0, 8, 25), '5': (172, 1, 25, 26, 0, 8, 25), '6': (198, 1, 25, 26, 0, 8, 25), '7': (224, 1, 25, 26, 0, 8, 25), '8': (250, 1, 25, 26, 0, 8, 25), '9': (276, 1, 25, 26, 0, 8, 25), 'A': (302, 1, 28, 26, 0, 8, 28), 'C': (331, 1, 26, 26, 0, 8, 26), 'D': (358, 1, 30, 26, 0, 8, 30), 'E': (389, 1, 25, 26, 0, 8, 25), 'H': (415, 1, 30, 26, 0, 8, 30), 'I': (446, 1, 13, 26, 0, 8, 13), 'K': (460, 1, 29, 26, 0, 8, 28), 'M': (1, 28, 36, 26, 0, 8, 36), 'P': (38, 28, 26, 26, 0, 8, 26), 'R': (65, 28, 28, 26, 0, 8, 28), 'S': (94, 28, 26, 26, 0, 8, 26)},
        'b64': (
            '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'
        ),
    },
    'B17': {
        'w': 256, 'h': 46, 'ascent': 16, 'descent': 5,
        'table': {' ': (1, 1, 6, 0, 0, 16, 6), "'": (8, 1, 5, 12, 0, 4, 5), '(': (14, 1, 8, 15, 0, 3, 8), ')': (23, 1, 8, 15, 0, 3, 8), ',': (32, 1, 6, 6, 0, 13, 6), '-': (39, 1, 7, 6, 0, 10, 7), '.': (47, 1, 6, 3, 0, 13, 6), '0': (54, 1, 12, 12, 0, 4, 12), '1': (67, 1, 12, 12, 0, 4, 12), '2': (80, 1, 12, 12, 0, 4, 12), '3': (93, 1, 12, 12, 0, 4, 12), '4': (106, 1, 12, 12, 0, 4, 12), '5': (119, 1, 12, 12, 0, 4, 12), '6': (132, 1, 12, 12, 0, 4, 12), '7': (145, 1, 12, 12, 0, 4, 12), '8': (158, 1, 12, 12, 0, 4, 12), '9': (171, 1, 12, 12, 0, 4, 12), ':': (184, 1, 7, 9, 0, 7, 7), 'A': (192, 1, 14, 12, 0, 4, 13), 'B': (207, 1, 13, 12, 0, 4, 13), 'C': (221, 1, 12, 12, 0, 4, 12), 'D': (234, 1, 14, 12, 0, 4, 14), 'E': (1, 17, 12, 12, 0, 4, 12), 'F': (14, 17, 12, 12, 0, 4, 12), 'G': (27, 17, 14, 12, 0, 4, 14), 'H': (42, 17, 14, 12, 0, 4, 14), 'I': (57, 17, 6, 12, 0, 4, 6), 'J': (64, 17, 7, 15, -1, 4, 6), 'K': (72, 17, 14, 12, 0, 4, 13), 'L': (87, 17, 11, 12, 0, 4, 11), 'M': (99, 17, 17, 12, 0, 4, 17), 'N': (117, 17, 14, 12, 0, 4, 14), 'O': (132, 17, 14, 12, 0, 4, 14), 'P': (147, 17, 12, 12, 0, 4, 12), 'Q': (160, 17, 14, 14, 0, 4, 14), 'R': (175, 17, 13, 12, 0, 4, 13), 'S': (189, 17, 12, 12, 0, 4, 12), 'T': (202, 17, 12, 12, 0, 4, 12), 'U': (215, 17, 14, 12, 0, 4, 14), 'V': (230, 17, 14, 12, 0, 4, 13), 'W': (1, 33, 19, 12, 0, 4, 19), 'X': (21, 33, 13, 12, 0, 4, 13), 'Y': (35, 33, 14, 12, -1, 4, 12), 'Z': (50, 33, 12, 12, 0, 4, 12)},
        'b64': (
            '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'
        ),
    },
    'R17': {
        'w': 256, 'h': 86, 'ascent': 16, 'descent': 5,
        'table': {' ': (1, 1, 5, 0, 0, 16, 5), '!': (7, 1, 7, 12, 0, 4, 7), '"': (15, 1, 8, 12, 0, 4, 8), '#': (24, 1, 14, 11, 0, 5, 14), '$': (39, 1, 11, 16, 0, 3, 11), '%': (51, 1, 16, 12, 0, 4, 16), '&': (68, 1, 13, 12, 0, 4, 13), "'": (82, 1, 5, 12, 0, 4, 5), '(': (88, 1, 7, 15, 0, 3, 7), ')': (96, 1, 7, 15, 0, 3, 7), '*': (104, 1, 9, 12, 0, 4, 8), '+': (114, 1, 14, 12, 0, 4, 14), ',': (129, 1, 5, 4, 0, 14, 5), '-': (135, 1, 6, 6, 0, 10, 6), '.': (142, 1, 5, 2, 0, 14, 5), '/': (148, 1, 6, 14, 0, 4, 6), '0': (155, 1, 11, 12, 0, 4, 11), '1': (167, 1, 11, 12, 0, 4, 11), '2': (179, 1, 11, 12, 0, 4, 11), '3': (191, 1, 11, 12, 0, 4, 11), '4': (203, 1, 11, 12, 0, 4, 11), '5': (215, 1, 11, 12, 0, 4, 11), '6': (227, 1, 11, 12, 0, 4, 11), '7': (239, 1, 11, 12, 0, 4, 11), '8': (1, 18, 11, 12, 0, 4, 11), '9': (13, 18, 11, 12, 0, 4, 11), ':': (25, 18, 6, 9, 0, 7, 6), ';': (32, 18, 6, 11, 0, 7, 6), '<': (39, 18, 14, 10, 0, 6, 14), '=': (54, 18, 14, 8, 0, 8, 14), '>': (69, 18, 14, 10, 0, 6, 14), '?': (84, 18, 9, 12, 0, 4, 9), '@': (94, 18, 17, 15, 0, 4, 17), 'A': (112, 18, 12, 12, 0, 4, 12), 'B': (125, 18, 12, 12, 0, 4, 12), 'C': (138, 18, 12, 12, 0, 4, 12), 'D': (151, 18, 13, 12, 0, 4, 13), 'E': (165, 18, 11, 12, 0, 4, 11), 'F': (177, 18, 10, 12, 0, 4, 10), 'G': (188, 18, 13, 12, 0, 4, 13), 'H': (202, 18, 13, 12, 0, 4, 13), 'I': (216, 18, 5, 12, 0, 4, 5), 'J': (222, 18, 6, 15, -1, 4, 5), 'K': (229, 18, 12, 12, 0, 4, 11), 'L': (242, 18, 10, 12, 0, 4, 9), 'M': (1, 34, 15, 12, 0, 4, 15), 'N': (17, 34, 13, 12, 0, 4, 13), 'O': (31, 34, 13, 12, 0, 4, 13), 'P': (45, 34, 10, 12, 0, 4, 10), 'Q': (56, 34, 13, 14, 0, 4, 13), 'R': (70, 34, 12, 12, 0, 4, 12), 'S': (83, 34, 11, 12, 0, 4, 11), 'T': (95, 34, 12, 12, -1, 4, 10), 'U': (108, 34, 12, 12, 0, 4, 12), 'V': (121, 34, 12, 12, 0, 4, 12), 'W': (134, 34, 17, 12, 0, 4, 17), 'X': (152, 34, 12, 12, 0, 4, 12), 'Y': (165, 34, 12, 12, -1, 4, 10), 'Z': (178, 34, 12, 12, 0, 4, 12), '[': (191, 34, 7, 15, 0, 3, 7), '\\': (199, 34, 6, 14, 0, 4, 6), ']': (206, 34, 7, 15, 0, 3, 7), '^': (214, 34, 14, 12, 0, 4, 14), '_': (229, 34, 10, 4, -1, 16, 8), '`': (240, 34, 9, 14, 0, 2, 8), 'a': (1, 50, 10, 9, 0, 7, 10), 'b': (12, 50, 11, 13, 0, 3, 11), 'c': (24, 50, 9, 9, 0, 7, 9), 'd': (34, 50, 11, 13, 0, 3, 11), 'e': (46, 50, 10, 9, 0, 7, 10), 'f': (57, 50, 7, 13, 0, 3, 6), 'g': (65, 50, 11, 13, 0, 7, 11), 'h': (77, 50, 11, 13, 0, 3, 11), 'i': (89, 50, 5, 13, 0, 3, 5), 'j': (95, 50, 6, 17, -1, 3, 5), 'k': (102, 50, 10, 13, 0, 3, 10), 'l': (113, 50, 5, 13, 0, 3, 5), 'm': (119, 50, 17, 9, 0, 7, 17), 'n': (137, 50, 11, 9, 0, 7, 11), 'o': (149, 50, 10, 9, 0, 7, 10), 'p': (160, 50, 11, 13, 0, 7, 11), 'q': (172, 50, 11, 13, 0, 7, 11), 'r': (184, 50, 7, 9, 0, 7, 7), 's': (192, 50, 9, 9, 0, 7, 9), 't': (202, 50, 7, 12, 0, 4, 7), 'u': (210, 50, 11, 9, 0, 7, 11), 'v': (222, 50, 10, 9, 0, 7, 10), 'w': (233, 50, 14, 9, 0, 7, 14), 'x': (1, 68, 10, 9, 0, 7, 10), 'y': (12, 68, 10, 13, 0, 7, 10), 'z': (23, 68, 9, 9, 0, 7, 9), '{': (33, 68, 11, 16, 0, 3, 11), '|': (45, 68, 6, 17, 0, 3, 6), '}': (52, 68, 11, 16, 0, 3, 11), '~': (64, 68, 14, 8, 0, 8, 14)},
        'b64': (
            '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'
        ),
    },
    'R14': {
        'w': 256, 'h': 59, 'ascent': 13, 'descent': 4,
        'table': {' ': (1, 1, 4, 0, 0, 13, 4), '!': (6, 1, 6, 10, 0, 3, 6), '"': (13, 1, 6, 10, 0, 3, 6), '#': (20, 1, 12, 10, 0, 3, 12), '$': (33, 1, 9, 13, 0, 2, 9), '%': (43, 1, 13, 10, 0, 3, 13), '&': (57, 1, 11, 10, 0, 3, 11), "'": (69, 1, 4, 10, 0, 3, 4), '(': (74, 1, 5, 12, 0, 2, 5), ')': (80, 1, 5, 12, 0, 2, 5), '*': (86, 1, 7, 10, 0, 3, 7), '+': (94, 1, 12, 9, 0, 4, 12), ',': (107, 1, 4, 3, 0, 11, 4), '-': (112, 1, 5, 4, 0, 9, 5), '.': (118, 1, 4, 2, 0, 11, 4), '/': (123, 1, 5, 12, 0, 3, 5), '0': (129, 1, 9, 10, 0, 3, 9), '1': (139, 1, 9, 10, 0, 3, 9), '2': (149, 1, 9, 10, 0, 3, 9), '3': (159, 1, 9, 10, 0, 3, 9), '4': (169, 1, 9, 10, 0, 3, 9), '5': (179, 1, 9, 10, 0, 3, 9), '6': (189, 1, 9, 10, 0, 3, 9), '7': (199, 1, 9, 10, 0, 3, 9), '8': (209, 1, 9, 10, 0, 3, 9), '9': (219, 1, 9, 10, 0, 3, 9), ':': (229, 1, 5, 7, 0, 6, 5), ';': (235, 1, 5, 8, 0, 6, 5), '<': (241, 1, 12, 8, 0, 5, 12), '=': (1, 15, 12, 7, 0, 6, 12), '>': (14, 15, 12, 8, 0, 5, 12), '?': (27, 15, 7, 10, 0, 3, 7), '@': (35, 15, 14, 12, 0, 3, 14), 'A': (50, 15, 10, 10, 0, 3, 10), 'B': (61, 15, 10, 10, 0, 3, 10), 'C': (72, 15, 10, 10, 0, 3, 10), 'D': (83, 15, 11, 10, 0, 3, 11), 'E': (95, 15, 9, 10, 0, 3, 9), 'F': (105, 15, 8, 10, 0, 3, 8), 'G': (114, 15, 11, 10, 0, 3, 11), 'H': (126, 15, 11, 10, 0, 3, 11), 'I': (138, 15, 4, 10, 0, 3, 4), 'J': (143, 15, 5, 13, -1, 3, 4), 'K': (149, 15, 10, 10, 0, 3, 9), 'L': (160, 15, 8, 10, 0, 3, 8), 'M': (169, 15, 12, 10, 0, 3, 12), 'N': (182, 15, 10, 10, 0, 3, 10), 'O': (193, 15, 11, 10, 0, 3, 11), 'P': (205, 15, 8, 10, 0, 3, 8), 'Q': (214, 15, 11, 12, 0, 3, 11), 'R': (226, 15, 10, 10, 0, 3, 10), 'S': (237, 15, 9, 10, 0, 3, 9), 'T': (1, 29, 10, 10, -1, 3, 9), 'U': (12, 29, 10, 10, 0, 3, 10), 'V': (23, 29, 10, 10, 0, 3, 10), 'W': (34, 29, 14, 10, 0, 3, 14), 'X': (49, 29, 10, 10, 0, 3, 10), 'Y': (60, 29, 10, 10, -1, 3, 9), 'Z': (71, 29, 10, 10, 0, 3, 10), '[': (82, 29, 5, 12, 0, 2, 5), '\\': (88, 29, 5, 12, 0, 3, 5), ']': (94, 29, 5, 12, 0, 2, 5), '^': (100, 29, 12, 10, 0, 3, 12), '_': (113, 29, 9, 3, -1, 13, 7), '`': (123, 29, 7, 11, 0, 2, 7), 'a': (131, 29, 9, 8, 0, 5, 9), 'b': (141, 29, 9, 11, 0, 2, 9), 'c': (151, 29, 8, 8, 0, 5, 8), 'd': (160, 29, 9, 11, 0, 2, 9), 'e': (170, 29, 9, 8, 0, 5, 9), 'f': (180, 29, 6, 11, 0, 2, 5), 'g': (187, 29, 9, 11, 0, 5, 9), 'h': (197, 29, 9, 11, 0, 2, 9), 'i': (207, 29, 4, 11, 0, 2, 4), 'j': (212, 29, 5, 14, -1, 2, 4), 'k': (218, 29, 9, 11, 0, 2, 8), 'l': (228, 29, 4, 11, 0, 2, 4), 'm': (233, 29, 14, 8, 0, 5, 14), 'n': (1, 44, 9, 8, 0, 5, 9), 'o': (11, 44, 9, 8, 0, 5, 9), 'p': (21, 44, 9, 11, 0, 5, 9), 'q': (31, 44, 9, 11, 0, 5, 9), 'r': (41, 44, 6, 8, 0, 5, 6), 's': (48, 44, 7, 8, 0, 5, 7), 't': (56, 44, 6, 10, 0, 3, 5), 'u': (63, 44, 9, 8, 0, 5, 9), 'v': (73, 44, 8, 8, 0, 5, 8), 'w': (82, 44, 11, 8, 0, 5, 11), 'x': (94, 44, 8, 8, 0, 5, 8), 'y': (103, 44, 8, 11, 0, 5, 8), 'z': (112, 44, 7, 8, 0, 5, 7), '{': (120, 44, 9, 13, 0, 2, 9), '|': (130, 44, 5, 14, 0, 2, 5), '}': (136, 44, 9, 13, 0, 2, 9), '~': (146, 44, 12, 6, 0, 7, 12)},
        'b64': (
            'eNrdmFtwG1cZx/+7ul9sbbnWTWqJGWZamiHaDC8kIbb6wgtNpDx2aGu9dApMGwt4A1q5MEMJTJ3NdIZSGjua6TBtJoktkgJJSGJ3UqfQAnYuxEkLsdI0iY1DJPmSOBdr+b5zdmXJlkMuLgbO2LvS2XP2d853vquAxW/DwBthDQijSN8C9L/2ApQzgNJzgr68ATRqvjYgyIMDKbq0aC1m0lsAXoFr6Djg7k8Aqy7tBhryffTcfQ1Imya9oWsEGDLNDLz5k4Avf4gn8x811+5q/mOOnMU/tzziT9LHXzdogv8LKEU8urQhYfF/wNOY/xHi69M6vtlMT35zT6eGH2utMaDpXWtM4y43PUE0gU49nsLOSGukzH8wv7ma/xNPhpd4AmrOn3yEHtQnIfavjAF74Dz4pr3/ty3JqQXsQ5BmhZiCEI+vpwHH91n8djmObn9EIINJBA1b6k9fT1ifLgi+apospy3LVmnMP8qsXsl3DwDPVPLtRgu+DO+AzQ/ztUWH3yB+urQLOCXH0SFs0JsSzO+1prYMR+y3DMqbUgiREN5h+X+0fOWPTqfguyqf+GmHzRrL38uLjJX5wSS90lOw+V0kEXMSeJykgic/0a1hqoeECyfJz2teAQ5EWnM2/2SZf1jeXNm1dO1YLfRvTd36s9iyJuvi8Sy0sF6hf3ajU6vge8d5F60x9Szz6STaYCaaDCnHdn1dkrRzW84+/xn5y1ZPOyvRS4bEco6F8TImlD/5jRk+5vAfQ6X8N4khgayL3jTGnzIYFasLJ+1x8PcyXOhGWf/sBeh9Yv4TRPAYUbysTCJwWivLvwb/dVTon2dcDsgC5f1vh4cEmEaZHxbTpf5W2B+3qDB/BHz0gi+inuTfFbt3mrFS/2rwiSjsT/D5jteUdELyX1O7I2gW8mct7NLXteFJdX9t/8Pt605e4K+WrCFCH5yn2+AZ+sdDR/hMhf3NbU7am/A/cdM0QFJvw+qS2BvxV7P+O4fI6zhYMML/3Ffa/O+c4UM8bnZ7hf3P3OY1PgZvHKjRJ/3vnFYX+w/x/4/bJlKbCXheEl8eKZHuuf8y/Tx9dtygS7c5Slp979BojD8mucMc4ItOnReTbM6OMb7S3w44p/hOgyjcXYd/Co4ilE7WuW7zJMfGEQ1+c7qNvcxg1SocPYNsaLtdE1A/eFhtp4P19ZOD3IH7clBG9U9l6eOnL3IH5IU6P/nzWfyWlOR3FVA/SiSN+I271IMaPYsbymhk2Rka4KBocEB/IFW1AOXZa0KZJlFHu3R8SCb9tTYmke/25yxoNDXDl51VfPdlSP72w3h8O/z7DeJTTKjjxftyPOMDHtDOmGr5U1tZov36jmAjtp7PfQt4gl0/7X8AoZQFFZu0+LKzis+eR/Kfxu+I/+YY8SnqkAtmPs9I84BO4OpcRRD8nRqOet9amgtTIMQ5PreSztmDhHpzfPQGXW5YnX7h6iW/exI2P/S5IvGz+xxFlTqd4zS5yeAZcV3Kv2X0O6ghf5UcXaEu5syFoBbxM4Z+dqyKX94/deavV+1/5981m+97Icv85i/ZfNY/wY/4OcmA8uhQsob+OSlY5Zj/FXCkZ70h7zyv/LdXy//+Izbf8c8Y8/2HZuQvZ7D8XeLw/YVKvmV/3D70vrXk7HHUJxBMSX5N/QsMzOErJADJx2l+llWnijho6R/NoNe8b+kfWXmhhjNwkZffiO4TZPRxcOgk+Y/PY38XH3a8N8v+lh6x+WJtWWydsT+2WGl/HJf7tDXZefj3y4P5PWnDBGsaqUVDlf+R0mT/83wFnxeo/Fmj470+ww/b/kfMaMjfEAJyF7Eqf0qbxyGq7+uOX95+1MjckrON3MIgT//0S7fNb07eyqjgwMcURQLD/6vxjxN6gxJcV4ETx2isFZhmzXuP0zZSFue4g0ZMI2hqx9nfkTrGz9iTOY/dynmWyM48Q4f4tg14dpqOo3McvtKrhny2l/8CnMQEDOzrGl5Ssg+MDVHwuUpo'
            'R1R35DXqiyZ9A1AusLGQXVxhZ7CRnUgMjqkDWmUyqnRY/PbYSsn3HHOcg4tW2bFiUy1+TyJ+zjU2m895KPFSnh0JMh13Ma6zv+4QqXGG+eskf3mK6glVOH7lqCj7IpJxWb5wGw/6Pjy9HObqjYrMtbx/1GVwfg6/ne3fnw18w+Aacj+VhfD9VdQ0fwPzQ5xox9Tz0sHYbVmezmRv1zA7Aj6Okb1o5gPrNgconBBtL9fg1v6dk9yzB8E2u+qr4EdjpALuQujzA1EihUWlmGcJB84Ivj8l9j+rjWiU/Pd8uykl+N5jDVfRzGZO+5f8niQZp8Vvid2EH8xQAatOrEORlBCtYjtpsSdd8F29NfhUG1Dxv5+dNcuf1jIiA1ZZ/vuoHrb4L5xFTT55L7q5is9xNfJT9JF81UlRqvBKOK9hPtcAc/c/rPYn6N2OgtC/aIQ+eyeVpwTf0j+qqCQ/r9fmk6rTHy5z6bHlMDbS0QczjSmL32xIPhfKc/lrS2mLz/Yn+HhmerPg+6X9lfldRm2+OqW1UHbQySJvGUOclK5dExbSynELFv97tfiiCfnDlr9040J/6lKV/B+OCH5VE4F4tfjZqJmnhHMIFeCYkEGL+G52UYIfnZffk2qS+ayP9a/M/+o9m7RKfttyYw7/Fhvz62Pz8dn+ZGP7K/N9lw6hiq8O3zGfsjGf4TfvvOTbs7iBRjm/uPx45r8y/grv7M2/bemQiJh7u7PO/kGhKYPkvNw5igpxRA1vtjGlTvLXDLl40q/nxtjundOJO+cL79y+gjIz9uF4ccVW9tgIJR/Ubb4yQWYd0jcMBFPO8TqDvGqYtHB5SkQ84nNdQnnmtdgX9NvnC+8sfhcVPkR4bMp9oxrnumOCT2NayP5eL1IA7KB4/Co2gFN58bsQ87ls8SQ/0z94R1bhy1KcEibqKMiItYcTulhZ/kQnn54920c1Qd04/xT3B1l/qBbfUcBdWGVNPr58OlLmh9ZPUB1e2EgFYZSKp7rvcqZEMZZqRMkv3h1/tvyFpwi2MX8PP/H9lg74WnbtO8C7aQ3uU71wcc3O58585fJd8ttXpCPSh3ew/hF/ZaQpyfwXI2mDFJwSp/5UaBzeM5R7KWaS0kM6djNhyb517O74s+yP+O6hkyx5+C/Rd+Qj/OtusIDmGKWk6CYi25/P3v+VhfAEln/2l+ODr3c+n2GXagtw/jfhq/21xeq0uxdC/2/Cn6/lUzO53wLy76BV+L9FaRuk/y8lsGht0WS/MO1fg5VjyA=='
        ),
    },
    'R13': {
        'w': 256, 'h': 55, 'ascent': 13, 'descent': 4,
        'table': {' ': (1, 1, 4, 0, 0, 13, 4), '!': (6, 1, 5, 9, 0, 4, 5), '"': (12, 1, 6, 9, 0, 4, 6), '#': (19, 1, 11, 10, 0, 3, 11), '$': (31, 1, 8, 11, 0, 4, 8), '%': (40, 1, 12, 9, 0, 4, 12), '&': (53, 1, 10, 9, 0, 4, 10), "'": (64, 1, 4, 9, 0, 4, 4), '(': (69, 1, 5, 12, 0, 2, 5), ')': (75, 1, 5, 12, 0, 2, 5), '*': (81, 1, 7, 9, 0, 4, 6), '+': (89, 1, 11, 9, 0, 4, 11), ',': (101, 1, 4, 3, 0, 11, 4), '-': (106, 1, 5, 4, 0, 9, 5), '.': (112, 1, 4, 2, 0, 11, 4), '/': (117, 1, 5, 11, 0, 4, 4), '0': (123, 1, 8, 9, 0, 4, 8), '1': (132, 1, 8, 9, 0, 4, 8), '2': (141, 1, 8, 9, 0, 4, 8), '3': (150, 1, 8, 9, 0, 4, 8), '4': (159, 1, 8, 9, 0, 4, 8), '5': (168, 1, 8, 9, 0, 4, 8), '6': (177, 1, 8, 9, 0, 4, 8), '7': (186, 1, 8, 9, 0, 4, 8), '8': (195, 1, 8, 9, 0, 4, 8), '9': (204, 1, 8, 9, 0, 4, 8), ':': (213, 1, 4, 7, 0, 6, 4), ';': (218, 1, 4, 8, 0, 6, 4), '<': (223, 1, 11, 8, 0, 5, 11), '=': (235, 1, 11, 6, 0, 7, 11), '>': (1, 14, 11, 8, 0, 5, 11), '?': (13, 14, 7, 9, 0, 4, 7), '@': (21, 14, 13, 11, 0, 4, 13), 'A': (35, 14, 9, 9, 0, 4, 9), 'B': (45, 14, 9, 9, 0, 4, 9), 'C': (55, 14, 9, 9, 0, 4, 9), 'D': (65, 14, 10, 9, 0, 4, 10), 'E': (76, 14, 8, 9, 0, 4, 8), 'F': (85, 14, 7, 9, 0, 4, 7), 'G': (93, 14, 10, 9, 0, 4, 10), 'H': (104, 14, 10, 9, 0, 4, 10), 'I': (115, 14, 4, 9, 0, 4, 4), 'J': (120, 14, 5, 12, -1, 4, 4), 'K': (126, 14, 9, 9, 0, 4, 9), 'L': (136, 14, 8, 9, 0, 4, 7), 'M': (145, 14, 11, 9, 0, 4, 11), 'N': (157, 14, 10, 9, 0, 4, 10), 'O': (168, 14, 10, 9, 0, 4, 10), 'P': (179, 14, 8, 9, 0, 4, 8), 'Q': (188, 14, 10, 11, 0, 4, 10), 'R': (199, 14, 9, 9, 0, 4, 9), 'S': (209, 14, 8, 9, 0, 4, 8), 'T': (218, 14, 9, 9, -1, 4, 8), 'U': (228, 14, 10, 9, 0, 4, 10), 'V': (239, 14, 9, 9, 0, 4, 9), 'W': (1, 27, 13, 9, 0, 4, 13), 'X': (15, 27, 9, 9, 0, 4, 9), 'Y': (25, 27, 9, 9, -1, 4, 8), 'Z': (35, 27, 9, 9, 0, 4, 9), '[': (45, 27, 5, 12, 0, 3, 5), '\\': (51, 27, 5, 11, 0, 4, 4), ']': (57, 27, 5, 12, 0, 3, 5), '^': (63, 27, 11, 9, 0, 4, 11), '_': (75, 27, 8, 3, -1, 13, 6), '`': (84, 27, 7, 10, 0, 3, 6), 'a': (92, 27, 8, 7, 0, 6, 8), 'b': (101, 27, 8, 11, 0, 2, 8), 'c': (110, 27, 7, 7, 0, 6, 7), 'd': (118, 27, 8, 11, 0, 2, 8), 'e': (127, 27, 8, 7, 0, 6, 8), 'f': (136, 27, 5, 11, 0, 2, 5), 'g': (142, 27, 8, 10, 0, 6, 8), 'h': (151, 27, 8, 11, 0, 2, 8), 'i': (160, 27, 4, 10, 0, 3, 4), 'j': (165, 27, 5, 13, -1, 3, 4), 'k': (171, 27, 8, 11, 0, 2, 8), 'l': (180, 27, 4, 11, 0, 2, 4), 'm': (185, 27, 13, 7, 0, 6, 13), 'n': (199, 27, 8, 7, 0, 6, 8), 'o': (208, 27, 8, 7, 0, 6, 8), 'p': (217, 27, 8, 10, 0, 6, 8), 'q': (226, 27, 8, 10, 0, 6, 8), 'r': (235, 27, 6, 7, 0, 6, 5), 's': (242, 27, 7, 7, 0, 6, 7), 't': (250, 27, 5, 9, 0, 4, 5), 'u': (1, 41, 8, 7, 0, 6, 8), 'v': (10, 41, 8, 7, 0, 6, 8), 'w': (19, 41, 11, 7, 0, 6, 11), 'x': (31, 41, 8, 7, 0, 6, 8), 'y': (40, 41, 8, 10, 0, 6, 8), 'z': (49, 41, 7, 7, 0, 6, 7), '{': (57, 41, 8, 12, 0, 3, 8), '|': (66, 41, 4, 13, 0, 3, 4), '}': (71, 41, 8, 12, 0, 3, 8), '~': (80, 41, 11, 6, 0, 7, 11)},
        'b64': (
            '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'
        ),
    },
}

# Dotted world map (equirectangular, Natural Earth land-110m rasterised).
# Each run: (row, start_col, length) on a 112x41 grid.
MAP_W = 112
MAP_H = 41
MAP_RUNS = [(1, 44, 4), (2, 23, 1), (2, 27, 5), (2, 35, 15), (2, 59, 4), (2, 86, 2), (3, 26, 1), (3, 28, 3), (3, 38, 12), (3, 73, 2), (3, 83, 8), (4, 6, 4), (4, 21, 3), (4, 26, 2), (4, 29, 6), (4, 39, 9), (4, 63, 2), (4, 77, 29), (5, 3, 57), (5, 63, 1), (5, 67, 2), (6, 4, 23), (6, 32, 2), (6, 41, 2), (6, 58, 3), (6, 63, 42), (6, 107, 3), (7, 15, 13), (7, 32, 5), (7, 54, 1), (7, 60, 1), (7, 64, 35), (7, 105, 2), (8, 16, 15), (8, 32, 7), (8, 53, 1), (8, 55, 46), (9, 18, 16), (9, 35, 1), (9, 38, 2), (9, 55, 45), (10, 17, 17), (10, 35, 1), (10, 56, 2), (10, 59, 1), (10, 61, 4), (10, 68, 3), (10, 72, 26), (10, 100, 1), (11, 17, 16), (11, 53, 3), (11, 62, 1), (11, 64, 7), (11, 73, 20), (11, 95, 1), (12, 18, 14), (12, 54, 5), (12, 66, 27), (12, 95, 1), (12, 97, 3), (13, 21, 10), (13, 53, 41), (14, 22, 4), (14, 30, 1), (14, 52, 20), (14, 74, 19), (15, 23, 3), (15, 31, 1), (15, 51, 16), (15, 68, 7), (15, 78, 6), (15, 85, 6), (16, 24, 5), (16, 51, 17), (16, 69, 4), (16, 79, 3), (16, 85, 4), (16, 93, 1), (17, 28, 2), (17, 51, 19), (17, 79, 2), (17, 87, 3), (17, 93, 2), (18, 30, 1), (18, 32, 5), (18, 52, 20), (19, 32, 8), (19, 53, 1), (19, 59, 12), (19, 86, 2), (19, 91, 2), (20, 31, 9), (20, 59, 10), (20, 87, 1), (20, 90, 3), (21, 31, 13), (21, 60, 8), (21, 88, 1), (21, 98, 3), (22, 31, 14), (22, 60, 8), (22, 92, 2), (22, 100, 1), (23, 32, 12), (23, 60, 9), (23, 71, 1), (23, 97, 1), (23, 100, 1), (24, 34, 10), (24, 60, 8), (24, 70, 1), (24, 94, 5), (24, 100, 1), (24, 111, 1), (25, 34, 9), (25, 60, 7), (25, 69, 2), (25, 91, 12), (26, 34, 7), (26, 61, 5), (26, 91, 13), (27, 34, 6), (27, 61, 4), (27, 92, 12), (28, 33, 5), (28, 99, 4), (29, 33, 4), (29, 110, 1), (30, 33, 3), (30, 109, 1), (31, 33, 2), (32, 33, 2), (35, 36, 1), (36, 34, 3), (36, 58, 1), (36, 60, 3), (36, 65, 12), (36, 79, 27), (37, 13, 9), (37, 25, 11), (37, 51, 57), (38, 5, 1), (38, 8, 24), (38, 40, 2), (38, 45, 62), (39, 8, 101)]

# ---- Page content: Wednesday 25 November 2026 ----
LEAD_KICKER = "LEAD STORY - LANGLEY, VIRGINIA, USA"
LEAD_HEADLINE = "AMERICA'S SPIES HACKED"
LEAD_SUMMARY = ("The CIA and the Office of the Director of National Intelligence "
    "discovered a cybersecurity breach that exposed some unclassified "
    "information, first reported by the New York Times on Tuesday and "
    "confirmed by AP and Reuters. The intrusion hit a network that mines "
    "public, unclassified material for intelligence insights. ODNI says no "
    "classified systems were disrupted; the CIA has not commented. It is "
    "not clear what was taken, or who did it.")
LEAD_CREDIT = "First reported by the New York Times; confirmed by AP and Reuters"

# (title, place, body, lat, lon) - 12 cards, 3 columns x 4 rows
CARDS = [
    ("HOUTHI DRONE HITS RIYADH'S TALLEST TOWER", "RIYADH, SAUDI ARABIA",
     "Second drone hit on the capital's tallest tower in under a week wounds 11.",
     24.71, 46.68),
    ("AUSTRALIA SAYS SORRY TO LGBTQ VETERANS", "CANBERRA, AUSTRALIA",
     "Canberra apologises for decades of discrimination, 34 years after the ban.",
     -35.28, 149.13),
    ("ZELENSKIY: WE HIT THE RUSSIAN SHIP", "GULF OF FINLAND",
     "Kyiv confirms it was behind the drone strike on the cargo ship Sparta II.",
     59.80, 24.00),
    ("KYIV DEFENDS LIBYA SHIP STRIKE", "BENGHAZI, LIBYA",
     "Ukraine calls the sinking of a Russian vessel in a Libyan port self-defence.",
     32.12, 20.07),
    ("HUAWEI GUILTY OF STEALING TRADE SECRETS", "NEW YORK, USA",
     "US jury convicts Huawei on 10 of 12 counts, including bank fraud.",
     40.71, -74.01),
    ("HOSTAGE SIEGE IN CARTAGENA SUPERMARKET", "CARTAGENA, COLOMBIA",
     "Gunmen fleeing a failed robbery hold 30 shoppers hostage; five freed.",
     10.39, -75.51),
    ("SHADOW STRIKE ON THE COLOMBIA BORDER", "APURE, VENEZUELA",
     "Venezuelan forces hit an ELN site near the border; watchdog reports 20-23 dead.",
     7.00, -70.00),
    ("EBOLA STAFF FLEE FIGHTING IN CONGO", "AKWE, ITURI, DR CONGO",
     "WHO evacuates health workers after three days sheltering amid fighting.",
     1.50, 29.50),
    ("NATO SENDS SPY PLANE TO POLAND", "WARSAW, POLAND",
     "AWACS deployed after three Russian cruise missiles landed on Polish soil.",
     52.23, 21.01),
    ("SARKOZY CASE GOES TO TRIAL", "PARIS, FRANCE",
     "Case against the former president and his wife Carla Bruni goes to trial.",
     48.86, 2.35),
    ("PUNJAB ALLIES REUNITE FOR 2027", "PUNJAB, INDIA",
     "BJP and Shiromani Akali Dal announce an alliance for the 2027 state elections.",
     30.90, 75.85),
    ("TRUMP GIVES GIULIANI TOP HONOUR", "WASHINGTON, USA",
     "President Trump awards Rudy Giuliani the Presidential Medal of Freedom.",
     38.90, -77.04),
]

BRIEFS = [
    "Gaza death toll reaches 74,746 amid continuing Israeli attacks, WAFA reports.",
    "266 million people now face acute food insecurity, the World Food Programme warns.",
    "Fort Hood gunman Nidal Hasan seeks a stay of his execution, set for next week.",
    "Trump pardons turkeys Freedom and Feathers in the annual Thanksgiving ceremony.",
    "Deposed Venezuelan leader Nicolas Maduro spends his first birthday behind bars.",
    "Brazil's Supreme Court summons Flavio Bolsonaro over claims he slandered Lula.",
    "A radar fault delays flights at Chicago's O'Hare airport, the FAA says.",
    "The European Union announces further sanctions against Russia over the war.",
    "A US envoy is 'not certain' military aid to Israel will end this year as promised.",
]

SPORT = "Donald 85 off 32 and Salt 58 off 30 as England level the T20I series"

NUMBERS = [
    ("266M", "people facing acute food insecurity (WFP)"),
    ("5,775", "Ebola deaths in DR Congo's worst outbreak (WHO)"),
    ("25", "hostages held in the Cartagena supermarket siege"),
]

LEAD_MARKER = (38.95, -77.14)  # Langley, Virginia

# ---- Text engine (embedded atlas only, no system fonts) ----
_SHEETS = {}


def _sheet(font):
    if font in _SHEETS:
        return _SHEETS[font]
    a = ATLAS[font]
    raw = zlib.decompress(base64.b64decode(a['b64']))
    # expand 4-bit nibbles to 8-bit alpha (nibble * 17)
    alpha = bytearray(len(raw) * 2)
    for i, b in enumerate(raw):
        alpha[2 * i] = (b >> 4) * 17
        alpha[2 * i + 1] = (b & 15) * 17
    img = Image.frombytes('L', (a['w'], a['h']), bytes(alpha))
    _SHEETS[font] = (img, a)
    return _SHEETS[font]


def _glyph(font, ch):
    a = ATLAS[font]
    g = a['table'].get(ch)
    if g is None:
        g = a['table'].get(' ', (0, 0, 0, 0, 0, 0, 0))
    return g


def text_width(font, s):
    return sum(_glyph(font, ch)[6] for ch in s)


def wrap(font, text, max_w, max_lines=None):
    words = text.split(' ')
    lines = []
    cur = ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        if text_width(font, trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and text_width(font, lines[-1] + '...') > max_w:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1] + '...'
    return lines


def draw_text(img, font, x, y_top, s, color, align='left', max_w=None):
    """Draw text with its ascender line at y_top. align: left/center/right
    (with max_w as the reference width for center/right)."""
    sheet, a = _sheet(font)
    if align != 'left' and max_w is not None:
        w = text_width(font, s)
        if align == 'center':
            x = x + (max_w - w) // 2
        else:
            x = x + max_w - w
    px = x
    for ch in s:
        sx, sy, w, h, l, t, adv = _glyph(font, ch)
        if w > 0 and h > 0:
            tile = Image.new('RGBA', (w, h), color + (0,))
            tile.putalpha(sheet.crop((sx, sy, sx + w, sy + h)))
            img.paste(tile, (px + l, y_top + t), tile)
        px += adv
    return px


def draw_lines(img, font, x, y_top, lines, color, line_h):
    y = y_top
    for ln in lines:
        draw_text(img, font, x, y, ln, color)
        y += line_h
    return y

# ---- Layout ----
MAP_X0, MAP_Y0, MAP_PW, MAP_PH = 620, 108, 380, 140


def _marker_xy(lat, lon):
    return (MAP_X0 + (lon + 180.0) / 360.0 * MAP_PW,
            MAP_Y0 + (90.0 - lat) / 180.0 * MAP_PH)


def build():
    img = Image.new('RGB', (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # masthead 0..96
    draw_text(img, 'B58', 0, 8, 'THE WORLD', INK, align='center', max_w=W)
    draw_text(img, 'R13', 24, 34, 'VOL. I - No. 329', GREY)
    dw = text_width('R13', '25 NOVEMBER 2026')
    draw_text(img, 'R13', 1000 - dw, 34, '25 NOVEMBER 2026', GREY)
    draw_text(img, 'R14', 0, 66, 'WEDNESDAY 25 NOVEMBER 2026', NAVY,
              align='center', max_w=W)
    d.rectangle([0, 93, W, 96], fill=NAVY)

    # lead story (left column)
    draw_text(img, 'B17', 24, 110, LEAD_KICKER, RED)
    draw_text(img, 'B36', 24, 134, LEAD_HEADLINE, INK)
    end_y = draw_lines(img, 'R17', 24, 182,
                       wrap('R17', LEAD_SUMMARY, 576), INK, 21)
    draw_text(img, 'R13', 24, end_y + 14, LEAD_CREDIT, GREY)
    d.rectangle([24, end_y + 44, 600, 45 + end_y], fill=LINEC)
    draw_text(img, 'B17', 24, end_y + 54, 'ALSO TODAY:', RED)
    ax = 24 + text_width('B17', 'ALSO TODAY:') + 8
    draw_lines(img, 'R17', ax, end_y + 52,
               wrap('R17', 'Houthi drone hits Riyadh tower - Australia says '
                    'sorry - Huawei guilty', 600 - ax, max_lines=2), INK, 21)

    # dotted world map (right column)
    d.rectangle([MAP_X0, MAP_Y0, MAP_X0 + MAP_PW, MAP_Y0 + MAP_PH], fill=MAPBG)
    px, py = MAP_PW / MAP_W, MAP_PH / MAP_H
    for (r, s, ln) in MAP_RUNS:
        for c in range(s, s + ln):
            x = MAP_X0 + c * px
            y = MAP_Y0 + r * py
            d.ellipse([x, y, x + 3, y + 3], fill=MAPDOT)
    draw_text(img, 'R13', MAP_X0, MAP_Y0 + MAP_PH + 8,
              'THE WORLD AT A GLANCE', GREY, align='center', max_w=MAP_PW)
    markers = [LEAD_MARKER] + [(c[3], c[4]) for c in CARDS]
    for (lat, lon) in markers:
        mx, my = _marker_xy(lat, lon)
        d.ellipse([mx - 5, my - 5, mx + 5, my + 5], fill=WHITE)
        d.ellipse([mx - 3.5, my - 3.5, mx + 3.5, my + 3.5], fill=RED)

    # by the numbers rail
    draw_text(img, 'B17', MAP_X0, 284, 'BY THE NUMBERS', NAVY)
    d.rectangle([MAP_X0, 306, MAP_X0 + MAP_PW, 307], fill=LINEC)
    for i, (num, label) in enumerate(NUMBERS):
        ry = 314 + i * 46
        draw_text(img, 'B36', MAP_X0, ry, num, RED)
        draw_lines(img, 'R14', MAP_X0 + 150, ry + 2,
                   wrap('R14', label, 230, max_lines=2), INK, 17)

    # rule above the cards
    d.rectangle([0, 446, W, 448], fill=NAVY)

    # 12 cards, 3 x 4
    for i, (title, place, body, _lat, _lon) in enumerate(CARDS):
        col, row = i % 3, i // 3
        x0 = 24 + col * 330
        y0 = 458 + row * 104
        d.rectangle([x0, y0, x0 + 314, y0 + 100], fill=CARD, outline=LINEC)
        draw_text(img, 'B17', x0 + 10, y0 + 6, place, RED)
        tlines = wrap('B17', title, 294, max_lines=2)
        draw_lines(img, 'B17', x0 + 10, y0 + 24, tlines, INK, 20)
        by = y0 + 24 + len(tlines) * 20 + 4
        max_body = 3 if len(tlines) == 1 else 2
        draw_lines(img, 'R13', x0 + 10, by,
                   wrap('R13', body, 294, max_lines=max_body), INK, 15)

    # briefs band (navy), 3 x 3
    d.rectangle([0, 882, W, 978], fill=NAVY)
    for i, b in enumerate(BRIEFS):
        col, row = i % 3, i // 3
        x0 = 24 + col * 330
        y0 = 888 + row * 28
        draw_lines(img, 'R13', x0, y0,
                   wrap('R13', b, 314, max_lines=2), WHITE, 13)

    # sport footer
    draw_text(img, 'B17', 24, 992, 'SPORT', RED)
    sx = 24 + text_width('B17', 'SPORT') + 10
    draw_text(img, 'R17', sx, 990, SPORT, INK)
    fw = text_width('R13', 'THE WORLD - 25 NOVEMBER 2026')
    draw_text(img, 'R13', 1000 - fw, 994, 'THE WORLD - 25 NOVEMBER 2026', GREY)
    return img


def main():
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR') or '.'
    out = os.path.join(out_dir, 'entry.png')
    img = build()
    img.save(out, optimize=True)


if __name__ == '__main__':
    main()
