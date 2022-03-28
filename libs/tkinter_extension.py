from tkinter.ttk import Combobox, Style, Entry, Button, Radiobutton
from tkinter import Frame, Listbox, Label, Toplevel
from tkinter import HORIZONTAL, X
from tkinter import W, E, S, N, END, BOTTOM
from tkinter import INSERT, ACTIVE, NORMAL, DISABLED
from tkinter import Text, IntVar, StringVar
import textwrap
import re
import os

class AutocompleteCombobox(Combobox):

	def set_completion_list(self, completion_list):
		"""Use our completion list as our drop down selection menu, arrows move
		through menu."""
		self._completion_list = sorted(completion_list, key=str.lower) # Work with a sorted list
		self._hits = []
		self._hit_index = 0
		self.position = 0
		self.bind('<KeyRelease>', self.handle_keyrelease)
		self['values'] = self._completion_list  # Setup our popup menu
		self.delete(0,END)	

	def Set_Entry_Width(self, width):
		self.configure(width=width)

	def Set_DropDown_Width(self, width):
		print('Change size: ', width)
		style = Style()
		style.configure('TCombobox', postoffset=(0,0,width,0))
		self.configure(style='TCombobox')

	def autofill(self, delta=0):
		"""autocomplete the Combobox, delta may be 0/1/-1 to cycle through possible hits"""
		if delta: # need to delete selection otherwise we would fix the current position
			self.delete(self.position, END)
		else: # set position to end so selection starts where textentry ended
			self.position = len(self.get())
		# collect hits
		_hits = []
		for element in self._completion_list:
			if self.get().lower() in element: # Match case insensitively
				_hits.append(element)
		# if we have a new hit list, keep this in mind
		if _hits != self._hits:
			self._hit_index = 0
			self._hits=_hits
		# only allow cycling if we are in a known hit list
		if _hits == self._hits and self._hits:
			self._hit_index = (self._hit_index + delta) % len(self._hits)
		# now finally perform the auto completion
		'''
		if self._hits:
			self.delete(0,END)
			self.insert(0,self._hits[self._hit_index])
			self.select_range(self.position,END)
		'''

	def autocomplete(self, delta=0):
		"""autocomplete the Combobox, delta may be 0/1/-1 to cycle through possible hits"""
		if delta: # need to delete selection otherwise we would fix the current position
			self.delete(self.position, END)
		else: # set position to end so selection starts where textentry ended
			self.position = len(self.get())
		# collect hits
		_hits = []
		for element in self._completion_list:
			if element.lower().startswith(self.get().lower()): # Match case insensitively
				_hits.append(element)
		# if we have a new hit list, keep this in mind
		if _hits != self._hits:
			self._hit_index = 0
			self._hits=_hits
		# only allow cycling if we are in a known hit list
		if _hits == self._hits and self._hits:
			self._hit_index = (self._hit_index + delta) % len(self._hits)
		# now finally perform the auto completion
		if self._hits:
			self.delete(0,END)
			self.insert(0,self._hits[self._hit_index])
			self.select_range(self.position,END)

	def handle_keyrelease(self, event):
		"""event handler for the keyrelease event on this widget"""
		if event.keysym == "BackSpace":
			self.delete(self.index(INSERT), END)
			self.position = self.index(END)
		if event.keysym == "Left":
			if self.position < self.index(END): # delete the selection
				self.delete(self.position, END)
			else:
				self.position = self.position-1 # delete one character
				self.delete(self.position, END)
		if event.keysym == "Right":
			self.position = self.index(END) # go to end (no selection)
		if len(event.keysym) == 1:
			self.autocomplete()
			#self.autofill()


