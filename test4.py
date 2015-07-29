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
	
	def closeConn(self):
		self.conn.close()


	def add_record(self, table_name, col_1, col_2, col_3, col_4, col_5):
		conn = psycopg2.connect(con_string)
        	cur = conn.cursor()
        	cur.execute('INSERT INTO %s (%s, %s, %s, %s, %s) \
                	    VALUES(%s, %s, %s, %s, %s)' % ("%s" % table_name, col_1, col_2, col_3, col_4, col_5,\
				col_1.value, col_2.value, col_3.value, col_4.value, col_5.value))
		cur.close()
    
	def update_record(self, record_id, last_name = '', other_names='', email_address=''):
		db = sqlite3.connect(self.dbfilename)
	        c = db.cursor()
	        c.execute('UPDATE records set last_name=?, other_names=?, email_address=? \
        	            WHERE record_internal_id=?', (last_name, other_names, email_address, \
                                                        record_id))
	        db.commit()
        	c.close()    
	def delete_record(self, record_id):
        	db = sqlite3.connect(self.dbfilename)
        	c = db.cursor()
        	c.execute('DELETE FROM table_name where record_internal_id=?', (record_id,))
        	db.commit()
   		c.close()    
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
class TableMenuForm(npyscreen.ActionForm):
	# set screen redirection based on user choice
	def afterEditing(self):
		selection = self.action.get_selected_objects()[0]
		if selection == 'Add Row':
			self.parentApp.setNextForm('Add Row')
		elif selection == 'Edit Row':
			self.parentApp.setNextForm('Edit Row')
		elif selection == 'Delete Row':
			self.parentApp.setNextForm('Delete Row')
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
		# Create MyGrid Widget object
#		self.myGrid =  self.add(MyGrid, col_titles = ['1','2','3','4'])
#		# populate the grid
#		self.myGrid.values = []
#		for x in range(rowNumber):
#			row = []
#			for y in range(4):
#				if bool(random.getrandbits(1)):
#					row.append("PASS")
#				else:
#					row.append("FAIL")
#			self.myGrid.values.append(row)
	
	def beforeEditing(self):
		if self.selectTable:
			self.name = "%s" % self.selectTable
			self.theList = self.parentApp.myDatabase.list_all_records()
			self.theGrid =  self.add(npyscreen.GridColTitles, relx=10, rely=15, width=95, col_titles=['1','2','3','4','5'],\
						 column_width=10, col_margin=5, scroll_exit=True) #scroll_exit doesn't seem to work

               		# initialize and populate the grid
   	     		self.theGrid.values = []
			myrow = []
			#get one record (row) and put that in the grid
			theOne = self.parentApp.myDatabase.get_record()
			self.theGrid.values.append(theOne)#[0]

			#the following are different tests for listing data from list_all_reccords
			#currently left off at trying to figure out how to parse the tuple that is data comes in, which seems to be what get_record does
			#I figured out get_record last, so the answer may lie there, or maybe it has to do with how the table was created?  not sure yet..

			#test1
#			for z in theList:
#				myrow.append(theList[z])
#			self.myGrid.values.append(myrow)	
#
			#test2
#			for x in range(rowNumber):
#				row = []
#				for y in range(4):
#					row.append(theList[y])
#				self.myGrid.values.append(row)
#	
			#test3
#   	        	for x in range(rowNumber):
#                     		row = []
#                        	for y in range(4):
#                        		row.append(theList[x])
#                        	self.myGrid.values.append(row)
		#return record

#		else:
#			self.name = "New Record"
			
		#return self.action.value;
		#self.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE]  = self.exit_application
		
	def exit_application(self):
		curses.beep()
		self.parentApp.setNextForm(None)
		self.editing = False


'''*********************************************************
   Class AddRowForm inherits ActionForm class
   
   Purpose:  Reponsible for adding a new row to the given table
*********************************************************'''
class AddRowForm(npyscreen.ActionForm):
	def afterEditing(self):
		self.parentApp.setNextFormPrevious()
	# It's just prototype, non-dynamic
	def create(self):
		self.value = None
		self.selectTable = None
		self.myArr = None
		self.myGrid =  self.add(MyGrid, col_titles = [], select_whole_line = True, max_height=12)#, scroll_exit = True)
		
	def beforeEditing(self):
		if self.selectTable:
			#self.name = "Table '%s'" % self.selectTable
			self.columns_list = self.parentApp.myDatabase.list_columns(self.selectTable)
			self.myGrid.col_titles = self.columns_list			

			# update query params from DridSettings
			self.limit = self.parentApp.myGridSet.limit
			self.offset = self.parentApp.myGridSet.offset
			self.sort_direction = self.parentApp.myGridSet.sort_direction
			self.sort_column = self.parentApp.myGridSet.column
			# when called with default settings
			if self.sort_column == '':
				self.sort_column = self.columns_list

			self.myGrid.values = []
			self.rows = []
			self.myGrid.default_column_number = 5
#			if len(self.columns_list) > 0:
#				self.rows = self.parentApp.myDatabase.list_records(self.selectTable, self.sort_column, self.sort_direction, self.offset, self.limit)
#			for row in self.rows:
#				self.myGrid.values.append(row)		

			self.myArr = {}
		        k = 0
                	x = 0
                	while k < 10:
                        	k = x
                        	x += 1
                        	value = x
                        	self.myArr[k] = value
                        	k += 1

                        self.name = "%s" % self.selectTable
			self.table = self.add(npyscreen.TitleText, name = "Add Row", editable = False)
			
			#for y in range (0,5):
			#	z = str(self.myArr[y])
			#	self.myArr[y] = self.add(npyscreen.TitleText, name = "Column " + z + ":")
			#	y += 1

			self.col_name = {}
			for y in range (0, self.myGrid.default_column_number):
				self.col_name[y] = self.columns_list[y]
				self.col_name[y] = self.add(npyscreen.TitleText, name = self.col_name[y])   

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

if __name__ == '__main__':
    TestApp = MyApplication().run()
    print TestApp
