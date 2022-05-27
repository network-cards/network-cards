##!/usr/bin/env python
# -*- coding: utf-8 -*-

# format_helpers.py
# Jim Bagrow
# Last Modified: 2022-04-19

import re

from pandas.io.formats.format import save_to_buffer


def tex_escape(text):
    """
        :param text: a plain text message
        :return: the message escaped to appear correctly in LaTeX
    """
    # https://stackoverflow.com/a/25875504
    conv = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
        '<': r'\textless{}',
        '>': r'\textgreater{}',
    }
    if isinstance(text, (int, float)):
        return text#"{:g}".format(text)
    text = str(text)
    regex = re.compile('|'.join(re.escape(str(key)) for key in sorted(conv.keys(), key = lambda item: - len(item))))
    return regex.sub(lambda match: conv[match.group()], text)



def draw_frame_border(
    workbook, worksheet, first_row, first_col, rows_count, cols_count, thickness=1
):
    # https://stackoverflow.com/a/60476284

    if cols_count == 1 and rows_count == 1:
        # whole cell
        worksheet.conditional_format(
            first_row,
            first_col,
            first_row,
            first_col,
            {
                "type": "formula",
                "criteria": "True",
                "format": workbook.add_format(
                    {
                        "top": thickness,
                        "bottom": thickness,
                        "left": thickness,
                        "right": thickness,
                    }
                ),
            },
        )
    elif rows_count == 1:
        # left cap
        worksheet.conditional_format(
            first_row,
            first_col,
            first_row,
            first_col,
            {
                "type": "formula",
                "criteria": "True",
                "format": workbook.add_format(
                    {"top": thickness, "left": thickness, "bottom": thickness}
                ),
            },
        )
        # top and bottom sides
        worksheet.conditional_format(
            first_row,
            first_col + 1,
            first_row,
            first_col + cols_count - 2,
            {
                "type": "formula",
                "criteria": "True",
                "format": workbook.add_format({"top": thickness, "bottom": thickness}),
            },
        )

        # right cap
        worksheet.conditional_format(
            first_row,
            first_col + cols_count - 1,
            first_row,
            first_col + cols_count - 1,
            {
                "type": "formula",
                "criteria": "True",
                "format": workbook.add_format(
                    {"top": thickness, "right": thickness, "bottom": thickness}
                ),
            },
        )

    elif cols_count == 1:
        # top cap
        worksheet.conditional_format(
            first_row,
            first_col,
            first_row,
            first_col,
            {
                "type": "formula",
                "criteria": "True",
                "format": workbook.add_format(
                    {"top": thickness, "left": thickness, "right": thickness}
                ),
            },
        )

        # left and right sides
        worksheet.conditional_format(
            first_row + 1,
            first_col,
            first_row + rows_count - 2,
            first_col,
            {
                "type": "formula",
                "criteria": "True",
                "format": workbook.add_format({"left": thickness, "right": thickness}),
            },
        )

        # bottom cap
        worksheet.conditional_format(
            first_row + rows_count - 1,
            first_col,
            first_row + rows_count - 1,
            first_col,
            {
                "type": "formula",
                "criteria": "True",
                "format": workbook.add_format(
                    {"bottom": thickness, "left": thickness, "right": thickness}
                ),
            },
        )

    else:
        # top left corner
        worksheet.conditional_format(
            first_row,
            first_col,
            first_row,
            first_col,
            {
                "type": "formula",
                "criteria": "True",
                "format": workbook.add_format({"top": thickness, "left": thickness}),
            },
        )

        # top right corner
        worksheet.conditional_format(
            first_row,
            first_col + cols_count - 1,
            first_row,
            first_col + cols_count - 1,
            {
                "type": "formula",
                "criteria": "True",
                "format": workbook.add_format({"top": thickness, "right": thickness}),
            },
        )

        # bottom left corner
        worksheet.conditional_format(
            first_row + rows_count - 1,
            first_col,
            first_row + rows_count - 1,
            first_col,
            {
                "type": "formula",
                "criteria": "True",
                "format": workbook.add_format({"bottom": thickness, "left": thickness}),
            },
        )

        # bottom right corner
        worksheet.conditional_format(
            first_row + rows_count - 1,
            first_col + cols_count - 1,
            first_row + rows_count - 1,
            first_col + cols_count - 1,
            {
                "type": "formula",
                "criteria": "True",
                "format": workbook.add_format(
                    {"bottom": thickness, "right": thickness}
                ),
            },
        )

        # top
        worksheet.conditional_format(
            first_row,
            first_col + 1,
            first_row,
            first_col + cols_count - 2,
            {
                "type": "formula",
                "criteria": "True",
                "format": workbook.add_format({"top": thickness}),
            },
        )

        # left
        worksheet.conditional_format(
            first_row + 1,
            first_col,
            first_row + rows_count - 2,
            first_col,
            {
                "type": "formula",
                "criteria": "True",
                "format": workbook.add_format({"left": thickness}),
            },
        )

        # bottom
        worksheet.conditional_format(
            first_row + rows_count - 1,
            first_col + 1,
            first_row + rows_count - 1,
            first_col + cols_count - 2,
            {
                "type": "formula",
                "criteria": "True",
                "format": workbook.add_format({"bottom": thickness}),
            },
        )

        # right
        worksheet.conditional_format(
            first_row + 1,
            first_col + cols_count - 1,
            first_row + rows_count - 2,
            first_col + cols_count - 1,
            {
                "type": "formula",
                "criteria": "True",
                "format": workbook.add_format({"right": thickness}),
            },
        )
