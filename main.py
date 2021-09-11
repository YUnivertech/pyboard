from tkinter.constants import LAST
import gui_comp as gui

from tkinter import ttk
import tkinter as tk
import db_manager as dbmngr

manager     = dbmngr.DBManager()
active_prj  = ''
active_brd  = None

close_prmpt = False
def connect( _name, _host, _pass ):
    global close_prmpt, prompt
    manager.connect( _name, _host, _pass )
    close_prmpt = True

def tree_click( _event ):

    global active_prj, active_brd

    iid     = tree_v.selection()[0]
    name    = iid[1:]

    if iid[0] == 'p':
        print( "SWITCHING PROJECT TO {}".format( name ) )
        manager.use_db( name )
        active_prj              = name
        active_brd              = None

        # enable buttons for manipulating active project
        del_prj_but["state"]    = tk.NORMAL
        edt_prj_but["state"]    = tk.NORMAL
        new_brd_but["state"]    = tk.NORMAL

        # disable buttons for manipulating active board
        del_brd_but["state"]    = tk.DISABLED
        edt_brd_but["state"]    = tk.DISABLED

    elif iid[0] == 'b':
        print( "SWITCHING BOARD TO {}".format( manager.get_board_name( int( name ) ) ) )
        active_brd              = name

        # enable buttons for manipulating active board
        del_brd_but["state"]    = tk.NORMAL
        edt_brd_but["state"]    = tk.NORMAL

def add_prj():

    global active_prj

    name = input("NAME: ")
    desc = input("DESC: ")

    # add project for manager
    manager.add_project( name, desc )

    # update widget
    tree_v.insert( '', 'end', iid = 'p' + name, text = name )

    # change active project to current project
    active_prj              = name

    # enable buttons for manipulating active project
    del_prj_but["state"]    = tk.NORMAL
    edt_prj_but["state"]    = tk.NORMAL
    new_brd_but["state"]    = tk.NORMAL

def del_prj():

    global active_prj, active_brd

    # delete project for manager
    manager.delete_current_project()

    # update widget
    tree_v.delete( 'p' + active_prj )

    # remove active project and board
    active_prj              = ''
    active_brd              = None

    # disable buttons for manipulating active project
    del_prj_but["state"]    = tk.DISABLED
    edt_prj_but["state"]    = tk.DISABLED

    # disable buttons for manipulating active board
    new_brd_but["state"]    = tk.DISABLED
    del_brd_but["state"]    = tk.DISABLED
    edt_brd_but["state"]    = tk.DISABLED

def edt_prj():

    global active_prj
    print( "CURRENT DESC: {}".format( manager.get_project_info() ) )
    desc = input("DESC: ")

    # change description for manager
    manager.update_project_info( desc )

def add_brd():

    global active_brd

    name    = input("NAME: ")
    desc    = input("DESC: ")
    iid     = manager.get_next_board_uid()

    # add board for manager
    manager.add_board( iid, name, desc )

    # update widget
    tree_v.insert( 'p' + active_prj, 'end', iid = 'b' + str( iid ), text = name )

    # change active board to current board
    active_brd              = iid

    # enable buttons for manipulating active board
    del_brd_but["state"]    = tk.NORMAL
    edt_brd_but["state"]    = tk.NORMAL

def del_brd():

    global active_brd

    # delete board for manager
    manager.delete_board( active_brd )

    # update widget
    tree_v.delete( 'b' + str( active_brd ) )

    # disable active board
    active_brd              = None

    # disable buttons for manipulating active board
    del_brd_but["state"]    = tk.DISABLED
    edt_brd_but["state"]    = tk.DISABLED

def edt_brd():

    global active_brd

    print( "CURRENT NAME: {}".format( manager.get_board_name( active_brd ) ) )
    print( "CURRENT DESC: {}".format( manager.get_board_description( active_brd ) ) )

    name = input("NAME: ")
    desc = input("DESC: ")

    # update board info for manager
    manager.update_board( active_brd, name, desc )

    # update widget
    tree_v.delete( 'b' + active_brd )
    tree_v.insert( 'p' + active_prj, 'end', iid = 'b' + str( active_brd ), text = name )

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

# ! ONLY FOR SQLITE BRANCH
conn_btn.invoke()

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
root                    = gui.get_window( (200, 200), "Pyboard" )

# widgets for layouting main window into sections
up_frme                 = tk.Frame( root )
lt_frme                 = tk.Frame( root )
mn_frme                 = tk.Frame( root  )

# buttons for managing projects
new_prj_but             = tk.Button( up_frme, text = "new project", command = add_prj )
del_prj_but             = tk.Button( up_frme, text = "del project", command = del_prj )
edt_prj_but             = tk.Button( up_frme, text = "edit project", command = edt_prj )

# buttons for managing boards
new_brd_but             = tk.Button( up_frme, text = "new board", command = add_brd )
del_brd_but             = tk.Button( up_frme, text = "del board", command = del_brd )
edt_brd_but             = tk.Button( up_frme, text = "edit board", command = edt_brd )

# disable buttons at start
del_prj_but["state"]    = tk.DISABLED
edt_prj_but["state"]    = tk.DISABLED

new_brd_but["state"]    = tk.DISABLED
del_brd_but["state"]    = tk.DISABLED
edt_brd_but["state"]    = tk.DISABLED

# widget for viewing projects and boards
tree_v                  = ttk.Treeview( lt_frme, selectmode = 'browse' )
tree_v.column( "#0", anchor = tk.W )
tree_v.bind( "<Double-1>", tree_click )

# insert all projects and views
for prj in manager.get_all_projects():
    tree_v.insert( '', 'end', iid = 'p' + prj, text = prj )
    manager.use_db( prj )
    for brd in manager.get_all_boards():
        tree_v.insert( 'p' + prj, 'end', iid = 'b' + str( brd[0] ), text = brd[1] )

# place widgets
new_prj_but.grid( row = 0, column = 0 )
del_prj_but.grid( row = 0, column = 1 )
edt_prj_but.grid( row = 0, column = 2 )

new_brd_but.grid( row = 0, column = 3 )
del_brd_but.grid( row = 0, column = 4 )
edt_brd_but.grid( row = 0, column = 5 )

tree_v.pack( side = 'right' )

up_frme.grid( row = 0, column = 0, columnspan = 2, sticky = "WNE" )
lt_frme.grid( row = 1, column = 0, sticky = "SW" )
mn_frme.grid( row = 1, column = 1, sticky = "SE" )

# manual implemented main loop
while 1:
    try:
        root.update_idletasks()
        root.update()
    except Exception as e:
        print(e)
        break

manager.stop()

# for getting projs -> get_project_names is API
# for creating projs -> add_project
# for editing proj -> update_project_info
# for deleting proj -> delete_current_project

# for getting board -> get_all_boards
# for creating board -> add_board
# for editing board -> 152 - 166 come there in dbmanager (got it)
# for deleting board -> delete_board (takes the UID NOT THE name)
# you need to do db.get_next_board_uid