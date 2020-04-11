def split_script_to_lines(raw_script):
    bracket_depth = 0
    lines = []
    line = ""
    comment_line = False
    for c in raw_script:
        if c == ';':
            comment_line = True
        elif c == '\r':
            pass
        elif c == '\n':
            line += ' '
            if comment_line:
                comment_line = False
                line = ""
        elif not comment_line:
            line += c
            if c == '(':
                bracket_depth += 1
            elif c == ')':
                bracket_depth -= 1
                if bracket_depth == 0:
                    lines.append(line)
                    line = ""
    return lines