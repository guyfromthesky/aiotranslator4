import tkinter as tk
import tkinter.scrolledtext as tkscrolled

# Create the root window
root = tk.Tk()

# Create the ScrolledText widget
text_widget = tkscrolled.ScrolledText(root, wrap=tk.WORD, width=50, height=10)

# Insert some HTML into the widget
text_widget.insert(tk.END, "<b>Bold</b> <i>Italic</i> <u>Underline</u>")

# Pack the widget and display the window
text_widget.pack()
root.mainloop()
