#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys,os
import curses
import socket
from pathlib import Path

class KeyBoardInput :
    #****************************************************************************
    # Initialzation definition
    #****************************************************************************
    def __init__( self ) :
        self.stdscr = None

        self.prompt  = "╭─"
        self.usercmd = "╰─➤  "
        self.inner_prompt = "╭─"
        self.home = str( Path.home() )
        self.cwd  = str( Path.cwd() ).replace( self.home, "~" )
        self.host = str( socket.gethostname() )
        self.is_inner = False
        self.tempbuff = self.usercmd
        self.cmdlst = []
        self.historylst = []

        self.height = 2000
        self.width  = 2000
        self.cursor_x = len( self.usercmd )
        self.cursor_y = 1
        self.buff = self.usercmd
        self.hist = -1
        self.key = -1

    def InitKeyBoardInput( self, stdscr ) :
        self.InitCurses()
        self.InitStdscr( stdscr )

    def InitCurses( self ) :
        # Create new color as an attribute
        curses.start_color()
        curses.use_default_colors()
        if curses.can_change_color():
            curses.init_color(100, 0, 212, 260)
            curses.init_color(200, 524, 592, 600)
            curses.init_color(50, 450, 600, 120)
            curses.init_color(25, 208, 416, 900)

        curses.init_pair(1, curses.COLOR_WHITE, -1)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(6, curses.COLOR_RED, -1)
        curses.init_pair(7, 25,  -1)
        curses.init_pair(4, 200, -1)
        curses.init_pair(5, 50,  -1)

    def InitStdscr( self, stdscr ) :
        # Clear and refresh the screen for a blank canvas
        self.stdscr = stdscr
        self.stdscr.scrollok(1)
        self.stdscr.clear()
        self.stdscr.refresh()
        self.stdscr.bkgd(' ', curses.color_pair(1))
        self.stdscr.nodelay(1)

    def InputCmdlst( self, lst ) :
        self.cmdlst = lst

    #****************************************************************************
    # Public bound method definition
    #****************************************************************************
    def GetBuff( self ) :
        return self.buff.replace( self.usercmd, "").lstrip().rstrip()

    def PrintRes( self, mes ) :
        messagelst = (str(mes) + "\n").split('\n')
        # remove the last term ""
        for m in messagelst[: -1] :
            self.MoveLine( 1 )
            self.Addstr( self.cursor_y, 0, m[: self.width-1], 4 )

    def PrintMes( self, mes ) :
        messagelst = (str(mes) + "\n").split('\n')
        # remove the last term ""
        for m in messagelst[: -1] :
            self.MoveLine( 1 )
            self.Addstr( self.cursor_y, 0, m[: self.width-1], 7 )

    def PrintHlt( self, mes ) :
        messagelst = (str(mes) + "\n").split('\n')
        # remove the last term ""
        for m in messagelst[: -1] :
            self.MoveLine( 1 )
            self.Addstr( self.cursor_y, 0, m[: self.width-1], 3 )

    def PrintErr( self, mes ) :
        # messagelst = str(mes).split('\n')
        messagelst = (str(mes) + "\n").split('\n')
        # remove the last term ""
        for m in messagelst[: -1] :
            self.MoveLine( 1 )
            self.Addstr( self.cursor_y, 0, m[: self.width-1], 6 )

    def StartInput( self ) :
        self.PrintScreen()
        self.Move()
        self.TakeInput()

    def EndInput( self ) :
        stat = self.KeyboardAction()
        self.Refresh()
        return stat

    #****************************************************************************
    # Settings
    #****************************************************************************
    def Addstr( self, y, x, mes, color) :
        self.stdscr.attron(curses.color_pair ( color ))
        self.stdscr.addstr( y, x, mes )
        self.stdscr.attroff(curses.color_pair( color ))

    def TakeInput( self ) :
        self.key = self.stdscr.getch()

    def Move( self ) :
        self.stdscr.move( self.cursor_y, self.cursor_x )

    def PrintScreen( self ) :
        self.SetBoundary()
        self.PrintStatusBar()
        self.PrintUserCmd()

    def SetBoundary(self) :
        height, width = self.stdscr.getmaxyx()
        if self.height != height or self.width != width :
            self.CleanScreen()
        self.height, self.width  = height, width

    def PrintStatusBar(self) :
        position = "Pos: {}, {}".format(self.cursor_x, self.cursor_y)
        statusbarstr = "Press 'esc' to exit | STATUS BAR | Width: {}, Height: {}".format(self.width, self.height)

        # Render status bar
        self.Addstr(self.height-1, 0, statusbarstr, 3)
        self.Addstr(self.height-1, len(statusbarstr), " " * (self.width - len(statusbarstr) - 1), 3 )
        self.stdscr.attron(curses.A_BOLD)
        self.Addstr(self.height-1, self.width - 1 - len(position), position, 2 )
        self.stdscr.attroff(curses.A_BOLD)

    def IsEndl( self ) :
        return self.key == 10

    def Refresh( self ) :
        if self.hist == -1 :
            self.tempbuff = self.buff
        self.stdscr.refresh()

    def KeyboardAction( self ) :
        return  (
        self.Keyboard_MoveHist() and
        self.Keyboard_MoveCursor() and
        self.Keyboard_RegularChar() and
        self.Keyboard_SpecialChar() and
        self.Keyboard_Common() and
        self.Keyboard_Remove()
        )

    def UpdatePrompt( self ) :


        home = str( Path.home() )
        cwd  = str( Path.cwd() ).replace( home, "~" )
        host = str( socket.gethostname() )
        return prompt + host + " " + cwd

    #****************************************************************************
    # Bound method definition
    #****************************************************************************
    # Only print buffer from beginning
    def PrintUserCmd( self ) :
        # Handle prompt
        prompt = self.inner_prompt if self.is_inner else self.prompt
        prompt += self.host
        self.Addstr( self.cursor_y-1, 0, prompt, 5 )
        self.Addstr( self.cursor_y-1, len(prompt), " " + self.cwd, 4 )

        from time import gmtime, strftime
        ctime = strftime("%Y-%m-%d %H:%M:%S")
        self.Addstr( self.cursor_y-1, self.width - 1 - len(ctime), ctime, 5 )

        # Handle buffer
        self.Addstr( self.cursor_y, 0, self.buff[: len(self.usercmd)], 5 )
        posx = len( self.buff[: len(self.usercmd)] )
        self.Addstr( self.cursor_y, posx, self.buff[len(self.usercmd) :], 1 )

    # Only make cursor move right or left and stand on which cursor_y is right now
    # move backward if pos < 0
    def MoveCursor( self, pos_x=0 ) :
        self.cursor_x += pos_x
        self.cursor_x = max( len( self.usercmd ), self.cursor_x )
        self.cursor_x = min( self.width-1, self.cursor_x )
        self.cursor_x = min( len(self.buff), self.cursor_x )

    # Only make cursor move up or down and stand on which cursor_x is right now
    # move up if pos < 0 (typically not in my case)
    def MoveLine( self, pos_y=0 ) :
        self.cursor_y += pos_y
        if self.cursor_y >= self.height - 1 :
            self.stdscr.addstr( "\n" * (self.cursor_y - self.height + 3)  )
            self.cursor_y = self.height - 2

        self.cursor_y = max( 0, self.cursor_y )
        self.cursor_y = min( self.height -1, self.cursor_y )

    # Only modify the buffer
    def InsertBuff( self, sub ) :
        self.buff = self.buff[: self.cursor_x] + sub + self.buff[ self.cursor_x :]
        self.buff = self.buff[: self.width - 1]

    def DeleteBuff( self, idx ) :
        newbuff = self.buff[: idx] + self.buff[idx+1 :]
        self.CleanBuff()
        self.buff = newbuff

    # Only modify the buffer
    # Also clean current buffer line on the screen
    def CleanBuff( self ) :
        self.buff = " " * self.width
        self.PrintUserCmd()
        self.buff = self.usercmd

    # Clean everything and go back to the initial
    def CleanScreen( self ) :
        self.stdscr.clear()
        self.buff = self.usercmd
        self.cursor_y = 1
        self.cursor_x = len( self.usercmd )
        self.hist = -1

    # Go to next line, also push non-empty buffer in historylst
    def Endl( self ) :
        self.MoveLine( 2 )
        if self.GetBuff() :
            self.historylst.insert( 0, self.buff )

    # Search up and down for historylst
    def SearchHistory( self, idx ) :
        self.CleanBuff()
        idx = min( len(self.historylst) - 1, idx)

        if idx < 0 :
            self.buff = self.tempbuff
            self.hist = -1
            return

        self.hist = idx
        self.buff = self.historylst[ idx ]

    # Demo all possible option when buffer is empty
    # Auto-complete the command if there is one
    def AutoComplete( self ) :
        cmd = self.buff[ len(self.usercmd) : self.cursor_x ].lstrip()
        if not cmd :
            option = "    ".join( self.cmdlst )
            self.MoveLine( 1 )
            self.Addstr( self.cursor_y, 0, option, 4 )
            self.MoveLine( 2 )
            return False

        lst = [s for s in self.cmdlst if cmd.lower() in s [: len(cmd) ].lower()]
        if lst :
            if len( lst ) == 1 :
                temp = self.buff
                self.CleanBuff()
                self.buff = temp[: self.cursor_x - len(cmd)] + lst[0] + temp[self.cursor_x:]
                self.buff = self.buff[: self.width-1]
                return True
            else :
                option = "    ".join(lst)
                self.MoveLine( 1 )
                self.Addstr( self.cursor_y, 0, option[: self.width-1], 4 )
                self.MoveLine( 2 )
                return False

    #****************************************************************************
    # Keyboard definition
    #****************************************************************************
    def Keyboard_MoveHist( self ) :
        if self.key == curses.KEY_UP:
            self.SearchHistory( self.hist + 1 )
            self.MoveCursor( len( self.buff ) )
        elif self.key == curses.KEY_DOWN:
            self.SearchHistory( self.hist - 1 )
            self.MoveCursor( len( self.buff ) )
        return True

    def Keyboard_MoveCursor( self ) :
        if self.key == curses.KEY_RIGHT:
            self.MoveCursor( 1 )
        elif self.key == curses.KEY_LEFT:
            self.MoveCursor( -1 )
        return True

    def Keyboard_RegularChar( self ) :
        if 32 <= self.key <= 126 :
            self.InsertBuff( chr(self.key) )
            self.MoveCursor( 1 )
        return True

    def Keyboard_SpecialChar( self ) :
        if self.key == 1 : #^A start of buffer
            self.MoveCursor( -1 * len(self.buff) ) # automatically fix to usercmd

        if self.key == 5 : #^E end of buffer
            self.MoveCursor( len(self.buff) - self.cursor_x )

        if self.key == 21 : #^U clear
            self.CleanBuff()
            self.MoveCursor( -1 * len(self.buff) )
        return True

    def Keyboard_Common( self ) :
        if self.key == 9 : #tab
            if self.AutoComplete() :
                self.MoveCursor( len(self.buff) )

        if self.key == 10 : #enter
            self.Endl()
            self.CleanBuff()
            self.MoveCursor( -1 * len(self.buff) )
            self.hist = -1

        if self.key == 27 : #esc
            return False

        return True

    def Keyboard_Remove( self ) :
        if self.key == 127 : #backspace
            if self.cursor_x > len( self.usercmd ) :
                self.DeleteBuff( self.cursor_x - 1 )
                self.MoveCursor( -1 )

        if self.key == 330 : #delete
            if len( self.buff ) != self.cursor_x :
                self.DeleteBuff( self.cursor_x )
        return True

    #****************************************************************************
    # Custom bound method
    #****************************************************************************
    def InnerStartInput( self, cmd ) :
        self.inner_prompt += cmd
        self.is_inner = True
        self.tempbuff = self.usercmd
        self.KeyboardAction()

    def InnerKeyboardAction( self ) :
        self.Keyboard_RegularChar()
        self.Keyboard_SpecialChar()
        self.Keyboard_Remove()
        self.Keyboard_MoveCursor()
        if self.IsEndl() :
            return False
        else :
            return True

    def InnerEndInput( self ) :
        self.is_inner = False
        self.inner_prompt = "╭─"
        self.buff = ""
        self.MoveCursor( -1 * len( self.buff ) )
        self.hist = -1
