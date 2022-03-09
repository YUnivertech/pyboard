#!/bin/python

import tkinter as tk
from tkinter import ttk
from tkinter import tix

import consts
import db_manager

import time

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

class Card( ttk.LabelFrame ):
    def __init__( self, master, uid, name, description):
        super( ).__init__( master, text="", padding=( 5, 5, 5, 5 ) )
        self.uid = uid
        self.master = master
        self.name_label = ttk.Label( master=self, text=name, font = ("pointfree", 10, "bold") )
        self.description_label = ttk.Label( master=self, text=description, wraplength=100, justify="left" )

        self.name_label.grid( row=0, column=0, padx=5, pady=5, sticky="w" )
        self.description_label.grid( row=2, column=0, padx=5, pady=5, sticky="w" )

        self.bind("<Configure>", lambda event: self.name_label.configure( wraplength=self.winfo_width() - 10 ) or self.description_label.configure( wraplength=self.winfo_width() - 10 ) )

        self.bind( consts.DOUBLE_LEFT_CLICK, self.select )
        for child in self.winfo_children( ):
            child.bind( consts.DOUBLE_LEFT_CLICK, self.select )

    def select( self, *params ):
        global edit_card_flag, edit_card_uid
        # print( f"CLICKED ON CARD {manager.get_card( self.uid )}" )
        edit_card_flag = not edit_card_flag
        edit_card_uid = self.uid


class AddProjectForm( ttk.LabelFrame ):
    def __init__( self, master, name="Add project form" ):
        super( ).__init__( master, text=name, padding=( 5, 5, 5, 5 ) )
        self.name_label = ttk.Label( self, text="Name: " )
        self.description_label = ttk.Label( self, text="Desc: " )
        self.name_entry = ttk.Entry( self )
        self.description_entry = ttk.Entry( self )
        self.warning_label = ttk.Label( self, text="" )
        self.cancel_button = ttk.Button( self, text="Cancel", command=self.cancel )
        self.confirm_button = ttk.Button( self, text="Confirm", command=self.confirm )

        self.name_label.grid( row=0, column=0, padx=3, pady=3 )
        self.name_entry.grid( row=0, column=1, padx=3, pady=3, columnspan=3 )
        self.description_label.grid( row=1, column=0, padx=3, pady=3 )
        self.description_entry.grid( row=1, column=1, padx=3, pady=3, columnspan=3 )
        self.cancel_button.grid( row=2, column=0, padx=3, pady=3, columnspan=2 )
        self.confirm_button.grid( row=2, column=2, padx=3, pady=3, columnspan=2 )
        self.warning_label.grid( row=3, column=0, padx=3, pady=3, columnspan=4 )

    def cancel( self ):
        global current_state, previous_state

        # clear text boxes
        self.name_entry.delete( 0, "end" )
        self.description_entry.delete( 0, "end" )

        # clear warning label
        self.warning_label.configure( text='' )

        temp_state = previous_state.copy( )
        previous_state = current_state.copy( )
        current_state = temp_state.copy( )

    def confirm( self ):
        global current_state, previous_state, manager, tree_v

        # get name and description as entered by user and clear text boxes
        name = self.name_entry.get( ).strip( )
        self.name_entry.insert( 0, '' )
        desc = self.description_entry.get( ).strip( )
        self.description_entry.insert( 0, '' )

        try:
            # create project
            manager.add_project( name, desc )

            # insert into widget
            tree_v.insert( '', 'end', iid='p' + name, text=name )

            # clear text entry widgets
            self.name_entry.delete( 0, "end" )
            self.description_entry.delete( 0, "end" )

            # clear warning label
            self.warning_label.configure( text='' )

            previous_state = current_state.copy( )
            current_state = [ name, None, None ]
        except Exception as e:
            print( e )
            self.warning_label.configure( text="A PROJECT WITH THIS NAME ALREADY EXISTS!" )


class EditProjectForm( ttk.LabelFrame ):
    def __init__( self, master, name="Edit project form" ):
        super( ).__init__( master, text=name, padding=( 5, 5, 5, 5 ) )
        self.name_label = ttk.Label( self, text="Name: " )
        self.description_label = ttk.Label( self, text="Desc: " )
        self.name_entry = ttk.Entry( self )
        self.description_entry = ttk.Entry( self )
        self.warning_label = ttk.Label( self, text="" )
        self.cancel_button = ttk.Button( self, text="Cancel", command=self.cancel )
        self.confirm_button = ttk.Button( self, text="Confirm", command=self.confirm )

        self.name_label.grid( row=0, column=0, padx=3, pady=3 )
        self.name_entry.grid( row=0, column=1, padx=3, pady=3, columnspan=3 )
        self.description_label.grid( row=1, column=0, padx=3, pady=3 )
        self.description_entry.grid( row=1, column=1, padx=3, pady=3, columnspan=3 )
        self.cancel_button.grid( row=2, column=0, padx=3, pady=3, columnspan=2 )
        self.confirm_button.grid( row=2, column=2, padx=3, pady=3, columnspan=2 )
        self.warning_label.grid( row=3, column=0, padx=3, pady=3, columnspan=4 )

    def cancel( self ):
        global current_state, previous_state

        # clear entries
        self.name_entry.config( state='normal' )
        self.name_entry.delete( 0, 'end' )
        self.description_entry.delete( 0, 'end' )

        temp_state = previous_state.copy( )
        previous_state = current_state.copy( )
        current_state = temp_state.copy( )

    def confirm( self ):
        global current_state, previous_state

        # update the description
        manager.update_project_info( self.description_entry.get( ).strip( ) )

        # clear entries
        self.name_entry.config( state='normal' )
        self.name_entry.delete( 0, 'end' )
        self.description_entry.delete( 0, 'end' )

        previous_state = current_state.copy( )
        current_state[ 2 ] = None


