import matplotlib.pyplot as plt
import base64
import io

def make_barplot(title, xtitle, names, values, figsize=(8, 2)):
    fig = plt.figure(figsize=figsize)
    plt.barh(range(len(names)), values, align='center', color="green")
    plt.yticks(range(len(names)), names)
    plt.xlabel(xtitle)
    plt.ylim(-1, len(names))
    plt.axes().xaxis.grid(True)
    plt.title(title)

    return fig

def make_pie(title, names, values, colors=None):
    fig = plt.figure(figsize=(2, 2))
    plt.pie(values, labels=names, shadow=True, colors=colors)
    return fig

def make_png(fig):
    f = io.BytesIO()
    fig.savefig(f, format="png", transparent=True, bbox_inches="tight")
    f.seek(0)
    return f.read()

def make_web_png(fig):
    png = make_png(fig)
    return "data:image/png;base64," + base64.b64encode(png).decode('ascii')