class CustomText(Text):

	def __init__(self, *args, **kwargs):
		Text.__init__(self, *args, **kwargs)
		Text.tag_configure(self, "red", background='deep pink', foreground='white')
		Text.tag_configure(self, "blue", background='deep sky blue', foreground='white')

	def highlight_pattern(self, pattern, tag, start="1.0", end="end",
						  regexp=False):
		'''Apply the given tag to all text that matches the given pattern

		If 'regexp' is set to True, pattern will be treated as a regular
		expression according to Tcl's regular expression syntax.
		'''
		start = self.index(start)
		end = self.index(end)
		self.mark_set("matchStart", start)
		self.mark_set("matchEnd", start)
		self.mark_set("searchLimit", end)

		count = IntVar()

		while True:
			index = self.search(pattern, "matchEnd","searchLimit",
								count=count, regexp=regexp)
			if index == "": break
			if count.get() == 0: break # degenerate pattern which matches zero-length strings
			real_index = index.split('.')
			start_pos = index
			end_pos = str(real_index[0]) + '.' + str(int(real_index[1]) + count.get())
			self.mark_set("matchStart", str(start_pos))	
			self.mark_set("matchEnd", str(end_pos))
			#self.mark_set("matchStart", str('1.'+ str(start_pos)))
			#self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
			self.tag_add(tag, "matchStart", "matchEnd")

	def highlight_fault_pattern(self, pattern, tag, start="1.0", end="end",
						  regexp=False):
		'''Apply the given tag to all text that matches the given pattern

		If 'regexp' is set to True, pattern will be treated as a regular
		expression according to Tcl's regular expression syntax.
		'''
		start = self.index(start)
		end = self.index(end)
		self.mark_set("matchStart", start)
		self.mark_set("matchEnd", start)
		self.mark_set("searchLimit", end)

		count = IntVar()

		while True:
			
			_index_lower = self.search(pattern, "matchEnd","searchLimit", nocase= 1, 
								count=count, regexp=regexp)
			if _index_lower == "": break
			if count.get() == 0: break # degenerate pattern which matches zero-length strings
			
			real_index = _index_lower.split('.')
			start_pos_lower = _index_lower
			end_pos_lower = str(real_index[0]) + '.' + str(int(real_index[1]) + count.get())
			index = self.search(pattern, "matchEnd","searchLimit", 
								count=count, regexp=regexp)
			if index == "":
				self.mark_set("matchStart", str(start_pos_lower))	
				self.mark_set("matchEnd", str(end_pos_lower))
				self.tag_add('red', "matchStart", "matchEnd")
				continue
			if count.get() == 0: 
				self.mark_set("matchStart", str(start_pos_lower))	
				self.mark_set("matchEnd", str(end_pos_lower))
				self.tag_add('red', "matchStart", "matchEnd")
				continue
			real_index = index.split('.')
			start_pos = index
			end_pos = str(real_index[0]) + '.' + str(int(real_index[1]) + count.get())
			
			if start_pos_lower != start_pos or end_pos_lower != end_pos:
				self.mark_set("matchStart", str(start_pos))	
				self.mark_set("matchEnd", str(end_pos))
				self.tag_add('red', "matchStart", "matchEnd")
			else:
				self.mark_set("matchStart", str(start_pos))	
				self.mark_set("matchEnd", str(end_pos))
				self.tag_add('blue', "matchStart", "matchEnd")		

# GUIDE
# In main FRAME, add this line:
# main_frame.pack(side=TOP, expand=Y, fill=X)
# In sub FRAME, add this line:
# 
# sub_frame.pack(side=TOP, expand=Y, fill=BOTH)

class BottomPanel(Frame):
	def __init__(self, master):
		Frame.__init__(self, master) 
		self.pack(side=BOTTOM, fill=X)          # resize with parent
		
		# separator widget
		#Separator(orient=HORIZONTAL).grid(in_=self, row=0, column=1, sticky=E+W, pady=5)
		#Row = 1
		
		#Label(text='Version', width=15).grid(in_=self, row=Row, column=Col, padx=5, pady=5, sticky=W)
		#Col += 1
		#Label(textvariable=master.VersionStatus, width=15).grid(in_=self, row=Row, column=Col, padx=0, pady=5, sticky=W)
		#master.VersionStatus.set('-')
		Col = 1
		Row = 1
		Label(text='Update', width=15).grid(in_=self, row=Row, column=Col, padx=5, pady=5)
		Col += 1
		Label(textvariable=master._update_day, width=15).grid(in_=self, row=Row, column=Col, padx=0, pady=5)
		master._update_day.set('-')
		Col += 1
		DictionaryLabelA = Label(text=master.LanguagePack.Label['Database'], width=15)
		DictionaryLabelA.grid(in_=self, row=Row, column=Col, padx=5, pady=5)
		Col += 1
		Label(textvariable=master.DictionaryStatus, width=15).grid(in_=self, row=Row, column=Col, padx=0, pady=5)
		master.DictionaryStatus.set('0')
		Col += 1
		Label(text=master.LanguagePack.Label['Header'], width=15).grid(in_=self, row=Row, column=Col, padx=5, pady=5)
		Col += 1
		Label(textvariable=master.HeaderStatus, width=15).grid(in_=self, row=Row, column=Col, padx=0, pady=5)
		master.HeaderStatus.set('0')
		Col += 1
		Label(text= master.LanguagePack.Label['ProjectKey'], width=15).grid(in_=self, row=Row, column=Col, padx=5, pady=5, sticky=W)
		Col += 1
		self.project_id_select = AutocompleteCombobox()
		self.project_id_select.Set_Entry_Width(20)
		self.project_id_select.set_completion_list([])
		self.project_id_select.grid(in_=self, row=Row, column=Col, padx=5, pady=5, stick=W)
		self.project_id_select.bind("<<ComboboxSelected>>", master._save_project_key)
		Col += 1
		self.RenewTranslatorMain = Button(text=master.LanguagePack.Button['RenewDatabase'], width=15, command= master.RenewMyTranslator, state=DISABLED)
		self.RenewTranslatorMain.grid(in_=self, row=Row, column=Col, padx=10, pady=5, stick=E)
		
		
		self.rowconfigure(0, weight=1)
		self.columnconfigure(0, weight=1)