class AddBoardForm( ttk.LabelFrame ):
    def __init__( self, master, name="Add board form" ):
        super( ).__init__( master, text=name, padding=( 5, 5, 5, 5 ) )
        self.name_label = ttk.Label( self, text="Name: " )
        self.description_label = ttk.Label( self, text="Desc: " )
        self.name_entry = ttk.Entry( self )
        self.description_entry = ttk.Entry( self )
        self.warning_label = ttk.Label( self, text="" )
        self.cancel_button = ttk.Button( self, text="Cancel", command=self.cancel )
        self.confirm_button = ttk.Button( self, text="Confirm", command=self.confirm )

        self.name_label.grid( row=0, column=0, padx=3, pady=3 )
        self.name_entry.grid( row=0, column=1, padx=3, pady=3, columnspan=3 )
        self.description_label.grid( row=1, column=0, padx=3, pady=3 )
        self.description_entry.grid( row=1, column=1, padx=3, pady=3, columnspan=3 )
        self.cancel_button.grid( row=2, column=0, padx=3, pady=3, columnspan=2 )
        self.confirm_button.grid( row=2, column=2, padx=3, pady=3, columnspan=2 )
        self.warning_label.grid( row=3, column=0, padx=3, pady=3, columnspan=4 )

    def cancel( self ):
        global current_state, previous_state

        # clear text boxes
        self.name_entry.delete( 0, "end" )
        self.description_entry.delete( 0, "end" )

        # clear warning label
        self.warning_label.configure( text='' )

        temp_state = previous_state.copy( )
        previous_state = current_state.copy( )
        current_state = temp_state.copy( )

    def confirm( self ):
        global current_state, previous_state

        # get name, description and iid as entered by user and clear text boxes
        name = self.name_entry.get( ).strip( )
        self.name_entry.insert( 0, '' )
        desc = self.description_entry.get( ).strip( )
        self.description_entry.insert( 0, '' )
        iid = manager.get_next_board_uid( )

        # get list of existing boards and check if name is already present
        existing_boards = set( map( lambda event: event[ 1 ], manager.get_all_boards( ) ) )
        if name in existing_boards:
            self.warning_label.configure( text='A BOARD WITH THIS NAME ALREADY EXISTS' )
        else:
            # create project
            manager.add_board( iid, name, desc )

            # insert into widget
            tree_v.insert( 'p' + str( current_state[ 0 ] ), 'end', iid=(str( iid ) + " " + str( current_state[ 0 ] )), text=name )

            # clear text entry widgets
            self.name_entry.delete( 0, "end" )
            self.description_entry.delete( 0, "end" )

            # clear warning label
            self.warning_label.configure( text='' )

            previous_state = current_state.copy( )
            current_state[ 1 ] = str( iid )
            current_state[ 2 ] = None


