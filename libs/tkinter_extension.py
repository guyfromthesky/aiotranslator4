from tkinter.ttk import Entry, Label, Style
from tkinter.ttk import Checkbutton, OptionMenu, Notebook, Radiobutton, LabelFrame, Button, Scale, Combobox


from tkinter import W, E, S, N, END,X, Y, BOTH, TOP, RIGHT, LEFT, BOTTOM, HORIZONTAL
from tkinter import INSERT, ACTIVE, NORMAL, DISABLED, WORD

from tkinter import Text, IntVar, StringVar, Menu, filedialog, messagebox
from tkinter import Frame, Listbox, Label, Toplevel, PhotoImage, Canvas

from tkhtmlview import HTMLScrolledText
from PIL import ImageTk, Image

import webbrowser

import textwrap
import re
import os

class AutocompleteCombobox(Combobox):

	def set_completion_list(self, completion_list):
		"""Use our completion list as our drop down selection menu, arrows move through menu."""
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
	def __init__(self, master, bg_cl= None):
		Frame.__init__(self, master, bg = bg_cl) 
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


class BugWriter_BottomPanel(Frame):
	def __init__(self, master):
		Frame.__init__(self, master) 

		Col = 1
		Row = 1
	
		#self.Bottom_Frame = master
		
		Label(master.Bottom_Frame, text='Update', width=10).grid(row=Row, column=Col, padx=5, pady=5, sticky=E)
		Col += 1
		Label(master.Bottom_Frame, textvariable=master._update_day, width=10).grid(row=Row, column=Col, padx=0, pady=5, sticky=E)
		master._update_day.set('-')
		Col += 1
		DictionaryLabelA = Label(master.Bottom_Frame, text=master.LanguagePack.Label['Database'], width=10)
		DictionaryLabelA.grid(row=Row, column=Col, padx=5, pady=5, sticky=W)
		Col += 1
		Label(master.Bottom_Frame, textvariable=master.DictionaryStatus, width=10).grid(row=Row, column=Col, padx=0, pady=5, sticky=W)
		master.DictionaryStatus.set('0')
		Col += 1
		Label(master.Bottom_Frame, text=master.LanguagePack.Label['Header'], width=10).grid(row=Row, column=Col, padx=5, pady=5, sticky=W)
		Col += 1
		Label(master.Bottom_Frame, textvariable=master.HeaderStatus, width=10).grid(row=Row, column=Col, padx=0, pady=5, sticky=W)
		master.HeaderStatus.set('0')
		Col += 1
		Label(master.Bottom_Frame, text= master.LanguagePack.Label['ProjectKey'], width=10).grid(row=Row, column=Col, padx=5, pady=5, sticky=W)
		Col += 2
		master.project_id_select = AutocompleteCombobox()
		master.project_id_select.Set_Entry_Width(30)
		master.project_id_select.set_completion_list([])
		master.project_id_select.grid(in_=master.Bottom_Frame, row=Row, column=Col, padx=5, pady=5, stick=W)
		master.project_id_select.bind("<<ComboboxSelected>>", master._save_project_key)
		Col += 1
		master.RenewTranslatorMain = Button(master.Bottom_Frame, text=master.LanguagePack.Button['RenewDatabase'], width=10, command= master.RenewMyTranslator, state=DISABLED, style= master.Btn_Style)
		master.RenewTranslatorMain.grid(row=Row, column=Col, padx=5, pady=5, stick=W)
		
		master.rowconfigure(0, weight=1)
		master.Bottom_Frame.grid_columnconfigure(7, minsize=200)

		for child in master.Bottom_Frame.winfo_children():
			if isinstance(child, Text) or isinstance(child, CustomText):
				master.text_widgets.append(child)
			elif isinstance(child, Label):
				master.label_widgets.append(child)	


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



# BUG WRITER CLASS
def Apply_Background_Image(Frame, name):
	bg_path =os.path.join( r'theme/background', name)
	
	if os.path.isfile(bg_path):
		print('Apply image: ', bg_path)
		background_image = PhotoImage(file = bg_path)
		background_label = Label(Frame, image = background_image)
		background_label.image = background_image
		background_label.place(x = 0, y = 0, relwidth = 1, relheight = 1)

# BUG WRITER TAB UI
def Generate_BugWriter_Tab_UI(master):

	
	
	MainPanel = Frame(master, name='mainpanel')
	MainPanel.pack(side=TOP, fill=BOTH, expand=Y)

	
	master.TAB_CONTROL = Notebook(MainPanel, name='notebook')
	 
	# extend bindings to top level window allowing
	#   CTRL+TAB - cycles thru tabs
	#   SHIFT+CTRL+TAB - previous tab
	#   ALT+K - select tab using mnemonic (K = underlined letter)
	master.TAB_CONTROL.enable_traversal()
	#TAB_CONTROL = Notebook(self.parent)
	
	## TAB 1
	master.BugWriterTab = Frame(master.TAB_CONTROL)
	master.TAB_CONTROL.add(master.BugWriterTab, text=master.LanguagePack.Tab['BugWriter'])
	#Apply_Background_Image(master.BugWriterTab, 'bg_writer.png')
	
	

	#img = ImageTk.PhotoImage(Image.open(r"C:\Users\evan\Documents\GitHub\aiotranslator4\theme\background\Knight.jpg"))
	#self.CustomWriter = Frame(TAB_CONTROL)
	#TAB_CONTROL.add(self.CustomWriter, text=self.LanguagePack.Tab['CustomBugWriter'])

	## TAB 2
	master.SimpleTranslatorTab = Frame(master.TAB_CONTROL)
	master.TAB_CONTROL.add(master.SimpleTranslatorTab, text=master.LanguagePack.Tab['SimpleTranslator'])
	
	#Apply_Background_Image(master.SimpleTranslatorTab, 'bg_simple.png')
	
	## TAB 3
	master.TranslateSettingTab = Frame(master.TAB_CONTROL)
	master.TAB_CONTROL.add(master.TranslateSettingTab, text=master.LanguagePack.Tab['Translator'])
	
	#Apply_Background_Image(master.TranslateSettingTab, 'bg_setting.png')

	master.TAB_CONTROL.pack(side=TOP, fill=BOTH, expand=Y)

	master.Bottom_Frame = Frame(master)
	master.Bottom_Frame.pack(side=RIGHT, fill=BOTH, expand=False)
	
	for frame_widget in master.TAB_CONTROL.winfo_children():
		master.frame_widgets.append(frame_widget)
	master.frame_widgets.append(master.Bottom_Frame)
	master.frame_widgets.append(MainPanel)
	master.frame_widgets.append(master)
	

