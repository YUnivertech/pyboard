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

class TopBar( GridLayout ):

    def __init__( self, **kwargs ):

        super( TopBar, self ).__init__( **kwargs )

    def update_text( self, _text ):
        pass

    def set_lt( self, _state ):
        pass

    def toggle_lt( self ):
        pass

class ActBar( BoxLayout ):

    def __init__( self, **kwargs ):

        super( ActBar, self ).__init__( **kwargs )

    def update_new_button( self ):
        pass

    def update_del_button( self ):
        pass

    def set_new( self, _state ):
        pass

    def set_del( self, _state ):
        pass

class MainWindowProjects( BoxLayout ):

    def __init_( self, **kwargs ):

        super( MainWindowProjects, self ).__init__( **kwargs )
class MainWindowBoards( GridLayout ):

    def __init_( self, **kwargs ):

        super( MainWindowBoards, self ).__init__( **kwargs )
class MainWindowCards( StackLayout ):

    def __init_( self, **kwargs ):

        super( MainWindowCards, self ).__init__( **kwargs )

class MainLayout( GridLayout ):

    def __init__( self, **kwargs ):

        super( MainLayout, self ).__init__( **kwargs )

# Main App Class
class PyBoardApp( App ):

    def build( self ):
        return MainLayout()

if __name__ == "__main__":

    prj_lst     = os.listdir( consts.PROJECTS_FOLDER )
    print( prj_lst )

    manager     = db_manager.DBManager()

    PyBoardApp().run()
