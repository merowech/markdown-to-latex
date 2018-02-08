import sys
import os
import re


fig_count = 0


def checkLine(line):

    line = line.replace("\\", "\\\\")
    if line[-2:] == "  ":
        line = line[-2:] + "\\newline"

    global fig_count

    m = re.search("^# (.*)", line)
    if m:
        return "\section{" + m.group(1) + "}\n"

    m = re.search("^## (.*)", line)
    if m:
        return "\subsection{" + m.group(1) + "}\n"

    m = re.search("^### (.*)", line)
    if m:
        return "\subsubsection{" + m.group(1) + "}\n"

    m = re.search("!\[(.*?)\]\((.*?)\)(\[(.*?)\]\((.*?)\))?", line)
    if m:
        img_path = m.group(2)
        caption = m.group(1)
        if m.group(3):
            caption += " - \href{" + m.group(5) + "}{" + m.group(4) + "}"
        out = """
\\begin{{figure}}[ht]
    \\centering
    \\includegraphics[width=\\maxwidth{{\\linewidth}}]{{{}}}
    \\caption{{{}}}
    \\label{{{}}}
\\end{{figure}}\n
""".format(img_path, caption, "fig" + str(fig_count))
        fig_count += 1
        return out

    m = re.search("\[(.*)\]\((.*)\)(.*)", line)
    if m:
        return "\href{" + m.group(2) + "}{" + m.group(1) + "}\n" + m.group(3)
        + "\n"

    return line


def readMetaFile(path):
    ret = {}

    with open(path, "r") as f:
        content = f.read()

        idx = content.find("# outline")
        if idx > -1:
            idx_b = idx + len("# outline")
            idx_e = content.find("# ", idx_b)
            if idx_e == -1:
                idx_e = len(content)

            substring = content[idx_b:idx_e]

            files = []
            for sub in substring.split("\n"):
                if sub:
                    files.append(sub)

            ret["files"] = files

        idx = content.find("# reference")
        if idx > -1:
            idx_b = idx + len("# reference")
            idx_e = content.find("# ", idx_b)
            if idx_e == -1:
                idx_e = len(content)

            substring = content[idx_b:idx_e]

            ret["reference"] = substring

        idx = content.find("# abstract")
        if idx > -1:
            idx_b = idx + len("# abstract")
            idx_e = content.find("# ", idx_b)
            if idx_e == -1:
                idx_e = len(content)

            substring = content[idx_b:idx_e]

            ret["abstract"] = substring

        idx = content.find("# metadata")
        if idx > -1:
            idx_b = idx + len("# metadata")
            idx_e = content.find("# ", idx_b)
            if idx_e == -1:
                idx_e = len(content)

            substring = content[idx_b:idx_e]
            lines = substring.split("\n")

            meta = {}
            for line in lines:
                if line == "":
                    continue
                meta_lines = line.split("=")
                meta[meta_lines[0].rstrip()] = meta_lines[1].lstrip()

            ret["meta"] = meta

    return ret


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

        meta_data = {}
        if "meta.md" in files:
            meta_data = readMetaFile(os.path.join(path, "meta.md"))

            if "files" in meta_data:
                files = meta_data["files"]

        # loop through files
        for f in files:
            with open(os.path.join(path, f)) as fd:
                lines = fd.readlines()

                for line in lines:
                    output += checkLine(line)
            output += "\n"

        # check for template
        if len(sys.argv) > 2:
            if sys.argv[2] == "lncs":
                with open("templates/lncs.tex", "r") as f:
                    content = f.read()
                    content = content.replace("CONTENT", output)

                    if "reference" in meta_data:
                        content = content.replace("BIBLIOGRAPHY", meta_data["reference"])

                    if "abstract" in meta_data:
                        content = content.replace("ABSTRACT", meta_data["abstract"])

                    if "meta" in meta_data:
                        for key in meta_data["meta"]:
                            content = content.replace(key, meta_data["meta"][key])

                    with open(os.path.join(path, "converted.tex"), "w+") as fd:
                        fd.write(content)

                        print("Finished writing")
            else:
                print(sys.argv[2])
        else:
            with open("templates/standard.tex", "r") as f:
                content = f.read()
                content = content.replace("CONTENT", output)

                with open(os.path.join(path, "converted.tex"), "w+") as fd:
                    fd.write(content)

                    print("Finished writing")
