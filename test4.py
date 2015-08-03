'''**************************************
# Name: Nikolay Goncharenko, Rory Bresnahan
# Email: goncharn@onid.oregonstate.edu
# Class: CS419 - Capstone Project
# Assignment: Python Ncurses UI for 
# MySQL/PostgreSQL Database Management
**************************************'''

import npyscreen, curses
import random
import psycopg2
from psycopg2.extensions import AsIs
import psycopg2.extras
import _mysql
import sys


# $mysqli = new mysqli("oniddb.cws.oregonstate.edu", "goncharn-db", $myPassword, "goncharn-db");
rowNumber = 5
colTitles = (1,2,3,4)#for testing
con_string = "dbname='muepyavy' user='muepyavy' host='babar.elephantsql.com' password='EQoh7fJJNxK-4ag4SNUIYwzzWqTVzj-8'"

'''**************************************************
* Class Database inherits object class
*
* Purpose:  Connect to the database and query it
**************************************************'''
class Database(object):
	def list_all_tables(self):
		try:
			conn = psycopg2.connect("dbname='muepyavy' user='muepyavy' host='babar.elephantsql.com' password='EQoh7fJJNxK-4ag4SNUIYwzzWqTVzj-8'")
		except:
			print "I am unable to connect to the database"
		
		# fetch list of the tables in the database
		cursor = conn.cursor()
		cursor.execute("SELECT table_name FROM information_schema.tables \
							WHERE \
								table_type = 'BASE TABLE' AND table_schema = 'public' \
							ORDER BY table_type, table_name")
		tables = cursor.fetchall()
		cursor.close()
		return tables
	
	# returns list of all column names in the table	
	def list_columns(self, table_name):
		columns_list = []
		conn = psycopg2.connect(con_string)
		cur = conn.cursor()
		cur.execute("SELECT column_name from information_schema.columns \
				WHERE table_name = %s;", (table_name,))
		columns_tuple = cur.fetchall()
		cur.close()
		# traverese tuple of tuples to list of strings
		for col in columns_tuple:
			col = list(col)
			col[0] = col[0].strip("(),'")
			columns_list.append(col[0])
		return columns_list

	def list_records(self, table_name, sort_column, sort_direction, offset, limit):
		conn = psycopg2.connect(con_string)
		cur = conn.cursor()
		cur.execute("SELECT * from %s ORDER BY %s %s OFFSET %s LIMIT %s;",\
						(AsIs(table_name), AsIs(sort_column), AsIs(sort_direction), offset, limit))
		rows = cur.fetchall()
		return rows
	
	def get_row_id(self, table_name, value_selected):
		conn = psycopg2.connect(con_string)
		cur = conn.cursor()
		try:
			cur.execute("SELECT id FROM %s WHERE id = %s;", (AsIs(table_name), value_selected))
			row_id = cur.fetchone()[0]
			cur.close()
			return row_id
		except:
			cur.close()
			return 0

	def closeConn(self):
		self.conn.close()


	def add_record(self, table_name, col_1, col_2, col_3, col_4, col_5):
		
		conn = psycopg2.connect(con_string)
        	cur = conn.cursor()
		
		#puts single parenthesis around variable- needed for inserting strings
   		col2 = wrap_and_encode(col_2.value)
		col4 = wrap_and_encode(col_4.value)
	
		cur.execute('INSERT INTO %s (%s, %s, %s, %s, %s) VALUES (%s, %s, %s, %s, %s)' % (AsIs(table_name), col_1.name, col_2.name, col_3.name, col_4.name, col_5.name,\
												col_1.value, col2, col_3.value, col4, col_5.value))
		conn.commit()
		cur.close()
    
	def update_record(self, record_id, last_name = '', other_names='', email_address=''):
		db = sqlite3.connect(self.dbfilename)
	        c = db.cursor()
	        c.execute('UPDATE records set last_name=?, other_names=?, email_address=? \
        	            WHERE record_internal_id=?', (last_name, other_names, email_address, \
                                                        record_id))
	        db.commit()
        	c.close()    

	def delete_record(self, table_name, record_id):
		conn = psycopg2.connect(con_string)
        	cur = conn.cursor()
        	cur.execute('DELETE FROM %s where id=%s', (AsIs(table_name), record_id,))
		conn.commit()
   		cur.close()
		npyscreen.notify_confirm("Deleted Row")
    
