"""tables module.

Contains:
class ModalWindow for creating modal windows in Table class
class Table for entering tables
def start(table=None) for making new Table window
"""
import tkinter as tk


class ModalWindow(tk.Toplevel):
    def __init__(self, master, function, labeltext, buttontext):
        self.master = master
        super().__init__(master)
        self.grid()
        self.label = tk.Label(self, text=labeltext)
        self.label.grid(row=0, column=0)
        self.entry = tk.Entry(self)
        self.entry.grid(row=0, column=1)
        self.button = tk.Button(self, text=buttontext, command=lambda: function(self.entry.get()))
        self.button.grid(row=0, column=2)


class Table(tk.Frame):
    def __init__(self, **kwargs):
        master = kwargs['master'] if "master" in kwargs else None
        super().__init__(master)
        self.master = master
        self.grid()
        self.table = []
        self.rowlabels = []
        self.collabels = []
        self.colnum = 5
        self.rownum = 3
        self.add_col_button = self.add_row_button = None
        self.del_col_button = self.del_row_button = None
        self.save_button = self.load_button = None
        self.create_widgets()
        # self.focus_x = self.focus_y = 0
        if "table" in kwargs:
            self.load_table(kwargs["table"])

    def change_size(self, xsize, ysize):
        while ysize < self.rownum:
            self.del_row(self.rownum - 1)
        while ysize > self.rownum:
            self.add_row(self.rownum)
        while xsize < self.colnum:
            self.del_col(self.colnum - 1)
        while xsize > self.colnum:
            self.add_col(self.colnum)

    def change_focus(self, tup_s, tup):
        row, entry = tup_s
        focus_x = row.index(entry)
        focus_y = self.table.index(row)
        focus_x = max(min(focus_x + tup[0], self.colnum - 1), 0)
        focus_y = max(min(focus_y + tup[1], self.rownum - 1), 0)
        # print(focus_y, focus_x, tup)
        self.table[focus_y][focus_x].focus_set()

    def save(self, filename):
        with open(filename, 'w') as file:
            file.write('\n'.join(['\t'.join([element.get() for element in row]) for row in self.table]))

    def load_table(self, new_table):
        new_rownum = len(new_table)
        new_colnum = len(new_table[0]) if new_rownum != 0 else 0
        self.change_size(new_colnum, new_rownum)
        for y in range(self.rownum):
            for x in range(self.colnum):
                self.table[y][x].delete(0, tk.END)
                self.table[y][x].insert(0, new_table[y][x])

    def load(self, filename):
        try:
            with open(filename, 'r') as file:
                new_table = [s.replace('\n', '').split('\t') for s in file]
                self.load_table(new_table)

        except Exception:
            pass

    def add_col(self, number):
        if number > self.colnum or number < 0:
            return
        self.remove_everything()
        for y in range(self.rownum):
            entry = tk.Entry(self)
            row = self.table[y]
            self.entry_bind(row, entry)
            row.insert(number, entry)
        self.collabels.append(tk.Label(self, text='{}'.format(self.colnum)))
        self.colnum += 1
        self.grid_everything()

    def del_col(self, number):
        if number >= self.colnum or number < 0:
            return
        self.remove_everything()
        for y in range(self.rownum):
            self.table[y].pop(number)
        self.colnum -= 1
        self.collabels[-1].destroy()
        self.collabels.pop()
        self.grid_everything()

    def add_row(self, number):
        if number > self.rownum or number < 0:
            return
        self.remove_everything()
        new_row = []
        for x in range(self.colnum):
            entry = tk.Entry(self)
            self.entry_bind(new_row, entry)
            new_row.append(entry)
        self.table.insert(number, new_row)
        self.rowlabels.append(tk.Label(self, text='{}'.format(self.rownum)))
        self.rownum += 1
        self.grid_everything()

    def del_row(self, number):
        if number >= self.rownum or number < 0:
            return
        self.remove_everything()
        self.table.pop(number)
        self.rownum -= 1
        self.rowlabels[-1].destroy()
        self.rowlabels.pop()
        self.grid_everything()

    def make_modal(self, func, label_text, button_text):
        modal = ModalWindow(self, func, label_text, button_text)
        modal.transient(self.master)
        modal.grab_set()
        modal.focus_set()
        modal.wait_window()

    def remove_everything(self):
        for row in self.table:
            for el in row:
                el.grid_remove()
        self.add_col_button.grid_remove()
        self.add_row_button.grid_remove()
        self.del_col_button.grid_remove()
        self.del_row_button.grid_remove()
        self.save_button.grid_remove()
        self.load_button.grid_remove()

    def grid_everything(self):
        for y in range(len(self.table)):
            self.rowlabels[y].grid(row=y + 1, column=0)
            if y == 0:
                for x in range(len(self.table[0])):
                    self.collabels[x].grid(row=0, column=x + 1)

            for x in range(len(self.table[y])):
                self.table[y][x].grid(row=y + 1, column=x + 1)
        self.add_col_button.grid(row=len(self.table) + 1, column=1)
        self.add_row_button.grid(row=len(self.table) + 1, column=2)
        self.del_col_button.grid(row=len(self.table) + 2, column=1)
        self.del_row_button.grid(row=len(self.table) + 2, column=2)
        self.save_button.grid(row=len(self.table) + 1, column=3)
        self.load_button.grid(row=len(self.table) + 2, column=3)

    def entry_bind(self, row, entry):
        entry.bind(
            "<Control-Down>",
            (lambda rw, en: lambda event: self.change_focus((rw, en), (0, 1)))(row, entry))
        entry.bind(
            "<Control-Up>",
            (lambda rw, en: lambda event: self.change_focus((rw, en), (0, -1)))(row, entry))
        entry.bind(
            "<Control-Left>",
            (lambda rw, en: lambda event: self.change_focus((rw, en), (-1, 0)))(row, entry))
        entry.bind(
            "<Control-Right>",
            (lambda rw, en: lambda event: self.change_focus((rw, en), (1, 0)))(row, entry))

    def create_widgets(self):
        self.table = []
        for x in range(self.colnum):
            self.collabels.append(tk.Label(self, text='{}'.format(x)))

        for y in range(self.rownum):
            self.rowlabels.append(tk.Label(self, text='{}'.format(y)))

        for y in range(self.rownum):
            row = []
            for x in range(self.colnum):
                entry = tk.Entry(self)
                self.entry_bind(row, entry)
                row.append(entry)
            self.table.append(row)
        self.add_col_button = tk.Button(self, text="add column",
                                        command=lambda: self.make_modal(lambda s: self.add_col(int(s)),
                                                                        "number", "add"))
        self.add_row_button = tk.Button(self, text="add row",
                                        command=lambda: self.make_modal(lambda s: self.add_row(int(s)),
                                                                        "number", "add"))
        self.del_col_button = tk.Button(self, text="del column",
                                        command=lambda: self.make_modal(lambda s: self.del_col(int(s)),
                                                                        "number", "delete"))
        self.del_row_button = tk.Button(self, text="del row",
                                        command=lambda: self.make_modal(lambda s: self.del_row(int(s)),
                                                                        "number", "delete"))
        self.save_button = tk.Button(self, text="save",
                                     command=lambda: self.make_modal(lambda s: self.save(s),
                                                                     "name", "save"))
        self.load_button = tk.Button(self, text="load",
                                     command=lambda: self.make_modal(lambda s: self.load(s),
                                                                     "name", "load"))
        self.grid_everything()


def start(table=None):
    root = tk.Tk()
    if table is not None:
        app = Table(master=root, table=table)
    else:
        app = Table(master=root)
    app.mainloop()


if __name__ == "__main__":
    start()