class EditBoardForm( ttk.LabelFrame ):
    def __init__( self, master, name="Edit board form" ):
        super( ).__init__( master, text=name, padding=( 5, 5, 5, 5 ) )
        self.name_label = ttk.Label( self, text="Name: " )
        self.description_label = ttk.Label( self, text="Desc: " )
        self.name_entry = ttk.Entry( self )
        self.description_entry = ttk.Entry( self )
        self.warning_label = ttk.Label( self, text="" )
        self.cancel_button = ttk.Button( self, text="Cancel", command=self.cancel )
        self.confirm_button = ttk.Button( self, text="Confirm", command=self.confirm )

        self.name_label.grid( row=0, column=0, padx=3, pady=3 )
        self.name_entry.grid( row=0, column=1, padx=3, pady=3, columnspan=3 )
        self.description_label.grid( row=1, column=0, padx=3, pady=3 )
        self.description_entry.grid( row=1, column=1, padx=3, pady=3, columnspan=3 )
        self.cancel_button.grid( row=2, column=0, padx=3, pady=3, columnspan=2 )
        self.confirm_button.grid( row=2, column=2, padx=3, pady=3, columnspan=2 )
        self.warning_label.grid( row=3, column=0, padx=3, pady=3, columnspan=4 )

    def cancel( self ):
        global current_state, previous_state

        # clear text boxes
        self.name_entry.delete( 0, 'end' )
        self.description_entry.delete( 0, 'end' )

        # clear warning label
        self.warning_label.configure( text='' )

        temp_state = previous_state.copy( )
        previous_state = current_state.copy( )
        current_state = temp_state.copy( )

    def confirm( self ):
        global current_state, previous_state

        name = self.name_entry.get( ).strip( )
        desc = self.description_entry.get( ).strip( )
        iid = int( current_state[ 1 ] )

        existing_boards = set( map( lambda event: event[ 1 ], manager.get_all_boards( ) ) )

        if name != manager.get_board_name( current_state[ 1 ] ) and name in existing_boards:
            self.warning_label.configure( text="A BOARD WITH THIS NAME ALREADY EXISTS" )
        else:
            # update board
            manager.update_board( iid, name, desc )

            # update tree view item
            tree_v.item( (str( current_state[ 1 ] ) + " " + str( current_state[ 0 ] )), text=name )

            # clear text entry widgets
            self.name_entry.delete( 0, "end" )
            self.description_entry.delete( 0, "end" )

            # clear warning label
            self.warning_label.configure( text='' )

            previous_state = current_state.copy( )
            current_state[ 2 ] = None


class AddCardForm( ttk.LabelFrame ):
    def __init__( self, master, name="Add card form" ):
        super( ).__init__( master, text=name, padding=( 5, 5, 5, 5 ) )
        self.name_label = ttk.Label( self, text="Name: " )
        self.description_label = ttk.Label( self, text="Desc: " )
        self.name_entry = ttk.Entry( self )
        self.description_entry = ttk.Entry( self )
        self.cancel_button = ttk.Button( self, text="Cancel", command=self.cancel )
        self.confirm_button = ttk.Button( self, text="Confirm", command=self.confirm )
        self.selection_frame = ttk.LabelFrame( self, text="Select board frame", padding=(5, 5, 5, 5) )
        self.selection_canvas = tk.Canvas( self.selection_frame, highlightthickness=0, borderwidth=0, background='#fafafa' )
        self.selection_scrollbar = ttk.Scrollbar( self.selection_frame, orient='vertical', command=self.selection_canvas.yview )
        self.frame_in_canvas = ttk.LabelFrame( self.selection_canvas, text="Frame in canvas", padding=(5, 5, 5, 5) )

        self.selection_canvas.configure( yscrollcommand=self.selection_scrollbar.set )
        self.frame_in_canvas.bind( "<Configure>", lambda event: self.selection_canvas.configure( width=self.frame_in_canvas.winfo_width( ), height=self.frame_in_canvas.winfo_height( ), scrollregion=self.selection_canvas.bbox( "all" ) ) )
        self.selection_canvas.bind( consts.VERTICAL_MOUSE_MOTION, lambda event: scroll_canvas( event, self.selection_canvas, self.selection_scrollbar ) )
        for child in get_all_children( self.selection_canvas ):
            child.bind( consts.VERTICAL_MOUSE_MOTION, lambda event: scroll_canvas( event, self.selection_canvas, self.selection_scrollbar ))

        self.selection_canvas.create_window( (4, 4), window=self.frame_in_canvas, anchor="nw" )
        self.selection_canvas.pack( side="left", fill="both", expand=True )
        self.selection_scrollbar.pack( side="right", fill="y" )
        self.name_label.grid( row=0, column=0, padx=3, pady=3 )
        self.name_entry.grid( row=0, column=1, padx=3, pady=3, columnspan=3, sticky="ew" )
        self.description_label.grid( row=1, column=0, padx=3, pady=3 )
        self.description_entry.grid( row=1, column=1, padx=3, pady=3, columnspan=3, sticky="ew" )
        self.selection_frame.grid( row=2, column=0, padx=3, pady=3, columnspan=4, sticky="ew" )
        self.cancel_button.grid( row=3, column=0, padx=3, pady=3, columnspan=2 )
        self.confirm_button.grid( row=3, column=2, padx=3, pady=3, columnspan=2 )

    def cancel( self ):
        global current_state, previous_state

        self.name_entry.delete( 0, "end" )
        self.description_entry.delete( 0, "end" )

        temp_state = previous_state.copy( )
        previous_state = current_state.copy( )
        current_state = temp_state.copy( )

        for child in self.frame_in_canvas.winfo_children( ):
            child.grid_forget( )
            child.destroy( )

    def confirm( self ):
        global current_state, previous_state, board_checkbox_states, boards, manager

        # get name, description and iid as entered by user and clear text boxes
        name = self.name_entry.get( ).strip( )
        self.name_entry.insert( 0, '' )
        desc = self.description_entry.get( ).strip ( )
        self.description_entry.insert( 0, '' )
        iid = manager.get_next_card_uid( )

        # create project
        manager.add_card( iid, name, desc, None )

        for state, board in zip( board_checkbox_states, boards ):
            if state.get( ):
                manager.add_card_to_board( board[ 0 ], iid )

        # clear text entry widgets
        self.name_entry.delete( 0, "end" )
        self.description_entry.delete( 0, "end" )

        previous_state = current_state.copy( )
        # current_state[ 1 ] = str( iid )
        current_state[ 2 ] = None

        for child in self.frame_in_canvas.winfo_children( ):
            child.grid_forget( )
            child.destroy( )


