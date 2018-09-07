from colorsys import rgb_to_hls, hls_to_rgb

"""
USEFUL FUNCTIONS
"""
def darken(color, amount):
    # Get the 3 hex values from the string
    hex_vals = [color[1:][i: i+2] for i in range(0, 5, 2)]
    # Convert them in RGB as normalized floats
    rgb_vals = [int(x, 16)/255 for x in hex_vals]
    # Convert to HLS
    hls_vals = rgb_to_hls(*rgb_vals)
    # Change the lightness and convert back to RBG
    new_vals = hls_to_rgb(hls_vals[0],
        max(0, 1 - amount*(1 - hls_vals[1])), hls_vals[2])
    # Convert back to hex values and return
    return '#' + ''.join([hex(int(255*x))[2:].zfill(2) for x in new_vals])

def lighten(color, amount):
    return darken(color, 1/amount)

""" CONSTANTS """
# Background color of app
BG_COLOR = '#292929'
# Background color of Song Tables
STBG_COLOR = '#06603d'
# Widget color
W_COLOR = '#84bd00'
# White (green) color
WHITE = '#e1f0e1'
# Black (green) color
BLACK = '#0a330a'
# Font for titles
TITLE_FONT = 'Georgia'
# Non-black font color used
FONT_COLOR = '#888888'

""" GLOBALS """
# Every QPushButton
BUTTON_STYLE = '''
QPushButton {{
    background-color: {w_color};
    font-weight: 800;
    font-size: 16px;
    color: {black};
    border: 1px solid {bg_color};
    border-radius: 3px;
    padding: 5px 10px 5px 10px;
}}
QPushButton:pressed {{
    border-style: inset;
    background-color: {pressed_color};
}}
'''.format(
    w_color=W_COLOR,
    black=BLACK,
    bg_color=BG_COLOR,
    pressed_color=darken(W_COLOR, 1.5)
)

# Every QComboBox
COMBOBOX_STYLE = '''
QComboBox {{
    background-color: {w_color};
    selection-background-color: {select_color};
    selection-color: #aaaaaa;
    font-weight: 800;
    color: {black};
}}
QComboBox QAbstractItemView {{
    background-color: {item_color};
    selection-background-color: {select_bg_color};
    selection-color: {select_color};
    color: {black};
}}
'''.format(
    w_color=W_COLOR,
    item_color=WHITE,
    select_bg_color=lighten(W_COLOR, 2),
    select_color=darken(BLACK, 2),    
    black=BLACK#darken(BLACK, 2)
)

# Every LineEdit
LINEEDIT_STYLE = '''
QLineEdit {{
    background-color: {w_color};
    color: {black};
}}
'''.format(
    w_color=W_COLOR,
    black=darken(BLACK, 2)
)

# Every QTableWidget (including SongDataTableWidget objects)
TABLEWIDGET_STYLE = '''
QTableWidget {{
    background-color: {stbg_color};
    selection-background-color: {select_color};
    selection-color: {white};
}}
QHeaderView::section {{
    background-color: #dddddd;
    font-weight: 600;
    font-size: 17px;
}}
QHeaderView::section:checked {{
    background-color: #dddddd;
}}
QTableWidget QTableCornerButton::section {{
    background-color: #dddddd;
}}
'''.format(
    stbg_color=STBG_COLOR,
    select_color=darken(STBG_COLOR, 2),
    white=WHITE
)


""" TAB-SPECIFIC """
# Advanced Search QGroupBoxes for Filter Playlists tab
AdvFilterPlaylistStyle = '''
QGroupBox::title {{
    color: {white};
    padding: 0 8px 6px 4px;
    left: 15px;
}}
QCheckBox {{
    color: {white};
}}
{button}
{combobox}
{tablewidget}
{lineedit}
'''.format(
    white=WHITE,
    button=BUTTON_STYLE,
    combobox=COMBOBOX_STYLE,
    tablewidget=TABLEWIDGET_STYLE,
    lineedit=LINEEDIT_STYLE
)

# Simple Search for Filter Playlist tab
SimpleFilterPlaylistStyle = '''
QLabel {{
    color: {white};
}}
{button}
{combobox}
{tablewidget}
'''.format(
    white=WHITE,
    button=BUTTON_STYLE,
    combobox=COMBOBOX_STYLE,
    tablewidget=TABLEWIDGET_STYLE
)

# Playlist Songs tab
PlaylistSongsStyle = '''
{button}
{combobox}
{tablewidget}
'''.format(
    button=BUTTON_STYLE,
    combobox=COMBOBOX_STYLE,
    tablewidget=TABLEWIDGET_STYLE
)

# Queue Maker tab
QueueMakerStyle = '''
{button}
{tablewidget}
'''.format(
    button=BUTTON_STYLE,
    tablewidget=TABLEWIDGET_STYLE
)

# Current Queue tab
CurrentQueueStyle = '''
{tablewidget}
'''.format(
    tablewidget=TABLEWIDGET_STYLE
)

# Tab bar/widgets
TabStyle = '''
QTabWidget::pane {{
    border-top: 3px solid #888888;
}}
QTabWidget::tab-bar {{
        left: 7px;
}}
QTabWidget > QWidget {{
    background-color: {bg_color};
    border-radius: 4px;
}}
QTabBar::tab {{
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 4px;
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
}}
QTabBar::tab::selected {{
    background: #aaaaaa;
}}
'''.format(
    bg_color=BG_COLOR,
    font_color=FONT_COLOR
)

# Login Popup
LoginStyle = '''
QDialog {{
    background-color: {bg_color};
}}
QLabel {{
    font-size: 25px;
    font-family: {title_font};
    font-weight: 300;
    color: {font_color}
}}
QLineEdit {{
    background-color: #bebebe;
    border-radius: 4px;
    font-size: 15px;
    color: {black};
}}
{button}
'''.format(
    bg_color=BG_COLOR,
    title_font=TITLE_FONT,
    font_color=FONT_COLOR,
    button=BUTTON_STYLE,
    black=darken(BLACK, 2)
)

NewPlaylistStyle = '''
QDialog {{
    background-color: {bg_color};
}}
QLabel {{
    font-size: 25px;
    font-family: {title_font};
    font-weight: 300;
    color: {font_color};
}}
{lineedit}
{button}
'''.format(
    bg_color=BG_COLOR,
    title_font=TITLE_FONT,
    font_color=FONT_COLOR,
    lineedit=LINEEDIT_STYLE,
    button=BUTTON_STYLE
)
