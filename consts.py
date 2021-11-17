import bz2

DBG                     = 1
PROJECTS_FOLDER         = "User_Projects"
PROJECT_PREFIX          = "project_"
ALLOWED_CHARS           = [ chr( ord( 'a' ) + i ) for i in range( 26 ) ] + [ chr( ord( 'A' ) + i ) for i in range( 26 ) ] + [ str( i ) for i in range( 10 ) ] + [ "_" ]
CYAN                    = (0, 0.7, 1, 1)
NEW_PROJECT_FORM        = 1
EDIT_PROJECT_FORM       = 2
NEW_BOARD_FORM          = 3
EDIT_BOARD_FORM         = 4
NEW_CARD_FORM           = 5
NO_TAG_SELECTED         = "-- None --"
VERTICAL_MOUSE_MOTION   = "<MouseWheel>"
DOUBLE_LEFT_CLICK       = "<Double-Button-1>"

def dbg( msg_priority, *args, **kwargs ):
    if msg_priority < DBG:
        print( *args, **kwargs )

def compress( _data ):
    bz2.compress( _data )

def validate_name( _name ):
    for _char in _name:
        if _char not in ALLOWED_CHARS:
            print( "Input name:", _name, "is not valid" )
            return False
    return True
