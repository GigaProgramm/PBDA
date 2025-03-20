import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox, Toplevel
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
from scipy.stats import gmean, hmean
import statistics
import seaborn as sns  # Import seaborn

plt.style.use('seaborn-v0_8')  # Set default plot style

class DataAnalyzerApp:
    def __init__(self, master):
        self.master = master
        master.title("Data Analysis")  # Default title in English

        self.df = None
        self.selected_column = None
        self.scatter_visible = tk.BooleanVar(value=True)
        self.boxplot_visible = tk.BooleanVar(value=True)
        self.scatter_color = "blue"
        self.boxplot_color = "green"
        self.current_language = "en"  # Default language is English

        # Translations dictionary
        self.translations = {
            "en": {
                "title": "Data Analysis",
                "load_data": "Load CSV",
                "select_column": "Select Column:",
                "scatter_plot": "Scatter Plot",
                "box_plot": "Box Plot",
                "scatter_color": "Scatter Color",
                "box_color": "Box Color",
                "save_scatter": "Save Scatter Plot",
                "save_box": "Save Box Plot",
                "open_scatter": "Open Scatter Plot in New Window",
                "open_box": "Open Box Plot in New Window",
                "mean": "Mean:",
                "variance": "Variance:",
                "range": "Range:",
                "max": "Max:",
                "min": "Min:",
                "geometric_mean": "Geometric Mean:",
                "harmonic_mean": "Harmonic Mean:",
                "quadratic_mean": "Quadratic Mean:",
                "median": "Median:",
                "std_dev": "Standard Deviation:",
                "mode": "Mode:",
                "info": "Information",
                "load_data_first": "Load data and select a column first.",
                "language": "Language",
                "english": "English",
                "russian": "Russian"
            },
            "ru": {
                "title": "Анализ Данных",
                "load_data": "Загрузить CSV",
                "select_column": "Выберите столбец:",
                "scatter_plot": "График расхождений",
                "box_plot": "Ящик с усами",
                "scatter_color": "Цвет графика",
                "box_color": "Цвет ящика с усами",
                "save_scatter": "Сохранить график расхождений",
                "save_box": "Сохранить ящик с усами",
                "open_scatter": "Открыть график расхождений в новом окне",
                "open_box": "Открыть ящик с усами в новом окне",
                "mean": "Среднее арифметическое:",
                "variance": "Дисперсия:",
                "range": "Размах:",
                "max": "Макс. значение:",
                "min": "Мин. значение:",
                "geometric_mean": "Среднее геометрическое:",
                "harmonic_mean": "Среднее гармоническое:",
                "quadratic_mean": "Среднее квадратическое:",
                "median": "Медиана:",
                "std_dev": "Стандартное отклонение:",
                "mode": "Мода:",
                "info": "Информация",
                "load_data_first": "Сначала загрузите данные и выберите столбец.",
                "language": "Язык",
                "english": "Английский",
                "russian": "Русский"
            }
        }

        # Frame для элементов управления и статистики
        self.control_frame = tk.Frame(master)
        self.control_frame.pack(side=tk.RIGHT, padx=10)

        # Frame для графиков
        self.plot_frame = tk.Frame(master)
        self.plot_frame.pack(side=tk.LEFT, padx=10)

        # Language selection menu
        self.language_label = tk.Label(self.control_frame, text=self.translations[self.current_language]["language"])
        self.language_label.pack()
        self.language_var = tk.StringVar(master)
        self.language_var.set(self.translations[self.current_language]["english"])  # Default language
        self.language_dropdown = tk.OptionMenu(self.control_frame, self.language_var, 
                                                self.translations[self.current_language]["english"], 
                                                self.translations[self.current_language]["russian"], 
                                                command=self.change_language)
        self.language_dropdown.pack()

        # Кнопка для загрузки данных
        self.load_data_button = tk.Button(self.control_frame, text=self.translations[self.current_language]["load_data"], command=self.load_data)
        self.load_data_button.pack()

        # Выпадающий список для выбора столбца
        self.column_label = tk.Label(self.control_frame, text=self.translations[self.current_language]["select_column"])
        self.column_label.pack()
        self.column_var = tk.StringVar(master)
        self.column_dropdown = tk.OptionMenu(self.control_frame, self.column_var, "")
        self.column_dropdown.pack()
        self.column_var.trace("w", self.update_plots_and_stats)

        # Чекбоксы для включения/выключения графиков
        self.scatter_check = tk.Checkbutton(self.control_frame, text=self.translations[self.current_language]["scatter_plot"], variable=self.scatter_visible, command=self.update_plots_and_stats)
        self.scatter_check.pack()
        self.boxplot_check = tk.Checkbutton(self.control_frame, text=self.translations[self.current_language]["box_plot"], variable=self.boxplot_visible, command=self.update_plots_and_stats)
        self.boxplot_check.pack()

        # Кнопки для выбора цвета
        self.scatter_color_button = tk.Button(self.control_frame, text=self.translations[self.current_language]["scatter_color"], command=self.choose_scatter_color)
        self.scatter_color_button.pack()
        self.boxplot_color_button = tk.Button(self.control_frame, text=self.translations[self.current_language]["box_color"], command=self.choose_boxplot_color)
        self.boxplot_color_button.pack()

        # Кнопки для сохранения графиков
        self.save_scatter_button = tk.Button(self.control_frame, text=self.translations[self.current_language]["save_scatter"], command=self.save_scatter_plot)
        self.save_scatter_button.pack()
        self.save_boxplot_button = tk.Button(self.control_frame, text=self.translations[self.current_language]["save_box"], command=self.save_boxplot)
        self.save_boxplot_button.pack()

        # Кнопки для открытия графиков в новом окне
        self.open_scatter_button = tk.Button(self.control_frame, text=self.translations[self.current_language]["open_scatter"], command=self.open_scatter_plot)
        self.open_scatter_button.pack()
        self.open_boxplot_button = tk.Button(self.control_frame, text=self.translations[self.current_language]["open_box"], command=self.open_boxplot)
        self.open_boxplot_button.pack()

        # Область для графиков (уменьшенные размеры)
        self.fig, (self.ax_scatter, self.ax_boxplot) = plt.subplots(2, 1, figsize=(4, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack()

        # Текстовые поля для отображения статистики
        self.mean_label = tk.Label(self.control_frame, text=self.translations[self.current_language]["mean"])
        self.mean_label.pack()
        self.mean_text = tk.Text(self.control_frame, height=1, width=30)
        self.mean_text.pack()

        self.variance_label = tk.Label(self.control_frame, text=self.translations[self.current_language]["variance"])
        self.variance_label.pack()
        self.variance_text = tk.Text(self.control_frame, height=1, width=30)
        self.variance_text.pack()

        self.range_label = tk.Label(self.control_frame, text=self.translations[self.current_language]["range"])
        self.range_label.pack()
        self.range_text = tk.Text(self.control_frame, height=1, width=30)
        self.range_text.pack()

        self.max_label = tk.Label(self.control_frame, text=self.translations[self.current_language]["max"])
        self.max_label.pack()
        self.max_text = tk.Text(self.control_frame, height=1, width=30)
        self.max_text.pack()

        self.min_label = tk.Label(self.control_frame, text=self.translations[self.current_language]["min"])
        self.min_label.pack()
        self.min_text = tk.Text(self.control_frame, height=1, width=30)
        self.min_text.pack()

        self.geometric_mean_label = tk.Label(self.control_frame, text=self.translations[self.current_language]["geometric_mean"])
        self.geometric_mean_label.pack()
        self.geometric_mean_text = tk.Text(self.control_frame, height=1, width=30)
        self.geometric_mean_text.pack()

        self.harmonic_mean_label = tk.Label(self.control_frame, text=self.translations[self.current_language]["harmonic_mean"])
        self.harmonic_mean_label.pack()
        self.harmonic_mean_text = tk.Text(self.control_frame, height=1, width=30)
        self.harmonic_mean_text.pack()
        
        self.quadratic_mean_label = tk.Label(self.control_frame, text=self.translations[self.current_language]["quadratic_mean"])
        self.quadratic_mean_label.pack()
        self.quadratic_mean_text = tk.Text(self.control_frame, height=1, width=30)
        self.quadratic_mean_text.pack()

        self.median_label = tk.Label(self.control_frame, text=self.translations[self.current_language]["median"])
        self.median_label.pack()
        self.median_text = tk.Text(self.control_frame, height=1, width=30)
        self.median_text.pack()

        self.std_dev_label = tk.Label(self.control_frame, text=self.translations[self.current_language]["std_dev"])
        self.std_dev_label.pack()
        self.std_dev_text = tk.Text(self.control_frame, height=1, width=30)
        self.std_dev_text.pack()

        self.mode_label = tk.Label(self.control_frame, text=self.translations[self.current_language]["mode"])
        self.mode_label.pack()
        self.mode_text = tk.Text(self.control_frame, height=1, width=30)
        self.mode_text.pack()

    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                self.df = pd.read_csv(file_path)
                columns = list(self.df.columns)
                self.column_var.set(columns[0])  # set the default value
                self.column_dropdown['menu'].delete(0, 'end')
                for column in columns:
                    self.column_dropdown['menu'].add_command(label=column, command=tk._setit(self.column_var, column))
                self.update_plots_and_stats()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def choose_scatter_color(self):
        color_code = colorchooser.askcolor(title=self.translations[self.current_language]["scatter_color"])
        if color_code:
            self.scatter_color = color_code[1]
            self.update_plots_and_stats()

    def choose_boxplot_color(self):
        color_code = colorchooser.askcolor(title=self.translations[self.current_language]["box_color"])
        if color_code:
            self.boxplot_color = color_code[1]
            self.update_plots_and_stats()

    def save_scatter_plot(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            self.fig.savefig(file_path)

    def save_boxplot(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            self.fig.savefig(file_path)

    def open_scatter_plot(self):
        if self.df is None or self.selected_column is None:
            messagebox.showinfo(self.translations[self.current_language]["info"], self.translations[self.current_language]["load_data_first"])
            return

        data = self.df[self.selected_column].dropna()

        # Создаем новое окно
        new_window = Toplevel(self.master)
        new_window.title(self.translations[self.current_language]["scatter_plot"])

        # Создаем новую фигуру и оси
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.scatterplot(x=data.index, y=data.values, color=self.scatter_color, ax=ax)  # Use seaborn
        ax.set_title(f"{self.translations[self.current_language]['scatter_plot']} ({self.selected_column})")
        ax.set_xlabel("Index")
        ax.set_ylabel("Value")

        # Создаем canvas для отображения графика в окне
        canvas = FigureCanvasTkAgg(fig, master=new_window)
        canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Добавляем панель инструментов навигации
        toolbar = NavigationToolbar2Tk(canvas, new_window)
        toolbar.update()
        toolbar.pack(side=tk.LEFT, fill=tk.Y)

        canvas.draw()

        # Добавляем возможность перетаскивания графика
        self.add_pan_and_zoom(canvas, ax)

    def open_boxplot(self):
        if self.df is None or self.selected_column is None:
            messagebox.showinfo(self.translations[self.current_language]["info"], self.translations[self.current_language]["load_data_first"])
            return

        data = self.df[self.selected_column].dropna()

        # Создаем новое окно
        new_window = Toplevel(self.master)
        new_window.title(self.translations[self.current_language]["box_plot"])

        # Создаем новую фигуру и оси
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.boxplot(y=data.values, color=self.boxplot_color, ax=ax)  # Use seaborn
        ax.set_title(f"{self.translations[self.current_language]['box_plot']} ({self.selected_column})")
        ax.set_ylabel("Value")

        # Создаем canvas для отображения графика в окне
        canvas = FigureCanvasTkAgg(fig, master=new_window)
        canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Добавляем панель инструментов навигации
        toolbar = NavigationToolbar2Tk(canvas, new_window)
        toolbar.update()
        toolbar.pack(side=tk.LEFT, fill=tk.Y)

        canvas.draw()

        # Добавляем возможность перетаскивания графика
        self.add_pan_and_zoom(canvas, ax)

    def add_pan_and_zoom(self, canvas, ax):
        def on_press(event):
            if event.inaxes == ax:
                self.x0, self.y0 = event.xdata, event.ydata

        def on_motion(event):
            if event.inaxes == ax:
                dx = event.xdata - self.x0
                dy = event.ydata - self.y0
                ax.set_xlim([ax.get_xlim()[0] - dx, ax.get_xlim()[1] - dx])
                ax.set_ylim([ax.get_ylim()[0] - dy, ax.get_ylim()[1] - dy])
                canvas.draw_idle()
                self.x0, self.y0 = event.xdata, event.ydata

        canvas.mpl_connect('button_press_event', on_press)
        canvas.mpl_connect('motion_notify_event', on_motion)

    def update_plots_and_stats(self, *args):
        if self.df is None:
            return

        self.selected_column = self.column_var.get()
        if self.selected_column not in self.df.columns:
            return

        data = self.df[self.selected_column].dropna()

        # График расхождений
        self.ax_scatter.clear()
        if self.scatter_visible.get():
            sns.scatterplot(x=data.index, y=data.values, color=self.scatter_color, ax=self.ax_scatter)  # Use seaborn
            self.ax_scatter.set_title(f"{self.translations[self.current_language]['scatter_plot']} ({self.selected_column})")
            self.ax_scatter.set_xlabel("Index")
            self.ax_scatter.set_ylabel("Value")
        self.ax_scatter.set_visible(self.scatter_visible.get())

        # Ящик с усами
        self.ax_boxplot.clear()
        if self.boxplot_visible.get():
            sns.boxplot(y=data.values, color=self.boxplot_color, ax=self.ax_boxplot)  # Use seaborn
            self.ax_boxplot.set_title(f"{self.translations[self.current_language]['box_plot']} ({self.selected_column})")
            self.ax_boxplot.set_ylabel("Value")
        self.ax_boxplot.set_visible(self.boxplot_visible.get())

        self.fig.tight_layout()
        self.canvas.draw()

        # Расчет статистики
        mean = data.mean()
        variance = data.var()
        range_val = data.max() - data.min()
        max_val = data.max()
        min_val = data.min()
        try:
            geometric_mean = gmean(data.values)
            harmonic_mean = hmean(data.values)
        except:
            geometric_mean = "N/A (values must be positive)"
            harmonic_mean = "N/A (values must be positive)"
        
        try:
            quadratic_mean = statistics.mean(x**2 for x in data.values)**0.5
        except:
            quadratic_mean = "N/A"

        median = data.median()
        std_dev = data.std()
        try:
            mode = data.mode().iloc[0]  # Handle multiple modes
        except:
            mode = "N/A"

        # Вывод статистики в отдельные текстовые поля
        self.mean_text.delete("1.0", tk.END)
        self.mean_text.insert(tk.END, f"{mean:.2f}")

        self.variance_text.delete("1.0", tk.END)
        self.variance_text.insert(tk.END, f"{variance:.2f}")

        self.range_text.delete("1.0", tk.END)
        self.range_text.insert(tk.END, f"{range_val:.2f}")

        self.max_text.delete("1.0", tk.END)
        self.max_text.insert(tk.END, f"{max_val:.2f}")

        self.min_text.delete("1.0", tk.END)
        self.min_text.insert(tk.END, f"{min_val:.2f}")

        self.geometric_mean_text.delete("1.0", tk.END)
        self.geometric_mean_text.insert(tk.END, f"{geometric_mean}")

        self.harmonic_mean_text.delete("1.0", tk.END)
        self.harmonic_mean_text.insert(tk.END, f"{harmonic_mean}")
        
        self.quadratic_mean_text.delete("1.0", tk.END)
        self.quadratic_mean_text.insert(tk.END, f"{quadratic_mean}")

        self.median_text.delete("1.0", tk.END)
        self.median_text.insert(tk.END, f"{median:.2f}")

        self.std_dev_text.delete("1.0", tk.END)
        self.std_dev_text.insert(tk.END, f"{std_dev:.2f}")

        self.mode_text.delete("1.0", tk.END)
        self.mode_text.insert(tk.END, f"{mode}")
    
    def change_language(self, language):
        if language == self.translations[self.current_language]["russian"]:
            self.current_language = "ru"
        else:
            self.current_language = "en"
        self.update_text()

    def update_text(self):
        # Update all the text elements in the UI
        self.master.title(self.translations[self.current_language]["title"])
        self.language_label.config(text=self.translations[self.current_language]["language"])
        self.language_var.set(self.translations[self.current_language][self.language_var.get() == self.translations[self.current_language]["english"] and "russian" or "english"])
        menu = self.language_dropdown["menu"]
        menu.delete(0, "end")
        for lang in [self.translations[self.current_language]["english"], self.translations[self.current_language]["russian"]]:
            menu.add_command(label=lang, command=tk._setit(self.language_var, lang))
        self.load_data_button.config(text=self.translations[self.current_language]["load_data"])
        self.column_label.config(text=self.translations[self.current_language]["select_column"])
        self.scatter_check.config(text=self.translations[self.current_language]["scatter_plot"])
        self.boxplot_check.config(text=self.translations[self.current_language]["box_plot"])
        self.scatter_color_button.config(text=self.translations[self.current_language]["scatter_color"])
        self.boxplot_color_button.config(text=self.translations[self.current_language]["box_color"])
        self.save_scatter_button.config(text=self.translations[self.current_language]["save_scatter"])
        self.save_boxplot_button.config(text=self.translations[self.current_language]["save_box"])
        self.open_scatter_button.config(text=self.translations[self.current_language]["open_scatter"])
        self.open_boxplot_button.config(text=self.translations[self.current_language]["open_box"])
        self.mean_label.config(text=self.translations[self.current_language]["mean"])
        self.variance_label.config(text=self.translations[self.current_language]["variance"])
        self.range_label.config(text=self.translations[self.current_language]["range"])
        self.max_label.config(text=self.translations[self.current_language]["max"])
        self.min_label.config(text=self.translations[self.current_language]["min"])
        self.geometric_mean_label.config(text=self.translations[self.current_language]["geometric_mean"])
        self.harmonic_mean_label.config(text=self.translations[self.current_language]["harmonic_mean"])
        self.quadratic_mean_label.config(text=self.translations[self.current_language]["quadratic_mean"])
        self.median_label.config(text=self.translations[self.current_language]["median"])
        self.std_dev_label.config(text=self.translations[self.current_language]["std_dev"])
        self.mode_label.config(text=self.translations[self.current_language]["mode"])
        self.update_plots_and_stats()

root = tk.Tk()
app = DataAnalyzerApp(root)
root.mainloop()
