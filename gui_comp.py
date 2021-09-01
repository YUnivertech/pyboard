import tkinter as tk

def get_window( _minsize = (1, 1), _title = "Pyboard", **kwargs ):
    res = tk.Tk( **kwargs )
    res.minsize( *_minsize )
    res.title( _title )

    return res

def get_entry( _master, _txt = "" ):
    res = tk.Entry( master = _master )
    res.insert( 0, _txt )

    return res

def get_but( _master, _com, _txt = ""):
    pass
