import tkinter as tk
from tkinter import ttk

import consts
import db_manager

manager                 = db_manager.DBManager( )
current_state           = [ None, None, None ]
previous_loop_state     = [ None, None, None ]
previous_state          = [ None, None, None ]
prompt_closed           = False
tag_name                = None

board_checkbox_states   = []
boards                  = []

edit_card_flag          = False
edit_card_flag_prv      = False
edit_card_uid           = False

tag_dict                = {}

class CardSelectHandler:

    def __init__( self, _uid, _widget ):
        self.uid        = _uid
        self.widget     = _widget

    def __call__( self, *params ):

        global edit_card_flag, edit_card_flag_prv, edit_card_uid

        edit_card_flag  = not edit_card_flag
        edit_card_uid   = self.uid


def generate_card( card_uid, name, description, master, _canvas ):

    card_frame              = ttk.LabelFrame( master=master, text="", padding=( 5, 0, 5, 5 ) )
    name_label              = ttk.Label( master=card_frame, text=name )
    description_label       = ttk.Label( master=card_frame, text=description )

    handler                 = CardSelectHandler( card_uid, master )

    name_label.grid( row=0, column=0, padx=5, pady=5, sticky="w" )
    description_label.grid( row=2, column=0, padx=5, pady=5, sticky="w" )
    card_frame.bind( consts.DOUBLE_LEFT_CLICK, handler )

    for child in card_frame.winfo_children():
        child.bind( consts.VERTICAL_MOUSE_MOTION, lambda event : _canvas.yview_scroll( ( event.delta // consts.deltaFactor ), "units" ) )
        child.bind( consts.DOUBLE_LEFT_CLICK, handler )

    return card_frame


def generate_column( _name, _cards, _cards_frame ):

    column_frame        = ttk.LabelFrame( _cards_frame, text=_name, labelanchor="n", padding=(5, 5, 1, 5) )
    column_canvas       = tk.Canvas( column_frame, borderwidth=0, background="#fafafa" )
    column_scrollbar    = ttk.Scrollbar( column_frame, orient="vertical", command=column_canvas.yview )
    frame_in_canvas     = ttk.LabelFrame( column_canvas, text="Frame in canvas", padding=(5, 5, 5, 5) )

    column_canvas.configure( yscrollcommand=column_scrollbar.set )

    for r, card in enumerate( _cards ):
        card_frame  = generate_card( card[ 0 ], card[ 1 ], card[ 2 ], frame_in_canvas, column_canvas )
        card_frame.grid( row=r, column=0, padx=5, pady=5, sticky="news" )
        card_frame.bind( consts.VERTICAL_MOUSE_MOTION, lambda event : column_canvas.yview_scroll( ( event.delta // consts.deltaFactor ) , "units" ) )

    column_canvas.bind( "<Configure>", lambda event: column_canvas.itemconfig( "frame", width=column_canvas.winfo_width( ) - 5 ) )
    column_canvas.bind( consts.VERTICAL_MOUSE_MOTION, lambda event: column_canvas.yview_scroll( ( event.delta // consts.deltaFactor ), "units" ) )
    frame_in_canvas.bind( "<Configure>", lambda event: column_canvas.configure( scrollregion=column_canvas.bbox( "all" ) ) )
    frame_in_canvas.bind( consts.VERTICAL_MOUSE_MOTION, lambda event: column_canvas.yview_scroll( ( event.delta // consts.deltaFactor ), "units" ) )
    # column_frame.bind_all( consts.VERTICAL_MOUSE_MOTION, lambda event: column_canvas.yview_scroll( ( event.delta // consts.deltaFactor )), "units" ) )
    frame_in_canvas.columnconfigure( 0, weight=1 )
    column_canvas.create_window( (0, 0), window=frame_in_canvas, anchor="n", tags="frame" )
    column_scrollbar.pack( side="right", fill="y" )
    column_canvas.pack( side="left", fill="both", expand=True )

    return column_frame


def connect( _username, _hostname, _password ):
    global prompt_closed, prompt
    manager.connect( _username, _hostname, _password )
    prompt_closed = True


def tree_click( _event ):

    global current_state, previous_state

    iid  = tree_v.selection( )[ 0 ]

    if iid[ 0 ] == 'p':
        project_name        = iid[ 1: ]
        previous_state      = current_state.copy()
        current_state       = [ project_name, None, None ]

        manager.use_project( project_name )

    else:
        board_uid           = iid.partition( " " )[ 0 ]
        project_name        = iid.partition( " " )[ 2 ]
        cur_project_name    = current_state[ 0 ]
        previous_state      = current_state.copy( )
        current_state       = [ project_name, board_uid, None ]

        if project_name != cur_project_name:
            manager.use_project( project_name )


def add_project_init( ):

    global current_state, previous_state

    previous_state     = current_state.copy( )
    current_state[ 2 ] = consts.NEW_PROJECT_FORM


def add_project_confirm( ):

    global current_state, previous_state
    global add_project_form, add_project_name_label, add_project_description_label, add_project_name_entry, add_project_description_entry, add_project_warning_label, add_project_cancel_button, add_project_confirm_button

    # get name and description as entered by user and clear text boxes
    name = add_project_name_entry.get( )
    add_project_name_entry.insert( 0, '' )
    desc = add_project_description_entry.get( )
    add_project_description_entry.insert( 0, '' )

    try:
        # create project
        manager.add_project( name, desc )

        # insert into widget
        tree_v.insert( '', 'end', iid='p' + name, text=name )

        # clear text entry widgets
        add_project_name_entry.delete( 0, "end" )
        add_project_description_entry.delete( 0, "end" )

        # clear warning label
        add_project_warning_label.configure( text='' )

        previous_state = current_state.copy( )
        current_state  = [ name, None, None ]

    except Exception as e:
        print( e )
        add_project_warning_label.configure( text="A PROJECT WITH THIS NAME ALREADY EXISTS!" )


def add_project_cancel( ):
    global current_state, previous_state
    global add_project_name_entry, add_project_description_entry, add_project_warning_label

    # clear text boxes
    add_project_name_entry.delete( 0, "end" )
    add_project_description_entry.delete( 0, "end" )

    # clear warning label
    add_project_warning_label.configure( text='' )

    temp_state     = previous_state.copy( )
    previous_state = current_state.copy( )
    current_state  = temp_state.copy( )


def delete_project_confirm( ):
    global current_state, previous_state

    # delete project for manager
    manager.delete_current_project( )

    # update widget
    tree_v.delete( 'p' + current_state[ 0 ] )

    previous_state = current_state.copy()
    current_state  = [ None, None, None ]


def edit_project_init( ):
    global current_state, previous_state
    global edit_project_name_entry, edit_project_description_entry

    # set default to current name and description
    edit_project_name_entry.insert( 0, current_state[ 0 ] )
    edit_project_description_entry.insert( 0, manager.get_project_info( ) )
    edit_project_name_entry.config( state='disabled' )

    previous_state     = current_state.copy( )
    current_state[ 2 ] = consts.EDIT_PROJECT_FORM


def edit_project_confirm( ):
    global current_state, previous_state
    global edit_project_form, edit_project_name_label, edit_project_description_label, edit_project_name_entry, edit_project_description_entry, edit_project_warning_label, edit_project_cancel_button, edit_project_confirm_button

    # update the description
    manager.update_project_info( edit_project_description_entry.get( ) )

    # clear entries
    edit_project_name_entry.config( state='normal' )
    edit_project_name_entry.delete( 0, 'end' )
    edit_project_description_entry.delete( 0, 'end' )

    previous_state     = current_state.copy( )
    current_state[ 2 ] = None


def edit_project_cancel( ):
    global current_state, previous_state
    global edit_project_form, edit_project_name_label, edit_project_description_label, edit_project_name_entry, edit_project_description_entry, edit_project_warning_label, edit_project_cancel_button, edit_project_confirm_button

    # clear entries
    edit_project_name_entry.config( state='normal' )
    edit_project_name_entry.delete( 0, 'end' )
    edit_project_description_entry.delete( 0, 'end' )

    temp_state     = previous_state.copy( )
    previous_state = current_state.copy( )
    current_state  = temp_state.copy( )


def add_board_init( ):
    global current_state, previous_state

    previous_state     = current_state.copy( )
    current_state[ 2 ] = consts.NEW_BOARD_FORM


def add_board_confirm( ):
    global current_state, previous_state
    global add_board_form, add_board_name_label, add_board_description_label, add_board_name_entry, add_board_description_entry, add_board_warning_label, add_board_cancel_button, add_board_confirm_button

    # get name, description and iid as entered by user and clear text boxes
    name = add_board_name_entry.get( )
    add_board_name_entry.insert( 0, '' )
    desc = add_board_description_entry.get( )
    add_board_description_entry.insert( 0, '' )
    iid = manager.get_next_board_uid( )

    # get list of existing boards and check if name is already present
    existing_boards = set( map( lambda event: event[ 1 ], manager.get_all_boards( ) ) )
    if name in existing_boards:
        add_board_warning_label.configure( text='A BOARD WITH THIS NAME ALREADY EXISTS' )
    else:
        # create project
        manager.add_board( iid, name, desc )

        # insert into widget
        tree_v.insert( 'p' + str( current_state[ 0 ] ), 'end', iid=( str( iid ) + " " + str( current_state[ 0 ] ) ), text=name )

        # clear text entry widgets
        add_board_name_entry.delete( 0, "end" )
        add_board_description_entry.delete( 0, "end" )

        # clear warning label
        add_board_warning_label.configure( text='' )

        previous_state     = current_state.copy( )
        current_state[ 1 ] = str( iid )
        current_state[ 2 ] = None


def add_board_cancel( ):
    global current_state, previous_state
    global add_board_form, add_board_name_label, add_board_description_label, add_board_name_entry, add_board_description_entry, add_board_warning_label, add_board_cancel_button, add_board_confirm_button

    # clear text boxes
    add_board_name_entry.delete( 0, "end" )
    add_board_description_entry.delete( 0, "end" )

    # clear warning label
    add_board_warning_label.configure( text='' )

    temp_state     = previous_state.copy( )
    previous_state = current_state.copy( )
    current_state  = temp_state.copy( )


def delete_board_confirm( ):
    global current_state, previous_state

    # delete board for manager
    manager.delete_board( current_state[ 1 ] )

    # update widget
    tree_v.delete( ( str( current_state[ 1 ] ) + " " + str( current_state[ 0 ] ) ) )

    previous_state     = current_state.copy( )
    current_state[ 1 ] = None
    current_state[ 2 ] = None


def edit_board_init( ):
    global current_state, previous_state
    global edit_board_name_entry, edit_board_description_entry

    edit_board_name_entry.insert( 0, manager.get_board_name( current_state[ 1 ] ) )
    edit_board_description_entry.insert( 0, manager.get_board_description( current_state[ 1 ] ) )

    previous_state     = current_state.copy( )
    current_state[ 2 ] = consts.EDIT_BOARD_FORM


def edit_board_confirm( ):
    global current_state, previous_state
    global edit_board_form, edit_board_name_label, edit_board_description_label, edit_board_name_entry, edit_board_description_entry, edit_board_warning_label, edit_board_cancel_button, edit_board_confirm_button

    name = edit_board_name_entry.get( )
    desc = edit_board_description_entry.get( )
    iid = int( current_state[ 1 ] )

    existing_boards = set( map( lambda event: event[ 1 ], manager.get_all_boards( ) ) )

    if name != manager.get_board_name( current_state[ 1 ] ) and name in existing_boards:
        edit_board_warning_label.configure( text="A BOARD WITH THIS NAME ALREADY EXISTS" )
    else:
        # update board
        manager.update_board( iid, name, desc )

        # update widget
        # tree_v.delete( ( str( current_state[ 1 ] ) + " " + str( current_state[ 0 ] ) ) )
        # tree_v.insert( 'p' + current_state[ 0 ], 'end', iid=( str( current_state[ 1 ] ) + " " + str( current_state[ 0 ] ) ), text=name )
        tree_v.item( ( str( current_state[ 1 ] ) + " " + str( current_state[ 0 ] ) ), text=name )

        # clear text entry widgets
        edit_board_name_entry.delete( 0, "end" )
        edit_board_description_entry.delete( 0, "end" )

        # clear warning label
        edit_board_warning_label.configure( text='' )

        previous_state     = current_state.copy( )
        current_state[ 2 ] = None


def edit_board_cancel( ):
    global current_state, previous_state
    global edit_board_form, edit_board_name_label, edit_board_description_label, edit_board_name_entry, edit_board_description_entry, edit_board_warning_label, edit_board_cancel_button, edit_board_confirm_button

    # clear text boxes
    edit_board_name_entry.delete( 0, 'end' )
    edit_board_description_entry.delete( 0, 'end' )

    # clear warning label
    edit_board_warning_label.configure( text='' )

    temp_state     = previous_state.copy( )
    previous_state = current_state.copy( )
    current_state  = temp_state.copy( )


def add_card_init( ):
    global current_state, previous_state
    global board_checkbox_states, add_card_board_frame

    previous_state     = current_state.copy( )
    current_state[ 2 ] = consts.NEW_CARD_FORM


def add_card_confirm( ):
    global current_state, previous_state, board_checkbox_states, boards
    global add_card_form, add_card_name_label, add_card_description_label, add_card_name_entry, add_card_description_entry, add_card_cancel_button, add_card_confirm_button, add_card_board_frame

    # get name, description and iid as entered by user and clear text boxes
    name = add_card_name_entry.get( )
    add_card_name_entry.insert( 0, '' )
    desc = add_card_description_entry.get( )
    add_card_description_entry.insert( 0, '' )
    iid = manager.get_next_card_uid( )

    # create project
    manager.add_card( iid, name, desc, None )

    for state, board in zip( board_checkbox_states, boards ):
        if state.get():
            manager.add_card_to_board( board[0], iid )

    # clear text entry widgets
    add_card_name_entry.delete( 0, "end" )
    add_card_description_entry.delete( 0, "end" )

    previous_state = current_state.copy( )
    # current_state[ 1 ] = str( iid )
    current_state[ 2 ] = None

    for child in add_card_board_frame.winfo_children():
        child.grid_forget()
        child.destroy()


def add_card_cancel( ):
    global current_state, previous_state
    global add_card_form, add_card_name_label, add_card_description_label, add_card_name_entry, add_card_description_entry, add_card_cancel_button, add_card_confirm_button, add_card_board_frame

    add_card_name_entry.delete( 0, "end" )
    add_card_description_entry.delete( 0, "end" )

    temp_state     = previous_state.copy( )
    previous_state = current_state.copy( )
    current_state  = temp_state.copy( )

    for child in add_card_board_frame.winfo_children():
        child.grid_forget()
        child.destroy()


def edit_card_cancel():
    global edit_card_flag
    edit_card_flag  = False


def edit_card_confirm():
    global current_state, previous_state, previous_loop_state, tag_name, tag_dropdown
    global add_project_form, edit_project_form, add_board_form, edit_board_form, add_card_form
    global board_checkbox_states, boards, tag_dict
    global edit_card_flag, edit_card_flag_prv, edit_card_uid
    global edit_card_root, edit_card_name_label, edit_card_name_entry, edit_card_desc_label, edit_card_desc_entry, edit_card_confirm_button, edit_card_cancel_button
    global edit_card_board_root

    edit_card_flag  = False

    manager.update_card( edit_card_uid, edit_card_name_entry.get(), edit_card_desc_entry.get(), None )

    if current_state[1] is not None:

        for tag, entry in tag_dict.items():

            new_val = entry.get().strip()

            if new_val:
                manager.update_card_tag_value( current_state[1], edit_card_uid, tag, new_val )

    else:
        valid_boards = manager.get_boards_of_card( edit_card_uid )

        for ( state, board ) in zip( board_checkbox_states, boards ):
            board_uid = board[0]

            if state.get() and (board_uid not in valid_boards):
                manager.add_card_to_board( board_uid, edit_card_uid )
                print(f"ADDING CARD TO BOARD {board[1]}")
            elif not state.get() and (board_uid in valid_boards):
                manager.remove_card_from_board( board_uid, edit_card_uid )
                print(f"REMOVING CARD FROM BOARD {board[1]}")

    update_state( root, main_frame )


def edit_card_remove():
    print("REMOVING CARD FROM BOARD")
    manager.remove_card_from_board( current_state[1], edit_card_uid )

    update_state( root, main_frame )

def edit_card_delete():
    print("DELETING CARD FROM PROJECT")
    manager.delete_card( edit_card_uid )

    update_state( root, main_frame )

def add_new_tag():

    print("ADD CARD TAG")

    global edit_card_new_tag_key_entry, edit_card_new_tag_val_entry, edit_card_flag

    tag_name = edit_card_new_tag_key_entry.get()
    tag_value = edit_card_new_tag_val_entry.get()

    manager.add_card_tag( current_state[1], edit_card_uid, tag_name, tag_value )

    edit_card_new_tag_key_entry.delete( 0, "end" )
    edit_card_new_tag_val_entry.delete( 0, "end" )

    update_state( root, main_frame )
    edit_card_flag = True
    update_internal_state()

def del_old_tag():

    print("DELETING CARD TAG")

    global edit_card_new_tag_key_entry, edit_card_new_tag_val_entry, edit_card_flag

    tag_name = edit_card_new_tag_key_entry.get()

    manager.delete_card_tag( current_state[1], edit_card_uid, tag_name )

    edit_card_new_tag_key_entry.delete( 0, "end" )
    edit_card_new_tag_val_entry.delete( 0, "end" )

    update_state( root, main_frame )
    edit_card_flag = True
    update_internal_state()

def update_internal_state():
    global current_state, previous_state, previous_loop_state, tag_name, tag_dropdown
    global add_project_form, edit_project_form, add_board_form, edit_board_form, add_card_form
    global board_checkbox_states, boards
    global edit_card_flag, edit_card_flag_prv, edit_card_uid
    global edit_card_root, edit_card_name_label, edit_card_name_entry, edit_card_desc_label, edit_card_desc_entry, edit_card_confirm_button, edit_card_cancel_button
    global edit_card_board_root
    global tag_dict

    print( f"NOW EDITING {edit_card_uid}" if edit_card_flag else "NOW NOT EDITING" )

    #!

    edit_card_name_entry.delete( 0, "end" )
    edit_card_desc_entry.delete( 0, "end" )

    for child in edit_card_board_frame.winfo_children():
        child.grid_forget()
        child.destroy()

    for child in edit_card_tag_frame.winfo_children():
        child.grid_forget()
        child.destroy()
        print("DESTROYING KEY VALUE PAIRS")

    tag_dict = {}

    edit_card_root.grid_forget()

    if edit_card_flag:

        edit_card_root.grid( row=0, column=2, padx=2, pady=2 )
        card    = manager.get_card( edit_card_uid )

        edit_card_name_entry.insert( 0, card[ 0 ] )
        edit_card_desc_entry.insert( 0, card[ 1 ] )

        if current_state[1] is not None:
            print("BOARD CARDS")

            edit_card_board_root.grid_forget()
            edit_card_delete_button.grid_forget()

            edit_card_remove_button.grid( row=0, column=2, columnspan=1 )

            tags = manager.get_card_tags( current_state[1], edit_card_uid )
            if tags[0][0] is None:
                tags = tags[1:]

            for row, ( tkey, tval ) in enumerate( tags ):

                key_label = ttk.Label( edit_card_tag_frame, text = tkey )
                val_entry = ttk.Entry( edit_card_tag_frame, validate='all', validatecommand=lambda: tk.BooleanVar( value=bool( val_entry.get().strip() ) )  )

                val_entry.insert( 0, tval )

                key_label.grid( row=2*row, column=0, columnspan=1 )
                val_entry.grid( row=2*row + 1, column=1, columnspan=3 )

                tag_dict[tkey] = val_entry

            edit_card_tag_root.grid( row=5, column=0, columnspan=2 )
            edit_card_new_tag_frame.grid( row=4, column=0, columnspan=2, padx=3, pady=3 )

        else:
            print("PROJECT CARDS")

            edit_card_tag_root.grid_forget()
            edit_card_new_tag_frame.grid_forget()
            edit_card_remove_button.grid_forget()

            edit_card_delete_button.grid( row=0, column=2, columnspan=1 )

            boards = manager.get_all_boards()
            valid_boards = manager.get_boards_of_card( edit_card_uid )
            board_checkbox_states   = [ tk.BooleanVar( value=(board[0] in valid_boards) ) for board in boards ]

            for row, ( state, board ) in enumerate( zip( board_checkbox_states, boards ) ):
                c   = ttk.Checkbutton( edit_card_board_frame, text=board[ 1 ], variable=state )
                c.grid( row=row, column=0, padx=3, pady=3, sticky="w" )

            edit_card_board_root.grid( row=4, column=0, columnspan=2 )

    # else:

    #     edit_card_name_entry.delete( 0, "end" )
    #     edit_card_desc_entry.delete( 0, "end" )

    #     for child in edit_card_board_frame.winfo_children():
    #         child.grid_forget()
    #         child.destroy()

    #     for child in edit_card_tag_frame.winfo_children():
    #         child.grid_forget()
    #         child.destroy()
    #         print("DESTROYING KEY VALUE PAIRS")

    #     tag_dict = {}

    #     edit_card_root.grid_forget()


def update_state( _root_window, _main_frame ):
    global current_state, previous_state, previous_loop_state, tag_name, tag_dropdown
    global add_project_form, edit_project_form, add_board_form, edit_board_form, add_card_form
    global board_checkbox_states, boards
    global edit_card_flag, edit_card_flag_prv, edit_card_uid

    edit_card_flag = False
    state_handled = False

    # Disable all buttons and dropdown
    new_project_button[ "state" ]    = tk.DISABLED
    delete_project_button[ "state" ] = tk.DISABLED
    edit_project_button[ "state" ]   = tk.DISABLED
    new_board_button[ "state" ]      = tk.DISABLED
    edit_board_button[ "state" ]     = tk.DISABLED
    delete_board_button[ "state" ]   = tk.DISABLED

    tag_dropdown["state"]            = tk.DISABLED
    new_card_button[ "state" ]       = tk.DISABLED

    if previous_loop_state[ 1 ] != current_state[ 1 ]:
        tag_name.set( consts.NO_TAG_SELECTED )

    for child in main_frame.winfo_children():
        child.grid_forget( )

    if current_state == [ None, None, None ]:
        state_handled = True
        new_project_button[ "state" ]    = tk.NORMAL

    elif current_state[ 2 ] == consts.NEW_PROJECT_FORM:
        state_handled = True
        add_project_form.grid( row=0, column=0, padx=5, pady=5, sticky="news" )

    elif current_state[ 0 ] is not None and current_state[ 1 ] is None and current_state[ 2 ] is None:        # Only a project is selected
        state_handled = True
        new_project_button[ "state" ]    = tk.NORMAL
        delete_project_button[ "state" ] = tk.NORMAL
        edit_project_button[ "state" ]   = tk.NORMAL
        new_board_button[ "state" ]      = tk.NORMAL
        new_card_button[ "state" ]       = tk.NORMAL

        cards_frame         = ttk.LabelFrame( _main_frame, text="Cards frame", padding=(5, 5, 5, 5) )
        all_cards_column    = generate_column( "All Cards", manager.get_all_cards( ), cards_frame )
        all_cards_column.grid( row=0, column=0, padx=5, pady=5, sticky="news" )
        cards_frame.rowconfigure( 0, weight=1 )
        cards_frame.columnconfigure( 0, weight=1 )
        cards_frame.grid( row=0, column=0, padx=5, pady=5, sticky="news" )

        #! CHECK TO SEE STATE OF EDIT CARD FLAG

    elif current_state[ 0 ] is not None and current_state[ 1 ] is not None and current_state[ 2 ] is None:      # A project and a board is selected
        state_handled = True
        new_project_button[ "state" ]    = tk.NORMAL
        delete_project_button[ "state" ] = tk.NORMAL
        edit_project_button[ "state" ]   = tk.NORMAL
        new_board_button[ "state" ]      = tk.NORMAL
        edit_board_button[ "state" ]     = tk.NORMAL
        delete_board_button[ "state" ]   = tk.NORMAL

        new_card_button[ "state" ]       = tk.NORMAL
        tag_dropdown["state"]            = tk.NORMAL

        tag_dropdown.set_menu( "", consts.NO_TAG_SELECTED, *manager.get_board_tag_names( current_state[ 1 ] )[ 1:: ] )
        tag_dropdown[ "menu" ].entryconfigure( 0, font=("pointfree", 9, "italic") )
        tag_dropdown[ "menu" ].insert_separator( 1 )

        cards_frame = ttk.LabelFrame( _main_frame, text="Cards frame", padding=( 5, 5, 5, 5 ) )
        if tag_name.get( ) == consts.NO_TAG_SELECTED:
            all_cards_column = generate_column( "All Cards in this Board", manager.get_cards_in_board( current_state[ 1 ] ), cards_frame )
            all_cards_column.grid( row=0, column=0, padx=5, pady=5, sticky="news" )
            cards_frame.columnconfigure( 0, weight=1 )
        else:
            grouped_cards = manager.get_board_grouped_cards( current_state[ 1 ], tag_name.get( ) )
            for j, tag_value in enumerate( grouped_cards ):
                column = generate_column( tag_value, grouped_cards[ tag_value ], cards_frame )
                column.grid( row=0, column=j, padx=5, pady=5, sticky="news")
                cards_frame.columnconfigure( j, weight=1, minsize=250 )
        cards_frame.rowconfigure( 0, weight=1 )
        cards_frame.grid( row=0, column=0, padx=5, pady=5, sticky="news" )
        # print("hello:", root.winfo_width())
    elif current_state[ 0 ] is not None and current_state[ 1 ] is not None and current_state[ 2 ] == consts.EDIT_BOARD_FORM:
        state_handled = True
        edit_board_form.grid( row=0, column=0, padx=5, pady=5, sticky="news" )

    elif current_state[ 0 ] is not None and current_state[ 2 ] == consts.EDIT_PROJECT_FORM:
        state_handled = True
        edit_project_form.grid( row=0, column=0, padx=5, pady=5, sticky="news" )

    elif current_state[ 0 ] is not None and current_state[ 2 ] == consts.NEW_BOARD_FORM:
        state_handled = True
        add_board_form.grid( row=0, column=0, padx=5, pady=5, sticky="news" )

    elif current_state[ 0 ] is not None and current_state[ 2 ] == consts.NEW_CARD_FORM:
        state_handled = True

        # Populate dropdown of board checkboxes in canvas
        boards                  = manager.get_all_boards()
        board_checkbox_states   = [ tk.BooleanVar( value=False )  for i in range( len( boards ) ) ]

        for row, ( state, board ) in enumerate( zip( board_checkbox_states, boards ) ):
            c   = ttk.Checkbutton( add_card_board_frame, text=board[ 1 ], variable=state )
            c.grid( row=row, column=0, padx=3, pady=3, sticky="w" )

        add_card_form.grid( row=0, column=0, padx=5, pady=5, sticky="news" )

    if current_state[ 0 ] is None and current_state[ 1 ] is not None:       # A board is selected but a project is not
        state_handled = False

    if not state_handled:
        print("STATE IS NOT HANDLED")
        print("Previous state:", previous_state)
        print("Current state:", current_state)

# Main

# Create initial prompt to enter server credentials
prompt                      = tk.Tk( )
prompt.title( "Pyboard" )
prompt.minsize( 250, 150 )
prompt.tk.call("source", "sun-valley.tcl")
prompt.tk.call("set_theme", "light")

prompt_frame                        = ttk.LabelFrame( prompt, text="Prompt frame", padding=( 5, 5, 5, 5 ) )
# prompt_frame = tk.Frame( prompt )

username_entry                      = ttk.Entry( prompt_frame )
hostname_entry                      = ttk.Entry( prompt_frame )
password_entry                      = ttk.Entry( prompt_frame )
connect_button                      = ttk.Button( master=prompt_frame, style="Accent.TButton", text="Connect", command=lambda: connect( username_entry.get( ), hostname_entry.get( ), password_entry.get( ) ) )

username_entry.insert( 0, "root" )
hostname_entry.insert( 0, "localhost" )
password_entry.config( show = "*" )

username_entry.grid( row=0, column=0, padx=3, pady=3 )
hostname_entry.grid( row=1, column=0, padx=3, pady=3 )
password_entry.grid( row=2, column=0, padx=3, pady=3 )
connect_button.grid( row=3, column=0, padx=3, pady=3 )

prompt_frame.grid( row=0, column=0, padx=5, pady=5 )

prompt.columnconfigure( index=0, weight=1 )
prompt.rowconfigure( index=0, weight=1 )

prompt.eval('tk::PlaceWindow . center')

# ! ONLY FOR SQLITE BRANCH
# connect_button.invoke( )

# manually implemented main loop
while not prompt_closed:
    try:
        prompt.update_idletasks( )
        prompt.update( )
    except Exception as e:
        print( e )
        break
try:
    prompt.destroy( )
except Exception as e:
    print( e )

# start of main application
root = tk.Tk( )
root.title( "Pyboard" )
root.minsize( 250, 150 )
root.tk.call("source", "sun-valley.tcl")
root.tk.call("set_theme", "light")

s = ttk.Style( )
s.configure( "my.TMenubutton", font = ( "pointfree", 9, "italic" ) )

# basic frames
top_frame                           = ttk.LabelFrame( root, text="top frame", padding=( 5, 5, 5, 5 ) )
left_frame                          = ttk.LabelFrame( root, text="left frame", padding=( 5, 5, 5, 5 ) )
main_frame                          = ttk.LabelFrame( root, text="main frame", padding=( 5, 5, 5, 5 ) )

# add_project_form, add_project_name_label, add_project_description_label, add_project_name_entry, add_project_description_entry, add_project_warning_label, add_project_cancel_button, add_project_confirm_button
# forms for project
add_project_form                    = ttk.LabelFrame( main_frame, text="new project form frame", padding=( 5, 5, 5, 5 ) )
add_project_name_label              = ttk.Label( add_project_form, text="Name: " )
add_project_description_label       = ttk.Label( add_project_form, text="Desc: " )
add_project_name_entry              = ttk.Entry( add_project_form )
add_project_description_entry       = ttk.Entry( add_project_form )
add_project_warning_label           = ttk.Label( add_project_form, text="" )
add_project_cancel_button           = ttk.Button( add_project_form, text="Cancel", command=add_project_cancel )
add_project_confirm_button          = ttk.Button( add_project_form, text="Confirm", command=add_project_confirm )

add_project_name_label.grid( row=0, column=0, padx=3, pady=3 )
add_project_name_entry.grid( row=0, column=1, padx=3, pady=3, columnspan = 3 )
add_project_description_label.grid( row=1, column=0, padx=3, pady=3 )
add_project_description_entry.grid( row=1, column=1, padx=3, pady=3, columnspan = 3 )
add_project_cancel_button.grid( row=2, column=0, padx=3, pady=3, columnspan = 2 )
add_project_confirm_button.grid( row=2, column=2, padx=3, pady=3, columnspan = 2 )
add_project_warning_label.grid( row=3, column=0, padx=3, pady=3, columnspan=4 )


# edit_project_form, edit_project_name_label, edit_project_description_label, edit_project_name_entry, edit_project_description_entry, edit_project_warning_label, edit_project_cancel_button, edit_project_confirm_button
edit_project_form                   = ttk.LabelFrame( main_frame, text="edit project form frame", padding=( 5, 5, 5, 5 ) )
edit_project_name_label             = ttk.Label( edit_project_form, text="Name: " )
edit_project_description_label      = ttk.Label( edit_project_form, text="Desc: " )
edit_project_name_entry             = ttk.Entry( edit_project_form )
edit_project_description_entry      = ttk.Entry( edit_project_form )
edit_project_warning_label          = ttk.Label( edit_project_form, text="" )
edit_project_cancel_button          = ttk.Button( edit_project_form, text="Cancel", command=edit_project_cancel )
edit_project_confirm_button         = ttk.Button( edit_project_form, text="Confirm", command=edit_project_confirm )

edit_project_name_label.grid( row=0, column=0, padx=3, pady=3 )
edit_project_name_entry.grid( row=0, column=1, padx=3, pady=3, columnspan = 3 )
edit_project_description_label.grid( row=1, column=0, padx=3, pady=3 )
edit_project_description_entry.grid( row=1, column=1, padx=3, pady=3, columnspan = 3 )
edit_project_cancel_button.grid( row=2, column=0, padx=3, pady=3, columnspan = 2 )
edit_project_confirm_button.grid( row=2, column=2, padx=3, pady=3, columnspan = 2 )
edit_project_warning_label.grid( row=3, column=0, padx=3, pady=3, columnspan=4 )


# add_board_form, add_board_name_label, add_board_description_label, add_board_name_entry, add_board_description_entry, add_board_warning_label, add_board_cancel_button, add_board_confirm_button
add_board_form                      = ttk.LabelFrame( main_frame, text="new board form frame", padding=( 5, 5, 5, 5 ) )
add_board_name_label                = ttk.Label( add_board_form, text="Name: " )
add_board_description_label         = ttk.Label( add_board_form, text="Desc: " )
add_board_name_entry                = ttk.Entry( add_board_form )
add_board_description_entry         = ttk.Entry( add_board_form )
add_board_warning_label             = ttk.Label( add_board_form, text="" )
add_board_cancel_button             = ttk.Button( add_board_form, text="Cancel", command=add_board_cancel )
add_board_confirm_button            = ttk.Button( add_board_form, text="Confirm", command=add_board_confirm )

add_board_name_label.grid( row=0, column=0, padx=3, pady=3 )
add_board_name_entry.grid( row=0, column=1, padx=3, pady=3, columnspan = 3 )
add_board_description_label.grid( row=1, column=0, padx=3, pady=3 )
add_board_description_entry.grid( row=1, column=1, padx=3, pady=3, columnspan = 3 )
add_board_cancel_button.grid( row=2, column=0, padx=3, pady=3, columnspan = 2 )
add_board_confirm_button.grid( row=2, column=2, padx=3, pady=3, columnspan = 2 )
add_board_warning_label.grid( row=3, column=0, padx=3, pady=3, columnspan=4 )


# edit_board_form, edit_board_name_label, edit_board_description_label, edit_board_name_entry, edit_board_description_entry, edit_board_warning_label, edit_board_cancel_button, edit_board_confirm_button
edit_board_form                     = ttk.LabelFrame( main_frame, text="edit board form frame", padding=( 5, 5, 5, 5 ) )
edit_board_name_label               = ttk.Label( edit_board_form, text="Name: " )
edit_board_description_label        = ttk.Label( edit_board_form, text="Desc: " )
edit_board_name_entry               = ttk.Entry( edit_board_form )
edit_board_description_entry        = ttk.Entry( edit_board_form )
edit_board_warning_label            = ttk.Label( edit_board_form, text="" )
edit_board_cancel_button            = ttk.Button( edit_board_form, text="Cancel", command=edit_board_cancel )
edit_board_confirm_button           = ttk.Button( edit_board_form, text="Confirm", command=edit_board_confirm )

edit_board_name_label.grid( row=0, column=0, padx=3, pady=3 )
edit_board_name_entry.grid( row=0, column=1, padx=3, pady=3, columnspan = 3 )
edit_board_description_label.grid( row=1, column=0, padx=3, pady=3 )
edit_board_description_entry.grid( row=1, column=1, padx=3, pady=3, columnspan = 3 )
edit_board_cancel_button.grid( row=2, column=0, padx=3, pady=3, columnspan = 2 )
edit_board_confirm_button.grid( row=2, column=2, padx=3, pady=3, columnspan = 2 )
edit_board_warning_label.grid( row=3, column=0, padx=3, pady=3, columnspan=4 )

# add_card_form, add_card_name_label, add_card_description_label, add_card_name_entry, add_card_description_entry, add_card_cancel_button, add_card_confirm_button
add_card_form                       = ttk.LabelFrame( main_frame, text="add card form frame", padding=( 5, 5, 5, 5 ) )
add_card_name_label                 = ttk.Label( add_card_form, text="Name: " )
add_card_description_label          = ttk.Label( add_card_form, text="Desc: " )
add_card_name_entry                 = ttk.Entry( add_card_form )
add_card_description_entry          = ttk.Entry( add_card_form )
add_card_cancel_button              = ttk.Button( add_card_form, text="Cancel", command=add_card_cancel )
add_card_confirm_button             = ttk.Button( add_card_form, text="Confirm", command=add_card_confirm )
add_card_board_root                 = ttk.LabelFrame( add_card_form, text="add card board root", padding=( 5, 5, 5, 5 ) )
add_card_board_dropdown             = tk.Canvas( add_card_board_root, highlightthickness=0, borderwidth=0, background='#fafafa' )
add_card_board_scrollbar            = ttk.Scrollbar( add_card_board_root, orient='vertical', command=add_card_board_dropdown.yview)
add_card_board_frame                = ttk.LabelFrame( add_card_board_dropdown, text="Frame in canvas", padding=( 5, 5, 5, 5 ) )
add_card_name_label.grid( row=0, column=0, padx=3, pady=3 )
add_card_name_entry.grid( row=0, column=1, padx=3, pady=3, columnspan = 3 )
add_card_description_label.grid( row=1, column=0, padx=3, pady=3 )
add_card_description_entry.grid( row=1, column=1, padx=3, pady=3, columnspan = 3 )

add_card_board_frame.bind("<Configure>", lambda event: add_card_board_dropdown.configure(scrollregion=add_card_board_dropdown.bbox("all")))
add_card_board_dropdown.configure( yscrollcommand=add_card_board_scrollbar.set )
add_card_board_dropdown.pack( side="left", fill="both", expand=True )
add_card_board_dropdown.create_window((4,4), window=add_card_board_frame, anchor="nw")
add_card_board_scrollbar.pack( side="right", fill="y" )

add_card_board_root.grid( row=2, column=0, padx=3, pady=3, columnspan=4 )

add_card_cancel_button.grid( row=3, column=0, padx=3, pady=3, columnspan = 2 )
add_card_confirm_button.grid( row=3, column=2, padx=3, pady=3, columnspan = 2 )

edit_card_root                      = ttk.LabelFrame( main_frame, text="Edit Card Form", padding=( 3, 3, 3, 3 ) )
edit_card_name_label                = ttk.Label( edit_card_root, text="Name:" )
edit_card_name_entry                = ttk.Entry( edit_card_root )
edit_card_desc_label                = ttk.Label( edit_card_root, text="Desc:" )
edit_card_desc_entry                = ttk.Entry( edit_card_root )

edit_card_board_root                = ttk.LabelFrame( edit_card_root, text="edit card board root" )
edit_card_board_dropdown            = tk.Canvas( edit_card_board_root, highlightthickness=0, borderwidth=0, background='#fafafa' )
edit_card_board_scrollbar           = ttk.Scrollbar( edit_card_board_root, orient='vertical', command=edit_card_board_dropdown.yview )
edit_card_board_frame               = ttk.LabelFrame( edit_card_board_dropdown, text="Frame in Canvas", padding=( 5, 5, 5, 5 ) )

edit_card_board_frame.bind("<Configure>", lambda event: edit_card_board_dropdown.configure(scrollregion=edit_card_board_dropdown.bbox("all")))
edit_card_board_dropdown.configure( yscrollcommand=edit_card_board_scrollbar.set )
edit_card_board_dropdown.pack( side="left", fill="both", expand=True )
edit_card_board_dropdown.create_window((4,4), window=edit_card_board_frame, anchor="center")
edit_card_board_scrollbar.pack( side="right", fill="y" )

edit_card_tag_root                  = ttk.LabelFrame( edit_card_root, text="edit card tag root" )
edit_card_tag_dropdown              = tk.Canvas( edit_card_tag_root, highlightthickness=0, borderwidth=0, background='#fafafa' )
edit_card_tag_scrollbar             = ttk.Scrollbar( edit_card_tag_root, orient='vertical', command=edit_card_tag_dropdown.yview )
edit_card_tag_frame                 = ttk.LabelFrame( edit_card_tag_dropdown, text="Frame in Canvas", padding=( 5, 5, 5, 5 ) )

edit_card_tag_frame.bind("<Configure>", lambda event: edit_card_tag_dropdown.configure(scrollregion=edit_card_tag_dropdown.bbox("all")))
edit_card_tag_dropdown.configure( yscrollcommand=edit_card_tag_scrollbar.set )
edit_card_tag_dropdown.pack( side="left", fill="both", expand=True )
edit_card_tag_dropdown.create_window((4,4), window=edit_card_tag_frame, anchor="center")
edit_card_tag_scrollbar.pack( side="right", fill="y" )

edit_card_button_parent             = tk.Frame( edit_card_root )

edit_card_confirm_button            = ttk.Button( edit_card_button_parent, text="Confirm", command=edit_card_confirm )
edit_card_cancel_button             = ttk.Button( edit_card_button_parent, text="Cancel", command=edit_card_cancel )

edit_card_delete_button             = ttk.Button( edit_card_button_parent, text="Delete", command=edit_card_delete )
edit_card_remove_button             = ttk.Button( edit_card_button_parent, text="Remove", command=edit_card_remove )

edit_card_new_tag_frame             = ttk.LabelFrame( edit_card_root, text="Add and Del tags", padding=( 5, 5, 5, 5 ) )
edit_card_new_tag_key_entry         = ttk.Entry( edit_card_new_tag_frame )
edit_card_new_tag_val_entry         = ttk.Entry( edit_card_new_tag_frame )
edit_card_new_tag_add_button        = ttk.Button( edit_card_new_tag_frame, text="Add", command=add_new_tag )
edit_card_del_tag_button            = ttk.Button( edit_card_new_tag_frame, text="Delete", command=del_old_tag )

edit_card_new_tag_key_entry.grid( row=0, column=1 )
edit_card_new_tag_val_entry.grid( row=0, column=2 )
edit_card_new_tag_add_button.grid( row=0, column=3 )
edit_card_del_tag_button.grid( row=0, column=4 )


edit_card_name_label.grid( row=0, column=0, columnspan=1 )
edit_card_name_entry.grid( row=1, column=0, columnspan=2 )
edit_card_desc_label.grid( row=2, column=0, columnspan=1 )
edit_card_desc_entry.grid( row=3, column=0, columnspan=2 )

edit_card_confirm_button.grid( row=0, column=0, columnspan=1 )
edit_card_cancel_button.grid( row=0, column=1, columnspan=1 )

edit_card_button_parent.grid( row=6, column=0, columnspan=2 )

new_project_button                  = ttk.Button( top_frame, text="new project", command=add_project_init, compound = "right" )
delete_project_button               = ttk.Button( top_frame, text="delete project", command=delete_project_confirm )
edit_project_button                 = ttk.Button( top_frame, text="edit project", command=edit_project_init )
new_board_button                    = ttk.Button( top_frame, text="new board", command=add_board_init )
delete_board_button                 = ttk.Button( top_frame, text="delete board", command=delete_board_confirm )
edit_board_button                   = ttk.Button( top_frame, text="edit board", command=edit_board_init )
new_card_button                     = ttk.Button( top_frame, text="new card", command=add_card_init )
tag_name                            = tk.StringVar( value=consts.NO_TAG_SELECTED )
tag_dropdown                        = ttk.OptionMenu( top_frame,  tag_name, "", consts.NO_TAG_SELECTED, "something", style="my.TMenubutton", command=lambda event: update_state(root, main_frame) )
tag_dropdown[ "menu" ].entryconfigure( 0, font = ( "pointfree", 9,"italic" ) )
tag_dropdown[ "menu" ].insert_separator( 1 )
# tag_dropdown = ChecklistCombobox( top_frame, values=("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20") )
# tag_dropdown[ "state" ] = tk.DISABLED

# disable buttons at start
new_project_button[ "state" ]       = tk.DISABLED
delete_project_button[ "state" ]    = tk.DISABLED
edit_project_button[ "state" ]      = tk.DISABLED
new_board_button[ "state" ]         = tk.DISABLED
delete_board_button[ "state" ]      = tk.DISABLED
edit_board_button[ "state" ]        = tk.DISABLED
new_card_button[ "state" ]          = tk.DISABLED
tag_dropdown["state"]               = tk.DISABLED

# place widgets in top frame
new_project_button.grid( row=0, column=0, padx=3, pady=3, sticky="ew" )
delete_project_button.grid( row=0, column=1, padx=3, pady=3, sticky="ew" )
edit_project_button.grid( row=0, column=2, padx=3, pady=3, sticky="ew" )
new_board_button.grid( row=0, column=3, padx=3, pady=3, sticky="ew" )
delete_board_button.grid( row=0, column=4, padx=3, pady=3, sticky="ew" )
edit_board_button.grid( row=0, column=5, padx=3, pady=3, sticky="ew" )
new_card_button.grid( row=0, column=6, padx=3, pady=3, sticky="ew" )
tag_dropdown.grid( row=0, column=7, padx=3, pady=3, sticky="ew" )

for i in range( 8 ):
    top_frame.columnconfigure( index=i, weight=1 )

# widgets in the left frame
tree_v = ttk.Treeview( left_frame, selectmode='browse' )
tree_v.column( "#0", anchor="center" )
tree_v.bind( consts.DOUBLE_LEFT_CLICK, tree_click )

# insert all projects and boards in the treeview
for project in manager.get_all_projects( ):
    tree_v.insert( '', 'end', iid='p' + project, text=project )
    manager.use_project( project )
    for board in manager.get_all_boards( ):
        tree_v.insert( 'p' + project, 'end', iid=( str( board[ 0 ] ) + " " + str( project ) ), text=board[ 1 ] )
manager.stop( )

# place widgets in the left frame
tree_v.pack( expand=True, fill="both" )

# place frames in the root window
top_frame.grid( row=0, column=0, columnspan=2, sticky="news", padx=5, pady=5 )
left_frame.grid( row=1, column=0, sticky="news", padx=5, pady=5 )
main_frame.rowconfigure( index=0, weight=1 )
# main_frame.rowconfigure( index=1, weight=1 )
main_frame.columnconfigure( index=0, weight=1 )
main_frame.grid( row=1, column=1, sticky="news", padx=5, pady=5 )

root.columnconfigure( index=1, weight=1 )
root.rowconfigure( index=1, weight=1 )

root.eval('tk::PlaceWindow . center')

# manually implemented main loop
update_state( root, main_frame )
while 1:
    try:
        root.update_idletasks( )
        root.update( )
    except Exception as e:
        print( e )
        break

    if previous_loop_state != current_state:
        update_state( root, main_frame )
        print( "STATE UPDATED" )
        previous_loop_state = current_state.copy( )

    if edit_card_flag_prv != edit_card_flag:
        update_internal_state()
        edit_card_flag_prv = edit_card_flag

manager.stop( )

# for getting projects -> get_project_names is API
# for creating projects -> add_project
# for editing proj -> update_project_info
# for deleting proj -> delete_current_project

# for getting board -> get_all_boards
# for creating board -> add_board
# for editing board -> 152 - 166 come there in db_manager (got it)
# for deleting board -> delete_board (takes the UID NOT THE name)
# you need to do db.get_next_board_uid

# ABBREVIATION'S LEGEND
# db   -> database
# btn  -> button
# col  -> column
# val  -> value
# lbl  -> label
# del  -> delete
# prj  -> project
# brd  -> board
# crnt -> current
# prev -> previous
# init -> initialize
# temp -> temporary