class EditProjectCardForm( ttk.LabelFrame ):
    def __init__( self, master, name="Edit project card" ):
        super( ).__init__( master, text=name, padding=(5, 5, 5, 5) )
        self.name_label = ttk.Label( self, text="Name:" )
        self.name_entry = ttk.Entry( self )
        self.desc_label = ttk.Label( self, text="Desc:" )
        self.desc_entry = ttk.Entry( self )
        self.selection_frame = ttk.LabelFrame( self, text="edit card board root" )
        self.selection_canvas = tk.Canvas( self.selection_frame, highlightthickness=0, borderwidth=0, background='#fafafa' )
        self.selection_scrollbar = ttk.Scrollbar( self.selection_frame, orient='vertical', command=self.selection_canvas.yview )
        self.frame_in_canvas = ttk.LabelFrame( self.selection_canvas, text="Frame in Canvas", padding=(5, 5, 5, 5) )
        self.cancel_button = ttk.Button( self, text="Cancel", command=self.cancel )
        self.confirm_button = ttk.Button( self, text="Confirm", command=self.confirm, style="Accent.TButton" )
        self.delete_button = ttk.Button( self, text="Delete", command=self.delete )

        self.selection_canvas.configure( yscrollcommand=self.selection_scrollbar.set )
        self.frame_in_canvas.bind( "<Configure>", lambda event: self.selection_canvas.configure( width=self.frame_in_canvas.winfo_width( ), height=self.frame_in_canvas.winfo_height( ), scrollregion=self.selection_canvas.bbox( "all" ) ) )
        self.selection_canvas.bind( consts.VERTICAL_MOUSE_MOTION, lambda event: scroll_canvas( event, self.selection_canvas, self.selection_scrollbar ) )
        for child in get_all_children( self.selection_canvas ):
            child.bind( consts.VERTICAL_MOUSE_MOTION, lambda event: scroll_canvas( event, self.selection_canvas, self.selection_scrollbar ) )

        self.selection_canvas.create_window( (4, 4), window=self.frame_in_canvas, anchor="center" )
        self.selection_canvas.pack( side="left", fill="both", expand=True )
        self.selection_scrollbar.pack( side="right", fill="y" )
        self.name_label.grid( row=0, column=0, padx=3, pady=3, columnspan=2, sticky="w" )
        self.name_entry.grid( row=1, column=1, padx=3, pady=3, columnspan=2, sticky="ew" )
        self.desc_label.grid( row=2, column=0, padx=3, pady=3, columnspan=2, sticky="w" )
        self.desc_entry.grid( row=3, column=1, padx=3, pady=3, columnspan=2, sticky="ew" )
        self.selection_frame.grid( row=4, column=0, padx=3, pady=3, columnspan=3, sticky="ew" )
        self.cancel_button.grid( row=5, column=0, padx=3, pady=3 )
        self.confirm_button.grid( row=5, column=1, padx=3, pady=3 )
        self.delete_button.grid( row=5, column=2, padx=3, pady=3 )
        self.rowconfigure( index=4, weight=1 )

    def cancel( self ):
        global edit_card_flag
        edit_card_flag = False

    def confirm( self ):
        global current_state, previous_state, previous_loop_state, edit_card_flag
        global board_checkbox_states, boards

        edit_card_flag = False
        manager.update_card( edit_card_uid, self.name_entry.get( ).strip( ), self.desc_entry.get( ).strip( ), None )
        valid_boards = manager.get_boards_of_card( edit_card_uid )

        for (state, board) in zip( board_checkbox_states, boards ):
            board_uid = board[ 0 ]

            if state.get( ) and (board_uid not in valid_boards):
                manager.add_card_to_board( board_uid, edit_card_uid )
                print( f"ADDING CARD TO BOARD {board[ 1 ]}" )
            elif not state.get( ) and (board_uid in valid_boards):
                manager.remove_card_from_board( board_uid, edit_card_uid )
                print( f"REMOVING CARD FROM BOARD {board[ 1 ]}" )

        update_state( root )

    def delete( self ):
        print( "DELETING CARD FROM PROJECT" )
        manager.delete_card( edit_card_uid )
        update_state( root )


