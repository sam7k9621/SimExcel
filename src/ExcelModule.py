#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import src.SimExcel as SE
import src.SimKeyboard as SK

class ExcelHandler :
    #****************************************************************************
    # Initialization
    #****************************************************************************
    def __init__( self, df ) :
        self.cmd = SE.Excelcmd( df )
        self.kbi = SK.KeyBoardInput()
        self.InitExcelHandler()

    def InitExcelHandler( self ) :
        #Adding operation 
        self.cmd.BasicOper( "add",    "+" ).add_argument("-r", "--rowid", action="store_true", help="add student id")
        self.cmd.BasicOper( "delete", "+" ).add_argument("-r", "--rowid", action="store_true", help="add student id")
        self.cmd.BasicOper( "split",  "+" ).add_argument("-o", "--output", type=str, help="outputfile", required=True)
        self.cmd.BasicOper( "upload", "+" )
        shift = self.cmd.BasicOper( "shift",  "+" )
        shift.add_argument("-f", "--function", type=str, help="modifying function")
        shift.add_argument("-g", "--grade", action="store_true", help="modifying function")

        self.cmd.BasicOper( "replace", 2  )
        self.cmd.BasicOper( "sort", 1  ).add_argument("-a", "--ascending", action="store_false", help="sorting")

        #Adding action
        self.cmd.BasicAct( "exit" )
        lst = self.cmd.BasicAct( "list" )
        lst.add_argument("-c", "--column", nargs="+", action="store", help="specific columns to show" )
        lst.add_argument("-r", "--row", nargs="+", action="store", help="specific columns to show" )

        calc = self.cmd.BasicAct( "calc" )
        calc.add_argument("-c", "--column", nargs="+", action="store", help="specific columns to show" )
        calc.add_argument("-a", "--ave", action="store_true", help="column average")
        calc.add_argument("-d", "--std", action="store_true", help="column average")
        calc.add_argument("-s", "--sum", action="store_true", help="column average")

        #Putting in command list
        lst = ["ADD", "REPLACE", "SPLIT", "DELETE", "UPLOAD", "LIST", "EXIT", "CALC", "SHIFT", "SORT"]
        self.kbi.InputCmdlst( lst )

    def StartWrapper( self ) :
        SK.curses.wrapper( self.Wrapper )

    #****************************************************************************
    # Wrapper
    #****************************************************************************
    def Wrapper(self, stdscr):
        self.kbi.InitKeyBoardInput( stdscr )
        #Parsing to command
        while(True) :

            # Prepare screen and take input
            self.kbi.StartInput()

            # First handle the command then take keyboard action
            if self.kbi.IsEndl() and self.kbi.GetBuff() :
                args = self.kbi.GetBuff().split(" ")
                try:
                    opt = self.cmd.Parsing( args )
                    # self.kbi.PrintMes( opt )
                    self.cmd.InputFilter( ["target", "column", "row"], self.kbi)
                    if not self.cmd.OperateCmd( self.kbi ) :
                        break

                except:
                    self.kbi.PrintErr( self.cmd.GetErrorMessage() )

            if not self.kbi.EndInput() :
                break
