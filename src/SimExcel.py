#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse

# subclass argparse to store error message
class MyParser(argparse.ArgumentParser):
    #****************************************************************************
    # Unbound method and variable
    #****************************************************************************
    error_message = ""

    def GetErrMes() :
        mes = MyParser.error_message.rstrip('\n')
        MyParser.error_message = ""
        return mes

    #****************************************************************************
    # Bound method 
    #****************************************************************************
    def __init__(self, *args, **kwargs):
        argparse.ArgumentParser.__init__(self, *args, **kwargs)

    def error(self, message):
        args = {'prog': self.prog, 'message': message}
        MyParser.error_message += ( ('%(prog)s: error: %(message)s\n') % args )
        MyParser.error_message += self.format_usage()
        self.exit(2)

class Excelcmd :
    #****************************************************************************
    # Initialization
    #****************************************************************************
    def __init__(self, df) :
        self.parser = MyParser()
        self.subparsers = self.parser.add_subparsers()
        self.df = df
        self.opt = None
        self.grade_func = \
           lambda x: (       x >= 90 and "A+" )\
                  or ( 85 <= x < 90  and "A"  )\
                  or ( 80 <= x < 85  and "A-" )\
                  or ( 77 <= x < 80  and "B+" )\
                  or ( 73 <= x < 77  and "B"  )\
                  or ( 70 <= x < 73  and "B-" )\
                  or ( 67 <= x < 70  and "C+" )\
                  or ( 63 <= x < 67  and "C"  )\
                  or ( 60 <= x < 63  and "C-" )\
                  or (       x < 60  and "F"  )

    # memeber function definition
    def BasicOper( self, arg, na="?" ):
        list_parser = self.subparsers.add_parser(arg.upper(), help=arg)
        list_parser.add_argument('target', action='store', nargs=na)
        list_parser.add_argument(arg, action='store_true', help=arg, default=True)
        return list_parser

    def BasicAct( self, arg ) :
        list_parser = self.subparsers.add_parser(arg.upper(), help=arg)
        list_parser.add_argument(arg, action='store_true', help=arg, default=True)
        return list_parser

    def Parsing( self, args ) :
        try :
            self.opt = self.parser.parse_args( args )
            return self.opt
        except :
            raise

    #****************************************************************************
    # Bound method 
    #****************************************************************************
    def GetErrorMessage(self) :
        return MyParser.GetErrMes()

    def InputFilter( self, options, kbi ) :
        self.DecimalDigit( 2 )
        for t in options :
            if hasattr( self.opt, t ) :
                if getattr( self.opt, t ) :
                    lst = getattr( self.opt, t )
                    setattr( self.opt, t, list( filter( None, lst ) ) )

    def OperateCmd( self, kbi ) :
        if( hasattr( self.opt, "split" ) ) :
            self.Split( kbi )

        elif( hasattr( self.opt, "replace" ) ) :
            self.Replace( kbi )

        elif( hasattr( self.opt, "add" ) ) :
            self.Add( kbi )

        elif( hasattr( self.opt, "delete" ) ) :
            self.Delete( kbi )

        elif( hasattr( self.opt, "calc" ) ) :
            self.Calc( kbi )

        elif( hasattr( self.opt, "shift" ) ) :
            self.Shift( kbi )

        elif( hasattr( self.opt, "upload" ) ) :
            kbi.PrintMes( "|‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|" )
            kbi.PrintMes( "|    Please let input string in the form of xxx | xxx    |" )
            kbi.PrintMes( '|    Type "done" when you finish                         |' )
            kbi.PrintMes( "|________________________________________________________|" )
            self.Upload( kbi )

        elif( hasattr( self.opt, "list" ) ) :
            self.List( kbi )

        elif( hasattr( self.opt, "sort" ) ) :
            self.Sort( kbi )

        elif( hasattr( self.opt, "exit" ) ) :
            return False

        return True

    def DecimalDigit( self, dig ) :
        for t in self.df.columns[1 :] :
            try:
                self.df[ t ] = self.df[ t ].astype(str).astype(float)
                self.df[ t ] = self.df[ t ].round( dig )
            except:
                pass

    #****************************************************************************
    # Operation definition
    #****************************************************************************
    def Upload( self, kbi ) :
        idelst = self.df["id"].values.tolist()
        self.Add( kbi )
        for t in self.opt.target :
            kbi.InnerStartInput( "[ID | {0}] ".format( t ) )
            while(True):

                # Prepare inner screen and take input
                kbi.StartInput()

                # Fist handle the input then take keyboard action
                if kbi.IsEndl() and kbi.GetBuff() :
                    # inputstr should be like : xxx | xxx
                    inputstr = kbi.GetBuff()
                    inputlst = inputstr.split("|")

                    # if "done" is in inputstr, then break or continue
                    if any( "done" in s.lower().lstrip().rstrip() for s in inputlst ) :
                        break

                    elif len( inputlst ) != 2  :
                        kbi.PrintErr( "Input should be in the form of : xxx | xxx" )

                    else :
                        row, val = inputlst[0].rstrip().lstrip(), inputlst[1].rstrip().lstrip()
                        try :
                            idx = idelst.index( row ) # maybe call exception
                            self.df.loc[idx, t] = val
                            kbi.PrintRes( "Successfully write in" )

                        except ValueError:
                            kbi.PrintErr( "Invalid ID" )

                if not kbi.EndInput() :
                    break

            kbi.InnerEndInput()

    def Split( self, kbi ) :
        with open( self.opt.output, 'w+') as f :
            headerlst = ["id"] + self.opt.target
            self.df[ headerlst ].to_csv( f, index=False )
        kbi.PrintRes('Successfully save as "{}"'.format( self.opt.output ))

    def Add( self, kbi ) :
        for t in self.opt.target :
            # add student id
            if hasattr( self.opt, "rowid" ) :  # for other function to use
                if self.opt.rowid :
                    self.df.loc[ -1 ] = [t] + [0] * ( len( self.df.columns ) -1 )
                    self.df.index += 1
                    self.df = self.df.sort_index()
                    continue
            # add new column
            if t not in list(self.df.columns.values) :
                self.df[ t ] = 0
            else :
                kbi.PrintMes('"{}" already exists'.format(t))
        kbi.PrintRes('Finish adding title/student id')

    def Delete( self, kbi ) :
        for t in self.opt.target :
            # delete student id 
            if self.opt.rowid :
                idelst = self.df["id"].values.tolist()
                try :
                    idx = idelst.index( t )
                    self.df = self.df.drop( self.df.index[ idx ] )
                except ValueError :
                    kbi.PrintErr( 'Student id "{}" not exist'.format(t) )
                continue
            # delete existing column
            try :
                del self.df[ t ]
            except :
                kbi.PrintErr('Title "{}" not exist'.format(t))
        kbi.PrintRes('Finish deleting title/student id')

    def Shift( self, kbi ) :
        if any( t not in self.df.columns for t in self.opt.target ) :
            kbi.PrintErr("Title not exist")
            return

        if not any( [self.opt.grade, self.opt.function] ) :
            kbi.PrintErr("Please assign method")
            return

        func = lambda x: eval( self.opt.function )
        if self.opt.grade :
            func = self.grade_func

        for t in self.opt.target :
            lst = list( self.df[ t ].tolist() )
            lst = [ func( val ) for val in lst ]
            self.df[ t + "*" ] = lst
        kbi.PrintRes('Successfully shift element')

    def Calc( self, kbi ) :
        if not self.opt.column :
            self.opt.column = list( self.df.columns.values )[1:]
        elif any( t not in self.df.columns for t in self.opt.column ) :
            kbi.PrintErr("Title not exsit")

        if not any( [self.opt.ave, self.opt.sum, self.opt.std] ) :
            kbi.PrintErr("Please assign method")
            return

        for t in self.opt.column :
            try :
                idx = max( self.df.index ) + 1
                if self.opt.ave :
                    self.df.loc[ -1, [ "id", t ] ] = [ 'Ave', self.df[t][: idx].mean()]
                if self.opt.sum :
                    self.df.loc[ -2, [ "id", t ] ] = [ 'Sum', self.df[t][: idx].sum()]
                if self.opt.std :
                    self.df.loc[ -3, [ "id", t ] ] = [ 'Std', self.df[t][: idx].std()]
            except :
                kbi.PrintErr('Title "{}" has non-float number'.format(t))

        kbi.PrintRes("Finish calculating average/sum/standard deviaiton")

    def Replace( self, kbi ) :
        kbi.PrintRes('Replacing title "{}" with "{}"'.format( self.opt.target[0], self.opt.target[1]))
        if self.opt.target[1] in self.df.columns :
            kbi.PrintErr('Title "{}" already exist'.format( self.opt.target[1]) )
            return

        try :
            if self.opt.target[0] not in list(self.df.columns.values) :
                kbi.PrintErr("Title not exist")
            self.df.rename(columns = { self.opt.target[0] : self.opt.target[1] }, inplace=True )
        except :
            kbi.PrintErr("Replacement failed")

    def Sort( self, kbi ) :
        idx    = max( self.df.index ) + 1
        minidx = min( self.df.index )
        temp = self.df.ix[-1 :]
        self.df = self.df[: idx].sort_values( [ self.opt.target[0] ], ascending=[ self.opt.ascending] )

        if minidx < 0 :
            self.df = self.df.append( temp )
        kbi.PrintRes('Finish sorting by title "{}"'.format(self.opt.target[0]))

    def List( self, kbi) :
        #prepare column
        if not self.opt.column :
            self.opt.column = list(self.df.columns.values)[1:]
        elif any( t not in self.df.columns for t in self.opt.column ) :
            kbi.PrintErr("Title not exist")
            return

        # prepare row
        if not self.opt.row :
            self.opt.row = self.df["id"].values.tolist()
        elif any( t not in self.df["id"].values.tolist() for t in self.opt.row ) :
            kbi.PrintErr("Column not exist")
            return

        width_id = len( max( list( map(str, ["id"] + self.df["id"].values.tolist() ) ), key=len ) ) + 2
        title_id = [ "{0: <{1}}".format(i, width_id) for i in ["id"] + self.df["id"].values.tolist() ]

        for t in self.opt.column :
            width = len( max( list( map(str, [t] + self.df[t].values.tolist() ) ), key=len ) ) + 2
            title = [ "{0: <{1}}".format(i, width) for i in [t] + self.df[ t ].values.tolist() ]
            title_id = [ title_id[i] + title[i] for i in range( len(title_id) ) ]

        rowidx =[ self.df["id"].values.tolist().index( r ) + 1 for r in self.opt.row ]

        # print title
        mes = ''.join( title_id[:1] )
        kbi.PrintHlt( mes )

        # print content
        for r in rowidx :
            mess = ''.join( title_id[r:r+1] )
            kbi.PrintRes( mess )