class AutocompleteEntry(Entry):
	def __init__(self, autocompleteList, *args, **kwargs):

		# Listbox length
		if 'listboxLength' in kwargs:
			self.listboxLength = kwargs['listboxLength']
			del kwargs['listboxLength']
		else:
			self.listboxLength = 8

		# Custom matches function
		if 'matchesFunction' in kwargs:
			self.matchesFunction = kwargs['matchesFunction']
			del kwargs['matchesFunction']
		else:
			def matches(fieldValue, acListEntry):
				pattern = re.compile('.*' + re.escape(fieldValue) + '.*', re.IGNORECASE)
				return re.match(pattern, acListEntry)
				
			self.matchesFunction = matches

		
		Entry.__init__(self, *args, **kwargs)
		self.focus()

		self.autocompleteList = autocompleteList
		
		self.var = self["textvariable"]
		if self.var == '':
			self.var = self["textvariable"] = StringVar()

		self.var.trace('w', self.changed)
		self.bind("<Right>", self.selection)
		self.bind("<Up>", self.moveUp)
		self.bind("<Down>", self.moveDown)
		self.bind("<FocusOut>", self.destroy_droplist)

		self.listboxUp = False

	def set_completion_list(self, completion_list):
		#print('Auto list updated')
		self.autocompleteList = sorted(completion_list, key=str.lower)

	def destroy_droplist(self, event):
		if self.listboxUp:
			self.listbox.destroy()
			self.listboxUp = False

	def changed(self, name, index, mode):
		if self.var.get() == '':
			if self.listboxUp:
				self.listbox.destroy()
				self.listboxUp = False
		else:
			words = self.comparison()
			if words:
				if not self.listboxUp:
					self.listbox = Listbox(width=self["width"], height=self.listboxLength)
					self.listbox.bind("<Button-1>", self.selection)
					self.listbox.bind("<Right>", self.selection)
					#print(self.winfo_x(), self.winfo_y(), self.winfo_height())
					self.listbox.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height()*2)
					self.listboxUp = True
				if self.listboxUp:
					self.listbox.delete(0, END)
				for w in words:
					self.listbox.insert(END,w)
			else:
				if self.listboxUp:
					self.listbox.destroy()
					self.listboxUp = False
		
	def selection(self, event):
		if self.listboxUp:
			self.var.set(self.listbox.get(ACTIVE))
			self.listbox.destroy()
			self.listboxUp = False
			self.icursor(END)

	def moveUp(self, event):
		if self.listboxUp:
			if self.listbox.curselection() == ():
				index = '0'
			else:
				index = self.listbox.curselection()[0]
				
			if index != '0':                
				self.listbox.selection_clear(first=index)
				index = str(int(index) - 1)
				
				self.listbox.see(index) # Scroll!
				self.listbox.selection_set(first=index)
				self.listbox.activate(index)

	def moveDown(self, event):
		if self.listboxUp:
			if self.listbox.curselection() == ():
				index = '0'
			else:
				index = self.listbox.curselection()[0]
				
			if index != END:                        
				self.listbox.selection_clear(first=index)
				index = str(int(index) + 1)
				
				self.listbox.see(index) # Scroll!
				self.listbox.selection_set(first=index)
				self.listbox.activate(index) 

	def comparison(self):
		return [ w for w in self.autocompleteList if self.matchesFunction(self.var.get(), w) ]


class CreateToolTip(object):


	'''
	create a tooltip for a given widget
	'''
	def __init__(self, widget, text='widget info'):
		self.widget = widget
		self.text = text
		self.widget.bind("<Enter>", self.enter)
		self.widget.bind("<Leave>", self.close)

	def enter(self, event=None):
		x = y = 0
		x, y, cx, cy = self.widget.bbox("insert")
		x += self.widget.winfo_rootx() + 25
		y += self.widget.winfo_rooty() + 20
		# creates a toplevel window
		self.tw = Toplevel(self.widget)
		# Leaves only the label and removes the app window
		self.tw.wm_overrideredirect(True)
		self.tw.wm_geometry("+%d+%d" % (x, y))
		label = Label(self.tw, text=self.text, justify='left',
					   background='yellow', relief='solid', borderwidth=1,
					   font=("times", "8", "normal"))
		label.pack(ipadx=1)

	def close(self, event=None):
		if self.tw:
			self.tw.destroy()


