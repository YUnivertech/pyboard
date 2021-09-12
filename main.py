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


def add_prj_init():

    global active_prj, active_brd
    global mn_frme, form_frme, form_conf_but, form_canc_but, label1, label2, entry1, entry2, warning_lbl

    # disable buttons for manipulating active project
    new_prj_but["state"]    = tk.DISABLED
    del_prj_but["state"]    = tk.DISABLED
    edt_prj_but["state"]    = tk.DISABLED

    # disable buttons for manipulating active board
    new_brd_but["state"]    = tk.DISABLED
    del_brd_but["state"]    = tk.DISABLED
    edt_brd_but["state"]    = tk.DISABLED

    # display form widget
    form_frme.grid( row = 0, column = 0 )
    form_conf_but.configure( command = add_prj_conf )
    form_canc_but.configure( command = add_prj_canc )

    # forget active board
    active_brd              = None

def add_prj_conf():

    global active_prj, active_brd
    global mn_frme, form_frme, form_conf_but, form_canc_but, label1, label2, entry1, entry2, warning_lbl

    # enable buttons for manipulating active project
    new_prj_but["state"]    = tk.NORMAL
    del_prj_but["state"]    = tk.NORMAL
    edt_prj_but["state"]    = tk.NORMAL
    new_brd_but["state"]    = tk.NORMAL

    # get name and decription as entered by user and clear text boxes
    name                    = entry1.get()
    entry1.insert( 0, '' )
    desc                    = entry2.get()
    entry2.insert( 0, '' )

    try:
        # create project
        manager.add_project( name, desc )

        # insert into widget
        tree_v.insert( '', 'end', iid = 'p' + name, text = name )

        # clear text entry widgets
        entry1.delete( 0, "end" )
        entry2.delete( 0, "end" )

        # clear warning label
        warning_lbl.configure( text = '' )

        # remove form from main frame
        form_frme.grid_forget()

        # update active project
        active_prj          = name

    except:

        warning_lbl.configure( text = "A PROJECT WITH THIS NAME ALREADY EXISTS!" )

        new_prj_but["state"]    = tk.DISABLED
        del_prj_but["state"]    = tk.DISABLED
        edt_prj_but["state"]    = tk.DISABLED
        new_brd_but["state"]    = tk.DISABLED

def add_prj_canc():

    global active_prj, active_brd
    global mn_frme, form_frme, form_conf_but, form_canc_but, label1, label2, entry1, entry2, warning_lbl

    new_prj_but["state"]    = tk.NORMAL

    if active_prj:
        new_prj_but["state"]    = tk.NORMAL
        del_prj_but["state"]    = tk.NORMAL
        edt_prj_but["state"]    = tk.NORMAL
        new_brd_but["state"]    = tk.NORMAL

    # clear text boxes
    entry1.delete( 0, "end" )
    entry2.delete( 0, "end" )

    # clear warning label
    warning_lbl.configure( text = '' )

    # remove form from main frame
    form_frme.grid_forget()


def rem_prj_conf():

    global active_prj, active_brd
    global mn_frme, form_frme, form_conf_but, form_canc_but, label1, label2, entry1, entry2, warning_lbl

    # enable new board creation button
    new_prj_but["state"]    = tk.NORMAL

    # disable all management buttons
    del_prj_but["state"] = tk.DISABLED
    edt_prj_but["state"] = tk.DISABLED

    new_brd_but["state"] = tk.DISABLED
    edt_brd_but["state"] = tk.DISABLED
    del_brd_but["state"] = tk.DISABLED

    # delete project for manager
    manager.delete_current_project()

    # update widget
    tree_v.delete( 'p' + active_prj )

    # remove active project
    active_prj              = ''


def edt_prj_init():

    global active_prj, active_brd
    global mn_frme, form_frme, form_conf_but, form_canc_but, label1, label2, entry1, entry2, warning_lbl

    # disable buttons for manipulating active project
    new_prj_but["state"]    = tk.DISABLED
    del_prj_but["state"]    = tk.DISABLED
    edt_prj_but["state"]    = tk.DISABLED

    # disable buttons for manipulating active board
    new_brd_but["state"]    = tk.DISABLED
    del_brd_but["state"]    = tk.DISABLED
    edt_brd_but["state"]    = tk.DISABLED

    # display form widget
    form_frme.grid( row = 0, column = 0 )
    form_conf_but.configure( command = edt_prj_conf )
    form_canc_but.configure( command = edt_prj_canc )

    # set default to current name and description
    entry1.insert( 0, active_prj )
    entry2.insert( 0, manager.get_project_info() )
    entry1.config( state = 'disabled' )

    # forget active board
    active_brd              = None

def edt_prj_conf():

    global active_prj, active_brd
    global mn_frme, form_frme, form_conf_but, form_canc_but, label1, label2, entry1, entry2, warning_lbl

    # enable buttons for manipulating active project
    new_prj_but["state"]    = tk.NORMAL
    del_prj_but["state"]    = tk.NORMAL
    edt_prj_but["state"]    = tk.NORMAL
    new_brd_but["state"]    = tk.NORMAL

    # update the description
    manager.update_project_info( entry2.get() )

    # clear entries
    entry1.config( state = 'normal' )
    entry1.delete( 0, 'end' )
    entry2.delete( 0, 'end' )

    # remove form
    form_frme.grid_forget()