# BUG WRITER 
def Generate_BugWriter_Menu_UI(master):
	menubar = Menu(master.parent)
	master.menubar = []

	menubar.configure(cursor='hand2')

	# Adding File Menu and commands 
	file = Menu(menubar, tearoff = 0)
	# Adding Load Menu  
	menubar.add_cascade(label =  master.LanguagePack.Menu['File'], menu = file) 
	file.add_command(label =  master.LanguagePack.Menu['LoadLicensePath'], command = lambda: Btn_Select_License_Path(master)) 
	#file.add_command(label =  self.LanguagePack.Menu['LoadDictionary'], command = self.SelectDictionary) 

	#file.add_command(label =  self.LanguagePack.Menu['LoadTM'], command = self.SelectTM) 
	file.add_separator() 
	#file.add_command(label =  self.LanguagePack.Menu['CreateTM'], command = self.SaveNewTM)
	#file.add_separator() 
	file.add_command(label =  master.LanguagePack.Menu['Exit'], command = master.on_closing) 
	# Adding Help Menu
	hotkey = Menu(menubar, tearoff=0)
	menubar.add_cascade(label =  'Hotkey', menu = hotkey) 
	hotkey.add_command(label = 'Save Report - Ctrl + S', command = master._save_report)
	hotkey.add_command(label = 'Load Report - Ctrl + L', command = master._load_report)
	hotkey.add_command(label = 'Reset Report - Ctrl + Q', command = master.ResetReport)
	hotkey.add_separator()
	hotkey.add_command(label = 'Get Title - Ctrl + E', command = master.GetTitle)
	hotkey.add_command(label = 'Get Report - Ctrl + R', command = master.generate_report)
	#hotkey.add_separator()  
	#hotkey.add_command(label = 'Grammar check - Ctrl + Q') 

	help_ = Menu(menubar, tearoff = 0)
	menubar.add_cascade(label =  master.LanguagePack.Menu['Help'], menu = help_) 
	help_.add_command(label =  master.LanguagePack.Menu['GuideLine'], command = OpenWeb) 
	help_.add_separator()
	help_.add_command(label =  master.LanguagePack.Menu['About'], command = About) 
	master.parent.config(menu = menubar)
	
	# Adding Help Menu
	language = Menu(menubar, tearoff = 0)
	menubar.add_cascade(label =  master.LanguagePack.Menu['Language'], menu = language) 
	language.add_command(label =  master.LanguagePack.Menu['Hangul'], command = master.SetLanguageKorean) 
	language.add_command(label =  master.LanguagePack.Menu['English'], command = master.SetLanguageEnglish) 
	master.parent.config(menu = menubar)

	# To change theme
	for menu_widget in menubar.winfo_children():
		master.menu_widgets.append(menu_widget)

def About():
	messagebox.showinfo("About....", "Creator: Evan@nexonnetworks.com")
def OpenWeb():
	webbrowser.open_new(r"https://confluence.nexon.com/display/NWMQA/%5BTranslation%5D+AIO+Translator")
def Error(self, ErrorText):
	messagebox.showerror('Translate error...', ErrorText)	