#I was working on the following 2 methods: list_all_records, get_record   Will have to change to accept different tables   
	def list_all_records(self, ):
        	db = psycopg2.connect(con_string)
	        c = db.cursor()
        	c.execute('SELECT * from company')
        	records = c.fetchall()
        	c.close()
        	return records
    
	def get_record(self):
		db = psycopg2.connect(con_string)
		cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)#makes a dictionary object for iteration
		work_mem = 2048
		cursor.execute('SET work_mem to %s', (work_mem,))
		cursor.execute('SELECT * from company')
		memory = cursor.fetchone()
        	cursor.close()
		return memory
	       
def wrap_and_encode(x):
	return ("'%s'" % x)

'''**************************************************
   Class MyGrid inherits GridColTitles class
   
   Purpose:  display data from database as greed,
    visualazing a table in database
**************************************************'''
class MyGrid(npyscreen.GridColTitles):
    # You need to override custom_print_cell to manipulate how
    # a cell is printed. In this example we change the color of the
    # text depending on the string value of cell.
    def custom_print_cell(self, actual_cell, cell_display_value):
        if cell_display_value =='FAIL':
           actual_cell.color = 'DANGER'
        elif cell_display_value == 'PASS':
           actual_cell.color = 'GOOD'
        else:
           actual_cell.color = 'DEFAULT'


'''**************************************************
   Class TableList inherits MultiLineAction class
   
   Purpose:  display list of tables as list and define an action
   when one of the tables is selected 
**************************************************'''
class TableList(npyscreen.MultiLineAction):
    def __init__(self, *args, **keywords):
        super(TableList, self).__init__(*args, **keywords)

    def display_value(self, value):
        return "%s" % (value[0])
    
    def actionHighlighted(self, act_on_this, keypress):
        #self.parent.parentApp.getForm('EDITRECORDFM').value = act_on_this[0]
        #parent.parentApp.switchForm('EDITRECORDFM')
		selectedTableName = act_on_this[0]
		self.parent.parentApp.myGridSet.table = selectedTableName
		self.parent.parentApp.getForm('Menu').selectTable = selectedTableName	
		self.parent.parentApp.getForm('Add Row').selectTable = selectedTableName
		self.parent.parentApp.getForm('delete row').selectTable = selectedTableName
		self.parent.parentApp.switchForm('Menu')

		
'''**************************************************
   Class TableListDisplay inherits FormMutt class
   
   Purpose:  Container for displaying of the dynamic list
**************************************************'''
class TableListDisplay(npyscreen.FormMutt):
	
	# type of widget to be displayed
	MAIN_WIDGET_CLASS = TableList
	MAIN_WIDGET_CLASS_START_LINE = 2
	STATUS_WIDGET_X_OFFSET = 5
	
	def beforeEditing(self):
		self.update_list()
	
	def update_list(self):
		self.wStatus1.value =  ' Select Table From List   '
		self.wMain.values = self.parentApp.myDatabase.list_all_tables()
		self.wMain.relx= 3
		self.wMain.display()