def edt_prj_canc():

    global active_prj, active_brd
    global mn_frme, form_frme, form_conf_but, form_canc_but, label1, label2, entry1, entry2, warning_lbl

    # enable buttons for manipulating active project
    new_prj_but["state"]    = tk.NORMAL
    del_prj_but["state"]    = tk.NORMAL
    edt_prj_but["state"]    = tk.NORMAL
    new_brd_but["state"]    = tk.NORMAL

    # clear entries
    entry1.config( state = 'normal' )
    entry1.delete( 0, 'end' )
    entry2.delete( 0, 'end' )

    # remove form
    form_frme.grid_forget()



def add_brd_init():

    global mn_frme, form_frme, form_conf_but, form_canc_but, label1, label2, entry1, entry2, warning_lbl

    # disable buttons for manipulating active project
    new_prj_but["state"]    = tk.DISABLED
    del_prj_but["state"]    = tk.DISABLED
    edt_prj_but["state"]    = tk.DISABLED

    # disable buttons for manipulating active board
    new_brd_but["state"]    = tk.DISABLED
    del_brd_but["state"]    = tk.DISABLED
    edt_brd_but["state"]    = tk.DISABLED

    form_frme.grid( row = 0, column = 0 )
    form_conf_but.configure( command = add_brd_conf )
    form_canc_but.configure( command = add_brd_canc )

def add_brd_conf():

    global mn_frme, form_frme, form_conf_but, form_canc_but, label1, label2, entry1, entry2, warning_lbl

    # disable buttons for manipulating active project
    new_prj_but["state"]    = tk.NORMAL
    del_prj_but["state"]    = tk.NORMAL
    edt_prj_but["state"]    = tk.NORMAL

    # disable buttons for manipulating active board
    new_brd_but["state"]    = tk.NORMAL
    del_brd_but["state"]    = tk.NORMAL
    edt_brd_but["state"]    = tk.NORMAL

def add_brd_canc():

    global mn_frme, form_frme, form_conf_but, form_canc_but, label1, label2, entry1, entry2, warning_lbl


def rem_brd_conf():

    global mn_frme, form_frme, form_conf_but, form_canc_but, label1, label2, entry1, entry2, warning_lbl

    # disable buttons for manipulating active project
    new_prj_but["state"]    = tk.DISABLED
    del_prj_but["state"]    = tk.DISABLED
    edt_prj_but["state"]    = tk.DISABLED

    # disable buttons for manipulating active board
    new_brd_but["state"]    = tk.DISABLED
    del_brd_but["state"]    = tk.DISABLED
    edt_brd_but["state"]    = tk.DISABLED


def edt_brd_init():

    global mn_frme, form_frme, form_conf_but, form_canc_but, label1, label2, entry1, entry2, warning_lbl

    # disable buttons for manipulating active project
    new_prj_but["state"]    = tk.DISABLED
    del_prj_but["state"]    = tk.DISABLED
    edt_prj_but["state"]    = tk.DISABLED

    # disable buttons for manipulating active board
    new_brd_but["state"]    = tk.DISABLED
    del_brd_but["state"]    = tk.DISABLED
    edt_brd_but["state"]    = tk.DISABLED

    form_frme.grid( row = 0, column = 0 )
    form_conf_but.configure( command = edt_brd_conf )
    form_canc_but.configure( command = edt_brd_canc )

def edt_brd_conf():

    global mn_frme, form_frme, form_conf_but, form_canc_but, label1, label2, entry1, entry2, warning_lbl

def edt_brd_canc():

    global mn_frme, form_frme, form_conf_but, form_canc_but, label1, label2, entry1, entry2, warning_lbl


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
# conn_btn.invoke()

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
new_prj_but             = tk.Button( up_frme, text = "new project", command = add_prj_init )
del_prj_but             = tk.Button( up_frme, text = "del project", command = rem_prj_conf )
edt_prj_but             = tk.Button( up_frme, text = "edit project", command = edt_prj_init )

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

# widgets for forms
form_frme                = tk.Frame( mn_frme )

label1                  = tk.Label( form_frme, text = "Name: " )
label2                  = tk.Label( form_frme, text = "Desc: " )
warning_lbl             = tk.Label( form_frme )

entry1                  = tk.Entry( form_frme )
entry2                  = tk.Entry( form_frme )

form_conf_but           = tk.Button( form_frme, text = "Confirm" )
form_canc_but           = tk.Button( form_frme, text = "Cancel" )

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

label1.grid( row = 0, column = 0 )
entry1.grid( row = 0, column = 1 )
label2.grid( row = 1, column = 0 )
entry2.grid( row = 1, column = 1 )

form_conf_but.grid( row = 2, column = 0 )
form_canc_but.grid( row = 2, column = 1 )

warning_lbl.grid( row = 3, column = 0, columnspan = 2 )

up_frme.grid( row = 0, column = 0, columnspan = 2, sticky = "WNE" )
lt_frme.grid( row = 1, column = 0, sticky = "SW" )
mn_frme.grid( row = 1, column = 1, sticky = "NESW" )

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