# SETTING UI
def Generate_Translate_Setting_UI(master, Tab):
	"""Create Translate Setting tab."""


	Top_Frame = Frame(Tab)
	Top_Frame.pack(side = TOP, fill=None, expand= False)

	Right_Frame = Frame(Tab)
	Right_Frame.pack(side = RIGHT, fill=BOTH, expand= False)
	Left_Frame = Frame(Tab)
	Left_Frame.pack(side = LEFT, fill=BOTH, expand= Y)

	Row = 1
	Label(Top_Frame, textvariable=master.Notice).grid(row=Row, column=0, columnspan = 10, padx=5, pady=5, sticky= E+W)

	Row += 1
	Label(Left_Frame, text= master.LanguagePack.Label['LicensePath']).grid(row=Row, column=0, padx=5, pady=5, sticky=E)
	master.TextLicensePath = Entry(Left_Frame,width = 100, state="readonly", textvariable=master.LicensePath)
	master.TextLicensePath.grid(row=Row, column=2, columnspan=7, padx=5, pady=5, sticky=W+E)
	master.Browse_License_Btn = Button(Right_Frame, width = master.HALF_BUTTON_SIZE, text=  master.LanguagePack.Button['Browse'], command = lambda: Btn_Select_License_Path(master), style=master.Btn_Style)
	master.Browse_License_Btn.grid(row=Row, column=9, padx=5, pady=5, sticky=W)

	Row += 1
	Label(Left_Frame, text= master.LanguagePack.Label['Transparent']) \
		.grid(row=Row, rowspan = 2, column=0, padx=5, pady=5, sticky=W)
	master.TransparentPercent = Scale(
		Left_Frame,
		length=400,
		from_=20,
		to=100,
		variable=master.Transparent,
		command= lambda value, root = master: Apply_Transparency(value, master),
		 
		orient=HORIZONTAL,)
	master.TransparentPercent.grid(
		row=Row, rowspan=2, column=2, columnspan=7, padx=5, pady=5,
		sticky=E+W)
	master.TransparentPercent.bind('<ButtonRelease-1>', lambda event, root = master: SaveAppTransparency(event, master),)	
	
	Button(
			Right_Frame,
			width=master.HALF_BUTTON_SIZE,
			text=master.LanguagePack.Button['Reset'],
			command=master.rebuild_UI, style=master.Btn_Style) \
		.grid(row=Row, column=9, padx=5, pady=5, rowspan=2, sticky=W)

	Row += 2
	Label(Left_Frame, text='Theme name:') \
		.grid(row=Row, rowspan=2, column=0, padx=5, pady=5, sticky=E)
	master.btn_remove_theme = Button(
		Right_Frame,
		width=master.HALF_BUTTON_SIZE,
		text="Remove Theme",
		command=master.remove_theme, style=master.Btn_Style)
	master.btn_remove_theme.grid(row=Row, column=9,  padx=5, pady=5, sticky=W)

	
	col = 2 # to add more buttons horizontally
	for theme_name in master.theme_names:
		master.radiobutton_theme_name = Radiobutton(
			Left_Frame,
			text=theme_name,
			value=theme_name,
			variable=master.strvar_theme_name,
			command=master.select_theme_name)
		master.radiobutton_theme_name.config(width=master.HALF_BUTTON_SIZE)
		master.radiobutton_theme_name.grid(
			row=Row, column=col, padx=0, pady=5, sticky=W)
		# Go to new line when reaching column 8
		if col < 7:
			col += 1
		else:
			col = 2
			Row += 1
	
	# Display selected theme
	config_theme_name = master.Configuration['Bug_Writer']['theme_name']
	if config_theme_name in master.theme_names:
		master.strvar_theme_name.set(config_theme_name)

	# Disable [Remove Theme] button if no theme is selected.
	if master.strvar_theme_name.get() not in master.theme_names:
		master.btn_remove_theme.config(state=DISABLED)

	for child in Left_Frame.winfo_children():
		if isinstance(child, Text) or isinstance(child, CustomText):
			master.text_widgets.append(child)
		elif isinstance(child, Label):
			master.label_widgets.append(child)
		

	for child in Right_Frame.winfo_children():
		if isinstance(child, Text) or isinstance(child, CustomText):
			master.text_widgets.append(child)
		elif isinstance(child, Label):
			master.label_widgets.append(child)
		
	for child in Top_Frame.winfo_children():
		if isinstance(child, Text) or isinstance(child, CustomText):
			master.text_widgets.append(child)
		elif isinstance(child, Label):
			master.label_widgets.append(child)
		


	master.frame_widgets.append(Right_Frame)
	master.frame_widgets.append(Left_Frame)
	master.frame_widgets.append(Top_Frame)