class EditBoardCardForm( ttk.LabelFrame ):
    def __init__( self, master, name="Edit board card" ):
        super( ).__init__( master, text=name, padding=(5, 5, 5, 5) )
        self.name_label = ttk.Label( self, text="Name:" )
        self.name_entry = ttk.Entry( self )
        self.desc_label = ttk.Label( self, text="Desc:" )
        self.desc_entry = ttk.Entry( self )
        self.edit_tag_frame = ttk.LabelFrame( self, text="Add and Del tags", padding=(5, 5, 5, 5) )
        self.tag_key_entry = ttk.Combobox( self.edit_tag_frame )
        self.tag_val_entry = ttk.Combobox( self.edit_tag_frame )
        self.new_tag_button = ttk.Button( self.edit_tag_frame, text="Add", command=self.add_tag )
        self.del_tag_button = ttk.Button( self.edit_tag_frame, text="Delete", command=self.del_tag )
        self.tag_frame = ttk.LabelFrame( self, text="edit card tag root" )
        self.tag_canvas = tk.Canvas( self.tag_frame, highlightthickness=0, borderwidth=0, background='#fafafa' )
        self.tag_scrollbar = ttk.Scrollbar( self.tag_frame, orient='vertical', command=self.tag_canvas.yview )
        self.frame_in_canvas = ttk.LabelFrame( self.tag_canvas, text="Frame in Canvas", padding=(5, 5, 5, 5) )
        self.cancel_button = ttk.Button( self, text="Cancel", command=self.cancel )
        self.confirm_button = ttk.Button( self, text="Confirm", command=self.confirm, style="Accent.TButton" )
        self.remove_button = ttk.Button( self, text="Remove", command=self.remove )

        self.card_tag_keys = [ ]
        self.tag_key_entry.bind( "<FocusIn>", self.update_tag_entries )
        self.tag_key_entry.bind( "<FocusOut>", self.update_tag_entries )
        self.tag_key_entry.bind( "<KeyRelease>", self.update_tag_entries )
        self.tag_val_entry[ "state" ] = tk.DISABLED
        self.new_tag_button[ "state" ] = tk.DISABLED
        self.del_tag_button[ "state" ] = tk.DISABLED

        self.tag_canvas.configure( yscrollcommand=self.tag_scrollbar.set )
        self.frame_in_canvas.bind( "<Configure>", lambda event: self.tag_canvas.configure( width=self.frame_in_canvas.winfo_width( ), height=self.frame_in_canvas.winfo_height( ), scrollregion=self.tag_canvas.bbox( "all" ) ) )
        self.tag_canvas.bind( consts.VERTICAL_MOUSE_MOTION, lambda event: scroll_canvas( event, self.tag_canvas, self.tag_scrollbar ) )
        for child in get_all_children( self.tag_canvas ):
            child.bind( consts.VERTICAL_MOUSE_MOTION, lambda event: scroll_canvas( event, self.tag_canvas, self.tag_scrollbar ) )

        self.tag_canvas.create_window( (4, 4), window=self.frame_in_canvas, anchor="center" )
        self.tag_canvas.pack( side="left", fill="both", expand=True )
        self.tag_scrollbar.pack( side="right", fill="y" )
        self.name_label.grid( row=0, column=0, columnspan=2, sticky="w" )
        self.name_entry.grid( row=1, column=1, columnspan=2, sticky="ew" )
        self.desc_label.grid( row=2, column=0, columnspan=2, sticky="w" )
        self.desc_entry.grid( row=3, column=1, columnspan=2, sticky="ew" )
        self.tag_key_entry.grid( row=0, column=1 )
        self.tag_val_entry.grid( row=0, column=2 )
        self.new_tag_button.grid( row=0, column=3 )
        self.del_tag_button.grid( row=0, column=4 )
        self.edit_tag_frame.grid( row=4, column=0, columnspan=3, sticky="ew" )
        self.tag_frame.grid( row=5, column=0, columnspan=3, sticky="ew" )
        self.cancel_button.grid( row=6, column=0 )
        self.confirm_button.grid( row=6, column=1 )
        self.remove_button.grid( row=6, column=2 )
        # self.columnconfigure( index=1, weight=1 )

    def update_tag_entries( self, *params ):
        # print("hihihihihihihhiiiiiiiiiiiii")
        self.tag_key_entry.state(["invalid"])
        self.tag_val_entry[ "state" ] = tk.DISABLED
        self.new_tag_button[ "state" ] = tk.DISABLED
        self.del_tag_button[ "state" ] = tk.DISABLED
        if self.tag_key_entry.get( ).strip( ):
            if self.tag_key_entry.get( ) not in self.card_tag_keys:
                self.tag_key_entry.state(["!invalid"])
                self.tag_val_entry[ "state" ] = tk.NORMAL
                self.new_tag_button[ "state" ] = tk.NORMAL
                self.tag_val_entry.configure( values=manager.get_tag_values_of_tag_key(current_state[ 1 ], self.tag_key_entry.get( )) )
            else:
                self.tag_val_entry[ "state" ] = tk.NORMAL
                self.tag_val_entry.delete( 0, "end" )
                self.tag_val_entry[ "state" ] = tk.DISABLED
                self.del_tag_button[ "state" ] = tk.NORMAL

    def cancel( self ):
        global edit_card_flag
        edit_card_flag = False

    def confirm( self ):
        global current_state, previous_state, tag_name, tag_dropdown
        global tag_dict
        global edit_card_flag, edit_card_uid

        edit_card_flag = False
        manager.update_card( edit_card_uid, self.name_entry.get( ).strip( ), self.desc_entry.get( ).strip( ), None )

        for tag, entry in tag_dict.items( ):
            new_val = entry.get( ).strip( )
            if new_val:
                manager.update_card_tag_value( current_state[ 1 ], edit_card_uid, tag, new_val )

        update_state( root )

    def remove( self ):
        print( "REMOVING CARD FROM BOARD" )
        manager.remove_card_from_board( current_state[ 1 ], edit_card_uid )

        update_state( root )

    def add_tag( self ):
        print( "ADD CARD TAG" )

        global edit_card_flag

        tag_name = self.tag_key_entry.get( ).strip( )
        tag_value = self.tag_val_entry.get( ).strip( )

        manager.add_card_tag( current_state[ 1 ], edit_card_uid, tag_name, tag_value )

        self.tag_key_entry.delete( 0, "end" )
        self.tag_val_entry.delete( 0, "end" )

        update_state( root )
        edit_card_flag = True
        update_internal_state( )

    def del_tag( self ):
        print( "DELETING CARD TAG" )

        global edit_card_flag

        tag_name = self.tag_key_entry.get( ).strip( )

        manager.delete_card_tag( current_state[ 1 ], edit_card_uid, tag_name )

        self.tag_key_entry.delete( 0, "end" )
        self.tag_val_entry.delete( 0, "end" )

        update_state( root )
        edit_card_flag = True
        update_internal_state( )


