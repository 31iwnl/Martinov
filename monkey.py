import os
import random
import dearpygui.dearpygui as dpg
import numpy as np
import win32con
import win32console
import win32gui

sequence = []

# Проверка, что скрипт выполняется на Windows
if os.name != "nt":
    input("This script only works on Windows.")
    os._exit(0)

# Скрытие консольного окна
win32gui.ShowWindow(win32console.GetConsoleWindow(), win32con.SW_HIDE)

# Параметры UI
uiWidth = 800
uiHeight = 600

# Инициализация Dear PyGui
dpg.create_context()

bar_width = 70
dpg_progress = 0.0  # dynamic progress gauge


def update_progress_bar():
    dpg.set_value("status_text", '')
    global dpg_progress
    global length
    create = "["
    for i in range(bar_width):
        pos = dpg_progress * bar_width
        if i < pos:
            create += "="
        else:
            create += " "

    create += "]"

    dpg.set_value("creating_status", create)


def generateBits():
    global sequence, dpg_progress, length
    result = ""
    t = 0
    input_value = dpg.get_value("input_text")
    if not input_value:
        result = "Sequence can't be empty"
        dpg.set_value("status_text", result)
        return
    try:
        length = int(input_value)
        if length > 0:
            sequence = [random.randint(0, 1) for i in range(length)]
            dpg_progress = 0.0
            for i in range(length):
                dpg_progress = (i + 1) / length
                update_progress_bar()

                t = (str(int((i * 1.0 / length * 100 + 0.1))))
                f = str(t) + '% '
                dpg.set_value("percent_status", f)

            result += "New sequence created"
            with open("random.txt", "w") as file:
                file.write(str(sequence))
            dpg.set_value("status_text", result)
        else:
            result = "Length of sequence should be more than 0"
            dpg.set_value("status_text", result)
    except ValueError:
        result = "Not correct sequence length"
        dpg.set_value("status_text", result)


def test_sequence(rel):
    result = ""
    # Проверяем, что последовательность состоит только из 0 и 1
    if not all(bit in (0, 1) for bit in sequence):
        raise ValueError("Последовательность должна состоять только из 0 и 1.")

    n = len(sequence)

    # Преобразуем последовательность ε в X
    X = [2 * bit - 1 for bit in sequence]

    # Вычисляем сумму Sn
    Sn = sum(X)

    # Вычисляем статистику S
    S = abs(Sn) / (n ** 0.5)
    result += f"S: {str(S)} \n"
    # Проверяем, прошёл ли тест
    if S <= 1.82138636:
        result += "S <= 1.82138636 \n"
        print("Последовательность прошла тест на случайность.")
        result += "The sequence passed the randomness test."
        dpg.set_value("status_text", result)
        dpg.set_value("percent_status", '')
        dpg.set_value("creating_status", '')

    else:
        result += "S > 1.82138636 \n"
        print("Последовательность не прошла тест на случайность.")
        result += "The sequence not passed the randomness test."
        dpg.set_value("status_text", result)
        dpg.set_value("percent_status", '')
        dpg.set_value("creating_status", '')


def readBits():
    global sequence
    with open("random.txt", "r") as file:
        for line in file:
            sequence = line
        sequence = list(map(int, sequence[1:-1].split(', ')))

    return sequence


rel = readBits()


def test_identical_bits_sequence(rel):
    result = ""
    # Проверяем, что последовательность состоит только из 0 и 1

    if not all(bit in (0, 1) for bit in sequence):
        raise ValueError("Последовательность должна состоять только из 0 и 1.")

    n = len(sequence)

    # Вычисляем частоту единиц π
    pi = sum(sequence) / n

    # Вычисляем Vn
    Vn = 1
    r = 0

    for k in range(n - 1):
        if sequence[k] != sequence[k + 1]:
            r += 1  # Увеличиваем счетчик при изменении
    Vn += r

    # Вычисляем статистику S
    S = abs(Vn - 2 * n * pi * (1 - pi)) / (2 * (2 ** 0.5) * n * pi * (1 - pi) ** 0.5)
    result += f"S: {str(S)} \n"
    # Проверяем, прошел ли тест
    if S <= 1.82138636:
        result += "S <= 1.82138636 \n"
        result += "The sequence passed the randomness test."
        dpg.set_value("status_text", result)
        dpg.set_value("percent_status", '')
        dpg.set_value("creating_status", '')


    else:
        result += "S > 1.82138636 \n"
        result += "The sequence not passed the randomness test."
        dpg.set_value("status_text", result)
        dpg.set_value("percent_status", '')
        dpg.set_value("creating_status", '')