# BASIC BUG WRITER TEMPLATE
def Generate_BugWriter_UI(master, Tab):

	# Label widget is used to display text or image on screen

	Row=1
	Label(Tab, text= master.LanguagePack.Label['SourceLanguage'], width= master.HALF_BUTTON_SIZE).grid(row = Row, column = 1, padx=5, pady=5, stick=E+W)
	Label(Tab, text= master.LanguagePack.Label['MainLanguage'], width= master.HALF_BUTTON_SIZE).grid(row = Row, column = 2, padx=5, pady=5, stick=E+W)
	Label(Tab, text= master.LanguagePack.Label['SecondaryLanguage'], width= master.HALF_BUTTON_SIZE).grid(row = Row, column = 3, padx=5, pady=5, stick=E+W)
	Label(Tab, textvariable=master.Notice).grid(row=Row, column=4, columnspan=7, padx=5, pady=5, stick=W+E)

	Row += 1

	master.source_language_select = OptionMenu(Tab, master.source_language, *master.language_list, command = master.set_writer_language)
	master.source_language_select.config(width=master.HALF_BUTTON_SIZE)
	master.source_language_select.grid(row=Row, column=1, padx=0, pady=5, sticky=W)

	
	master.target_language_select = OptionMenu(Tab, master.target_language, *master.language_list, command = master.set_writer_language)
	master.target_language_select.config(width=master.HALF_BUTTON_SIZE)
	master.target_language_select.grid(row=Row, column=2, padx=0, pady=5, sticky=W)
	
	
	secondary_language_list = master.language_list + ['']
	master.secondary_target_language_select = OptionMenu(Tab, master.secondary_target_language, *secondary_language_list, command = master.set_writer_language)
	master.secondary_target_language_select.config(width=master.HALF_BUTTON_SIZE)
	master.secondary_target_language_select.grid(row=Row, column=3, padx=0, pady=5, sticky=W)
	
	#Button(Tab, width = master.HALF_BUTTON_SIZE, text= master.LanguagePack.Button['Save'], command= master._save_project_key).grid(row=Row, column=7, padx=5, pady=5, sticky=E)
	master.GetTitleBtn = Button(Tab, text=master.LanguagePack.Button['GetTitle'], width=10, command=master.GetTitle, state=DISABLED, style=master.Btn_Style)
	master.GetTitleBtn.grid(row=Row, column=10, padx=5, pady=5, stick=W+E)
	
	Row+=1
	Label(Tab, text=master.LanguagePack.Label['BugTitle']).grid(row=Row, column = 1, padx=5, pady=5, stick=W)

	#AutocompleteCombobox
	master.HeaderOptionA = AutocompleteCombobox(Tab)
	master.HeaderOptionA.Set_Entry_Width(master.HALF_BUTTON_SIZE*2)
	master.HeaderOptionA.set_completion_list(master.header_list)
	master.HeaderOptionA.grid(row=Row, column=2, columnspan=2, padx=5, pady=5, sticky=W+E)
	
	master.TextTitle = CustomText(Tab, width=75, height=3, undo=True, wrap=WORD)
	master.TextTitle.grid(row=Row, column=4, columnspan=8, rowspan=2, padx=5, pady=5, stick=W+E)

	Row+=1

	master.HeaderOptionB = AutocompleteCombobox(Tab)
	master.HeaderOptionB.Set_Entry_Width(master.HALF_BUTTON_SIZE*2)
	master.HeaderOptionB.set_completion_list(master.header_list)
	master.HeaderOptionB.grid(row=Row, column=2, columnspan=2, padx=5, pady=5, sticky=W+E)
	
	Row+=1
	Label(Tab, text=master.LanguagePack.Label['Server']).grid(row=Row, column=1, padx=5, pady=5, stick=W)

	master.TextServer = Text(Tab, width=35, height=1, undo=True)
	master.TextServer.grid(row=Row, column=2, columnspan=2, padx=5, pady=5, stick=W)

	Label(Tab, text=master.LanguagePack.Label['ReproduceTime']).grid(row=Row, column=4, padx=5, pady=5, stick=W)

	master.TextReprodTime = Text(Tab,width=20, height=1, undo=True)
	master.TextReprodTime.grid(row=Row, column=5, columnspan=3, padx=5, pady=5, stick=W+E)

	
	Checkbutton(Tab, text=master.LanguagePack.Label['TestInfo'], variable = master.SkipTestInfo, command = master.SaveSetting).grid(row=Row, column=8, padx=5, pady=5, stick=W)
	#master.SkipTestInfo.set(1)

	Button(Tab, text=master.LanguagePack.Button['Reset'], width=10, command= master.ResetTestReport, style=master.Btn_Style).grid(row=Row, column=10, padx=5, pady=5, stick=W+E)


	Row+=1
	Label(Tab, text=master.LanguagePack.Label['Client']).grid(row=Row, column=1, padx=5, pady=5, stick=W)

	master.TextClient = Text(Tab, width=35, height=1, undo=True)
	master.TextClient.grid(row=Row, column=2, columnspan=2, padx=5, pady=5, stick=W)
	master.TextClient.insert("end", "ver.")

	master.TextAccount = Text(Tab,width=20, height=1, undo=True)
	Label(Tab, text=master.LanguagePack.Label['IDChar']).grid(row=Row, column=4, padx=5, pady=5, stick=W)
	
	master.TextAccount.grid(row=Row, column=5, columnspan=3, padx=5, pady=5, stick=W+E)

	Checkbutton(Tab, text= 'Use Simple Template', variable = master.UseSimpleTemplate, command = master.SaveSetting).grid(row=Row, column=8, padx=5, pady=5, stick=W)
	#master.UseSimpleTemplate.set(1)

	Button(Tab, text=master.LanguagePack.Button['Load'], width=10, command= master._load_report, style=master.Btn_Style).grid(row=Row, column=9, padx=5, pady=5, stick=W+E)
	Button(Tab, text=master.LanguagePack.Button['Save'], width=10, command= master._save_report, style=master.Btn_Style).grid(row=Row, column=10, padx=5, pady=5, stick=W+E)

	Row+=1
	Label(Tab, width=10, text=master.LanguagePack.Label['Report']).grid(row=Row, column=1, columnspan=2, padx=5, pady=5, stick=W)
	
	Label(Tab, width=10, text=master.LanguagePack.Label['Search']).grid(row=Row, column=4, padx=5, pady=5, stick=W)

	master.search_entry = AutocompleteEntry([], Tab, listboxLength=6, width=75, matchesFunction=matches)
	master.search_entry.grid(row=Row, column=5, columnspan=6, padx=5, pady=5, sticky=E)

	Row+=1
	master.TextTestReport = CustomText(Tab, width=100, height=8, undo=True, wrap=WORD)
	master.TextTestReport.grid(row=Row, column=1, columnspan=10, rowspan=7, padx=5, pady=5, stick=W+E)
	Row+=7
	
	
	Row+=1
	Label(Tab, width=10, text=master.LanguagePack.Label['Steps']).grid(row=Row, column=1, columnspan=2, padx=0, pady=0, stick=W)


	Label(Tab, width=10, text=master.LanguagePack.Label['Expected']).grid(row=Row, column=6, columnspan=2, padx=0, pady=0, stick=W)
	#Button(Tab, text=master.LanguagePack.Button['Load'], width=10, command= master._load_report).grid(row=Row, column=9, padx=5, pady=5, stick=W+E)
	#master.grammar_check = Button(Tab, text="Grammar Check", width=10, command= master.analyze_grammar)
	#master.grammar_check.grid(row=Row, column=9, padx=5, pady=5, stick=W+E)

	#master.db_correction = Button(Tab, text="DB Falt Alarm", width=10	, command= master.analyze_fault_terminology, state=DISABLED)
	#master.db_correction.grid(row=Row, column=8, padx=5, pady=5, stick=W+E)


	master.ReviewReportBtn = Button(Tab, text="Review Report", width=10, command = lambda: review_report(master), state=DISABLED, style=master.Btn_Style)
	master.ReviewReportBtn.grid(row=Row, column=9, padx=5, pady=5, stick=W+E)	

	master.GetReportBtn = Button(Tab, text=master.LanguagePack.Button['GetReport'], width=10, command= master.generate_report, state=DISABLED, style=master.Btn_Style)
	master.GetReportBtn.grid(row=Row, column=10, padx=5, pady=5, stick=W+E)
	

	Row+=1
	master.TextReproduceSteps = CustomText(Tab, width=50, height=7, undo=True, wrap=WORD)
	master.TextReproduceSteps.grid(row=Row, column=1, columnspan=5, rowspan=7, padx=5, pady=5, stick=W+E)
	master.TextShouldBe = CustomText(Tab, width=50, height=7, undo=True, wrap=WORD) 
	master.TextShouldBe.grid(row=Row, column=6, columnspan=5, padx=5, pady=5, stick=W+E)

	Tab.bind_all('<Key>', master.handle_wait)
	Tab.bind_all('<Control-r>', master.generate_report)
	Tab.bind_all('<Control-e>', master.GetTitle)
	Tab.bind_all('<Control-s>', master._save_report)
	Tab.bind_all('<Control-l>', master._load_report)
	Tab.bind_all('<Control-q>', master.ResetReport)

	# Add all Text in the tab to a list to change theme dynamically
	for child in Tab.winfo_children():
		if isinstance(child, Text) or isinstance(child, CustomText):
			master.text_widgets.append(child)
		elif isinstance(child, Label):
			master.label_widgets.append(child)
		#elif isinstance(child, OptionMenu):
		#	master.menu_widgets.append(child)