def ADB_Controller(Tab):
	# resize with parent
	Button_Width_Half=15
	# separator widget
	#Separator(orient=HORIZONTAL).grid(in_=self, row=0, column=1, sticky=E+W, pady=5)
	Row = 1
	Button(Tab, width = Button_Width_Half, text=  "TAB", command= lambda : os.popen('adb shell input keyevent \'61\'')).grid(row=Row, column=1,padx=5, pady=5, sticky=W)
	Button(Tab, width = Button_Width_Half, text=  "Enter", command= lambda : os.popen('adb shell input keyevent \'66\'')).grid(row=Row, column=2,padx=5, pady=5, sticky=W)
	Button(Tab, width = Button_Width_Half, text=  "Home", command= lambda : os.popen('adb shell input keyevent \'3\'')).grid(row=Row, column=3,padx=5, pady=5, sticky=W)
	Button(Tab, width = Button_Width_Half, text=  "Backkey", command= lambda : os.popen('adb shell input keyevent \'4\'')).grid(row=Row, column=4,padx=5, pady=5, sticky=W)
	Row += 1
	Label(Tab, text= 'Send text').grid(row=Row, column=1, padx=5, pady=5, sticky= W)
	_Edit = Text(Tab, width = 80, height=1, undo=True)
	_Edit.grid(row=Row, column=2, columnspan=7, padx=5, pady=5, sticky=W+E)
	Button(Tab, width = Button_Width_Half, text= 'Send', command= lambda : os.popen("adb shell input text \'" + _Edit.get("1.0", END).replace('\n', '') + "\'")).grid(row=Row, column=9, columnspan=2,padx=5, pady=5, sticky=W)

	for i in range (0,10):
		Tab.columnconfigure(i,weight=1, uniform='third')

class ConfirmationPopup:
	def __init__(self, master, dif_dict, index_list):
		self.Root = master
		self.master = master.Child_Window
		#self.master.geometry("400x350+300+300")
		self.index = index_list
		row = 1
		self.All_Widget = []
		self.diff = dif_dict
		for diff_object in dif_dict:
			widget = {}
			sentence = diff_object['old'].replace('\r', '')
			corrected_sentence = diff_object['new'].replace('\r', '')
			widget['var'] = IntVar()
			_wraped_sentence = textwrap.fill(sentence, 40)
			_wraped_corrected_sentence = textwrap.fill(corrected_sentence, 40)
			row_count = len(_wraped_corrected_sentence) + 1
			a = Radiobutton(self.master, width= 40, text=  _wraped_sentence, value=1, variable= widget['var'])
			a.grid(row=row, column=1, columnspan=3, rowspan= row_count, padx=5, pady=5, sticky=W)
			#a.configure(wraplength=30 + 10)  
			
			b = Radiobutton(self.master, width= 40, text=  _wraped_corrected_sentence, value=2, variable= widget['var'])
			b.grid(row=row, column=4, columnspan=3, rowspan= row_count, padx=5, pady=5, sticky=W)
			#b.configure(wraplength=30 + 10)  
		
			widget['var'].set(2)
			self.All_Widget.append(widget)
			row += row_count
		Button(self.master, width = 20, text= 'Accept All', command = self.Accept_All).grid(row=row, column=1, columnspan=2, padx=5, pady=5)
		Button(self.master, width = 20, text= 'Decline All', command = self.Decline_All).grid(row=row, column=3, columnspan=2, padx=5, pady=5)
		Button(self.master, width = 20, text= 'Confirm', command = self.Confirm_Correction).grid(row=row, column=5, columnspan=2, padx=5, pady=5)

		self.master.protocol("WM_DELETE_WINDOW", self.Confirm_Correction)	

	def Accept_All(self):
		for widget in self.All_Widget:
			widget['var'].set(2)
		self.Confirm_Correction()

	def Decline_All(self):
		for widget in self.All_Widget:
			widget['var'].set(1)
		self.Confirm_Correction()	

	def Confirm_Correction(self):
		i = 0
		for widget in self.All_Widget:
			result = widget['var'].get()
			if result == 2:
				to_update = self.diff[i]['new']
				_index_in_check_list = self.index[i]
				self.Root.for_grammar_check[_index_in_check_list] = to_update
			i+=1

		for dict_key in self.Root.grammar_index_list:	
			all_index = self.Root.grammar_index_list[dict_key]
			temp_list = []
			for index in all_index:
				temp_list.append(self.Root.for_grammar_check[index])
			self.Root.report_details[dict_key] = ('\n').join(temp_list)
		self.master.destroy()
		self.Root.update_report_elements()
		self.Root.enable_btn()
		#self.Root.GenerateReportCSS()