def extended_deviation_test(rel):
    result = ""
    x = 2 * np.array(sequence) - 1  # Преобразуем последовательность бит в -1 и 1
    s = np.cumsum(x)  # Вычисляем кумулятивные суммы
    s_prime = np.concatenate(([0], s, [0]))  # Добавляем нули в начале и конце
    l = np.sum(s_prime == 0) - 1  # Вычисляем количество нулей

    counts = np.zeros(18)  # Создаем массив для подсчета посещений состояний
    for i in range(len(s_prime)):
        state = int(s_prime[i])
        if state >= -9 and state <= 9:
            counts[state + 8] += 1  # Увеличиваем счетчик для соответствующего состояния

    y = np.zeros(18)  # Создаем массив для хранения статистик
    for j in range(18):

        if 2 * l * (4 * np.abs(j - 9) - 2) > 0:
            y[j] = np.abs(counts[j] - l) / np.sqrt(2 * l * (4 * np.abs(j - 9) - 2))
        else:
            y[j] = 0

    result += "Extended test for random deviations: \n"
    for j in range(-9, 9):
        result += f"State {j}: appears {counts[j + 9]} times, Statistic: {y[j + 9]:.4f} \n"
    states_not_passing = np.where(y > 1.82138636)[0] - 9
    states_not_passing_str = ', '.join([str(state) for state in states_not_passing])
    states_list = [state for state in states_not_passing_str.split(', ') if state]

    # Проверяем, что все статистики меньше порогового значения
    if np.all(y <= 1.82138636):
        result += "The sequence passed the randomness test."
        dpg.set_value("status_text", result)
        dpg.set_value("percent_status", '')
        dpg.set_value("creating_status", '')

    else:

        result += "The sequence not passed the randomness test. \n"

        result += f"The following states did not pass the test: {states_list}"
        dpg.set_value("status_text", result)
        dpg.set_value("percent_status", '')
        dpg.set_value("creating_status", '')


with dpg.window(label='Lab1 by A.V.V', width=uiWidth, height=uiHeight, no_collapse=False, no_move=True,
                no_resize=True, on_close=lambda: os._exit(0)) as window:
    dpg.add_spacer(width=75)
    dpg.add_input_text(label="Length of sequence", tag="input_text", default_value='0')
    dpg.add_button(label="Generate", callback=generateBits)
    dpg.add_button(label="First Test", callback=test_sequence)
    dpg.add_button(label="Second Test", callback=test_identical_bits_sequence)
    dpg.add_button(label="Third Test", callback=extended_deviation_test)
    dpg.add_text("", tag="status_text")  # Поле для отображения статуса
    dpg.add_text("", tag="creating_status")  # Поле для отображения статуса
    dpg.add_text("", tag="percent_status")  # Поле для отображения статуса

with dpg.theme() as globalTheme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (0, 0, 0, 255))
        dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (0, 0, 0, 255))
        dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (255, 255, 255, 255))
        dpg.add_theme_color(dpg.mvThemeCol_Text, (225, 225, 225, 255))
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (0, 0, 0, 255))
        dpg.add_theme_color(dpg.mvThemeCol_Tab, (0, 0, 0, 255))
        dpg.add_theme_color(dpg.mvThemeCol_TabActive, (100, 100, 100, 255))
        dpg.add_theme_color(dpg.mvThemeCol_TabUnfocused, (100, 100, 100, 255))
        dpg.add_theme_color(dpg.mvThemeCol_TabUnfocusedActive, (100, 100, 100, 255))
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (0, 0, 0, 255))
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (0, 0, 0, 255))
        dpg.add_theme_color(dpg.mvThemeCol_TabHovered, (100, 100, 100, 255))
        dpg.add_theme_color(dpg.mvThemeCol_PlotLinesHovered, (100, 100, 100, 255))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (100, 100, 100, 255))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (100, 100, 100, 255))

dpg.bind_theme(globalTheme)
dpg.create_viewport(title='Lab1', width=uiWidth, height=uiHeight, decorated=True, resizable=False)
dpg.show_viewport()

dpg.setup_dearpygui()
dpg.start_dearpygui()
