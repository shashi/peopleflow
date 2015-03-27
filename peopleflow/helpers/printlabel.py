import os, time, tempfile, re

from code128.format import code128_format

def tmpfile(ext):
    f = tempfile.NamedTemporaryFile(suffix='.' + ext, delete=False)
    fname = f.name
    f.close()
    return fname


def printmodel(p):
    return dict(
            name=p.name,
            badgetype="SPEAKER" if p.speaker else "", # Crew also should go here..
            twitter="@" + p.twitter,
            job=p.job,
            barcode=p.public+p.secret,
            company=p.company)


def barcode_svg(data, size, offset):
    """encodes 'data' in a code128 barcode and returns an SVG graphic as string"""

    width, height = size
    barcode_widths = code128_format(data, 3)
    print barcode_widths
    _width = sum(barcode_widths)
    print _width
    barcode_widths = [(float(w) * width / _width) for w in barcode_widths]
    print barcode_widths
    x = 0

    svg_elements = [ '<g transform="translate(%d, %d)">\n' % offset,
                     '<svg width="%dpx" height="%dpx">' % \
                     (width, height),
                     '    <rect width="%d" height="%d" fill="white"/>' % (width, height) ]
    draw_bar = True
    for width in barcode_widths:
        if draw_bar:
            svg_elements.append('    <rect x="%0.3f" width="%0.3f" height="%0.3f"/>' % \
                                (x, width, height) )
        draw_bar = not draw_bar
        x += width

    svg_elements.append('</svg>')
    svg_elements.append('</g>')

    return "\n".join(svg_elements)

#### This is a configurable function to place the badge.

def makelabel(model, template, output, barcode_size, barcode_offset):
    with open(template, "r") as f:
        tpl = f.read()
    res = tpl
    endtag = re.compile("</svg>\s*$", re.MULTILINE)
    for k in model:
        if k == "barcode":
            res = endtag.sub(barcode_svg(model[k], barcode_size, barcode_offset) + "\n</svg>", res)
            print res
            continue
        res = res.replace("{{" + k + "}}", str(model[k]))
    tmpsvg = tmpfile("svg")
    with open(tmpsvg, "w") as f:
        f.write(res)
    makepdf(tmpsvg, output)
    return output

def makepdf(svg, fname):
    os.system("inkscape -f " + svg + " -A " + fname)

def printfile(printer, fname):
    os.system("lpr -o page-ranges=1 -P %s %s" % (printer, fname))
    time.sleep(2)

def printlabel(participant, mixin, printer, template, barcode_size, barcode_offset, output=tmpfile("pdf")):
    x = printmodel(participant)
    x.update(mixin)
    printfile(printer, makelabel(x, template, output, barcode_size, barcode_offset))

if __name__ == '__main__':
    makelabel(dict(name="Kiran Jonnalagadda",
                   badgetype="SPEAKER",
                   twitter="@jackerhack",
                   job="Founder",
                   barcode="2%6{,dD<@X",
                   company="HasGeek"),
               "badge-template.svg", "test.pdf",
               (300, 75), (25, 325))

