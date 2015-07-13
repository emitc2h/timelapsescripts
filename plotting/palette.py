"""
==========================================================
Pre-defined colors
----------------------------------------------------------
"""

orange   = '#ee7700'
yellow   = '#ddaa44'
green    = '#00bb00'
blue     = '#0000ff'
skyblue  = '#00a3ff'
indigo   = '#0000bb'
purple   = '#9900dd'
pink     = '#ff00bb'
red      = '#ee0000'
darkred  = '#bb0000'
grey     = '#888888'
white    = '#ffffff'
black    = '#000000'
brown    = '#884400'
beige    = '#ffd075'
peach    = '#ff9f71'
slime    = '#cef0cd'
bandyellow = '#ffff00'
bandgreen  = '#00ff00'

conf_red = '#ff0000'
conf_yellow = '#ffff00'
conf_green = '#0dff00'
conf_orange = '#ffb400'
conf_cyan = '#00ffff'
conf_vermillion = '#ff6100'
conf_blue = '#008cff'


"""
Rainbow spectrum generator
----------------------------------------------------------
"""

## ========================================== ##
def blue_function(x):
    """
    0 to 1 is a color spectrum from blue to red, passing by green.
    This function defines the behavior of the blue component in that range.
    """
    if x < 0.25:
        return 255.0
    if 0.25 <= x < 0.50:
        return 255.0 - 255.0*4*(x-0.25)
    if x >= 0.50:
        return 0.0
    return 0.0

## ========================================== ##
def green_function(x):
    """
    0 to 1 is a color spectrum from blue to red, passing by green.
    This function defines the behavior of the green component in that range.
    """
    if x < 0.25:
        return 255.0*4*(x)
    if 0.25 <= x < 0.75:
        return 255.0
    if x >= 0.75:
        return 255.0 - 255.0*4*(x-0.75)
    return 0.0

## ========================================== ##
def red_function(x):
    """
    0 to 1 is a color spectrum from blue to red, passing by green.
    This function defines the behavior of the red component in that range.
    """
    if x < 0.50:
        return 0.0
    if 0.50 <= x < 0.75:
        return 255.0*4*(x-0.50)
    if x >= 0.75:
        return 255.0
    return 0.0
    
## ========================================== ##
def color_string(r, g, b):
    """
    Transforms a triplet of numbers from 0 to 255 into an hexadecimal string
    to be interpreted by ROOT TColor
    """
    if r > 0.0: r_string = hex( int(r) ).lstrip('0x')
    else:       r_string = '00'
    if len(r_string) == 1:
        r_string = '0%s' % r_string 
    
    if g > 0.0: g_string = hex( int(g) ).lstrip('0x')
    else:       g_string = '00'
    if len(g_string) == 1:
        g_string = '0%s' % g_string 
        
    if b > 0.0: b_string = hex( int(b) ).lstrip('0x')
    else:       b_string = '00'
    if len(b_string) == 1:
        b_string = '0%s' % b_string 

    return '#%s%s%s' % (r_string, g_string, b_string)

## ========================================== ##
def color_spectrum(n):
    """
    Generates a color spectrum from blue to red, passing by green with n steps
    """
    if n > 1:
        step = 1.0 / (n-1)
    else:
        step = 1.0
    color_list = []
    for i in range(n):
        x = i*step
        color = color_string(red_function(x)*0.80,
                             green_function(x)*0.80,
                             blue_function(x)*0.80)
        color_list.append(color)
    return color_list
