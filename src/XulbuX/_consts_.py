class DEFAULT:

    text_color:str = '#95B5FF'
    color:dict[str,str] = {
        'white':       '#F1F2FF',
        'lightgray':   '#B6B7C0',
        'gray':        '#7B7C8D',
        'darkgray':    '#67686C',
        'black':       '#202125',
        'red':         '#FF606A',
        'coral':       '#FF7069',
        'orange':      '#FF876A',
        'tangerine':   '#FF9962',
        'gold':        '#FFAF60',
        'yellow':      '#FFD260',
        'green':       '#7EE787',
        'teal':        '#50EAAF',
        'cyan':        '#3EE6DE',
        'ice':         '#77EFEF',
        'lightblue':   '#60AAFF',
        'blue':        '#8085FF',
        'lavender':    '#9B7DFF',
        'purple':      '#AD68FF',
        'magenta':     '#C860FF',
        'pink':        '#EE60BB',
        'rose':        '#FF6090',
    }




class CHARS:

    # CODE TO SIGNAL, ALL CHARACTERS ARE ALLOWED
    all =                     '<*allowed>'

    # DIGIT SETS
    digits =                  '0123456789'
    float_digits =            digits + '.'
    hex_digits =              digits + '#abcdefABCDEF'

    # LETTER CATEGORIES
    lowercase =               'abcdefghijklmnopqrstuvwxyz'
    lowercase_extended =      lowercase + 'äëïöüÿàèìòùáéíóúýâêîôûãñõåæç'
    uppercase =               'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    uppercase_extended =      uppercase + 'ÄËÏÖÜÀÈÌÒÙÁÉÍÓÚÝÂÊÎÔÛÃÑÕÅÆÇß'

    # COMBINED LETTER SETS
    letters =                 lowercase + uppercase
    letters_extended =        lowercase_extended + uppercase_extended

    # ASCII sets
    special_ascii =           ' !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    special_ascii_extended =  special_ascii + 'ø£Ø×ƒªº¿®¬½¼¡«»░▒▓│┤©╣║╗╝¢¥┐└┴┬├─┼╚╔╩╦╠═╬¤ðÐı┘┌█▄¦▀µþÞ¯´≡­±‗¾¶§÷¸°¨·¹³²■ '
    standard_ascii =          special_ascii + digits + letters
    full_ascii =              special_ascii_extended + digits + letters_extended




class ANSI:

    global CHAR, START, SEP, END

    CHAR  = char  = '\x1b'
    START = start = '['
    SEP   = sep   = ';'
    END   = end   = 'm'

    def seq(parts:int = 1) -> str:
        """Generate an ANSI sequence with `parts` amount of placeholders."""
        return CHAR + START + SEP.join(['{}' for _ in range(parts)]) + END

    seq_color:str = CHAR + START + '38' + SEP + '2' + SEP + '{}' + SEP + '{}' + SEP + '{}' + END
    seq_bg_color:str = CHAR + START + '48' + SEP + '2' + SEP + '{}' + SEP + '{}' + SEP + '{}' + END

    color_map:list[str] = [
        ########### DEFAULT CONSOLE COLOR NAMES ############
        'black',
        'red',
        'green',
        'yellow',
        'blue',
        'magenta',
        'cyan',
        'white'
    ]

    codes_map:dict[str|tuple[str], int] = {
        ###################### RESETS ######################
        '_':                          0,
        ('_bold','_b'):               22,
        ('_dim','_d'):                22,
        ('_italic','_i'):             23,
        ('_underline','_u'):          24,
        ('_double-underline','_du'):  24,
        ('_inverse','_invert','_in'): 27,
        ('_hidden','_hide','_h'):     28,
        ('_strikethrough','_s'):      29,
        ('_color','_c'):              39,
        ('_background','_bg'):        49,
        ################### TEXT FORMATS ###################
        ('bold','b'):              1,
        ('dim','d'):               2,
        ('italic','i'):            3,
        ('underline','u'):         4,
        ('inverse','invert','in'): 7,
        ('hidden','hide','h'):     8,
        ('strikethrough','s'):     9,
        ('double-underline','du'): 21,
        ############## DEFAULT CONSOLE COLORS ##############
        'black':   30,
        'red':     31,
        'green':   32,
        'yellow':  33,
        'blue':    34,
        'magenta': 35,
        'cyan':    36,
        'white':   37,
        ########## BRIGHT DEFAULT CONSOLE COLORS ###########
        ('bright:black','br:black'):     90,
        ('bright:red','br:red'):         91,
        ('bright:green','br:green'):     92,
        ('bright:yellow','br:yellow'):   93,
        ('bright:blue','br:blue'):       94,
        ('bright:magenta','br:magenta'): 95,
        ('bright:cyan','br:cyan'):       96,
        ('bright:white','br:white'):     97,
        ######## DEFAULT CONSOLE BACKGROUND COLORS #########
        'bg:black':   40,
        'bg:red':     41,
        'bg:green':   42,
        'bg:yellow':  43,
        'bg:blue':    44,
        'bg:magenta': 45,
        'bg:cyan':    46,
        'bg:white':   47,
        ##### BRIGHT DEFAULT CONSOLE BACKGROUND COLORS #####
        ('bg:bright:black','bg:br:black'):     100,
        ('bg:bright:red','bg:br:red'):         101,
        ('bg:bright:green','bg:br:green'):     102,
        ('bg:bright:yellow','bg:br:yellow'):   103,
        ('bg:bright:blue','bg:br:blue'):       104,
        ('bg:bright:magenta','bg:br:magenta'): 105,
        ('bg:bright:cyan','bg:br:cyan'):       106,
        ('bg:bright:white','bg:br:white'):     107,
    }