def Generate_MDNF_BugWriter_UI(master, Tab):
	# Title
	Row=1

	Label(Tab, text= master.LanguagePack.Label['SourceLanguage'], width= master.HALF_BUTTON_SIZE).grid(row = Row, column = 1, padx=5, pady=5, stick=E+W)
	Label(Tab, text= master.LanguagePack.Label['MainLanguage'], width= master.HALF_BUTTON_SIZE).grid(row = Row, column = 2, padx=5, pady=5, stick=E+W)
	Label(Tab, text= master.LanguagePack.Label['SecondaryLanguage'], width= master.HALF_BUTTON_SIZE).grid(row = Row, column = 3, padx=5, pady=5, stick=E+W)
	Label(Tab, textvariable=master.Notice).grid(row=Row, column=4, columnspan=7, padx=5, pady=5, stick=E)

	Row += 1

	master.source_language_select = OptionMenu(Tab, master.source_language, *master.language_list, command = master.set_writer_language)
	master.source_language_select.config(width=master.HALF_BUTTON_SIZE)
	master.source_language_select.grid(row=Row, column=1, padx=0, pady=5, sticky=W)

	master.target_language_select = OptionMenu(Tab, master.target_language, *master.language_list, command = master.set_writer_language)
	master.target_language_select.config(width=master.HALF_BUTTON_SIZE)
	master.target_language_select.grid(row=Row, column=2, padx=5, pady=5, sticky=W)
	
	secondary_language_list = master.language_list + ['']
	master.secondary_target_language_select = OptionMenu(Tab, master.secondary_target_language, *secondary_language_list, command = master.set_writer_language)
	master.secondary_target_language_select.config(width=master.HALF_BUTTON_SIZE)
	master.secondary_target_language_select.grid(row=Row, column=3, padx=5, pady=5, sticky=W)

	Label(Tab, width=10, text=master.LanguagePack.Label['Search']).grid(row=Row, column=4, padx=0, pady=5, stick=W)
	master.search_entry = AutocompleteEntry([], Tab, listboxLength=6, width=50, matchesFunction=matches)
	master.search_entry.grid(row=Row, column=5, columnspan=5, padx=5, pady=5, sticky=W+E)

	master.GetTitleBtn = Button(Tab, text=master.LanguagePack.Button['GetTitle'], width=10, command=master.GetTitle, style=master.Btn_Style, state=DISABLED)
	master.GetTitleBtn.grid(row=Row, column=10, padx=5, pady=5, stick=W+E)
	
	Row+=1
	Label(Tab, text=master.LanguagePack.Label['BugTitle']).grid(row=Row, column = 1, padx=5, pady=5, stick=W)

	#AutocompleteCombobox
	master.HeaderOptionA = AutocompleteCombobox(Tab)
	master.HeaderOptionA.Set_Entry_Width(master.HALF_BUTTON_SIZE*2)
	master.HeaderOptionA.set_completion_list(master.header_list)
	master.HeaderOptionA.grid(row=Row, column=2, columnspan=2, padx=5, pady=5, sticky=W+E)
	
	master.TextTitle = CustomText(Tab, width=90, height=3, undo=True, wrap=WORD)
	master.TextTitle.grid(row=Row, column=4, columnspan=7, rowspan=2, padx=5, pady=5, stick=W+E)
	
	Row+=1

	master.HeaderOptionB = AutocompleteCombobox(Tab)
	master.HeaderOptionB.Set_Entry_Width(master.HALF_BUTTON_SIZE*2)
	master.HeaderOptionB.set_completion_list(master.header_list)
	master.HeaderOptionB.grid(row=Row, column=2, columnspan=2, padx=5, pady=5, sticky=W+E)
	

	# Report
	Row+=1
	Label(Tab, text=master.LanguagePack.Label['Reproducibility']).grid(row=Row, column=1, padx=5, pady=5, stick=W)
	master.Reproducibility = Text(Tab, width=20, height=1, undo=True)
	master.Reproducibility.grid(row=Row, column=2, columnspan=2,  padx=5, pady=5, stick=W+E)		


	#Label(Tab, width=10, text=master.LanguagePack.Label['Search']).grid(row=Row, column=4, padx=0, pady=5, stick=W)
	#master.search_entry = AutocompleteEntry([], Tab, listboxLength=6, width=50, matchesFunction=matches)
	#master.search_entry.grid(row=Row, column=5, columnspan=5, padx=5, pady=5, sticky=W+E)

	Button(Tab, text=master.LanguagePack.Button['Reset'], width=10, command= master.ResetTestReport, style=master.Btn_Style).grid(row=Row, column=10, padx=5, pady=5, stick=W+E)
	
	Row+=1
	Label(Tab, text=master.LanguagePack.Label['EnvInfo']).grid(row=Row, column=1, padx=5, pady=5, stick=W)
	
	#Checkbutton(Tab, text= 'Use Simple Template', variable = master.UseSimpleTemplate, command = master.SaveSetting).grid(row=Row, column=8, padx=5, pady=5, stick=W)
	#master.UseSimpleTemplate.set(1)
	
	Label(Tab, width=10, text=master.LanguagePack.Label['Report']).grid(row=Row, column=4, columnspan=2, padx=0, pady=5, stick=W)

	#Button(Tab, text=master.LanguagePack.Button['Load'], width=10, command= master.LoadTempReport).grid(row=Row, column=8, padx=5, pady=5, stick=W+E)

	Button(Tab, text=master.LanguagePack.Button['Load'], width=10, command= master._load_report, style=master.Btn_Style).grid(row=Row, column=9, padx=5, pady=5, stick=W+E)
	
	Button(Tab, text=master.LanguagePack.Button['Save'], width=10, command= master._save_report, style=master.Btn_Style).grid(row=Row, column=10, padx=5, pady=5, stick=W+E)

	Row+=1
	master.EnvInfo = Text(Tab, width=40, height=9, undo=True)
	master.EnvInfo.grid(row=Row, column=1, columnspan=3, rowspan= 9,  padx=5, pady=5, stick=W+E)
	master.EnvInfo.config(state=DISABLED)
	
	master.ResetInfoSection()
	

	master.TextTestReport = CustomText(Tab, width=90, height=9, undo=True, wrap=WORD)
	master.TextTestReport.grid(row=Row, column=4, columnspan=7, rowspan=9, padx=5, pady=5, stick=W+E)
	Row+=8
	
	
	Row+=1
	Label(Tab, width=10, text=master.LanguagePack.Label['Steps']).grid(row=Row, column=1, columnspan=2, padx=0, pady=0, stick=W)


	Label(Tab, width=10, text=master.LanguagePack.Label['Expected']).grid(row=Row, column=6, columnspan=2, padx=0, pady=0, stick=W)
	#Button(Tab, text=master.LanguagePack.Button['Load'], width=10, command= master._load_report).grid(row=Row, column=9, padx=5, pady=5, stick=W+E)
	
	#master.grammar_check.grid(row=Row, column=9, padx=5, pady=5, stick=W+E)

	#master.db_correction = Button(Tab, text="DB Falt Alarm", width=10	, command= master.analyze_fault_terminology, state=DISABLED)
	#master.db_correction.grid(row=Row, column=8, padx=5, pady=5, stick=W+E)
	#master.grammar_check = Button(Tab, text="Grammar Check", width=10, command= master.analyze_grammar)
	#master.grammar_check.grid(row=Row, column=7, padx=5, pady=5, stick=W+E)	
	master.ReviewReportBtn = Button(Tab, text="Review Report", width=10, command= master.review_report, state=DISABLED, style=master.Btn_Style)
	master.ReviewReportBtn.grid(row=Row, column=8, padx=5, pady=5, stick=W+E)	

	#master.ReviewReportBtn = Button(Tab, text="Review Report", width=10, command= master.review_report, state=DISABLED, style=master.Btn_Style)
	#master.ReviewReportBtn.grid(row=Row, column=9, padx=5, pady=5, stick=W+E)	

	master.GetReportBtn = Button(Tab, text=master.LanguagePack.Button['GetReport'], width=10, command= master.generate_report, state=DISABLED, style=master.Btn_Style)
	master.GetReportBtn.grid(row=Row, column=10, padx=5, pady=5, stick=W+E)
	

	Row+=1
	master.TextReproduceSteps = CustomText(Tab, width=50, height=7, undo=True, wrap=WORD)
	master.TextReproduceSteps.grid(row=Row, column=1, columnspan=5, rowspan=7, padx=5, pady=5, stick=W+E)
	master.TextShouldBe = CustomText(Tab, width=50, height=7, undo=True, wrap=WORD) 
	master.TextShouldBe.grid(row=Row, column=6, columnspan=5, padx=5, pady=5, stick=W+E)
	
	if master.language_tool_enable == True:
		Tab.bind_all('<Control-q>', master.analyze_report_grammar)
	
	master.TextTitle.focus_set()
	Tab.bind_all('<Key>', master.handle_wait)
	Tab.bind_all('<Control-r>', master.generate_report)
	Tab.bind_all('<Control-e>', master.GetTitle)
	Tab.bind_all('<Control-s>', master._save_report)
	Tab.bind_all('<Control-l>', master._load_report)
	Tab.bind_all('<Control-q>', master.ResetReport)

	for child in Tab.winfo_children():
		if isinstance(child, Text) or isinstance(child, CustomText):
			master.text_widgets.append(child)
		elif isinstance(child, Label):
			master.label_widgets.append(child)	

