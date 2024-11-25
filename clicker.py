import pyautogui
import keyboard
import tkinter as tk
from tkinter import messagebox, ttk
from threading import Thread, Event
import time


class AutoClickerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Автокликер GUI")
        self.geometry("600x800")
        self.configure(bg="#2C3E50")  # Темный, современный фон
        self.resizable(False, False)
        self.attributes('-topmost', True)  # Держать окно поверх всех других

        # Инициализация переменных
        self.start_stop_key = None
        self.clicker_active = False
        self.clicker_ready = False
        self.clicks_per_second = 1
        self.stop_event = Event()
        self.mode = "Обычный"  # Режим по умолчанию
        self.hotkey_registered = False
        self.mouse_button = "left"  # Кнопка мыши по умолчанию
        self.click_position = None  # Позиция клика по умолчанию
        self.capture_window = None  # Окно захвата координат

        # Настройка пользовательского интерфейса
        self.setup_ui()

        # Обработка закрытия окна
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        # Заголовок
        title_label = tk.Label(self, text="Инструмент автокликера", font=("Helvetica Neue", 20, "bold"),
                               bg="#2C3E50", fg="#ECF0F1")
        title_label.pack(pady=20)

        # Метка статуса
        self.status_label = tk.Label(self, text="Нажмите 'Установить клавишу' для начала.", font=("Helvetica Neue", 14),
                                     bg="#2C3E50", fg="#BDC3C7", wraplength=580, justify="center")
        self.status_label.pack(pady=10)

        # Кнопка установки клавиши
        set_key_button = tk.Button(self, text="Установить клавишу", command=self.set_key_dialog,
                                   font=("Helvetica Neue", 14),
                                   bg="#2980B9", fg="white", activebackground="#3498DB", activeforeground="white",
                                   padx=20, pady=10, bd=0, relief="flat")
        set_key_button.pack(pady=10)

        # Выбор режима работы из списка
        mode_label = tk.Label(self, text="Выберите режим работы клика:", font=("Helvetica Neue", 14), bg="#2C3E50",
                              fg="#ECF0F1", wraplength=580, justify="center")
        mode_label.pack(pady=10)

        self.mode_combo = ttk.Combobox(self, values=["Обычный", "Ультиматум"], font=("Helvetica Neue", 14),
                                       state='readonly')
        self.mode_combo.current(0)  # По умолчанию выбран обычный режим
        self.mode_combo.bind("<<ComboboxSelected>>", self.update_clicker_mode)
        self.mode_combo.pack(pady=10)

        # Ввод количества кликов в секунду (для обычного режима)
        self.clicks_label = tk.Label(self,
                                     text="Выберите количество кликов в секунду (для обычного режима):",
                                     font=("Helvetica Neue", 14), bg="#2C3E50",
                                     fg="#ECF0F1", wraplength=580, justify="center")
        self.clicks_label.pack(pady=10)

        self.clicks_spinbox = tk.Spinbox(self, from_=1, to=1000, font=("Helvetica Neue", 14), justify="center",
                                         width=5, increment=1, command=self.update_clicks_per_second)
        self.clicks_spinbox.bind("<MouseWheel>", self.on_spinbox_mousewheel)
        self.clicks_spinbox.pack(pady=10)

        # Выбор кнопки мыши для клика
        mouse_button_label = tk.Label(self, text="Выберите кнопку мыши для клика:", font=("Helvetica Neue", 14),
                                      bg="#2C3E50", fg="#ECF0F1", wraplength=580, justify="center")
        mouse_button_label.pack(pady=10)

        self.mouse_button_combo = ttk.Combobox(self, values=["Левая кнопка", "Правая кнопка", "Средняя кнопка"],
                                               font=("Helvetica Neue", 14), state='readonly')
        self.mouse_button_combo.current(0)  # По умолчанию выбрана левая кнопка
        self.mouse_button_combo.bind("<<ComboboxSelected>>", self.update_mouse_button)
        self.mouse_button_combo.pack(pady=10)

        # Ввод координат клика (опционально)
        click_position_label = tk.Label(self, text="Указать координаты клика (опционально):",
                                        font=("Helvetica Neue", 14),
                                        bg="#2C3E50", fg="#ECF0F1", wraplength=580, justify="center")
        click_position_label.pack(pady=10)

        position_frame = tk.Frame(self, bg="#2C3E50")
        position_frame.pack(pady=10)

        x_label = tk.Label(position_frame, text="X:", font=("Helvetica Neue", 14), bg="#2C3E50", fg="#ECF0F1")
        x_label.grid(row=0, column=0, padx=5)

        self.x_entry = tk.Entry(position_frame, font=("Helvetica Neue", 14), width=5, justify="center")
        self.x_entry.grid(row=0, column=1, padx=5)

        y_label = tk.Label(position_frame, text="Y:", font=("Helvetica Neue", 14), bg="#2C3E50", fg="#ECF0F1")
        y_label.grid(row=0, column=2, padx=5)

        self.y_entry = tk.Entry(position_frame, font=("Helvetica Neue", 14), width=5, justify="center")
        self.y_entry.grid(row=0, column=3, padx=5)

        # Кнопка захвата текущих координат
        capture_button = tk.Button(position_frame, text="Захватить координаты с экрана",
                                   command=self.capture_mouse_position,
                                   font=("Helvetica Neue", 12), bg="#2980B9", fg="white",
                                   activebackground="#3498DB",
                                   activeforeground="white", padx=10, pady=5, bd=0, relief="flat")
        capture_button.grid(row=0, column=4, padx=5)

        # Кнопка старта
        start_button = tk.Button(self, text="Запустить кликер", command=self.prepare_clicker,
                                 font=("Helvetica Neue", 14),
                                 bg="#27AE60", fg="white", activebackground="#2ECC71", activeforeground="white",
                                 padx=20, pady=10, bd=0, relief="flat")
        start_button.pack(pady=10)

    def set_key_dialog(self):
        # Диалог для выбора клавиши
        key_dialog = tk.Toplevel(self)
        key_dialog.transient(self)
        key_dialog.grab_set()
        key_dialog.title("Выбор клавиши")
        key_dialog.geometry(f"400x200+{self.winfo_x() + 100}+{self.winfo_y() + 150}")
        key_dialog.configure(bg="#34495E")
        key_dialog.resizable(False, False)

        dialog_label = tk.Label(key_dialog,
                                text="Введите клавишу для включения/выключения кликера:",
                                font=("Helvetica Neue", 12), bg="#34495E", fg="#ECF0F1", wraplength=380,
                                justify="center")
        dialog_label.pack(pady=20)

        key_entry = tk.Entry(key_dialog, font=("Helvetica Neue", 14), justify="center")
        key_entry.pack(pady=10)

        ok_button = tk.Button(key_dialog, text="OK",
                              command=lambda: self.set_key_from_dialog(key_dialog, key_entry),
                              font=("Helvetica Neue", 12),
                              bg="#27AE60", fg="white", activebackground="#2ECC71", activeforeground="white", padx=20,
                              pady=5, relief="flat")
        ok_button.pack(pady=10)

    def set_key_from_dialog(self, dialog, key_entry):
        new_key = key_entry.get()
        if new_key:
            # Удаляем предыдущую горячую клавишу, если она была установлена
            if self.hotkey_registered:
                keyboard.remove_hotkey(self.start_stop_key)
                self.hotkey_registered = False

            self.start_stop_key = new_key
            self.status_label.config(
                text=f"Кликер будет управляться клавишей '{self.start_stop_key}'. Нажмите 'Запустить кликер', а затем клавишу для включения/выключения.",
                wraplength=580, justify="center")
            dialog.destroy()
        else:
            messagebox.showwarning("Ошибка ввода", "Клавиша не введена. Попробуйте снова.", parent=dialog)

    def prepare_clicker(self):
        if not self.start_stop_key:
            messagebox.showwarning("Клавиша не установлена",
                                   "Пожалуйста, сначала установите клавишу для включения/выключения.", parent=self)
            return

        # Определение выбранного режима работы
        self.mode = self.mode_combo.get()

        # Обновление количества кликов в секунду
        self.update_clicks_per_second()

        # Обновление кнопки мыши
        self.update_mouse_button()

        # Чтение координат клика
        x_text = self.x_entry.get()
        y_text = self.y_entry.get()
        if x_text and y_text:
            try:
                x = int(x_text)
                y = int(y_text)
                self.click_position = (x, y)
            except ValueError:
                messagebox.showwarning("Ошибка ввода", "Введите корректные целые числа для координат X и Y.", parent=self)
                self.click_position = None
        else:
            self.click_position = None  # Координаты не указаны

        # Подготовка кликера
        self.clicker_ready = True
        self.status_label.config(
            text=f"Кликер готов в режиме '{self.mode}'. Нажмите '{self.start_stop_key}' для начала работы или остановки.\n"
                 f"Кнопка мыши: {self.mouse_button_combo.get()}\n"
                 f"Координаты клика: {self.click_position if self.click_position else 'Текущая позиция курсора'}",
            wraplength=580, justify="center")

        # Показать или скрыть элементы ввода в зависимости от режима
        if self.mode == "Ультиматум":
            self.clicks_label.pack_forget()
            self.clicks_spinbox.pack_forget()
        else:
            self.clicks_label.pack(pady=10)
            self.clicks_spinbox.pack(pady=10)

        # Удаляем предыдущую горячую клавишу, если она была установлена
        if self.hotkey_registered:
            keyboard.remove_hotkey(self.start_stop_key)

        # Регистрируем горячую клавишу
        keyboard.add_hotkey(self.start_stop_key, self.toggle_clicker)
        self.hotkey_registered = True

    def toggle_clicker(self):
        self.clicker_active = not self.clicker_active
        if self.clicker_active:
            self.stop_event.clear()
            self.status_label.config(
                text=f"Кликер запущен в режиме '{self.mode}'. Нажмите '{self.start_stop_key}' для остановки.",
                wraplength=580, justify="center")

            # Устанавливаем паузу PyAutoGUI в 0 для более быстрого клика
            pyautogui.PAUSE = 0

            # Запускаем поток клика
            if self.mode == "Ультиматум":
                self.clicker_thread = Thread(target=self.ultimatum_clicker, daemon=True)
            else:
                self.update_clicks_per_second()
                self.clicker_thread = Thread(target=self.normal_clicker, daemon=True)
            self.clicker_thread.start()
        else:
            self.stop_event.set()
            self.status_label.config(
                text="Кликер остановлен. Нажмите установленную клавишу, чтобы начать снова.", wraplength=580,
                justify="center")

    def update_clicker_mode(self, event=None):
        # Обновление режима работы
        self.mode = self.mode_combo.get()
        self.status_label.config(
            text=f"Режим клика установлен на '{self.mode}'. Нажмите 'Запустить кликер', чтобы начать.",
            wraplength=580, justify="center")

        # Показать или скрыть элементы ввода в зависимости от режима
        if self.mode == "Ультиматум":
            self.clicks_label.pack_forget()
            self.clicks_spinbox.pack_forget()
        else:
            self.clicks_label.pack(pady=10)
            self.clicks_spinbox.pack(pady=10)

    def update_clicks_per_second(self):
        # Обновление количества кликов в секунду
        try:
            cps = int(self.clicks_spinbox.get())
            if cps <= 0:
                raise ValueError
            self.clicks_per_second = cps
        except ValueError:
            messagebox.showwarning("Ошибка ввода",
                                   "Введите корректное положительное число для количества кликов в секунду.",
                                   parent=self)
            self.clicks_per_second = 1
            self.clicks_spinbox.delete(0, tk.END)
            self.clicks_spinbox.insert(0, "1")

    def on_spinbox_mousewheel(self, event):
        # Обновление количества кликов в секунду при использовании колесика мыши
        if event.delta > 0:
            self.clicks_spinbox.invoke("buttonup")
        else:
            self.clicks_spinbox.invoke("buttondown")
        self.update_clicks_per_second()

    def update_mouse_button(self, event=None):
        # Обновление выбранной кнопки мыши
        button_text = self.mouse_button_combo.get()
        if button_text == "Левая кнопка":
            self.mouse_button = "left"
        elif button_text == "Правая кнопка":
            self.mouse_button = "right"
        elif button_text == "Средняя кнопка":
            self.mouse_button = "middle"
        else:
            self.mouse_button = "left"
        self.status_label.config(
            text=f"Кнопка мыши для клика установлена на '{button_text}'.",
            wraplength=580, justify="center")

    def capture_mouse_position(self):
        # Создаем полноэкранное прозрачное окно для захвата клика
        self.capture_window = tk.Toplevel(self)
        self.capture_window.attributes('-fullscreen', True)
        self.capture_window.attributes('-alpha', 0.01)  # Почти прозрачное окно
        self.capture_window.config(bg='black')
        self.capture_window.bind('<Button-1>', self.on_capture_click)
        self.capture_window.bind('<Escape>', self.on_capture_cancel)
        self.capture_window.focus_set()
        self.capture_window.grab_set()
        self.status_label.config(
            text="Нажмите левой кнопкой мыши в место, куда хотите кликать, или нажмите 'Esc' для отмены.",
            wraplength=580, justify="center")

    def on_capture_click(self, event):
        # Получаем координаты клика
        x = event.x_root
        y = event.y_root
        self.x_entry.delete(0, tk.END)
        self.x_entry.insert(0, str(x))
        self.y_entry.delete(0, tk.END)
        self.y_entry.insert(0, str(y))
        self.status_label.config(
            text=f"Координаты клика установлены на X: {x}, Y: {y}.",
            wraplength=580, justify="center")
        # Закрываем окно захвата
        self.capture_window.destroy()

    def on_capture_cancel(self, event):
        # Отмена захвата координат
        self.capture_window.destroy()
        self.status_label.config(
            text="Захват координат отменен.",
            wraplength=580, justify="center")

    def normal_clicker(self):
        # Клик с заданным количеством кликов в секунду
        interval = 1 / self.clicks_per_second
        try:
            while not self.stop_event.is_set():
                if self.click_position:
                    pyautogui.click(x=self.click_position[0], y=self.click_position[1], button=self.mouse_button)
                else:
                    pyautogui.click(button=self.mouse_button)
                time.sleep(interval)
        except Exception as e:
            self.status_label.config(text=f"Произошла ошибка: {e}", wraplength=580, justify="center")

    def ultimatum_clicker(self):
        # Клик максимально быстро
        try:
            while not self.stop_event.is_set():
                if self.click_position:
                    pyautogui.click(x=self.click_position[0], y=self.click_position[1], button=self.mouse_button)
                else:
                    pyautogui.click(button=self.mouse_button)
        except Exception as e:
            self.status_label.config(text=f"Произошла ошибка: {e}", wraplength=580, justify="center")

    def on_closing(self):
        # Очистка при закрытии приложения
        if self.hotkey_registered:
            keyboard.remove_hotkey(self.start_stop_key)
        self.stop_event.set()
        self.destroy()


if __name__ == "__main__":
    app = AutoClickerApp()
    app.mainloop()
