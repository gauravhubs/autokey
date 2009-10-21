# -*- coding: utf-8 -*-

# Copyright (C) 2009 Chris Dekter

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import subprocess, threading, time, re
import gtk

class Keyboard:
    """
    Provides access to the keyboard for event generation.
    """
    
    def __init__(self, mediator):
        self.mediator = mediator
        
    def send_keys(self, keyString):
        """
        Send a sequence of keys via keyboard events
        
        Usage: C{keyboard.send_keys(keyString)}
        
        @param keyString: string of keys (including special keys) to send
        """
        self.mediator.send_string(keyString.decode("utf-8"))
        self.mediator.flush()
        
    def send_key(self, key, repeat=1):
        """
        Send a keyboard event
        
        Usage: C{keyboard.send_key(key, repeat=1)}
        
        @param key: they key to be sent (e.g. "s" or "<enter>")
        @param repeat: number of times to repeat the key event
        """        
        for x in range(repeat):
            self.mediator.send_key(key.decode("utf-8"))
        self.mediator.flush()
            
            
class Store(dict):
    """
    Allows persistent storage of values between invocations of the script.
    """
    
    def set_value(self, key, value):
        """
        Store a value
        
        Usage: C{store.set_value(key, value)}
        """
        self[key] = value
        
    def get_value(self, key):
        """
        Get a value
        
        Usage: C{store.get_value(key)}
        """
        return self[key]        
        
    def remove_value(self, key):
        """
        Remove a value
        
        Usage: C{store.remove_value(key)}
        """
        del self[key]
        
class Dialog:
    """
    Provides a simple interface for the display of some basic dialogs to collect information from the user.
    """
    
    def __runZenity(self, title, args):
        p = subprocess.Popen(["zenity", "--title", title] + args, stdout=subprocess.PIPE)
        retCode = p.wait()
        output = p.stdout.read()[:-1] # Drop trailing newline
        
        return (retCode, output)
        
    def input_dialog(self, title="Enter a value", message="Enter a value", default=""):
        """
        Show an input dialog
        
        Usage: C{dialog.input_dialog(title="Enter a value", message="Enter a value", default="")}
        
        @param title: window title for the dialog
        @param message: message displayed above the input box
        @param default: default value for the input box
        """
        return self.__runZenity(title, ["--entry", "--text", message, "--entry-text", default])
        
    def password_dialog(self, title="Enter password", message="Enter password"):
        """
        Show a password input dialog
        
        Usage: C{dialog.password_dialog(title="Enter password", message="Enter password")}
        
        @param title: window title for the dialog
        @param message: message displayed above the password input box
        """
        return self.__runZenity(title, ["--entry", "--text", message, "--hide-text"])
        
    #def combo_menu(self, options, title="Choose an option", message="Choose an option"):
        """
        Show a combobox menu - not supported by zenity
        
        Usage: C{dialog.combo_menu(options, title="Choose an option", message="Choose an option")}
        
        @param options: list of options (strings) for the dialog
        @param title: window title for the dialog
        @param message: message displayed above the combobox      
        """
        #return self.__runZenity(title, ["--combobox", message] + options)
        
    def list_menu(self, options, title="Choose a value", message="Choose a value", default=None):
        """
        Show a single-selection list menu
        
        Usage: C{dialog.list_menu(options, title="Choose a value", message="Choose a value", default=None)}
        
        @param options: list of options (strings) for the dialog
        @param title: window title for the dialog
        @param message: message displayed above the list
        @param default: default value to be selected
        """
        
        choices = []
        #optionNum = 0
        for option in options:
            if option == default:
                choices.append("TRUE")
            else:
                choices.append("FALSE")
                
            #choices.append(str(optionNum))
            choices.append(option)
            #optionNum += 1
            
        return self.__runZenity(title, ["--list", "--radiolist", "--text", message, "--column", " ", "--column", "Options"] + choices)
        
        #return retCode, choice    
        
    def list_menu_multi(self, options, title="Choose one or more values", message="Choose one or more values", defaults=[]):
        """
        Show a multiple-selection list menu
        
        Usage: C{dialog.list_menu_multi(options, title="Choose one or more values", message="Choose one or more values", defaults=[])}
        
        @param options: list of options (strings) for the dialog
        @param title: window title for the dialog
        @param message: message displayed above the list
        @param defaults: list of default values to be selected
        """
        
        choices = []
        #optionNum = 0
        for option in options:
            if option in defaults:
                choices.append("TRUE")
            else:
                choices.append("FALSE")
                
            #choices.append(str(optionNum))
            choices.append(option)
            #optionNum += 1
            
        retCode, output = self.__runZenity(title, ["--list", "--checklist", "--text", message, "--column", " ", "--column", "Options"] + choices)
        results = output.split()
    
        choices = []
        for choice in results:
            choices.append(choice)
        
        return retCode, choices
        
    def open_file(self, title="Open File"):
        """
        Show an Open File dialog
        
        Usage: C{dialog.open_file(title="Open File")}
        
        @param title: window title for the dialog
        @param initialDir: starting directory for the file dialog
        """
        #if rememberAs is not None:
        #    return self.__runZenity(title, ["--getopenfilename", initialDir, fileTypes, ":" + rememberAs])
        #else:
        return self.__runZenity(title, ["--file-selection"])
        
    def save_file(self, title="Save As"):
        """
        Show a Save As dialog
        
        Usage: C{dialog.save_file(title="Save As")}
        
        @param title: window title for the dialog
        """
        #if rememberAs is not None:
        #    return self.__runZenity(title, ["--getsavefilename", initialDir, fileTypes, ":" + rememberAs])
        #else:
        return self.__runZenity(title, ["--file-selection", "--save"])
        
    def choose_directory(self, title="Select Directory", initialDir="~"):
        """
        Show a Directory Chooser dialog
        
        Usage: C{dialog.choose_directory(title="Select Directory")}
        
        @param title: window title for the dialog
        """
        #if rememberAs is not None:
        #    return self.__runZenity(title, ["--getexistingdirectory", initialDir, ":" + rememberAs])
        #else:
        return self.__runZenity(title, ["--file-selection", "--directory"])
        
    #def choose_colour(self, title="Select Colour"):
        """
        Show a Colour Chooser dialog - not supported by zenity
        
        Usage: C{dialog.choose_colour(title="Select Colour")}
        
        @param title: window title for the dialog
        """
        #return self.__runZenity(title, ["--getcolor"])
        
        