def Generate_XH_BugWriter_UI(master, Tab):

	Row=1
	Label(Tab, text= master.LanguagePack.Label['SourceLanguage'], width= master.HALF_BUTTON_SIZE).grid(row = Row, column = 1, padx=5, pady=5, stick=E+W)
	Label(Tab, text= master.LanguagePack.Label['MainLanguage'], width= master.HALF_BUTTON_SIZE).grid(row = Row, column = 2, padx=5, pady=5, stick=E+W)
	Label(Tab, text= master.LanguagePack.Label['SecondaryLanguage'], width= master.HALF_BUTTON_SIZE).grid(row = Row, column = 3, padx=5, pady=5, stick=E+W)
	Label(Tab, textvariable=master.Notice).grid(row=Row, column=4, columnspan=7, padx=5, pady=5, stick=E)

	Row += 1
	
	master.source_language_select = OptionMenu(Tab, master.source_language, *master.language_list, command = master.set_writer_language)
	master.source_language_select.config(width=master.HALF_BUTTON_SIZE)
	master.source_language_select.grid(row=Row, column=1, padx=0, pady=5, sticky=W)

	master.target_language_select = OptionMenu(Tab, master.target_language, *master.language_list, command = master.set_writer_language)
	master.target_language_select.config(width=master.HALF_BUTTON_SIZE)
	master.target_language_select.grid(row=Row, column=2, padx=5, pady=5, sticky=W)

	secondary_language_list = master.language_list + ['']
	master.secondary_target_language_select = OptionMenu(Tab, master.secondary_target_language, *secondary_language_list, command = master.set_writer_language)
	master.secondary_target_language_select.config(width=master.HALF_BUTTON_SIZE)
	master.secondary_target_language_select.grid(row=Row, column=3, padx=5, pady=5, sticky=W)

	Label(Tab, width=10, text=master.LanguagePack.Label['Search']).grid(row=Row, column=4, padx=0, pady=5, stick=W)
	master.search_entry = AutocompleteEntry([], Tab, listboxLength=6, width=55, matchesFunction=matches)
	master.search_entry.grid(row=Row, column=5, columnspan=5, padx=5, pady=5, sticky=W+E)


	master.GetTitleBtn = Button(Tab, text=master.LanguagePack.Button['GetTitle'], width=10, command=master.GetTitle, state=DISABLED, style=master.Btn_Style)
	master.GetTitleBtn.grid(row=Row, column=10, padx=5, pady=5, stick=W+E)
	
	Row+=1
	Label(Tab, text=master.LanguagePack.Label['BugTitle']).grid(row=Row, column = 1, padx=5, pady=5, stick=W)

	master.HeaderOptionA = AutocompleteCombobox(Tab)
	master.HeaderOptionA.Set_Entry_Width(master.HALF_BUTTON_SIZE*2)
	master.HeaderOptionA.set_completion_list(master.header_list)
	master.HeaderOptionA.grid(row=Row, column=2, columnspan=2, padx=5, pady=5, sticky=W+E)
	
	master.TextTitle = CustomText(Tab, width=97, height=3, undo=True, wrap=WORD)
	master.TextTitle.grid(row=Row, column=4, columnspan=7, rowspan=2, padx=5, pady=5, stick=W+E)
	
	Row+=1

	master.HeaderOptionB = AutocompleteCombobox(Tab)
	master.HeaderOptionB.Set_Entry_Width(master.HALF_BUTTON_SIZE*2)
	master.HeaderOptionB.set_completion_list(master.header_list)
	master.HeaderOptionB.grid(row=Row, column=2, columnspan=2, padx=5, pady=5, sticky=W+E)

	Row+=1
	Label(Tab, text=master.LanguagePack.Label['PreConition']).grid(row=Row, column=1, padx=5, pady=5, stick=W)
	
	Label(Tab, width=10, text=master.LanguagePack.Label['Report']).grid(row=Row, column=7, columnspan=2, padx=0, pady=5, stick=W)

	Row+=1
	master.Precondition = Text(Tab, width=75, height=9, undo=True)
	master.Precondition.grid(row=Row, column=1, columnspan=5, rowspan= 9,  padx=5, pady=5, stick=W+E)
	
	master.TextTestReport = CustomText(Tab, width=75, height=9, undo=True, wrap=WORD)
	master.TextTestReport.grid(row=Row, column=7, columnspan=5, rowspan=9, padx=5, pady=5, stick=W+E)
	Row+=8
	
	
	Row+=1
	Label(Tab, width=10, text=master.LanguagePack.Label['Steps']).grid(row=Row, column=1, columnspan=2, padx=0, pady=0, stick=W)


	Label(Tab, width=10, text=master.LanguagePack.Label['Expected']).grid(row=Row, column=7, columnspan=2, padx=0, pady=0, stick=W)

	master.ReviewReportBtn = Button(Tab, text="Review Report", width=10, command= master.review_report,  state=DISABLED, style=master.Btn_Style)
	master.ReviewReportBtn.grid(row=Row, column=9, padx=5, pady=5, stick=W+E)	

	master.GetReportBtn = Button(Tab, text=master.LanguagePack.Button['GetReport'], width=10, command= master.generate_report,  state=DISABLED, style=master.Btn_Style)
	master.GetReportBtn.grid(row=Row, column=10, padx=5, pady=5, stick=W+E)
	

	Row+=1
	master.TextReproduceSteps = CustomText(Tab, width=50, height=8, undo=True, wrap=WORD)
	master.TextReproduceSteps.grid(row=Row, column=1, columnspan=5, rowspan=7, padx=5, pady=5, stick=W+E)
	master.TextShouldBe = CustomText(Tab, width=50, height=8, undo=True, wrap=WORD) 
	master.TextShouldBe.grid(row=Row, column=7, columnspan=5, padx=5, pady=5, stick=W+E)

	master.TextTitle.focus_set()
	Tab.bind_all('<Key>', master.handle_wait)
	Tab.bind_all('<Control-r>', master.generate_report)
	Tab.bind_all('<Control-e>', master.GetTitle)
	Tab.bind_all('<Control-s>', master._save_report)
	Tab.bind_all('<Control-l>', master._load_report)
	Tab.bind_all('<Control-q>', master.ResetReport)

	for child in Tab.winfo_children():
		if isinstance(child, Text) or isinstance(child, CustomText):
			master.text_widgets.append(child)
		elif isinstance(child, Label):
			master.label_widgets.append(child)	

