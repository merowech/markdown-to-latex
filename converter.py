import sys
import os
import re


fig_count = 0


def checkLine(line):

    global fig_count

    m = re.search("^# (.*)", line)
    if m:
        return "\section{" + m.group(1) + "}"

    m = re.search("^## (.*)", line)
    if m:
        return "\subsection{" + m.group(1) + "}"

    m = re.search("^### (.*)", line)
    if m:
        return "\subsubsection{" + m.group(1) + "}"

    m = re.search("!\[(.*)\]\((.*)\)", line)
    if m:
        out = """
\\begin{{figure}}[ht]
    \\centering
    \\includegraphics{{{}}}
    \\caption{{{}}}
    \\label{{{}}}
\\end{{figure}}
""".format(m.group(2), m.group(1), "fig" + str(fig_count))
        fig_count += 1
        return out

    m = re.search("\[(.*)\]\((.*)\)", line)
    if m:
        return "\href{" + m.group(2) + "}{" + m.group(1) + "}"

    return line


if __name__ == "__main__":

    output = ""

    # check for parameter
    if len(sys.argv) < 2:
        print("Error: needs more arguments")
        exit()

    # check for directory
    path = sys.argv[1]
    if os.path.isdir(path):
        # get files
        files = [f for f in os.listdir(path)
                 if os.path.isfile(os.path.join(path, f))]

        # loop through files
        for f in files:
            with open(os.path.join(path, f)) as fd:
                lines = fd.readlines()

                for line in lines:
                    output += checkLine(line)
            output += "\n"

        # check for template
        if len(sys.argv) > 2:
            print(sys.argv[2])
        else:
            with open("templates/standard.tex", "r") as f:
                content = f.read()
                content = content.replace("CONTENT", output)

                with open(os.path.join(path, "converted.tex"), "w") as fd:
                    fd.write(content)

                    print("Finished writing")
