import bz2

DBG             = 0
PROJECTS_FOLDER = "User_Projects"
ALLOWED_CHARS   = [ chr( ord( 'a' ) + i ) for i in range( 26 ) ] + [ chr( ord( 'A' ) + i ) for i in range( 26 ) ] + [ str( i ) for i in range( 10 ) ] + [ "_" ]
CYAN            = (0, 0.7, 1, 1)
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