def matches(fieldValue, acListEntry):
	pattern = re.compile(re.escape(fieldValue) + '.*', re.IGNORECASE)
	return re.match(pattern, acListEntry)

def Generate_SimpleTranslator_UI(master, Tab):
	Top_Frame = Frame(Tab)
	Top_Frame.pack(side = TOP, fill=None, expand= False)

	#Right_Frame = Frame(Tab)
	#Right_Frame.pack(side = RIGHT, fill=BOTH, expand= False)
	Main_Frame = Frame(Tab)
	Main_Frame.pack(side = BOTTOM, fill=BOTH, expand= False)
	
	master.parent.update()
	x_delta = int(round((master.parent.winfo_width() - 1080)/20))
	master.SOURCE_WIDTH += x_delta
	print(master.SOURCE_WIDTH, master.parent.winfo_width())
	print(master.ROW_SIZE, master.parent.winfo_height())
	y_delta = int(round((master.parent.winfo_height() - 560)/20))
	master.ROW_SIZE += y_delta 
	Row=1
	Label(Top_Frame, textvariable=master.Notice).grid(row=Row, column=0, columnspan=10, padx=5, pady=5, sticky=W+E)

	Row +=1
	Label(Main_Frame, text=master.LanguagePack.Label['SourceText']).grid(row=Row, column=0, columnspan = 5, padx=5, pady=0)
	Label(Main_Frame, text=master.LanguagePack.Label['TargetText']).grid(row=Row, column=5, columnspan = 5, padx=5, pady=0)
	#New Row

	Row +=1
	master.SourceText = Text(Main_Frame, width = master.SOURCE_WIDTH, height=master.ROW_SIZE, undo=True) 
	master.SourceText.grid(row=Row, column=0, columnspan=5, rowspan=master.ROW_SIZE, padx=5, pady=5, sticky=N+S+E+W)
	master.SourceText.bind("<Double-Tab>", master.BindSwap)

	master.TargetText = Text(Main_Frame, width = master.SOURCE_WIDTH, height=master.ROW_SIZE, undo=True) #
	master.TargetText.grid(row = Row, column=5, columnspan=5, rowspan=master.ROW_SIZE, padx=5, pady=5, sticky=N+S+E+W)
	
	Row +=master.ROW_SIZE

	Label(Main_Frame, text= master.LanguagePack.Label['SourceLanguage'], width= master.HALF_BUTTON_SIZE).grid(row = Row, column = 0, padx=5, pady=5, stick=E+W)
	

	master.simple_source_language_select = OptionMenu(Main_Frame, master.simple_source_language, *master.language_list, command = master.set_simple_language)
	master.simple_source_language_select.config(width=master.HALF_BUTTON_SIZE)
	master.simple_source_language_select.grid(row=Row, column=1, padx=0, pady=5, sticky=W)
	master.simple_source_language.set('Hangul')



	Button(Main_Frame, text=master.LanguagePack.Button['Swap'], width = 20, command= master.Swap, style=master.Btn_Style).grid(row=Row, column=6, padx=5, pady=5)	
	
	Button(Main_Frame, text=master.LanguagePack.Button['Copy'], width = master.BUTTON_SIZE, command= master.BtnCopy, style=master.Btn_Style).grid(row = Row, column=7, padx=5, pady=5, sticky=E)

	master.TranslateBtn = Button(Main_Frame, text=master.LanguagePack.Button['Translate'], width = master.BUTTON_SIZE, command= master.single_translate, style=master.Btn_Style, state=DISABLED)
	master.TranslateBtn.grid(row=Row, column=8, padx=5, pady=5, sticky=E)		

	Row +=1

	Label(Main_Frame, text= master.LanguagePack.Label['MainLanguage'], width= master.HALF_BUTTON_SIZE).grid(row = Row, column = 0, padx=5, pady=5, stick=E+W)
	
	
	master.simple_target_language_select = OptionMenu(Main_Frame, master.simple_target_language, *master.language_list, command = master.set_simple_language)
	master.simple_target_language_select.config(width=master.HALF_BUTTON_SIZE)
	master.simple_target_language_select.grid(row=Row, column=1, padx=0, pady=5, sticky=W)
	master.simple_target_language.set('English')		
	
	Label(Main_Frame, text= master.LanguagePack.Label['SecondaryLanguage'], width= master.HALF_BUTTON_SIZE).grid(row = Row, column = 2, padx=5, pady=5, stick=E+W)
	
	secondary_language_list = master.language_list + ['']

	
	master.simple_secondary_target_language_select = OptionMenu(Main_Frame, master.simple_secondary_target_language, *secondary_language_list, command = master.set_simple_language)
	master.simple_secondary_target_language_select.config(width=master.HALF_BUTTON_SIZE)
	master.simple_secondary_target_language_select.grid(row=Row, column=3, padx=0, pady=5, sticky=W)
	master.simple_secondary_target_language.set('Japanese')
	
	Button(Main_Frame, text= 'Trilingual Copy', width = master.BUTTON_SIZE, command= master.btn_trilingual, style=master.Btn_Style).grid(row = Row, column=6, padx=5, pady=5)
	
	Button(Main_Frame, text=master.LanguagePack.Button['Bilingual'], width = master.BUTTON_SIZE, command= master.btn_bilingual_copy, style=master.Btn_Style).grid(row = Row, column=7, padx=5, pady=5, sticky=E)
	master.dual_translate_btn = Button(Main_Frame, text= 'Dual Translate', width = master.BUTTON_SIZE, command= master.dual_translate, style=master.Btn_Style, state=DISABLED)
	master.dual_translate_btn.grid(row = Row, column=8, padx=5, pady=5, sticky=E)

	# Add all Text in the tab to a list to change color dynamically
	for child in Main_Frame.winfo_children():
		if isinstance(child, Text) or isinstance(child, CustomText):
			master.text_widgets.append(child)
		elif isinstance(child, Label):
			master.label_widgets.append(child)

	for child in Top_Frame.winfo_children():
		if isinstance(child, Text) or isinstance(child, CustomText):
			master.text_widgets.append(child)
		elif isinstance(child, Label):
			master.label_widgets.append(child)	


	master.frame_widgets.append(Main_Frame)
	master.frame_widgets.append(Top_Frame)


	Tab.bind_all('<Key>', master.handle_wait)