'''**************************************************
   Class TableMenuForm inherits ActionForm class
   
   Purpose:  Displays main table menu and grid
**************************************************'''													
class TableMenuForm(npyscreen.ActionFormWithMenus):
	# set screen redirection based on user choice
	def afterEditing(self):
		selection = self.action.get_selected_objects()[0]
		if selection == 'Add Row':
			self.parentApp.setNextForm('Add Row')
		elif selection == 'Edit Row':
			self.parentApp.setNextForm('Edit Row')
		elif selection == 'Delete Row':
		
			#trying to put row id into an array and iterate over in addItem below to let user pick row in popup menu
			#but the funciton deleteTheRow is called even though onSelect should only call it if the user selects it
			#so far issue is not resolved.
			#also if menus are used in TableMenuForm, we will have to change the other options to accomodate this
			#otherwise you can access the menu before picking the delete option
			#right not I left the implementaton for a different page
			#self.row = 1
			#self.menu = self.new_menu(name="Delete Row")
			#self.menu.addItemsFromList([
                        #("Display text", self.whenDisplayText, None, None, ("Delete Row?",)),
                        #("Exit Menu", self.exit_menu, "e"),
			#("row delete", self.deleteTheRow(row)),
			#])
			#for x in range (0, 5):
			#	self.menu.addItem(text=str(self.row), onSelect=self.deleteTheRow())
			#	self.row += 1
		
			#self.edit()
			self.parentApp.setNextForm('delete row')
		elif selection == 'Next Page':
			self.parentApp.setNextForm('Next Page')
		elif selection == 'Prev Page':
			self.parentApp.setNextForm('Prev Page')
		else:
			self.parentApp.setNextForm(None)
		#self.parentApp.setNextFormPrevious()
		
		return selection
	
	# Create Widgets
	def create(self):
		self.selectTable = None
		self.rowNum = self.add(npyscreen.TitleText, name='Rows: ', value = str(rowNumber))
		self.action = self.add(npyscreen.TitleSelectOne, max_height=5, name='Select Action',\
					values = ['Next Page', 'Prev Page', 'Add Row', 'Edit Row', 'Delete Row'],\
					scroll_exit = True #Let the user move out of the widget by pressing 																		# the down arrow instead of tab.  Try it without to see the difference.
					)
		# move one line down from  the previous form
		self.nextrely += 1
			
	def beforeEditing(self):
		if self.selectTable:
			self.name = "%s" % self.selectTable
			self.theList = self.parentApp.myDatabase.list_all_records()
			self.theGrid =  self.add(npyscreen.GridColTitles, relx=10, rely=15, width=95, col_titles=['1','2','3','4','5'],\
						 column_width=10, col_margin=5, scroll_exit=True) #scroll_exit doesn't seem to work

               		# initialize and populate the grid
   	     		self.theGrid.values = []
			myrow = []
			theOne = self.parentApp.myDatabase.get_record()
			self.theGrid.values.append(theOne)#[0]

	def deleteTheRow(self):
		if self.selectTable and self.row:
                        self.the_row_id = self.parentApp.myDatabase.get_row_id(self.selectTable, self.row)
                        if self.the_row_id:
                                npyscreen.notify_ok_cancel("Delete Row?")
                                self.parentApp.myDatabase.delete_record(self.selectTable, self.the_row_id)
                        elif self.the_row_id == 0:
                                npyscreen.notify_confirm("Row does not exist")

        def whenDisplayText(self, argument):
                npyscreen.notify_ok_cancel(argument)

	def exit_menu(self):
		self.editing = False

	def exit_application(self):
		curses.beep()
		self.parentApp.setNextForm(None)
		self.editing = False

'''*********************************************************
   Class deleteForm  inherits FormWithMenus class

   Purpose:  Reponsible for deleting a row  to the given table
*********************************************************'''
class deleteForm(npyscreen.FormWithMenus):
	def create(self):
		self.selectTable = None
		self.add(npyscreen.TitleText, name = "Press ctrl-x to enter menu", editable = False)
		self.rowPicked = self.add(npyscreen.TitleText, name =  "But first enter row id number from the row you want to delete and press OK...")
		self.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE] = self.exit_application
		
		self.m1 = self.add_menu(name="Main menu", shortcut="^m")
		self.m1.addItemsFromList([
			("Display text", self.whenDisplayText, None, None, ("Delete Row?",)),
			("Delete Row", self.deleteTheRow, "d"),
			("Exit application", self.exit_application, "e"),
		])
		
		#testing more popup menus
		#self.m2 = self.add_menu(name="another menu", shortcut="^b")
		#self.m2.addItemsFromList([
		#	("Beep", self.whenJustBeep),
		#])

		#self.m3 = self.m2.addNewSubmenu("A sub menu", "^F")
        	#self.m3.addItemsFromList([
            	#	("Just Beep",   self.whenJustBeep),
        	#])    

	def deleteTheRow(self):
		if self.selectTable and self.rowPicked:
			self.row_id = self.parentApp.myDatabase.get_row_id(self.selectTable, self.rowPicked.value)
			if self.row_id:
				if(npyscreen.notify_ok_cancel("Delete Row?") == True):
					self.parentApp.myDatabase.delete_record(self.selectTable, self.row_id)
			elif self.row_id == 0:
				npyscreen.notify_confirm("Row does not exist")

	def whenDisplayText(self, argument):
 		npyscreen.notify_ok_cancel(argument)

        #def whenJustBeep(self):
    	#	curses.beep()

	def exit_application(self):
       		self.parentApp.setNextForm(None)
        	self.editing = False
        	#self.parentApp.switchFormNow()
		self.parentApp.switchForm('Menu')

