import gui_comp as gui

import tkinter as tk
import db_manager as dbmngr

manager     = dbmngr.DBManager()

close_prmpt = False
def connect( _name, _host, _pass ):
    global close_prmpt, prompt
    manager.connect( _name, _host, _pass )
    close_prmpt = True

# Create initial prompt to enter server credentials
prompt      = gui.get_window( (200, 200), "Pyboard" )

host_entry  = gui.get_entry( prompt, "127.0.0.1" )
name_entry  = gui.get_entry( prompt )
pass_entry  = gui.get_entry( prompt )

conn_btn    = tk.Button( master = prompt,
                        text = "Connect",
                        command = lambda : connect( name_entry.get(), host_entry.get(), pass_entry.get() ) )

host_entry.grid( row = 0, column = 0 )
name_entry.grid( row = 1, column = 0 )
pass_entry.grid( row = 2, column = 0 )

conn_btn.grid( row = 3, column = 0 )

# manual implemented main loop
while not close_prmpt:
    try:
        prompt.update_idletasks()
        prompt.update()
    except Exception as e:
        print(e)
        break
prompt.destroy()

# start of main application
root        = gui.get_window( (200, 200), "Pyboard" )

# manual implemented main loop
while 1:
    try:
        root.update_idletasks()
        root.update()
    except Exception as e:
        print(e)
        break

manager.stop()
