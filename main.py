import os
import db_manager
import consts

from kivy.app import App
from kivy.uix.widget import Widget

from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

# When clicking on a project button.
# The text of the top bar should be changed to the name of the project
# The Left button should become useable

# Function to be called when project button is pressed
def prj_button_press( instance ):
    print( "Project" )
    print( instance.text )

# Function to be called when board button is pressed
def brd_button_press( instance ):
    print( "Board" )
    print( instance.text )

# Function to be called when Action button is pressed
def act_button_press( instance ):
    print( "Action" )
    print( instance.text )

class TopBar( GridLayout ):

    rows = 1
    cols = 2

    def __init__( self, **kwargs ):

        super( TopBar, self ).__init__( **kwargs )

        # States of the buttons
        self.lt_disabled    = False

        # Text to be displayed in the centre
        self.text           = ""

        # BUtton objects for going back and front
        self.lt_but         = Button( text = "L button", background_color  = consts.CYAN, height = 40, width = 60 )

        # Label object for center
        self.label          = Label( text = self.text , height = 40 )

        # Add all widgets to screen
        self.add_widget( self.lt_but )
        self.add_widget( self.label )

    def update_text( self, _text ):
        """[summary]

        Args:
            _text ([type]): [description]
        """

        self.text           = _text
        self.label.text     = self.text

    def set_lt( self, _state ):
        """[summary]

        Args:
            _state ([type]): [description]
        """

        self.lt_disabled        = _state
        self.lt_but.disabled    = _state

    def toggle_lt( self ):
        """[summary]
        """

        self.lt_disabled        = not self.lt_disabled
        self.lt_but.disabled    = self.lt_disabled

class ActBar( BoxLayout ):

    orientation = "horizontal"

    def __init__( self, **kwargs ):

        super( ActBar, self ).__init__( **kwargs )

        self.new_button     = Button( text = "New" )
        self.del_button     = Button( text = "Delete" )

        self.add_widget( self.new_button )
        self.add_widget( self.del_button )

    def update_new_button( self ):
        pass

    def update_del_button( self ):
        pass

    def set_new( self, _state ):

        self.new_button.disabled = not _state

    def set_del( self, _state ):

        self.del_button.disabled = not _state

class MainWindowProjects( BoxLayout ):

    orientation = "vertical"

    def __init_( self, **kwargs ):

        super( MainWindowProjects, self ).__init__( **kwargs )

    def load_projects( self, _lst ):

        self.prj_lst    = []

        for elem in _lst:
            self.prj_lst.append( elem[9:] )

    def add_project( self, _name ):
        pass

    def rem_project( self, _name ):
        pass

    def add_buttons( self ):

        self.but_lst    = []

        for prj in self.prj_lst:
            but = Button( text = prj )
            but.bind( on_press = prj_button_press )
            self.but_lst.append( but )
            self.add_widget( but )

class MainWindowBoards( BoxLayout ):

    orientation = "vertical"

    def __init_( self, **kwargs ):

        super( MainWindowBoards, self ).__init__( **kwargs )

    def load_boards( self, _lst ):

        self.brd_lst    = _lst.copy()

    def add_board( self, _name ):
        pass

    def rem_board( self, _name ):
        pass

    def add_buttons( self ):

        self.but_lst    = []

        for board in self.brd_lst:
            but = Button( text = board )
            but.bind( on_press = brd_button_press )
            self.but_lst.append( but )
            self.add_widget( but )

class MainWindowCards( StackLayout ):

    def __init_( self, **kwargs ):

        super( MainWindowCards, self ).__init__( **kwargs )

class MainLayout( GridLayout ):

    def __init__( self, **kwargs ):

        super( MainLayout, self ).__init__( **kwargs )

        self.rows       = 3
        self.cols       = 1

        self.top_bar    = TopBar()
        self.act_bar    = ActBar()

        self.prj_layout = MainWindowProjects( )

        self.top_bar.update_text( "Projects" )
        self.prj_layout.load_projects( os.listdir( consts.PROJECTS_FOLDER ) )
        self.prj_layout.add_buttons()

        self.add_widget( self.top_bar )
        self.add_widget( self.act_bar )
        self.add_widget( self.prj_layout )

# Main App Class
class PyBoardApp( App ):

    def build( self ):
        return MainLayout()

if __name__ == "__main__":

    PyBoardApp().run()