class System:
    """
    Simplified access to some system commands.
    """    
    
    def exec_command(self, command):
        """
        Execute a shell command
        
        Usage: C{system.exec_command(command)}
        
        @param command: command to be executed (including any arguments) - e.g. "ls -l"
        @raises subprocess.CalledProcessError: if the command returns a non-zero exit code
        """
        p = subprocess.Popen(command, shell=True, bufsize=-1, stdout=subprocess.PIPE)
        retCode = p.wait()
        output = p.stdout.read()[:-1]
        if retCode != 0:
            raise subprocess.CalledProcessError(retCode, output)
        else:
            return output
    
    def create_file(self, fileName, contents=""):
        """
        Create a file with contents
        
        Usage: C{system.create_file(fileName, contents="")}
        
        @param fileName: full path to the file to be created
        @param contents: contents to insert into the file
        """
        f = open(fileName, "w")
        f.write(contents)
        f.close()
        
    
class Clipboard:
    """
    Read/write access to the X selection and clipboard
    """
    
    def __init__(self, app):
        self.clipBoard = gtk.Clipboard()
        self.selection = gtk.Clipboard(selection="PRIMARY")
        self.app = app
        
    def fill_selection(self, contents):
        """
        Copy text into the X selection
        
        Usage: C{clipboard.fill_selection(contents)}
        
        @param contents: string to be placed in the selection
        """
        #self.__execAsync(self.__fillSelection, contents)
        self.__fillSelection(contents)
        
    def __fillSelection(self, string):
        self.selection.set_text(string.encode("utf-8"))
        #self.sem.release()
        
    def get_selection(self):
        """
        Read text from the X selection
        
        Usage: C{clipboard.get_selection()}
        """
        self.__execAsync(self.selection.request_text, self.__receive)
        return self.text.decode("utf-8")
        
    def __receive(self, cb, text, data=None):
        self.text = text
        self.sem.release()
        
    def fill_clipboard(self, contents):
        """
        Copy text into the clipboard
        
        Usage: C{clipboard.fill_clipboard(contents)}
        
        @param contents: string to be placed in the selection
        """
        self.__fillClipboard(contents)
        
    def __fillClipboard(self, string):
        self.clipBoard.set_text(string.encode("utf-8"))
        #self.sem.release()        
        
    def get_clipboard(self):
        """
        Read text from the clipboard
        
        Usage: C{clipboard.get_clipboard()}
        """
        self.__execAsync(self.clipBoard.request_text, self.__receive)
        return self.text.decode("utf-8")
        
    def __execAsync(self, callback, *args):
        self.sem = threading.Semaphore(0)
        callback(*args)
        self.sem.acquire()        
        
        
