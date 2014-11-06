import matplotlib.pyplot as plt
import base64
import io

import numpy as np

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

def make_polar_chart(title, gamma, p, fontsize0=12):
    fig = plt.figure(figsize=(6, 6))
    str_degree = u'\xb0'
    line_style ='k:'
    line_width = 0.5
    radial_label = r'$\nu$'
    axial_label = 'p'

    max_p = max(p)
    # Roundup to nearest multiple of 60
    outer_circle = float(((int(max_p) - 1) // 60 + 1) * 60)
    """
    if max_p > 0 and max_p <= 60:
        outer_circle = 60.0
    elif (max_p <= 120):
        outer_circle = 120.0
    elif (max_p <= 180):
        outer_circle = 180.0
    elif (max_p <= 240):
        outer_circle = 240.0
    elif (max_p <= 300):
        outer_circle = 300.0
    else:
        outer_circle = 360.0
    """

    n_phi = 60
    phi = np.linspace(0.0, 2 * np.pi,n_phi)

    for r in [ 1, 1/3, 2/3 ]:
        x = r * outer_circle * np.sin(phi)
        y = r *outer_circle * np.cos(phi)
        plt.plot(x, y, 'k', lw=1)

    '''-------- labels of outher circle --------------'''
    n_phi_lab = 13
    phi_lab = np.linspace(0.0, 2 * np.pi, n_phi_lab)
    r_lab = outer_circle*1.1
    x = r_lab*np.sin(phi_lab)-0.07 * outer_circle
    y = r_lab*np.cos(phi_lab)

    for i in range(n_phi_lab - 1):
        str_label = str(int(np.round(phi_lab[i] / np.pi * 180))) + str_degree
        plt.text(x[i], y[i], str_label, fontsize=fontsize0)

    ''' name of radial axes '''
    x_name = 1.1 * outer_circle * np.sin(np.mean(phi_lab[-2:]))
    y_name = 1.15 * outer_circle * np.cos(np.mean(phi_lab[-2:]))
    plt.text(x_name, y_name, axial_label, fontsize=fontsize0 + 2)

    ''' -------- radial lines --------------------- '''
    phi_radial_lines = np.linspace(0, 2*np.pi, 12, endpoint=False)
    for i in range(phi_radial_lines.shape[0]):
        x1 = outer_circle * np.sin(phi_radial_lines[i])
        x = np.array([0.025*x1, x1])
        y1 = outer_circle * np.cos(phi_radial_lines[i])
        y = np.array([0.025 * y1, y1])
        plt.plot(x, y, line_style, lw=line_width)

    ''' --------- radial lines labels -------------------'''
    nr_radlab = 3
    delr_radlab = outer_circle / nr_radlab
    r_radlab = np.linspace(delr_radlab, outer_circle, nr_radlab)
    phiRadLab = 85.0*np.pi/180.0-0.1
    for i in range(r_radlab.shape[0]):
        x = r_radlab[i] * np.sin(phiRadLab)
        y = r_radlab[i] * np.cos(phiRadLab)
        strLabel = str(int(np.round(r_radlab[i]))) + str_degree
        plt.text(x, y, strLabel, fontsize=fontsize0)

    x_name = 1.4 * r_radlab[i] * np.sin(phiRadLab)
    y_name = 1.3 * r_radlab[i] * np.cos(phiRadLab)
    plt.text(x_name, y_name, radial_label, fontsize=fontsize0 + 3)
    x_data = p * np.sin(gamma)
    y_data = p * np.cos(gamma)
    plt.plot(x_data, y_data, 'r.', markersize=5, color="green")
    plt.axis('equal')
    plt.axis('off')
    return fig

def make_png(fig):
    f = io.BytesIO()
    fig.savefig(f, format="png", transparent=True, bbox_inches="tight")
    f.seek(0)
    return f.read()

def make_web_png(fig):
    png = make_png(fig)
    return "data:image/png;base64," + base64.b64encode(png).decode('ascii')
