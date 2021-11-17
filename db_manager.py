import os
import sqlite3

import send2trash

import consts

if not os.path.isdir( consts.PROJECTS_FOLDER ):
    os.mkdir( consts.PROJECTS_FOLDER )


class DBManager:

    def __init__( self ):
        self.db     = None
        self.conn   = None
        self.cursor = None

        self.get_active_project = lambda: self.db[ len( consts.PROJECTS_FOLDER ) + 1 + len( consts.PROJECT_PREFIX ):-3 ]

    def connect( self, _username, _hostname, _password ):
        print( "Connecting to {}@{} {}".format( _username, _hostname, _password ) )

    def use_project( self, _project_name ):
        self.stop( )
        projects      = os.listdir( consts.PROJECTS_FOLDER )
        _project_name = consts.PROJECT_PREFIX + _project_name
        db_exists     = ( _project_name + ".db" ) in projects
        if not db_exists:
            raise FileNotFoundError( "DB does not exist" )
            # return False
        else:
            self.db     = consts.PROJECTS_FOLDER + "/" + _project_name + ".db"
            self.conn   = sqlite3.connect( self.db )
            self.cursor = self.conn.cursor( )
        # return True

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

    def add_project( self, _project_name, _project_description ):
        projects = os.listdir( consts.PROJECTS_FOLDER )
        _project_name = consts.PROJECT_PREFIX + _project_name
        db_exists = ( _project_name + ".db" ) in projects
        if db_exists:
            raise FileExistsError( "DB already exists" )
            # return False
        else:
            self.db     = consts.PROJECTS_FOLDER + "/" + _project_name + ".db"
            self.conn   = sqlite3.connect( self.db )
            self.cursor = self.conn.cursor( )
            self.cursor.execute( "CREATE TABLE IF NOT EXISTS 'Cards'"
                                    "( "
                                        "'uid' UNSIGNED BIGINT PRIMARY KEY, "
                                        "'name' TEXT, 'description' TEXT, "
                                        "'color' TEXT "
                                    ");" )
            self.cursor.execute( "CREATE TABLE IF NOT EXISTS 'Boards'"
                                    "( "
                                        "'uid' UNSIGNED BIGINT PRIMARY KEY, "
                                        "'name' TEXT, "
                                        "'description' TEXT "
                                    ");" )
            self.cursor.execute( "CREATE TABLE IF NOT EXISTS 'Relations'"
                                    "( "
                                        "'board_uid' UNSIGNED BIGINT, "
                                        "'tag_name' TEXT, 'tag_value' TEXT, "
                                        "'card_uid' UNSIGNED BIGINT, "
                                        "UNIQUE( 'board_uid', 'tag_name', 'card_uid' ), "
                                        "FOREIGN KEY( card_uid ) REFERENCES Cards( uid ) ON DELETE CASCADE, "
                                        "FOREIGN KEY( board_uid ) REFERENCES Boards( uid ) ON DELETE CASCADE "
                                    ");" )
            self.cursor.execute( "CREATE TABLE IF NOT EXISTS 'Info'"
                                    "( "
                                        "'project_info' TEXT, "
                                        "'board_last_used_uid' UNSIGNED BIGINT, "
                                        "'card_last_used_uid' UNSIGNED BIGINT "
                                    ");" )
            self.cursor.execute( "INSERT INTO `Info` "
                                    "( `project_info`, `board_last_used_uid`, `card_last_used_uid` ) "
                                    "VALUES ( ?, '0', '0' );",
                                    ( _project_description, ) )
            self.conn.commit( )

    def add_board( self, _board_uid, _board_name, _board_description ):
        consts.dbg( 1, "Class DBManager - function add_board - value of _board_uid:", _board_uid )
        self.cursor.execute( "INSERT INTO `Boards` "
                                "( `uid`, `name`, `description` ) "
                                "VALUES ( ?, ?, ? );",
                                ( _board_uid, _board_name, _board_description ) )
        self.cursor.execute( "UPDATE `Info` SET `board_last_used_uid` = ?;", ( _board_uid, ) )
        self.conn.commit( )

    def add_card( self, _card_uid, _card_name, _card_description, _card_color ):
        consts.dbg( 1, "Class DBManager - function add_card - value of _card_uid:", _card_uid )
        self.cursor.execute( "INSERT INTO `Cards` "
                                "( `uid`, `name`, `description`, `color` ) "
                                "VALUES ( ?, ?, ?, ? );",
                                ( _card_uid, _card_name, _card_description, _card_color ) )
        self.cursor.execute( "UPDATE `Info` "
                                "SET `card_last_used_uid` = ?;",
                                ( _card_uid, ) )
        self.conn.commit( )

    def add_card_to_board( self, _board_uid, _card_uid ):
        self.cursor.execute( "INSERT INTO `Relations` "
                                "( `board_uid`, `card_uid` ) "
                                "VALUES ( ?, ? );",
                                ( _board_uid, _card_uid ) )
        self.conn.commit( )

    def add_card_tag( self, _board_uid, _card_uid, _tag_name, _tag_value ):
        self.cursor.execute( "INSERT INTO `Relations` "
                                "( `board_uid`, `card_uid`, `tag_name`, `tag_value` ) "
                                "VALUES ( ?, ?, ?, ? );",
                                ( _board_uid, _card_uid, _tag_name, _tag_value ) )
        self.conn.commit( )

    def add_card_tag_name( self, _board_uid, _card_uid, _tag_name ):
        self.cursor.execute( "INSERT INTO `Relations` "
                                "( `board_uid`, `card_uid`, `tag_name` ) "
                                "VALUES ( ?, ?, ? );",
                                ( _board_uid, _card_uid, _tag_name ) )
        self.conn.commit( )

    def make_tag_value_permanent( self, _board_uid, _tag_name, _tag_value ):
        self.cursor.execute( "INSERT INTO `Relations` "
                                "( `board_uid`, `tag_name`, `tag_value` ) "
                                "VALUES ( ?, ?, ? );",
                                ( _board_uid, _tag_name, _tag_value ) )
        self.conn.commit( )

    def make_tag_value_temporary( self, _board_uid, _tag_name, _tag_value ):
        self.cursor.execute( "DELETE FROM `Relations` "
                                "WHERE `board_uid` = ? AND `tag_name` = ? AND `tag_value` = ? AND `card_uid` is NULL;",
                                ( _board_uid, _tag_name, _tag_value ) )
        self.conn.commit( )

    def update_project_info( self, _project_info ):
        self.cursor.execute( "UPDATE `Info` "
                                "SET `project_info` = ?;",
                                ( _project_info, ) )
        self.conn.commit( )

    def update_board( self, _board_uid, _board_name, _board_description ):
        self.cursor.execute( "UPDATE `Boards` "
                                "SET `name` = ?, `description` = ? "
                                "WHERE `uid` = ?;",
                                ( _board_name, _board_description, _board_uid ) )
        self.conn.commit( )

    def update_board_name( self, _board_uid, _board_name ):
        self.cursor.execute( "UPDATE `Boards` "
                                "SET `name` = ? "
                                "WHERE `uid` = ?;",
                                ( _board_name, _board_uid ) )
        self.conn.commit( )

    def update_board_description( self, _board_uid, _board_description ):
        self.cursor.execute( "UPDATE `Boards` "
                                "SET `description` = ? "
                                "WHERE `uid` = ?;",
                                ( _board_description, _board_uid ) )
        self.conn.commit( )

    def update_card( self, _card_uid, _card_name, _card_description, _card_color ):
        self.cursor.execute( "UPDATE `Cards` "
                                "SET `name` = ?, `description` = ?, `color` = ? "
                                "WHERE `uid` = ?;",
                                ( _card_name, _card_description, _card_color, _card_uid ) )
        self.conn.commit( )

    def update_card_name( self, _card_uid, _card_name ):
        self.cursor.execute( "UPDATE `Cards` "
                                "SET `name` = ? "
                                "WHERE `uid` = ?;",
                                ( _card_name, _card_uid ) )
        self.conn.commit( )

    def update_card_description( self, _card_uid, _card_description ):
        self.cursor.execute( "UPDATE `Cards` "
                                "SET `description` = ? "
                                "WHERE `uid` = ?;",
                                ( _card_description, _card_uid ) )
        self.conn.commit( )

    def update_card_color( self, _card_uid, _card_color ):
        self.cursor.execute( "UPDATE `Cards` "
                                "SET `color` = ? "
                                "WHERE `uid` = ?;",
                                ( _card_color, _card_uid ) )
        self.conn.commit( )

    def update_card_tag( self, _board_uid, _card_uid, _new_tag_name, _new_tag_value, _prev_tag_name ):
        self.cursor.execute( "UPDATE `Relations` "
                                "SET `tag_name` = ?, `tag_value` = ? "
                                "WHERE `board_uid` = ? AND `tag_name` = ? AND `card_uid` = ?;",
                                ( _new_tag_name, _new_tag_value, _board_uid, _prev_tag_name, _card_uid ) )
        self.conn.commit( )

    def update_card_tag_name( self, _board_uid, _card_uid, _new_tag_name, _prev_tag_name ):
        self.cursor.execute( "UPDATE `Relations` "
                                "SET `tag_name` = ? "
                                "WHERE `board_uid` = ? AND `tag_name` = ? AND `card_uid` = ?;",
                                ( _new_tag_name, _board_uid, _prev_tag_name, _card_uid ) )
        self.conn.commit( )

    def update_card_tag_value( self, _board_uid, _card_uid, _tag_name, _tag_value ):
        self.cursor.execute( "UPDATE `Relations` "
                                "SET `tag_value` = ? "
                                "WHERE `board_uid` = ? AND `tag_name` = ? AND `card_uid` = ?;",
                                ( _tag_value, _board_uid, _tag_name, _card_uid ) )
        self.conn.commit( )

    def update_tag_name( self, _board_uid, _new_tag_name, _prev_tag_name ):
        self.cursor.execute( "UPDATE `Relations` "
                                "SET `tag_name` = ? "
                                "WHERE `board_uid` = ? AND `tag_name` = ?;",
                                ( _new_tag_name, _board_uid, _prev_tag_name ) )
        self.conn.commit( )

    def update_tag_value( self, _board_uid, _new_tag_value, _prev_tag_value, _tag_name ):
        self.cursor.execute( "UPDATE `Relations` "
                                "SET `tag_value` = ? "
                                "WHERE `board_uid` = ? AND `tag_name` = ? AND `tag_value` = ?;",
                                ( _new_tag_value, _board_uid, _tag_name, _prev_tag_value ) )
        self.conn.commit( )

    def delete_project( self, _project_name ):
        db = consts.PROJECTS_FOLDER + "/" + consts.PROJECT_PREFIX + _project_name + ".db"
        if db == self.db:
            self.stop( )
        send2trash.send2trash( db )

    def delete_current_project( self ):
        db = self.db
        self.stop( )
        send2trash.send2trash( db )

    def delete_board( self, _board_uid ):
        self.cursor.execute( "DELETE FROM `Boards` "
                                "WHERE `uid` = ?;",
                                ( _board_uid, ) )
        self.conn.commit( )

    def delete_card( self, _card_uid ):
        self.cursor.execute( "DELETE FROM `Cards` "
                                "WHERE `uid` = ?;",
                                ( _card_uid, ) )
        self.conn.commit( )

    def delete_card_tag( self, _board_uid, _card_uid, _tag_name ):
        self.cursor.execute( "DELETE FROM `Relations` "
                                "WHERE `board_uid` = ? AND `card_uid` = ? AND `tag_name` = ?;",
                                ( _board_uid, _card_uid, _tag_name ) )
        self.conn.commit( )

    def delete_board_tag( self, _board_uid, _tag_name ):
        self.cursor.execute( "DELETE FROM `Relations` "
                                "WHERE `board_uid` = ? AND `tag_name` = ?;",
                                ( _board_uid, _tag_name ) )
        self.conn.commit( )

    def delete_tag_value( self, _board_uid, _tag_name, _tag_value ):
        self.cursor.execute( "DELETE FROM `Relations` "
                                "WHERE `board_uid` = ? AND `tag_name` = ? AND `tag_value` = ?;",
                                ( _board_uid, _tag_name, _tag_value ) )
        self.conn.commit( )

    def remove_card_from_board( self, _board_uid, _card_uid ):
        self.cursor.execute( "DELETE FROM `Relations` "
                                "WHERE `board_uid` = ? AND `card_uid` = ?;",
                                ( _board_uid, _card_uid ) )
        self.conn.commit( )

    def get_all_projects( self ):
        projects      = os.listdir( consts.PROJECTS_FOLDER )
        _len          = len( consts.PROJECT_PREFIX )
        project_names = list( map( lambda e: e[ _len:-3:1 ], projects ) )
        consts.dbg( 1, "Class DBManager - function get_all_projects - value of project_names:", project_names )
        return project_names

    def get_project_info( self ):
        self.cursor.execute( "SELECT `project_info` FROM `Info`;" )
        fetched_data = self.cursor.fetchall( )
        project_info = fetched_data[ 0 ][ 0 ]
        consts.dbg( 1, "Class DBManager - function get_project_info - value of project_info:", project_info )
        return project_info

    def get_board_grouped_cards( self, _board_uid, _tag_name ):
        self.cursor.execute( "SELECT DISTINCT `tag_value` FROM `Relations` "
                                "WHERE `board_uid` = ? AND `tag_name` = ?;",
                                ( _board_uid, _tag_name ) )
        fetched_data  = self.cursor.fetchall( )
        grouped_cards = { }
        for i in fetched_data:
            self.cursor.execute( "SELECT `Cards`.`uid`, `Cards`.`name`, `Cards`.`description`, `Cards`.`color` FROM `Cards`, `Relations` "
                                    "WHERE `Cards`.`uid` = `Relations`.`card_uid` AND `Relations`.`board_uid` = ? AND `Relations`.`tag_name` = ? AND `Relations`.`tag_value` = ?;",
                                    ( _board_uid, _tag_name, i[ 0 ] ) )
            fetched_data_2 = self.cursor.fetchall( )
            cards = fetched_data_2
            grouped_cards[ i[ 0 ] ] = cards
        consts.dbg( 1, "Class DBManager - function get_board_grouped_cards - value of grouped_cards:", grouped_cards )
        return grouped_cards

    def get_board( self, _board_uid ):
        self.cursor.execute( "SELECT `name`, `description` FROM `Boards` "
                                "WHERE `uid` = ?;",
                                ( _board_uid, ) )
        fetched_data = self.cursor.fetchall( )
        board        = fetched_data[ 0 ]
        consts.dbg( 1, "Class DBManager - function get_board - value of board:", board )
        return board

    def get_board_name( self, _board_uid ):
        self.cursor.execute( "SELECT `name` FROM `Boards` "
                                "WHERE `uid` = ?;",
                                ( _board_uid, ) )
        fetched_data = self.cursor.fetchall( )
        board_name   = fetched_data[ 0 ][ 0 ]
        consts.dbg( 1, "Class DBManager - function get_board_name - value of board_name:", board_name )
        return board_name

    def get_board_description( self, _board_uid ):
        self.cursor.execute( "SELECT `description` FROM `Boards` "
                                "WHERE `uid` = ?;",
                                ( _board_uid, ) )
        fetched_data      = self.cursor.fetchall( )
        board_description = fetched_data[ 0 ][ 0 ]
        consts.dbg( 1, "Class DBManager - function get_board_description - value of board_description:", board_description )
        return board_description

    def get_all_boards( self ):
        self.cursor.execute( "SELECT * FROM `Boards`;" )
        fetched_data = self.cursor.fetchall( )
        all_boards   = fetched_data
        consts.dbg( 1, "Class DBManager - function get_all_boards - value of all_boards:", all_boards )
        return all_boards

    def get_all_boards_uid( self ):
        self.cursor.execute( "SELECT `uid` FROM `Boards`;" )
        fetched_data   = self.cursor.fetchall( )
        all_boards_uid = [ ]
        for i in fetched_data:
            all_boards_uid.append( i[ 0 ] )
        consts.dbg( 1, "Class DBManager - function get_all_boards_uid - value of all_boards_uid:", all_boards_uid )
        return all_boards_uid

    def get_board_tag_names( self, _board_uid ):
        self.cursor.execute( "SELECT DISTINCT `tag_name` FROM `Relations` "
                                "WHERE `board_uid` = ?;",
                                ( _board_uid, ) )
        fetched_data = self.cursor.fetchall( )
        tag_names    = [ ]
        for i in fetched_data:
            tag_names.append( i[ 0 ] )
        consts.dbg( 1, "Class DBManager - function get_board_tag_names - value of tag_names:", tag_names )
        return tag_names

    def get_card( self, _card_uid ):
        self.cursor.execute( "SELECT `name`, `description`, `color` FROM `Cards` "
                                "WHERE `uid` = ?;",
                                ( _card_uid, ) )
        fetched_data = self.cursor.fetchall( )
        card         = fetched_data[ 0 ]
        consts.dbg( 1, "Class DBManager - function get_card - value of card:", card )
        return card

    def get_card_name( self, _card_uid ):
        self.cursor.execute( "SELECT `name`, FROM `Cards` "
                                "WHERE `uid` = ?;",
                                ( _card_uid, ) )
        fetched_data = self.cursor.fetchall( )
        card_name    = fetched_data[ 0 ][ 0 ]
        consts.dbg( 1, "Class DBManager - function get_card_name - value of card_name:", card_name )
        return card_name

    def get_card_description( self, _card_uid ):
        self.cursor.execute( "SELECT `description` FROM `Cards` "
                                "WHERE `uid` = ?;",
                                ( _card_uid, ) )
        fetched_data     = self.cursor.fetchall( )
        card_description = fetched_data[ 0 ][ 0 ]
        consts.dbg( 1, "Class DBManager - function get_card_description - value of card_description:", card_description )
        return card_description

    def get_card_color( self, _card_uid ):
        self.cursor.execute( "SELECT `color` FROM `Cards` "
                                "WHERE `uid` = ?;",
                                ( _card_uid, ) )
        fetched_data = self.cursor.fetchall( )
        card_color = fetched_data[ 0 ][ 0 ]
        consts.dbg( 1, "Class DBManager - function get_card_color - value of card_color:", card_color )
        return card_color

    def get_cards_uid_in_board( self, _board_uid ):
        self.cursor.execute( "SELECT DISTINCT `card_uid` FROM `Relations` "
                                "WHERE `board_uid` = ? AND `tag_name` is NULL;",
                                ( _board_uid, ) )
        fetched_data = self.cursor.fetchall( )
        cards_uid    = [ ]
        for i in fetched_data:
            cards_uid.append( i[ 0 ] )
        consts.dbg( 1, "Class DBManager - function get_cards_uid_in_board - value of cards_uid:", cards_uid )
        return cards_uid

    def get_cards_in_board( self, _board_uid ):
        self.cursor.execute( "SELECT DISTINCT `Cards`.`uid`, `Cards`.`name`, `Cards`.`description`, `Cards`.`color` FROM `Cards`, `Relations` "
                                "WHERE `Cards`.`uid` = `Relations`.`card_uid` AND `Relations`.`board_uid` = ?;",
                                ( _board_uid, ) )
        fetched_data   = self.cursor.fetchall( )
        cards_in_board = fetched_data
        consts.dbg( 1, "Class DBManager - function get_cards_in_board - value of cards_in_board:", cards_in_board )
        return cards_in_board

    def get_card_tags( self, _board_uid, _card_uid ):
        self.cursor.execute( "SELECT `tag_name`, `tag_value` FROM `Relations` "
                                "WHERE `board_uid` = ? And `card_uid` = ?;",
                                ( _board_uid, _card_uid ) )
        fetched_data = self.cursor.fetchall( )
        tags         = fetched_data
        consts.dbg( 1, "Class DBManager - function get_card_tags - value of tags:", tags )
        return tags

    def get_all_cards( self ):
        self.cursor.execute( "SELECT * FROM `Cards`;" )
        fetched_data = self.cursor.fetchall( )
        all_cards    = fetched_data
        consts.dbg( 1, "Class DBManager - function get_all_cards - value of all_cards:", all_cards )
        return all_cards

    def get_all_cards_uid( self ):
        self.cursor.execute( "SELECT `uid` FROM `Cards`;" )
        fetched_data  = self.cursor.fetchall( )
        all_cards_uid = [ ]
        for i in fetched_data:
            all_cards_uid.append( i[ 0 ] )
        consts.dbg( 1, "Class DBManager - function get_all_cards_uid - value of all_cards_uid:", all_cards_uid )
        return all_cards_uid

    def get_unused_board_cards( self ):
        pass

    def get_boards_of_card( self, _card_uid ):

        res = set()

        for board_uid in self.get_all_boards_uid():
            if _card_uid in self.get_cards_uid_in_board( board_uid ):
                res.add( board_uid )

        return res

    def stop( self ):
        self.db = None
        self.cursor = None
        if self.conn:
            self.conn.close( )


