import tkinter as tk
from tkinter import ttk

# create main window
root       = tk.Tk()
root.minsize( 200, 200 )

# Widgets for left and top explorers
left_frame = tk.Frame( master = root )
top_frame  = tk.Frame( master = root )

# Widgets for text entries in left explorer
host_entry = tk.Entry( master = left_frame )
host_entry.insert( 0, "127.0.0.1" )

user_entry = tk.Entry( master = left_frame, text = "Your Name" )
user_entry.insert( 0, "Enter Name" )

pass_entry = tk.Entry( master = left_frame, text = "Your Pass" )
pass_entry.insert( 0, "Enter Pass" )

con_button = tk.Button( master = left_frame, text = "Connect" )

# Widgets for project management
new_prj_but = tk.Button( master = left_frame, text = "New Project" )
del_prj_but = tk.Button( master = left_frame, text = "Delete Project" )
sel_prj_but = tk.Button( master = left_frame, text = "Select Project" )

# Widgets for board management
new_brd_but = tk.Button( master = left_frame, text = 'New Board')
del_brd_but = tk.Button( master = left_frame, text = "Delete Board")
sel_brd_but = tk.Button( master = left_frame, text = "Select Board")

# Widgets for text entries in top explorer
prj_select = tk.Entry( master = top_frame )
prj_select.insert( 0, "Enter Project" )

brd_select = tk.Entry( master = top_frame, text = "Board select" )
brd_select.insert( 0, " Enter Board" )

sel_button = tk.Button( master = top_frame, text = "Select" )

# Place widgets into top explorer
host_entry.grid( row = 0, column = 0 )
user_entry.grid( row = 1, column = 0 )
pass_entry.grid( row = 2, column = 0 )
con_button.grid( row = 3, column = 0 )

# Place Project management widgets
new_prj_but.grid( row = 4, column = 0 )
del_prj_but.grid( row = 4, column = 1 )
sel_prj_but.grid( row = 5, column = 0 )

# Place Board management widgets
new_prj_but.grid( row = 4, column = 0 )
del_prj_but.grid( row = 4, column = 1 )
sel_prj_but.grid( row = 5, column = 0 )

new_brd_but.grid( row = 6, column = 0 )
del_brd_but.grid( row = 6, column = 1 )
sel_brd_but.grid( row = 7, column = 0 )

# Place widgets into left explorer
prj_select.grid( row = 0, column = 0 )
brd_select.grid( row = 0, column = 1 )
sel_button.grid( row = 0, column = 2 )

# Place explorers
left_frame.grid( row = 0, column = 0, sticky = tk.W )
top_frame.grid( row = 0, column = 1, sticky = tk.N )

# manual implemented main loop
while 1:
    try:
        root.update_idletasks()
        root.update()
    except Exception as e:
        print(e)
        break

# automatic main loop
# root.mainloop()