class Window:
    """
    Basic window management using wmctrl
    
    Note: in all cases where a window title is required (with the exception of wait_for_focus()), 
    two special values of window title are permitted:
    
    :ACTIVE: - select the currently active window
    :SELECT: - select the desired window by clicking on it
    """
    
    def __init__(self, mediator):
        self.mediator = mediator
        
    def wait_for_focus(self, title, timeOut=5):
        """
        Wait for window with the given title to have focus
        
        Usage: C{window.wait_for_focus(title, timeOut=5)}
        
        If the window becomes active, returns True. Otherwise, returns False if
        the window has not become active by the time the timeout has elapsed.
        
        @param title: title to match against (as a regular expression)
        @param timeOut: period (seconds) to wait before giving up
        """
        regex = re.compile(title)
        waited = 0
        while waited < timeOut:
            if regex.match(self.mediator.interface.get_window_title()):
                return True
            time.sleep(0.3)
            waited += 0.3
            
        return False
        
    def wait_for_exist(self, title, timeOut=5):
        """
        Wait for window with the given title to be created
        
        Usage: C{window.wait_for_exist(title, timeOut=5)}

        If the window is in existence, returns True. Otherwise, returns False if
        the window has not been created by the time the timeout has elapsed.
        
        @param title: title to match against (as a regular expression)
        @param timeOut: period (seconds) to wait before giving up
        """
        regex = re.compile(title)
        waited = 0
        while waited < timeOut:
            retCode, output = self.__runWmctrl(["-l"])
            for line in output.split('\n'):
                if regex.match(line.split(' ', 4)[-1]):
                    return True

            time.sleep(0.3)
            waited += 0.3
            
        return False
        
    def activate(self, title, switchDesktop=False):
        """
        Activate the specified window, giving it input focus

        Usage: C{window.activate(title, switchDesktop=False)}
        
        If switchDesktop is False (default), the window will be moved to the current desktop
        and activated. Otherwise, switch to the window's current desktop and activate it there.
        
        @param title: window title to match against (as case-insensitive substring match)
        @param switchDesktop: whether or not to switch to the window's current desktop
        """
        if switchDesktop:
            args = ["-a", title]
        else:
            args = ["-R", title]
        self.__runWmctrl(args)
        
    def close(self, title):
        """
        Close the specified window gracefully
        
        Usage: C{window.close(title)}
        
        @param title: window title to match against (as case-insensitive substring match)
        """
        self.__runWmctrl(["-c", title])
        
    def resize_move(self, title, xOrigin=-1, yOrigin=-1, width=-1, height=-1):
        """
        Resize and/or move the specified window
        
        Usage: C{window.close(title, xOrigin=-1, yOrigin=-1, width=-1, height=-1)}

        Leaving and of the position/dimension values as the default (-1) will cause that
        value to be left unmodified.
        
        @param title: window title to match against (as case-insensitive substring match)
        @param xOrigin: new x origin of the window (upper left corner)
        @param yOrigin: new y origin of the window (upper left corner)
        @param width: new width of the window
        @param height: new height of the window
        """
        mvArgs = ["0", str(xOrigin), str(yOrigin), str(width), str(height)]
        self.__runWmctrl(["-r", title, "-e", ','.join(mvArgs)])
        
        
    def move_to_desktop(self, title, deskNum):
        """
        Move the specified window to the given desktop
        
        Usage: C{window.move_to_desktop(title, deskNum)}
        
        @param title: window title to match against (as case-insensitive substring match)
        @param deskNum: desktop to move the window to (note: zero based)
        """
        self.__runWmctrl(["-r", title, "-t", str(deskNum)])
        
        
    def switch_desktop(self, deskNum):
        """
        Switch to the specified desktop
        
        Usage: C{window.switch_desktop(deskNum)}
        
        @param deskNum: desktop to switch to (note: zero based)
        """
        self.__runWmctrl(["-s", str(deskNum)])
        
    def set_property(self, title, action, prop):
        """
        Set a property on the given window using the specified action

        Usage: C{window.set_property(title, title, action, prop)}
        
        Allowable actions: C{add, remove, toggle}
        Allowable properties: C{modal, sticky, maximized_vert, maximized_horz, shaded, skip_taskbar,
        skip_pager, hidden, fullscreen, above}
       
        @param title: window title to match against (as case-insensitive substring match)
        @param action: one of the actions listed above
        @param prop: one of the properties listed above
        """
        self.__runWmctrl(["-r", title, "-b" + action + ',' + prop])
        
    def __runWmctrl(self, args):
        p = subprocess.Popen(["wmctrl"] + args, stdout=subprocess.PIPE)
        retCode = p.wait()
        output = p.stdout.read()[:-1] # Drop trailing newline
        
        return (retCode, output)