# Related function
def Btn_Select_License_Path(master):
	filename = filedialog.askopenfilename(title =  master.LanguagePack.ToolTips['SelectDB'],filetypes = (("JSON files","*.json" ), ), )	
	if filename != "":
		LicensePath = master.CorrectPath(filename)
		master.AppConfig.Save_Config(master.AppConfig.Translator_Config_Path, 'Translator', 'license_file', LicensePath, True)
		os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = LicensePath
		master.LicensePath.set(LicensePath)
		master.rebuild_UI()
	else:
		master.Notice.set("No file is selected")

def review_report(master):

	child_windows = Toplevel(master.parent)
	child_windows.resizable(False, False)
	child_windows.title("Report reviewer")
	master.report_review = HTMLScrolledText(child_windows)
	master.report_review.set_html(master.html_content)
	master.report_review.pack(pady=5, padx=5, fill=BOTH)

# SUPPORT FUNCTION

def SaveAppTransparency(event, master):
	transparency = int(float(master.TransparentPercent.get()))
	Apply_Transparency(transparency, master)
	master.AppConfig.Save_Config(master.AppConfig.Writer_Config_Path, 'Bug_Writer', 'Transparent', transparency)

def Apply_Transparency(transparency, master):
	_transparency = int(float(transparency))
	if _transparency < 75:
		_transparency = 80 - (_transparency/3)
	elif _transparency < 50:
		_transparency = 50 - (_transparency/5)
	elif _transparency < 25:
		_transparency = 25 - (_transparency/10)	
	master.parent.attributes("-alpha", float(_transparency)/100)