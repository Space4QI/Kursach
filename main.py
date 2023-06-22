import tkinter as tk
import psycopg2
from psycopg2 import OperationalError
from tkinter import ttk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.datatr = []
        self.title("PostgreSQL GUI")
        self.geometry("600x400")

        self.create_connection("myDB", "postgres", "itsme", "127.0.0.1", "5432")

        self.left_frame = tk.Frame(self)
        self.right_frame = tk.Frame(self)
        self.entity_selection_button = tk.Button(self.left_frame, text="Entity Selection", command=self.show_entity_list)
        self.add_button = tk.Button(self.left_frame, text="Add", command=self.show_add_window, state=tk.DISABLED)
        self.edit_button = tk.Button(self.left_frame, text="Edit", command=self.show_edit_window, state=tk.DISABLED)
        self.delete_button = tk.Button(self.left_frame, text="Delete", command=self.delete_record, state=tk.DISABLED)
        self.ext_srch1 = tk.Button(self.left_frame, text="SearchQ1", command=self.show_srch1_window, state=tk.DISABLED)
        self.ext_srch2 = tk.Button(self.left_frame, text="SearchQ2", command=self.show_srch2_window, state=tk.DISABLED)
        self.ext_srch3 = tk.Button(self.left_frame, text="SearchQ3", command=self.show_srch3_window, state=tk.DISABLED)
        self.ext_srch4 = tk.Button(self.left_frame, text="SearchQ4", command=self.show_srch4_window, state=tk.DISABLED)
        self.ext_srch5 = tk.Button(self.left_frame, text="SearchQ5", command=self.show_srch5_window, state=tk.DISABLED)

        self.entity_list = None
        self.selected_entity = None
        self.entity_details = ttk.Treeview(self.right_frame)
        self.create_widgets()
        self.id_type = ""

    def create_widgets(self):
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.edit_button.size = self.left_frame.size()[1]
        self.entity_selection_button.pack(side=tk.TOP)
        self.add_button.pack(side=tk.TOP)
        self.delete_button.pack(side=tk.TOP)
        self.edit_button.pack(side=tk.TOP)
        self.ext_srch1.pack(side=tk.TOP)
        self.ext_srch2.pack(side=tk.TOP)
        self.ext_srch3.pack(side=tk.TOP)
        self.ext_srch4.pack(side=tk.TOP)
        self.ext_srch5.pack(side=tk.TOP)
        self.entity_details.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


    def create_connection(self, db_name, db_user, db_password, db_host, db_port):
        try:
            self.connection = psycopg2.connect(
                database=db_name,
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port,
            )
            print("Connection to PostgreSQL DB successful")
        except OperationalError as e:
            print(f"The error '{e}' occurred")

    def show_entity_list(self):
        if self.entity_list is None:
            self.entity_list = tk.Listbox(self.left_frame, width=30)
            self.entity_list.bind("<<ListboxSelect>>", self.update_selected_entity)

            scrollbar = tk.Scrollbar(self.left_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.entity_list.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=self.entity_list.yview)

            self.select_data()

        self.entity_list.pack(side=tk.TOP, fill=tk.Y)

        self.add_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)
        self.edit_button.config(state=tk.DISABLED)
        self.ext_srch1.config(state=tk.DISABLED)
        self.ext_srch2.config(state=tk.DISABLED)
        self.ext_srch3.config(state=tk.DISABLED)
        self.ext_srch4.config(state=tk.DISABLED)
        self.ext_srch5.config(state=tk.DISABLED)


    def select_data(self):
        if not self.connection:
            print("No connection to the database")
            return

        select_tables_query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name NOT IN ('Зарегистрировано', 'Нахождение', 'Принадлежит')
        """

        try:
            cursor = self.connection.cursor()
            cursor.execute(select_tables_query)
            tables = cursor.fetchall()

            self.entity_list.delete(0, tk.END)
            for table in tables:
                self.entity_list.insert(tk.END, table[0])
        except psycopg2.Error as e:
            print(f"The error '{e}' occurred")

    def update_selected_entity(self, event):
        selected_indices = self.entity_list.curselection()

        if selected_indices:
            self.selected_entity = self.entity_list.get(selected_indices[0])

            if self.selected_entity:
                self.add_button.config(state=tk.NORMAL)
                self.delete_button.config(state=tk.NORMAL)
                self.edit_button.config(state=tk.NORMAL)
                self.ext_srch1.config(state=tk.NORMAL)
                self.ext_srch2.config(state=tk.NORMAL)
                self.ext_srch3.config(state=tk.NORMAL)
                self.ext_srch4.config(state=tk.NORMAL)
                self.ext_srch5.config(state=tk.NORMAL)

                self.show_entity_details()

    def show_entity_details(self):
        if not self.selected_entity or not self.connection:
            return

        select_data_query = f"SELECT * FROM {self.selected_entity}"

        try:
            cursor = self.connection.cursor()
            cursor.execute(select_data_query)
            rows = cursor.fetchall()

            self.entity_details.delete(*self.entity_details.get_children())

            columns = [desc[0] for desc in cursor.description]
            self.entity_details["columns"] = columns

            for col in columns:
                max_width_rw = max([len(str(row)) for row in rows])
                max_width_cl = max([len(str(col)) for col in columns])
                max_width = max(max_width_cl, max_width_rw) * 2
                self.geometry(f"{max_width * (len(columns) + 1)}x600")
                self.entity_details.column(col, width=max_width)
                self.entity_details.heading(col, text=col, anchor=tk.W)
                self.entity_details.configure(show="headings", selectmode="browse")
                self.entity_details.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

            for row in rows:
                self.entity_details.insert(parent="", index=tk.END, values=row)

            self.entity_details.update_idletasks()  # перерисовываем таблицу
        except psycopg2.Error as e:
            print(f"The error '{e}' occurred")

    def show_add_window(self):
        if not self.selected_entity or not self.connection:
            return

        add_window = tk.Toplevel(self)
        add_window.title("Add Record")
        add_window.geometry("400x200")

        add_label = tk.Label(add_window, text=f"Add Record to {self.selected_entity}")
        add_label.pack()

        columns = self.get_table_columns(self.selected_entity)
        entry_boxes = []

        for col in columns:
            label = tk.Label(add_window, text=col)
            label.pack()

            entry = tk.Entry(add_window, width=30)
            entry.pack()

            entry_boxes.append(entry)

        add_button = tk.Button(add_window, text="Add", command=lambda: self.add_record(entry_boxes, columns))
        add_button.pack()

        self.wait_window(add_window)

    def show_edit_window(self):
        if not self.selected_entity or not self.connection:
            return

        selected_item = self.entity_details.focus()
        if not selected_item:
            return

        edit_window = tk.Toplevel(self)
        edit_window.title("Edit Record")
        edit_window.geometry("400x200")

        edit_label = tk.Label(edit_window, text=f"Edit record in {self.selected_entity}")
        edit_label.pack()

        record_id = self.entity_details.item(selected_item)["values"]
        columns = self.entity_details["columns"]
        entry_boxes = []
        ix = 0
        for col in columns:
            label = tk.Label(edit_window, text=col)
            label.pack()

            entry = tk.Entry(edit_window, width=30)
            entry.insert(0, record_id[ix])
            entry.pack()

            entry_boxes.append(entry)
            ix += 1

        edit_button = tk.Button(edit_window, text="Edit", command=lambda: self.edit_record(entry_boxes, columns))
        edit_button.pack()

        self.wait_window(edit_window)

    def show_srch1_window(self):
        if not self.selected_entity or not self.connection:
            return

        srch1_window = tk.Toplevel(self)
        srch1_window.title("Advanced Search I")
        srch1_window.geometry("500x200")
        objective = tk.Label(srch1_window,
                             text="Найти все сообщения, написанные пользователями с табельным номером роли\n"
                                  "в голосовых каналах, созданных после указанной даты:")
        objective.pack()

        columns = ['Тип Канала', 'Дата создания', 'Номер роли']
        entry_boxes = []
        ix = 0
        for col in columns:
            label = tk.Label(srch1_window, text=col)
            label.pack()

            entry = tk.Entry(srch1_window, width=30)
            entry.pack()

            entry_boxes.append(entry)
            ix += 1

        advI = tk.Button(srch1_window, text="Search", command=lambda: self.ext_srch1q(entry_boxes))
        advI.pack()

    def show_srch2_window(self):
        if not self.selected_entity or not self.connection:
            return

        srch2_window = tk.Toplevel(self)
        srch2_window.title("Advanced Search II")
        srch2_window.geometry("550x200")
        objective = tk.Label(srch2_window, text="Найти все каналы, в которых участвует пользователь с почтой, заканчивающейся на ...\n" "и есть хотя бы одно сообщение с текстом, содержащим слово ...:")
        objective.pack()
        columns = ['Конец email', 'Текст']
        entry_boxes = []
        ix = 0
        for col in columns:
            label = tk.Label(srch2_window, text=col)
            label.pack()

            entry = tk.Entry(srch2_window, width=30)
            entry.pack()

            entry_boxes.append(entry)
            ix += 1

        advII = tk.Button(srch2_window, text="Search", command=lambda: self.ext_srch2q(entry_boxes))
        advII.pack()

    def show_srch3_window(self):
        if not self.selected_entity or not self.connection:
            return

        srch3_window = tk.Toplevel(self)
        srch3_window.title("Advanced Search III")
        srch3_window.geometry("400x200")
        objective = tk.Label(srch3_window, text="Найти всех пользователей с ролью:")
        objective.pack()
        columns = ['Роль']
        entry_boxes = []
        ix = 0
        for col in columns:
            label = tk.Label(srch3_window, text=col)
            label.pack()

            entry = tk.Entry(srch3_window, width=30)
            entry.pack()

            entry_boxes.append(entry)
            ix += 1

        advIII = tk.Button(srch3_window, text="Search", command=lambda: self.ext_srch3q(entry_boxes))
        advIII.pack()

    def show_srch4_window(self):
        if not self.selected_entity or not self.connection:
            return

        srch4_window = tk.Toplevel(self)
        srch4_window.title("Advanced Search IV")
        srch4_window.geometry("400x200")
        objective = tk.Label(srch4_window, text="Найти все каналы, в которых участвует пользователь с ID")
        objective.pack()
        columns = ['ID пользователя']
        entry_boxes = []
        ix = 0
        for col in columns:
            label = tk.Label(srch4_window, text=col)
            label.pack()

            entry = tk.Entry(srch4_window, width=30)
            entry.pack()

            entry_boxes.append(entry)
            ix += 1

        advIV = tk.Button(srch4_window, text="Search", command=lambda: self.ext_srch4q(entry_boxes))
        advIV.pack()

    def show_srch5_window(self):
        if not self.selected_entity or not self.connection:
            return

        srch5_window = tk.Toplevel(self)
        srch5_window.title("Advanced Search IV")
        srch5_window.geometry("400x200")
        objective = tk.Label(srch5_window, text="Найти все сервера, созданные после указанной даты:")
        objective.pack()
        columns = ['Дата']
        entry_boxes = []
        ix = 0
        for col in columns:
            label = tk.Label(srch5_window, text=col)
            label.pack()

            entry = tk.Entry(srch5_window, width=30)
            entry.pack()

            entry_boxes.append(entry)
            ix += 1

        advV = tk.Button(srch5_window, text="Search", command=lambda: self.ext_srch5q(entry_boxes))
        advV.pack()

    def get_table_columns(self, table_name):#возврат столбцов сущностей
        if not self.connection:
            print("No connection to the database")
            return []

        select_columns_query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'"

        try:
            cursor = self.connection.cursor()
            cursor.execute(select_columns_query)
            columns = [col[0] for col in cursor.fetchall()]
            return columns
        except psycopg2.Error as e:
            print(f"The error '{e}' occurred")

        return []

    def add_record(self, entry_boxes, columns): #добавление записи
        if not self.selected_entity or not self.connection:
            return

        values = []
        for entry in entry_boxes:
            value = entry.get()
            if value.lower() == "true":
                values.append(True)
            elif value.lower() == "false":
                values.append(False)
            elif value.isdigit():
                values.append(int(value))
            else:
                values.append(value)

        if len(values) != len(columns):
            print("Number of values does not match number of columns")
            return

        insert_query = f"INSERT INTO {self.selected_entity} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(values))})"

        try:
            cursor = self.connection.cursor()
            cursor.execute(insert_query, values)
            self.connection.commit()
            print("Record added successfully")
            self.show_entity_details()
        except psycopg2.Error as e:
            self.connection.rollback()
            print(f"The error '{e}' occurred")

    def edit_record(self, entry_boxes, columns): #редактирование записи
        if not self.selected_entity or not self.connection:
            return

        selected_item = self.entity_details.focus()

        values = []
        for entry in entry_boxes:
            value = entry.get()
            if value.lower() == "true":
                values.append(True)
            elif value.lower() == "false":
                values.append(False)
            elif value.isdigit():
                values.append(int(value))
            else:
                values.append(value)

        if len(values) != len(columns):
            print("Number of values does not match number of columns")
            return

        selected_item = self.entity_details.focus()
        record_id = self.entity_details.item(selected_item)["values"][0]  # Assuming the first column is the id
        type = self.entity_details["columns"][0]
        update_query = f"UPDATE {self.selected_entity} SET {', '.join([f'{column} = %s' for column in columns])} WHERE {type} = %s"
        values.append(record_id)

        try:
            cursor = self.connection.cursor()
            cursor.execute(update_query, values)
            self.connection.commit()
            print("Record updated successfully")
            self.show_entity_details()
        except psycopg2.Error as e:
            self.connection.rollback()
            print(f"The error '{e}' occurred")

    def delete_record(self): #удаление записи
        if not self.selected_entity or not self.connection:
            return

        selected_item = self.entity_details.focus()
        if not selected_item:
            return

        record_id = self.entity_details.item(selected_item)["values"][0]  # Assuming the first column is the id
        type = self.entity_details["columns"][0]

        delete_query = f"DELETE FROM {self.selected_entity} WHERE {type} = {record_id}"

        try:
            cursor = self.connection.cursor()
            cursor.execute(delete_query)
            self.connection.commit()
            print("Record deleted successfully")
            self.show_entity_details()
        except psycopg2.Error as e:
            self.connection.rollback()
            print(f"The error '{e}' occurred")

    def ext_srch1q(self, datapack):
        values = []
        for entry in datapack:
            value = entry.get()
            if value.lower() == "true":
                values.append(True)
            elif value.lower() == "false":
                values.append(False)
            elif value.isdigit():
                values.append(int(value))
            else:
                values.append(value)
        try:
            find_query = f"""
            SELECT message.Текст
            FROM message
            JOIN user_data ON message.id_user_data = user_data.id_user_data
            JOIN channel ON message.id_channel = channel.id_channel
            WHERE channel.Тип_канала = '{values[0]}'
              AND DATE(channel.Дата_создания) > '{values[1]}'
              AND EXISTS (
                SELECT *
                FROM message AS sub_message
                JOIN user_data AS sub_user_data ON sub_message.id_user_data = sub_user_data.id_user_data
                JOIN channel AS sub_channel ON sub_message.id_channel = sub_channel.id_channel
                WHERE sub_channel.Тип_канала = '{values[0]}'
                  AND DATE(sub_channel.Дата_создания) > '{values[1]}'
                  AND sub_user_data.id_role = '{values[2]}'
                  AND sub_message.Текст IS NOT NULL
                  AND sub_message.id_user_data = message.id_user_data
                  AND sub_message.id_channel = message.id_channel
  )
                  """

            cursor = self.connection.cursor()
            cursor.execute(find_query)
            self.connection.commit()
            data = [ix[0] for ix in cursor.fetchall()]
            print(data)
            self.show_entity_details()
            res_window = tk.Toplevel(self)
            res_window.title("Result")
            res_window.geometry("400x200")
            for ix in data:
                labelix = tk.Label(res_window, text=ix)
                labelix.pack()
        except psycopg2.Error as e:
            self.connection.rollback()
            print(f"The error '{e}' occurred")

    def ext_srch2q(self, datapack):
        values = []
        for entry in datapack:
            value = entry.get()
            if value.lower() == "true":
                values.append(True)
            elif value.lower() == "false":
                values.append(False)
            elif value.isdigit():
                values.append(int(value))
            else:
                values.append(value)
        try:
            find_query = f"""
              SELECT channel.Название
                FROM channel
                JOIN Нахождение ON channel.id_channel = Нахождение.id_channel
                JOIN user_data ON Нахождение.id_user_data = user_data.id_user_data
                JOIN message ON channel.id_channel = message.id_channel
                WHERE user_data.Почта LIKE '%{values[0]}'
                  AND message.Текст LIKE '%{values[1]}%'
                  AND message.Текст IS NOT NULL
                ORDER BY channel.Название ASC;
                    """

            cursor = self.connection.cursor()
            cursor.execute(find_query)
            self.connection.commit()
            data = [ix[0] for ix in cursor.fetchall()]
            print(data)
            self.show_entity_details()
            res_window = tk.Toplevel(self)
            res_window.title("Result")
            res_window.geometry("400x200")
            for ix in data:
                labelix = tk.Label(res_window, text=ix)
                labelix.pack()

        except psycopg2.Error as e:
            self.connection.rollback()
            print(f"The error '{e}' occurred")

    def ext_srch3q(self, datapack):
        values = []
        for entry in datapack:
            value = entry.get()
            if value.lower() == "true":
                values.append(True)
            elif value.lower() == "false":
                values.append(False)
            elif value.isdigit():
                values.append(int(value))
            else:
                values.append(value)
        try:
            find_query = f"""
            SELECT COUNT(*) FROM user_data
            WHERE id_user_data IN (
              select id_user_data from role
                WHERE Название = '{values[0]}'
                );
                  """

            cursor = self.connection.cursor()
            cursor.execute(find_query)
            self.connection.commit()
            data = [ix[0] for ix in cursor.fetchall()]
            print(data)
            self.show_entity_details()
            res_window = tk.Toplevel(self)
            res_window.title("Result")
            res_window.geometry("400x200")
            for ix in data:
                labelix = tk.Label(res_window, text=ix)
                labelix.pack()
        except psycopg2.Error as e:
            self.connection.rollback()
            print(f"The error '{e}' occurred")

    def ext_srch4q(self, datapack):
        values = []
        for entry in datapack:
            value = entry.get()
            if value.lower() == "true":
                values.append(True)
            elif value.lower() == "false":
                values.append(False)
            elif value.isdigit():
                values.append(int(value))
            else:
                values.append(value)
        try:
            find_query = f"""
            SELECT channel.Название
                FROM Channel
                JOIN user_data ON Channel.id_user_data = user_data.id_user_data
                    WHERE user_data.id_user_data = {values[0]};

                  """
            print("f4")
            cursor = self.connection.cursor()
            cursor.execute(find_query)
            self.connection.commit()
            data = [ix[0] for ix in cursor.fetchall()]
            print(data)
            self.show_entity_details()
            res_window = tk.Toplevel(self)
            res_window.title("Result")
            res_window.geometry("400x200")
            for ix in data:
                labelix = tk.Label(res_window, text=ix)
                labelix.pack()
        except psycopg2.Error as e:
            self.connection.rollback()
            print(f"The error '{e}' occurred")

    def ext_srch5q(self, datapack):
        values = []
        for entry in datapack:
            value = entry.get()
            if value.lower() == "true":
                values.append(True)
            elif value.lower() == "false":
                values.append(False)
            elif value.isdigit():
                values.append(int(value))
            else:
                values.append(value)
        try:
            find_query = f"""
            SELECT * FROM server_data
                WHERE Дата_создания > '{values[0]}'
                  """
            cursor = self.connection.cursor()
            cursor.execute(find_query)
            self.connection.commit()
            data = [ix[0] for ix in cursor.fetchall()]
            print(data)
            self.show_entity_details()
            res_window = tk.Toplevel(self)
            res_window.title("Result")
            res_window.geometry("400x200")
            for ix in data:
                labelix = tk.Label(res_window, text=ix)
                labelix.pack()
        except psycopg2.Error as e:
            self.connection.rollback()
            print(f"The error '{e}' occurred")
app = App()
app.mainloop()