# Testing
if __name__ == "__main__":
    db_manager = DBManager( )
    db_manager.connect( None, None, None )
    db_manager.use_project( "Project 1" )
    # db_manager.add_board( 1, "board 1", "" )
    # db_manager.add_card( 1, "card 1", "temp description 1", None )
    # db_manager.add_card( 2, "card 2", "temp description 2", None )
    # db_manager.add_card( 3, "card 3", "temp description 3", None )
    # db_manager.add_card( 4, "card 4", "temp description 4", None )
    # db_manager.add_card( 5, "card 5", "temp description 5", None )
    # db_manager.add_card( 6, "card 6", "temp description 6", None )
    # db_manager.add_card( 7, "card 7", "temp description 7", None )
    # db_manager.add_card( 8, "card 8", "temp description 8", None )
    # db_manager.add_card_to_board( 1, 1 )
    # db_manager.add_card_to_board( 1, 2 )
    # db_manager.add_card_to_board( 1, 3 )
    # db_manager.add_card_to_board( 1, 4 )
    # db_manager.add_card_to_board( 1, 5 )
    # db_manager.add_card_to_board( 1, 6 )
    # db_manager.add_card_tag( 1, 1, "Stage", "TODO" )
    # db_manager.add_card_tag( 1, 2, "Stage", "TODO" )
    # db_manager.add_card_tag( 1, 3, "Stage", "In Progress" )
    # db_manager.add_card_tag( 1, 4, "Stage", "In Progress" )
    # db_manager.add_card_tag( 1, 5, "Stage", "Done" )
    # db_manager.add_card_tag( 1, 6, "Stage", "Done" )
    # db_manager.add_card_tag( 1, 1, "Complexity", "Easy" )
    # db_manager.add_card_tag( 1, 2, "Complexity", "Easy" )
    # db_manager.add_card_tag( 1, 3, "Complexity", "Easy" )
    # db_manager.add_card_tag( 1, 4, "Complexity", "Easy" )
    # db_manager.add_card_tag( 1, 5, "Complexity", "Easy" )
    # db_manager.add_card_tag( 1, 6, "Complexity", "Hard" )
    db_manager.stop()

