####---------------------------------------------------------------------######
#### 			     Notepad clone	   	   	              +  				  +	
####     		Created By PamekasanCode                              +
####	The Program is open source and free so everyone can develop it        +
####--------------------------------------------------------------------------+


from tkinter import filedialog as fdial, ttk, messagebox as msgbox
import tkinter.font as tkf
from tkinter import *
import os, sys, time, sqlite3

class UI:
	def __init__(self):
		self.root = Tk()
		self.database_name = "AF_dat.db"		# not build yet :v
		self.default_geometry = "500x530"
		if not self.load_current_size():
			self.root.geometry(self.default_geometry)	# this instance will be set if there is no user configuration yet
		self.root.iconbitmap("note.ico")
		self.initialized = False
		self.file_saved = False
		self.name_saved = False
		self.window_widget_init = False
		self.scroll_stat = False
		self.indexes = []
		self.prev_string = None 			# for the search function only
		self.counter_index = 0
		self.idx = None
		self.status_bar_ = BooleanVar()
		self.results = False
		self.word_wrap_ = BooleanVar()
		self.word_wrap_.set(False)
		self.status_bar_.set(False)
		self._default_program_name = "Alvin Fastnote"
		self.cur_row = 0
		self.cur_col = 0	

	def load_current_size(self):
		if not os.path.isfile(self.database_name):
			return False

		con = sqlite3.connect(self.database_name)
		cur = con.cursor()
		return cur.execute("SELECT * FROM configuration").fetchall()

	def make_database(self, *conf_to_save):
		if os.path.isfile(self.database_name):
			return False

		con = sqlite3.connect(self.database_name)
		cur = con.cursor()

		cur.execute(f"CREATE TABLE configuration {conf_to_save}")
		con.commit()
		con.close()

	def save_current(*conf_to_save):
		if not os.path.isfile(self.database_name):
			self.make_database()
			return False

		con = sqlite3.connect(self.database_name)
		cur = con.cursor()

		cur.execute(f"INSERT INTO configuration VALUES {conf_to_save}")
		con.commit()
		con.close()

	def change_title(self, args):
		self.root.title(args + " - " + self._default_program_name)

	def movement_bind(self, filename):
		def unbinding():
			self.canvas.unbind("<Key>")
			self.change_title(filename + " " + u'\u2022')
			self.file_saved = False

		self.canvas.bind("<Key>", lambda x: unbinding())

	def search_function(self, mode):
		current_conf = {"fg" : self.canvas["fg"], "bg" : self.canvas["bg"]}
		self.counter = 0

		def Find():
			gotocurrent()
			string = find_entry.get()
			self.canvas.tag_remove('found', "1.0", END)
			if string != self.prev_string and string:
				if not self.idx:
					self.idx = "1.0"
				else:
					self.idx = self.idx

				while True:
					self.idx = self.canvas.search(string, self.idx, nocase=1, stopindex=END)
					if not self.idx:
						break
					lastdix = '%s+%dc' % (self.idx, len(string))
					self.indexes.append([self.idx, lastdix])
					self.idx = lastdix
				self.prev_string = string

			if len(self.indexes) > 0:
				if self.counter_index == len(self.indexes):
					self.counter_index = 0								
				self.canvas.tag_add('found', self.indexes[self.counter_index][0], self.indexes[self.counter_index][1])
				self.counter_index += 1
				self.canvas.tag_config('found', foreground="red", background="yellow")
			self.counter += 1
			if self.counter > 0:
				self.find_button.config(text="Next")

		def closing_proc():
			if len(find_entry.get()) == 0:
				find_entry.unbind("<Return>")
				node_root.unbind("<FocusOut>")
				self.counter_index = 0
				self.counter = 0
				return node_root.destroy()
			gotocurrent()
			self.counter_index = 0
			self.prev_string = None
			self.indexes.clear()
			find_entry.unbind("<Return>")
			node_root.unbind("<FocusOut>")
			self.counter = 0
			node_root.destroy()

		def gotocurrent():
			self.canvas.tag_config('found', foreground=current_conf["fg"], background=current_conf["bg"], border=5)
			self.canvas.tag_remove('found', "1.0", END)

		def find_only():
			global node_root, find_entry
			
			node_root = Toplevel()
			node_root.title("Find a Word")
			node_root.iconbitmap("note.ico")
			node_root.protocol("WM_DELETE_WINDOW", closing_proc)
			node_root.bind("<FocusOut>", lambda x: gotocurrent())

			find_ = Label(node_root, text="Find what? ")
			find_.pack(side=LEFT)
			find_entry = Entry(node_root, width=50)
			find_entry.pack(side=LEFT)
			find_entry.bind("<Return>", lambda x: Find())
			find_entry.focus()

			self.find_button = Button(node_root, text="Find", command=Find)
			self.find_button.pack(side=LEFT)

		def replace_():
			self.indexes.clear()
			gotocurrent()
			string = find_entry.get()
			replacement = self.replaces.get()
			self.canvas.tag_remove("found", "1.0", END)
			self.idx = "1.0"

			text = self.canvas.get("1.0", END)

			new = text.replace(string, replacement)

			self.canvas.delete("1.0", "end")
			self.canvas.insert("1.0", new)

			if self.prev_string != string:
				while True:
					self.idx = self.canvas.search(replacement, self.idx, nocase=1, stopindex=END)

					if not self.idx:
						break

					lastdix = "%s+%dc" % (self.idx, len(replacement))
					self.canvas.tag_add('found', self.idx, lastdix)
					self.idx = lastdix

				self.canvas.tag_config('found', foreground="red", background="yellow")
			self.prev_string = string

		def replace():
			global node_root, find_entry
			node_root = Toplevel()
			node_root.title("Find and Replace a Word")
			node_root.iconbitmap("note.ico")
			node_root.protocol("WM_DELETE_WINDOW", closing_proc)
			node_root.bind("<FocusOut>", lambda x: gotocurrent())

			find_ = Label(node_root, text="Find what? ")
			find_.grid(row=0, column=0)
			find_entry = Entry(node_root, width=50)
			find_entry.grid(row=0, column=1)
			find_entry.bind("<Return>", lambda x: Find())
			find_entry.focus()

			self.find_button = Button(node_root, text="Find", command=Find, bd=2)
			self.find_button.grid(row=0, column=2)

			replace_label = Label(node_root, text="Replace with")
			replace_label.grid(row=1, column=0)

			self.replaces = Entry(node_root, width=50)
			self.replaces.grid(row=1, column=1)

			self.replace_btn = Button(node_root, text="Replace all", command=replace_, bd=2)
			self.replace_btn.grid(row=1, column=2, padx=5)

			return "break"

		if mode == "find_only":
			return find_only()
		elif mode == "replace":
			return replace()
		else:
			return

	def progress_bar(self):
		self.bars = ttk.Progressbar(self.status, orient=HORIZONTAL, mode="determinate", length=100)
		self.bars.pack(side=LEFT)

	def save(self):
		if not self.name_saved:
			return self.save_as()

		with open(self.filename_path, "w") as f:
			f.write(self.canvas.get("1.0", END))
			f.close()

		if self.status_bar_:
			self.status_bar(mode="conf", args="File has been saved!")

		self.change_title(self.filename_path) 
		self.movement_bind(self.filename_path)

	def save_as(self, rename=False):
		if self.status_bar_.get():
			self.progress_bar()
		def increase_progress():
			if not self.status_bar_.get():
				return
			self.bars["value"] += 25
			self.root.update_idletasks()
			time.sleep(0.1)

		if self.name_saved:
			if not rename:
				return self.save()

		increase_progress()

		self.filename_path = fdial.asksaveasfilename(filetypes=[("Text Documents, '.txt'", ".txt"), ("All File", "*.*")], defaultextension=[("Text Documents '.txt'", ".txt")])
		if not self.filename_path or self.filename_path == "":
			return False
		self.status_bar("conf", "Saving your file in " + self.filename_path)
	
		increase_progress()

		with open(self.filename_path, "w") as f:
			f.write(self.canvas.get("1.0", END))
			f.close()

		increase_progress()

		if self.status_bar_:
			self.status_bar(mode="conf", args="File has been saved in " + self.filename_path)

		self.change_title(self.filename_path) 
		self.movement_bind(self.filename_path)

	def check_save(self, rename=False):
		if rename:
			self.save_as(rename=True)
		elif not self.file_saved: 		# check for any changed data in that the name of the file is not saved. is guarantee that the name is not saved
			if not self.name_saved:
				self.save_as()
				self.name_saved = True
				self.file_saved = True
			else:
				self.save()
				self.file_saved = True

	def confirm_exit(self, just_check=False):
		if not self.name_saved:
			if not self.file_saved:
				try: 
					respond = msgbox.askyesnocancel("Attention", f"'{self.filename_path}'" + " is not saved Do you want to save it?")
				except:
					respond = msgbox.askyesnocancel("Attention", f"'{self.filename_path_default}'" + " is not saved Do you want to save any changed of it?")
				finally:
					if respond:
						self.save_as()

					elif respond == False:
						self.save_current()
						self.root.destroy()

					elif respond == None:
						pass

		else:
			self.save_current()
			self.root.destroy()

	def Nodes(self):
		self.main_frame = Frame(self.root)
		self.main_frame.pack(side=TOP, expand=True, fill=BOTH)
		self.bottom_frame = Frame(self.root)
		self.bottom_frame.pack(side=BOTTOM)
		self.canvas = Text(self.main_frame, wrap="none", selectbackground="yellow", selectforeground="red")
		self.canvas.grid(row=0, column=0, sticky=W+E+S+N)
		Grid.rowconfigure(self.root, 0, weight=1)
		Grid.columnconfigure(self.root, 0, weight=1)
		self.canvas.bind("<Control-s>", lambda x: self.check_save())
		self.canvas.bind("<Control-S>", lambda x: self.check_save(rename=True))

	def New_(self):
		if not self.file_saved:
			if not self.name_saved:
				respond = msgbox.askyesnocancel("Attention", f"'{self.filename_path_default}' is not saved you want to save any changes of it?")
				if respond:
					self.save_as()
					self.results = True
					return self.root.destroy()
				elif respond == False:
					self.results = True
					return self.root.destroy()
				else:
					return
			else:
				respond = msgbox.askyesnocancel("Attention", f"'{self.filename_path}' is not saved you want to save any changes of it?")
				if respond:
					self.save()
					self.results = True
					return self.root.destroy()
				elif respond == False:
					self.results = True
					return self.root.destroy()
				else:
					return
		else:
			self.results = True
			return self.root.destroy()

	def _Open(self):
		self.filename_path = fdial.askopenfilename(filetypes=[("Text", ".txt")])
		if not self.filename_path or self.filename_path == "":
			return
		with open(self.filename_path, "r") as f:
			self.change_title(self.filename_path)
			self.canvas.insert(END, f.read())
			self.name_saved = True
			self.movement_bind(self.filename_path)
			f.close()

	def menus(self):
		def active_status_bar():
			if self.status_bar_.get():
				self.window()
			else:
				self.window(disable=True)

		def active_word_wrap():
			if self.word_wrap_:
				self.canvas.config(wrap="char")
			else:
				self.canvas.config(wrap="none")

		self.main_menu = Menu(self.root)
		self.root.config(menu=self.main_menu)
		##### ----- file menu -----#########
		self.file_menu = Menu(self.main_menu, tearoff=0)
		self.File_cascade = self.main_menu.add_cascade(label="File", menu=self.file_menu)
		self.new_commands = self.file_menu.add_command(label="New    Ctrl+n", command=self.New_)
		self.open_commands = self.file_menu.add_command(label="Open    Ctrl+o", command=self._Open)
		self.file_menu.add_separator()
		self.save_command = self.file_menu.add_command(label="Save    Ctrl+s", command=self.save)
		self.save_as_command = self.file_menu.add_command(label="Save As    Ctrl+S", command=self.save_as)
		self.file_menu.add_separator()
		self.exit_command = self.file_menu.add_command(label="Exit", command=self.confirm_exit)


		self.Edit_menu = Menu(self.main_menu, tearoff=0)
		self.Edit_cascade = self.main_menu.add_cascade(label="Edit", menu=self.Edit_menu)
		self.new_commands = self.Edit_menu.add_command(label="Search a Word    Ctrl+f", command=lambda: self.search_function("find_only"))
		
		self.format_menu = Menu(self.main_menu, tearoff=0)
		self.format_cascade = self.main_menu.add_cascade(label="Format", menu=self.format_menu)
		self.word_wrap = self.format_menu.add_checkbutton(label="Word Wrap", variable=self.word_wrap_, onvalue=True, offvalue=False, command=active_word_wrap)
		
		self.View_menu = Menu(self.main_menu, tearoff=0)
		self.View_cascade = self.main_menu.add_cascade(label="View", menu=self.View_menu)
		self.status_bar_commands = self.View_menu.add_checkbutton(label="Status Bar", variable=self.status_bar_, onvalue=True, offvalue=False, command=active_status_bar)

	def status_bar(self, mode, args):
		if mode == "set":
			self.status = Label(self.main_frame, text=args, anchor=E, relief=SUNKEN, bd=1, height=1)
			self.status.grid(row=3, column=0, sticky="WE")
		else:
			if not self.status_bar_.get():
				return
			self.status.config(text=args)

	def window(self, disable=False):
		if disable:
			self.status.destroy()
			self.window_widget_init = False
			self.root.unbind("<Key>")			
			self.root.unbind("<Configure>")
			
		elif self.status_bar_.get():
			default = False
			def get_cur_row():
				CURRENT_ROW_COL = str(self.canvas.index("insert")).split(".")
				if not self.window_widget_init:
					self.window_widget_init = True
					self.status_bar("set", "Row: " + CURRENT_ROW_COL[0] + " Column: " + CURRENT_ROW_COL[-1])
				else:
					self.status_bar("conf", "Row: " + CURRENT_ROW_COL[0] + " Column: " + CURRENT_ROW_COL[-1])

			def change_conf():
				self.windows_height = self.root.winfo_height()
				self.windows_weight = self.root.winfo_width()
				if not self.window_widget_init:
					self.window_widget_init = True
					self.status_bar("set", "Height: " + str(self.windows_height) + " " + "Width: " + str(self.windows_weight))
				else:
					self.status_bar("conf", "Height: " + str(self.windows_height) + " " + "Width: " + str(self.windows_weight))
			if not default:
				default = True
				change_conf()
			self.root.bind("<Key>", lambda x: get_cur_row())
			self.root.bind("<Configure>", lambda x: change_conf())

		else:
			return

	def create_scrollbar(self):
		if self.scroll_stat:
			return
		self.xscroll = ttk.Scrollbar(self.main_frame, orient=HORIZONTAL, command=self.canvas.xview)
		self.xscroll.grid(row=1, column=0, sticky=W+E)
		self.canvas.config(xscrollcommand=self.xscroll.set)

		self.yscroll = ttk.Scrollbar(self.main_frame, orient=VERTICAL, command=self.canvas.yview)
		self.yscroll.grid(row=0, column=1, sticky=N+S)
		self.canvas.config(yscrollcommand=self.yscroll.set)

	def routine(self):
		self.create_scrollbar()
		self.canvas.bind("<Control-f>", lambda x: self.search_function("find_only"))
		self.canvas.bind("<Control-h>", lambda x: self.search_function("replace"))
		self.canvas.bind("<Control-o>", lambda x: self._Open())

	def run(self):
		self.root.protocol('WM_DELETE_WINDOW', self.confirm_exit)
		if not self.initialized:
			self.filename_path_default = "untitled "
			self.change_title(self.filename_path_default + u'\u2022')
			self.Nodes()
			self.canvas.focus()
			self.initialized = True
			self.default_option = {"fg" : self.canvas["fg"], "bg" : self.canvas["bg"]}

		self.root.rowconfigure(0, weight=1)
		self.root.columnconfigure(1, weight=1)

		self.main_frame.rowconfigure(0, weight=1)
		self.main_frame.columnconfigure(0, weight=1)

		self.menus()
		self.routine()

		self.root.mainloop()

		if self.results:
			return "rebuild"
		else:
			return 

def main():
	res = UI().run()
	while res == "rebuild":
		res = UI().run()

main()