'''*********************************************************
   Class AddRowForm inherits ActionForm class
   
   Purpose:  Reponsible for adding a new row to the given table
*********************************************************'''
class AddRowForm(npyscreen.ActionForm):
	def afterEditing(self):
		self.parentApp.setNextFormPrevious()
		self.columns_list = self.parentApp.myDatabase.list_columns(self.selectTable)
               
	# It's just prototype, non-dynamic
	def create(self):
		self.value = None
		self.sort_column = ''
		self.selectTable = None
		self.col_name = []
		self.myArr = {}
		self.columns_list = []
                k = 0
                x = 0
                while k < 10:
                	k = x
                        x += 1
                        value = x
                        self.myArr[k] = value
                        k += 1
		
		self.table = self.add(npyscreen.TitleText, name="Add Row", editable=False)

	def beforeEditing(self):
		if self.selectTable:
			self.name = "%s" % self.selectTable
			self.col_name = {}
			self.columns_list = self.parentApp.myDatabase.list_columns(self.selectTable)
                        for y in range (0, 5):
                                self.col_name[y] = self.columns_list[y]
                                self.col_name[y] = self.add(npyscreen.TitleText, name = self.col_name[y])


			self.myGrid = self.add(MyGrid, relx=10, rely=15, width=95, column_width=10, col_margin=5, scroll_exit=True)

                        # initialize and populate the grid
                        self.myGrid.values = []
			self.limit = self.parentApp.myGridSet.limit
			self.offset = self.parentApp.myGridSet.offset
			self.sort_direction = self.parentApp.myGridSet.sort_direction
			self.columns_list = self.parentApp.myDatabase.list_columns(self.selectTable)

			#self.sort_column = self.parentApp.myGridSet.sort_column
			# when called with default settings
			if self.sort_column == '':
				self.sort_column = self.columns_list[0]

			self.rows = self.parentApp.myDatabase.list_records(self.selectTable, self.sort_column, self.sort_direction, self.offset, self.limit)
			self.parentApp.myGridSet.rows = self.rows
                   
			

			for row in self.parentApp.myGridSet.rows:
				self.myGrid.values.append(row)
		
	def on_ok(self):
		if self.selectTable:		
			self.parentApp.myDatabase.add_record(self.selectTable, self.col_name[0], self.col_name[1], self.col_name[2],\
								 self.col_name[3], self.col_name[4])
			
'''*********************************************************
   Class GridSettings inherits object
   
   Purpose:  Save current GridView pagination settings + table_name
*********************************************************'''
class GridSettings(object):
	def __init__ (self):
		self.limit = 3
		self.sort_direction = 'ASC'
		self.offset = 0
		self.table = ''
		self.column = ''


# Form containing pagination settings
class GridSetForm(npyscreen.ActionForm):
	def afterEditing(self):
		self.parentApp.myGridSet.limit = int(self.limitWidget.value)
		self.parentApp.myGridSet.offset = int(self.offsetWidget.value)
		self.parentApp.myGridSet.sort_direction = self.sortDirWidget.get_selected_objects()[0]
		self.parentApp.myGridSet.column = self.columnWidget.get_selected_objects()[0]
		self.parentApp.setNextFormPrevious()
	
	def create(self):
		self.limitWidget = self.add(npyscreen.TitleText, name='Rows per page: ', begin_entry_at = 21, value = str(self.parentApp.myGridSet.limit))
		self.nextrely += 1
		self.offsetWidget = self.add(npyscreen.TitleText, name='Start at row #:', begin_entry_at = 21, value = str(self.parentApp.myGridSet.offset))
		self.nextrely += 1
		self.columnWidget = self.add(npyscreen.TitleSelectOne, max_height=5,
									    name='Order by',
										#values = [],
										scroll_exit = True
										 # Let the user move out of the widget by pressing 
										# the down arrow instead of tab.  Try it without to see the difference.
										)
		self.nextrely += 1
		self.sortDirWidget = self.add(npyscreen.TitleSelectOne, max_height=6,
									    name='Sort',
										values = ['ASC', 'DESC'],
										scroll_exit = True
										 # Let the user move out of the widget by pressing 
										# the down arrow instead of tab.  Try it without to see the difference.
										)

	def beforeEditing(self):
		if self.columns_list:
			self.columnWidget.values = self.columns_list
'''**************************************************
   Class MyApplication inherits NPSAppManaged class
   
   Purpose:  Manages  flow between application screens.
	It's a main app environment
**************************************************'''
class MyApplication(npyscreen.NPSAppManaged):
    def onStart(self):
		self.myDatabase = Database()
		self.myGridSet = GridSettings()
		selTableF = self.addForm('MAIN', TableListDisplay, name='Select Table')
		tabMenuF = self.addForm('Menu', TableMenuForm, name='Table Menu')
		addRowF = self.addForm('Add Row', AddRowForm, name='Add Row')
		GridSetF = self.addForm('GridSet', GridSetForm, name='Pagination Settings')
		deleteRowF = self.addForm('delete row', deleteForm, name='delete row')

if __name__ == '__main__':
    TestApp = MyApplication().run()
    print TestApp