def get_all_children( widget ):
    all_children = [ ]
    for child in widget.winfo_children():
        all_children.append(child)
        all_children.extend( get_all_children( child ) )
    return all_children

def scroll_canvas( _event, _canvas:tk.Canvas, _scrollbar:ttk.Scrollbar ):
    # print(_scrollbar.get())
    if _scrollbar.get( ) != ( 0.0, 1.0 ):
        _canvas.yview_scroll( ( _event.delta // consts.deltaFactor ), "units" )

def generate_column( _name, _cards, _cards_frame ):

    column_name_label   = ttk.Label( master = _cards_frame, text=_name, font = ("pointfree", 10))
    column_frame        = ttk.LabelFrame( _cards_frame, labelwidget = column_name_label, labelanchor="n", padding=(5, 5, 1, 5) )
    # column_canvas       = tk.Canvas( column_frame, borderwidth=0, background="#000000" )
    column_canvas       = tk.Canvas( column_frame, background="#fafafa" )
    column_scrollbar    = ttk.Scrollbar( column_frame, orient="vertical", command=column_canvas.yview )
    frame_in_canvas     = ttk.LabelFrame( column_canvas, text="Frame in canvas", padding=(5, 5, 5, 5) )

    column_canvas.configure( yscrollcommand=column_scrollbar.set )

    for row, card_details in enumerate( _cards ):
        card = Card( frame_in_canvas, card_details[ 0 ], card_details[ 1 ], card_details[ 2 ] )
        card.grid( row=row, column=0, padx=5, pady=5, sticky="news" )

    column_canvas.bind( consts.VERTICAL_MOUSE_MOTION, lambda event: scroll_canvas( event, column_canvas, column_scrollbar ) )
    for child in get_all_children( column_canvas ):
        # print( child.winfo_name() )
        child.bind( consts.VERTICAL_MOUSE_MOTION, lambda event: scroll_canvas( event, column_canvas, column_scrollbar ) )

    column_canvas.bind( "<Configure>", lambda event: column_canvas.itemconfig( "frame", width=column_canvas.winfo_width( ) - 5 ) )
    frame_in_canvas.bind( "<Configure>", lambda event: column_canvas.configure( scrollregion=column_canvas.bbox( "all" ) ) )
    # print( frame_in_canvas.winfo_width() )
    # frame_in_canvas.bind( "<Configure>", lambda event: column_canvas.configure( width=frame_in_canvas.winfo_width( ) + 5, height= 1 ) )
    # frame_in_canvas.bind( "<Configure>", lambda event: print("hi" ) )
    frame_in_canvas.columnconfigure( index=0, weight=1 )
    column_canvas.create_window( (0, 0), window=frame_in_canvas, anchor="nw", tags="frame" )
    column_scrollbar.pack( side="right", fill="y" )
    column_canvas.pack( side="left", fill="both", expand=True )
    return column_frame

def connect( _username, _hostname, _password ):
    global prompt_closed, prompt
    manager.connect( _username, _hostname, _password )
    prompt_closed = True

def tree_click( _event ):

    global current_state, previous_state

    if not len( tree_v.selection ( ) ):
        return

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
    global edit_project_form

    # set default to current name and description
    edit_project_form.name_entry.insert( 0, current_state[ 0 ] )
    edit_project_form.description_entry.insert( 0, manager.get_project_info( ) )
    edit_project_form.name_entry.config( state='disabled' )

    previous_state     = current_state.copy( )
    current_state[ 2 ] = consts.EDIT_PROJECT_FORM

def add_board_init( ):
    global current_state, previous_state

    previous_state     = current_state.copy( )
    current_state[ 2 ] = consts.NEW_BOARD_FORM

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
    global edit_board_form

    edit_board_form.name_entry.insert( 0, manager.get_board_name( current_state[ 1 ] ) )
    edit_board_form.description_entry.insert( 0, manager.get_board_description( current_state[ 1 ] ) )

    previous_state     = current_state.copy( )
    current_state[ 2 ] = consts.EDIT_BOARD_FORM

def add_card_init( ):
    global current_state, previous_state
    global board_checkbox_states

    previous_state     = current_state.copy( )
    current_state[ 2 ] = consts.NEW_CARD_FORM

def update_internal_state():
    global current_state, previous_state, previous_loop_state, tag_name, tag_dropdown
    global add_project_form, edit_project_form, add_board_form, edit_board_form, add_card_form
    global board_checkbox_states, boards
    global edit_card_flag, edit_card_flag_prv, edit_card_uid
    global tag_dict, edit_project_form, edit_board_card

    print( f"NOW EDITING {edit_card_uid}" if edit_card_flag else "NOW NOT EDITING" )

    edit_project_card.name_entry.delete( 0, "end" )
    edit_project_card.desc_entry.delete( 0, "end" )
    edit_board_card.name_entry.delete( 0, "end" )
    edit_board_card.desc_entry.delete( 0, "end" )

    edit_board_card.card_tag_keys = [ ]

    edit_board_card.tag_key_entry.configure(values=[ ])
    edit_board_card.tag_val_entry.configure(values=[ ])

    for child in edit_project_card.frame_in_canvas.winfo_children():
        child.grid_forget()
        child.destroy()

    for child in edit_board_card.frame_in_canvas.winfo_children():
        child.grid_forget()
        child.destroy()
        print("DESTROYING KEY VALUE PAIRS")

    tag_dict = {}

    edit_project_card.grid_forget()
    edit_board_card.grid_forget()

    if edit_card_flag:
        card = manager.get_card( edit_card_uid )
        if current_state[1] is not None:
            print("BOARD CARDS")
            edit_board_card.name_entry.insert( 0, card[ 0 ] )
            edit_board_card.desc_entry.insert( 0, card[ 1 ] )

            tags = manager.get_card_tags( current_state[1], edit_card_uid )
            if tags[0][0] is None:
                tags = tags[1:]

            card_tag_keys = [ tags[i][0] for i in range(len(tags)) ]
            all_tag_keys = manager.get_board_tag_names( current_state[1] )
            if all_tag_keys[ 0 ] is None:
                all_tag_keys = all_tag_keys[1::]

            edit_board_card.card_tag_keys = card_tag_keys
            edit_board_card.tag_key_entry.configure(values=all_tag_keys)
            # edit_board_card.tag_val_entry.configure(values=tag_vals)

            for row, ( tkey, tval ) in enumerate( tags ):
                key_label = ttk.Label( edit_board_card.frame_in_canvas, text = tkey )
                val_entry = ttk.Combobox( edit_board_card.frame_in_canvas, values=manager.get_tag_values_of_tag_key( current_state[ 1 ], tkey ) )
                val_entry.insert( 0, tval )
                key_label.grid( row=2*row, column=0, columnspan=1 )
                val_entry.grid( row=2*row + 1, column=1, columnspan=3 )
                tag_dict[tkey] = val_entry

            edit_board_card.grid( row=0, column=1, padx=3, pady=3, sticky="news" )

        else:
            print("PROJECT CARDS")
            edit_project_card.name_entry.insert( 0, card[ 0 ] )
            edit_project_card.desc_entry.insert( 0, card[ 1 ] )

            boards = manager.get_all_boards()
            valid_boards = manager.get_boards_of_card( edit_card_uid )
            board_checkbox_states   = [ tk.BooleanVar( value=(board[0] in valid_boards) ) for board in boards ]

            for row, ( state, board ) in enumerate( zip( board_checkbox_states, boards ) ):
                c   = ttk.Checkbutton( edit_project_card.frame_in_canvas, text=board[ 1 ], variable=state )
                c.grid( row=row, column=0, padx=3, pady=3, sticky="w" )

            edit_project_card.grid( row=0, column=1, padx=3, pady=3, sticky="news" )

def update_state( _root_window ):
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

    if ( previous_loop_state[ 0 ] != current_state[ 0 ] ) or ( previous_loop_state[ 1 ] != current_state[ 1 ] ):
        tag_name.set( consts.NO_TAG_SELECTED )

    for child in main_frame.winfo_children():
        child.grid_forget( )

    if cards_frame:
        cards_frame.columnconfigure( "all", weight=0 )  # Clears effect of all previous columnconfigure as frame remembers it even after grid forget
        cards_frame.columnconfigure( 0, weight=1 )      # Default columnconfigure of column 0
        for child in cards_frame.winfo_children( ):
            child.grid_forget( )
            child.destroy( )

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

        all_cards_column    = generate_column( "All Cards", manager.get_all_cards( ), cards_frame )
        all_cards_column.grid( row=0, column=0, padx=5, pady=5, sticky="news" )
        cards_frame.rowconfigure( 0, weight=1 )
        cards_frame.columnconfigure( "all", weight=1 )
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

        if tag_name.get( ) == consts.NO_TAG_SELECTED:
            all_cards_column = generate_column( "All Cards in this Board", manager.get_cards_in_board( current_state[ 1 ] ), cards_frame )
            all_cards_column.grid( row=0, column=0, padx=5, pady=5, sticky="news" )
            cards_frame.columnconfigure( "all", weight=1 )
        else:
            grouped_cards = manager.get_board_grouped_cards( current_state[ 1 ], tag_name.get( ) )
            for j, tag_value in enumerate( grouped_cards ):
                column = generate_column( tag_value, grouped_cards[ tag_value ], cards_frame )
                column.grid( row=0, column=j, padx=5, pady=5, sticky="news")
        cards_frame.rowconfigure( 0, weight=1 )
        cards_frame.columnconfigure( "all", weight=1 )
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
        board_checkbox_states   = [ tk.BooleanVar( value=False ) for _ in range( len( boards ) ) ]

        for row, ( state, board ) in enumerate( zip( board_checkbox_states, boards ) ):
            c   = ttk.Checkbutton( add_card_form.frame_in_canvas, text=board[ 1 ], variable=state )
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
top_frame   = ttk.LabelFrame( root, text="top frame", padding=( 5, 5, 5, 5 ) )
left_frame  = ttk.LabelFrame( root, text="left frame", padding=( 5, 5, 5, 5 ) )
main_frame  = ttk.LabelFrame( root, text="main frame", padding=( 5, 5, 5, 5 ) )
cards_frame = ttk.LabelFrame( main_frame, text="cards frame", padding=( 5, 5, 5, 5 ) )

add_project_form  = AddProjectForm( main_frame )
edit_project_form = EditProjectForm( main_frame )
add_board_form    = AddBoardForm( main_frame )
edit_board_form   = EditBoardForm( main_frame )
add_card_form     = AddCardForm( main_frame )
edit_project_card = EditProjectCardForm( main_frame )
edit_board_card   = EditBoardCardForm( main_frame )

new_project_button                  = ttk.Button( top_frame, text="new project", command=add_project_init )
delete_project_button               = ttk.Button( top_frame, text="delete project", command=delete_project_confirm )
edit_project_button                 = ttk.Button( top_frame, text="edit project", command=edit_project_init )
new_board_button                    = ttk.Button( top_frame, text="new board", command=add_board_init )
delete_board_button                 = ttk.Button( top_frame, text="delete board", command=delete_board_confirm )
edit_board_button                   = ttk.Button( top_frame, text="edit board", command=edit_board_init )
new_card_button                     = ttk.Button( top_frame, text="new card", command=add_card_init )
tag_name                            = tk.StringVar( value=consts.NO_TAG_SELECTED )
tag_dropdown                        = ttk.OptionMenu( top_frame,  tag_name, "", consts.NO_TAG_SELECTED, "something", style="my.TMenubutton", command=lambda event: update_state( root ) )
tag_dropdown[ "menu" ].entryconfigure( 0, font = ( "pointfree", 9,"italic" ) )
tag_dropdown[ "menu" ].insert_separator( 1 )
# tag_dropdown = ChecklistCombobox( top_frame, values=("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20") )
# tag_dropdown[ "state" ] = tk.DISABLED
# temp_button = ttk.Button( top_frame, text="Reload", command=lambda: update_state( root ))

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
# temp_button.grid( row=0, column=8, padx=3, pady=3, sticky="ew" )

top_frame.columnconfigure( index="all", weight=1 )

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
update_state( root )
# root.mainloop( )
while 1:
    try:
        root.update_idletasks( )
        root.update( )
        time.sleep( 0.000001 )
    except Exception as e:
        print( e )
        break

    if edit_card_flag_prv != edit_card_flag:
        update_internal_state()
        edit_card_flag_prv = edit_card_flag

    if previous_loop_state != current_state:
        update_state( root )
        print( "STATE UPDATED" )
        previous_loop_state = current_state.copy( )

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
