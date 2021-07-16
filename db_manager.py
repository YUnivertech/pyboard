import os
import sqlite3

import consts

if not os.path.isdir( consts.PROJECTS_FOLDER ):
    os.mkdir( consts.PROJECTS_FOLDER )


class DBManager:

    def __init__( self ):
        self.db     = None
        self.conn   = None
        self.cursor = None

    def connect( self, _project_name ):
        projects    = os.listdir( consts.PROJECTS_FOLDER )
        db_exists   = ( _project_name + ".db" ) in projects
        self.db     = consts.PROJECTS_FOLDER + "/" + _project_name + ".db"
        self.conn   = sqlite3.connect( self.db )
        self.cursor = self.conn.cursor( )
        if not db_exists:
            self.cursor.execute( "CREATE TABLE IF NOT EXISTS 'Cards'( 'uid' UNSIGNED BIGINT PRIMARY KEY, 'data' TEXT );" )
            self.cursor.execute( "CREATE TABLE IF NOT EXISTS 'Boards'( 'uid' UNSIGNED BIGINT PRIMARY KEY, 'info' TEXT, 'data' TEXT );" )
            self.cursor.execute( "CREATE TABLE IF NOT EXISTS 'Info'( 'project_data' TEXT, 'board_last_used_uid' UNSIGNED BIGINT, 'card_last_used_uid' UNSIGNED BIGINT );" )
            self.cursor.execute( "INSERT INTO `Info` ( `board_last_used_uid`, `card_last_used_uid` ) VALUES ( '0', '0' );" )
            self.conn.commit( )

    def get_next_board_uid( self ):
        self.cursor.execute( "SELECT `board_last_used_uid` FROM `Info`;" )
        fetched_data   = self.cursor.fetchall( )
        next_board_uid = fetched_data[ 0 ][ 0 ] + 1
        consts.dbg( 1, "Class DBManager - function get_next_board_uid - value of next_board_uid:", next_board_uid )
        return next_board_uid

    def get_next_card_uid( self ):
        self.cursor.execute( "SELECT `card_last_used_uid` FROM `Info`;" )
        fetched_data  = self.cursor.fetchall( )
        next_card_uid = fetched_data[ 0 ][ 0 ] + 1
        consts.dbg( 1, "Class DBManager - function get_next_card_uid - value of next_card_uid:", next_card_uid )
        return next_card_uid

    def add_board( self, _board_uid, _board_info ):
        consts.dbg( 1, "Class DBManager - function add_board - value of _board_uid:", _board_uid )
        self.cursor.execute( "INSERT INTO `Boards` ( `uid`, `info` ) VALUES ( ?, ? );", ( _board_uid, _board_info, ) )
        self.cursor.execute( "UPDATE `Info` SET `board_last_used_uid` = ?;", ( _board_uid, ) )
        self.conn.commit( )

    def add_card( self, _card_uid, _card_data ):
        consts.dbg( 1, "Class DBManager - function add_card - value of _card_uid:", _card_uid )
        self.cursor.execute( "INSERT INTO `Cards` ( `uid`, `data` ) VALUES ( ?, ? );", ( _card_uid, _card_data ) )
        self.cursor.execute( "UPDATE `Info` SET `card_last_used_uid` = ?;", ( _card_uid, ) )
        self.conn.commit( )

    def update_project_info( self, _project_info ):
        self.cursor.execute( "UPDATE `Info` SET `project_data` = ?;", ( _project_info, ) )
        self.conn.commit( )

    def update_board_info( self, _board_uid, _board_info ):
        self.cursor.execute( "UPDATE `Boards` SET `info` = ? WHERE `uid` = ?;", ( _board_info, _board_uid ) )
        self.conn.commit( )

    def update_board_data( self, _board_uid, _board_data ):
        self.cursor.execute( "UPDATE `Boards` SET `data` = ? WHERE `uid` = ?;", ( _board_data, _board_uid ) )
        self.conn.commit( )

    def update_card( self, _card_uid, _card_data ):
        self.cursor.execute( "UPDATE `Cards` SET `data` = ? WHERE `uid` = ?;", ( _card_data, _card_uid ) )
        self.conn.commit( )

    def delete_board( self, _board_uid ):
        self.cursor.execute( "DELETE FROM `Boards` WHERE `uid` = ?;", ( _board_uid, ) )
        self.conn.commit( )

    def delete_card( self, _card_uid ):
        # Delete card completely
        self.cursor.execute( "DELETE FROM `Cards` WHERE `uid` = ?;", ( _card_uid, ) )
        self.conn.commit( )

    def get_project_info( self ):
        self.cursor.execute( "SELECT `project_data` FROM `Info`;" )
        fetched_data = self.cursor.fetchall( )
        project_info = fetched_data[ 0 ][ 0 ]
        consts.dbg( 1, "Class DBManager - function get_project_info - value of project_info:", project_info )
        return project_info

    def get_board_info( self, _board_uid ):
        self.cursor.execute( "SELECT `info` FROM `Boards` WHERE `uid` = ?;", ( _board_uid, ) )
        fetched_data = self.cursor.fetchall( )
        board_info   = fetched_data[ 0 ][ 0 ]
        consts.dbg( 1, "Class DBManager - function get_board_info - value of board_info:", board_info )
        return board_info

    def get_all_boards_info( self ):
        self.cursor.execute( "SELECT `info` FROM `Boards`;" )
        fetched_data    = self.cursor.fetchall( )
        all_boards_info = [ ]
        for i in fetched_data:
            for board in i:
                all_boards_info.append( board )
        consts.dbg( 1, "Class DBManager - function get_all_boards_info - value of all_boards_info:", all_boards_info )
        return all_boards_info

    def get_board_data( self, _board_uid ):
        self.cursor.execute( "SELECT `data` FROM `Boards` WHERE `uid` = ?;", ( _board_uid, ) )
        fetched_data = self.cursor.fetchall( )
        board_data   = [ ]
        for i in fetched_data:
            for card in i:
                board_data.append( card )
        consts.dbg( 1, "Class DBManager - function get_board_data - value of board_data:", board_data )
        return board_data

    def get_all_boards_uid( self ):
        self.cursor.execute( "SELECT `uid` FROM `Boards`;" )
        fetched_data   = self.cursor.fetchall( )
        all_boards_uid = [ ]
        for i in fetched_data:
            for card in i:
                all_boards_uid.append( card )
        consts.dbg( 1, "Class DBManager - function get_all_boards_uid - value of all_boards_uid:", all_boards_uid )
        return all_boards_uid

    def get_card_from_uid( self, _card_uid ):
        self.cursor.execute( "SELECT `data` FROM `Cards` WHERE `uid` = ?;", ( _card_uid, ) )
        fetched_data = self.cursor.fetchall( )
        card         = fetched_data[0][0]
        consts.dbg( 1, "Class DBManager - function get_card_from_uid - value of card:", card )
        return fetched_data

    def get_all_cards( self ):
        self.cursor.execute( "SELECT `data` FROM `Cards`;" )
        fetched_data = self.cursor.fetchall( )
        all_cards    = [ ]
        for i in fetched_data:
            for card in i:
                all_cards.append( card )
        consts.dbg( 1, "Class DBManager - function get_all_cards - value of all_cards:", all_cards )
        return all_cards

    def get_all_cards_uid( self ):
        self.cursor.execute( "SELECT `uid` FROM `Cards`;" )
        fetched_data  = self.cursor.fetchall( )
        all_cards_uid = [ ]
        for i in fetched_data:
            for card in i:
                all_cards_uid.append( card )
        consts.dbg( 1, "Class DBManager - function get_all_cards_uid - value of all_cards_uid:", all_cards_uid )
        return all_cards_uid

    def get_unused_cards( self ):
        pass

    def stop( self ):
        self.conn.close( )
