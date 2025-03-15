import json
import re
import random as rand
from os import system


def clear():
    # Очищення терміналу
    system("cls")
    
def style_text(text, *styles):
    # Стилізування тексту
    new_text = ""
    for style in styles:
        new_text += style
    new_text += text
    new_text += font_decors["clear"]
    return new_text

def style_error_text(text):
    # Текст помилки
    return style_text(text, font_colors["white"], bg_colors["red"])

def get_text_from_error(error):
    # Визначає який повинен бути текст взалежності від помилки
    err_text = ""
    if type(error) == ValueError:
        err_text += "Невірний формат даних! "
            
        match str(error):
            case "NegativeNumber":
                err_text += "Число повинне буди додатнім!"
            case "FloatInsteadInt":
                err_text += "Отримано дробове число в той час як очикувалось ціле!"
            case "WrongAge":
                err_text += "Неможливий вік!"
            case "NumberOutOfRange":
                err_text += "Число не входить в діапазон!"
            case "EmptyString":
                err_text += "Пустий рядок!"
            case "KeyNotFound":
                err_text += "Ключ не знайдено!"
            case "WrongTel":
                err_text += "Невірний формат телефона! (+380#########) (9 цифр після +380)"
            case _:
                err_text += "Не вдалось конвертувати до числа!"

    else:
        err_text += str(error)
        
    return style_error_text(err_text)

def convert_to(data, data_type):
    # Конвертує з String до визначеного типу, якщо не виходить повертає None
    err_text = None
    converted_data = None
    try:
        if data_type.find("int") != -1: # Ціле число
            float_data = float(data)
            int_data = int(float_data)
            if int_data != float_data:
                raise ValueError("FloatInsteadInt")
            if data_type.find("+") != -1 and int_data < 0: # Повинне бути додатнім
                raise ValueError("NegativeNumber")
            converted_data = int_data
            
        if data_type.find("float") != -1: # Дробове число
            float_data = float(data)
            if data_type.find("+") != -1 and float_data < 0: # Повинне бути додатнім
                raise ValueError("NegativeNumber")
            converted_data = float_data
            
        if data_type.find("age") != -1: # Вік
            age_data, err_text = convert_to(data, "int")
            if age_data is not None:
                if age_data < 0 or age_data > 120: 
                    raise ValueError("WrongAge")
                converted_data = age_data
                
        if data_type.find("tel") != -1: # Номер телефона
            tel_template_data = re.search(r"^\+380\d{9}$", data)
            if tel_template_data is None:
                raise ValueError("WrongTel")
            converted_data = tel_template_data.group()
        
        if data_type.find("str") != -1: # Звичайний рядок, але не пустий
            if not data:
                raise ValueError("EmptyString")
            converted_data = data
                
    except Exception as e:
        err_text = get_text_from_error(e)
        
    return (converted_data, err_text)

def input_and_convert_to(msg, data_type):
    # Запитує дані і поки вони не будуть введені відповідно
    # до типу який запитується програма не продовжиться
    while True:
        input_data = input(msg).strip()
        converted_data, err_msg = convert_to(input_data, data_type)
        if converted_data is not None:
            return converted_data
        else:
            print(err_msg)

def print_critical_error(msg="Критична помилка!"):
    # Помилка яка вимагає перейти в головне меню
    while True:
        input(style_error_text(f"{msg} {text_button_for_main_menu}"))

def get_db():
    # Повертає дані з бази даних
    try:
        with open(db_file_path, "r", encoding="utf-8") as file:
            data = file.read()
            if data:
                try:
                    return json.loads(data)
                except Exception: # Якщо база була редагована вручну і якісь знаки упустили
                    print_critical_error("Помилка імпорту бази даних! База даних містить помилки!")
            else:
                return []
    except FileNotFoundError: # Якщо того файлу немає, то створиться пустий
        write_db([])
        return get_db()
        
    
def write_db(db_list):
    # Переписування бази даних
    with open(db_file_path, "w", encoding="utf-8") as file:
        file.write(json.dumps(db_list, ensure_ascii=False, indent=4))
        
def add_record_to_db(record):
    # Додає один запис до бази
    db = get_db()
    db.append(record)
    write_db(db)

def show_add_few_records_to_db():
    # Меню додавання записів до бази
    clear()
    count_records = input_and_convert_to("Кількість записів: ", "+int")
    add_few_records_to_db(count_records)

def add_few_records_to_db(count_records):
    # Додає кілька записів до бази
    for i in range(count_records):
        new_db_record(f"Новий запис ({i+1}/{count_records})")

def new_db_record(header_text="Новий запис"):
    # Керування створенням нового запису
    clear()
    print(style_text(header_text.center(30), bg_colors["green"]))
    add_record_to_db(create_record())

def show_warning(msg="Ви впевнені?"):
    # Попередження про серйозність дії
    menu_options = [("Так", lambda: None)]
    return show_menu(menu_options, msg)

def press_enter_to_continue(msg="Натисність Enter щоб продовжити..."):
    # Замороження терміналу
    input(msg)
    
def show_create_new_empty_db():
    # Меню створення пустої бази
    clear()
    if not show_warning("Ви впевнені що хочете створити нову базу даних, при цьому видаливши стару?"):
        return
    create_new_empty_db()

def create_new_empty_db():
    # Створення пустої бази
    write_db([])
    add_few_records_to_db()
    
    
def get_last_id_in_db():
    # Повертає найбільший ID в базі
    try:
        return max(get_db(), key=lambda record: record["id"])["id"]
    except ValueError:
        return -1
        
def create_record():
    # Створює запис в форматі Dict
    record = {}
    for key, data_type in employee_record_keys_with_types.items():
        if key == "id":
            data = get_last_id_in_db() + 1
        else:
            data = input_and_convert_to(f"{key} : ", data_type)
        record[key] = data
    return record

def make_table_element(values, start_chr, sep_chr, end_chr):
    # Повертає елемент таблиці (боки таблиці та розмежування даних)
    return start_chr + sep_chr.join(values) + end_chr

def make_table_line(keys_widthes, line_type):
    # Повертає лінію розмежування таблиці яка не містить даних
    match line_type:
        case "up":
            start_chr, sep_chr, end_chr = table_chrs["ul"], table_chrs["uc"], table_chrs["ur"]
        case "split":
            start_chr, sep_chr, end_chr = table_chrs["lc"], table_chrs["cc"], table_chrs["rc"]
        case "down":
            start_chr, sep_chr, end_chr = table_chrs["dl"], table_chrs["dc"], table_chrs["dr"]
            
    values = [table_chrs["hor"] * size for size in keys_widthes.values()]
    return make_table_element(values, start_chr, sep_chr, end_chr)

def detect_content_align_by_key(key):
    # Повертає знак центрування елемента в залежності від його типу
    if key in keys_types:
        value_type = keys_types[key]
        if value_type.find("int") != -1 or value_type.find("float") != -1 or value_type.find("age") != -1:
            detected_content_align = ">"
        else:
            detected_content_align = "<"
    else:
        detected_content_align = "^"
    return detected_content_align

def make_table_content_line(record, keys_widthes, style=None, content_align=None):
    # Повертає елемент таблиці з контентом, а якщо контент не вписується в свою ширину
    # То рекурсивно викликається з аргументами залишку контенту
    if style == None:
        style = font_decors["clear"]
    
    data = style
    values = []
    for key, value in record.items():
        val = str(value)
        width = keys_widthes[key]
        val, record[key] = val[:width], val[width:]
        detected_content_align = detect_content_align_by_key(key) # Знак центрування
            
        if content_align is None: # Якщо знак центрування заданий, то він в пріорітеті
            used_content_align = detected_content_align
        else:
            used_content_align = content_align
            
        val = f"{val:{used_content_align}{width}}"
        values.append(val)
    data += make_table_element(values, table_chrs["ver"], table_chrs["ver"], table_chrs["ver"])
    is_has_rest = False
    for value in record.values():
        if value != "":
            is_has_rest = True
            break
    
    if is_has_rest: # Якщо є остача то виконується рекурсія з збереженням стилю
        data += font_decors["clear"] + '\n' + style + make_table_content_line(record, keys_widthes, style)
    data += font_decors["clear"]
    return data

def change_beetween_styles(style_counter, color1=None, color2=None):
    # Міняє почергово стилі в залежності від лічильника
    if color1 is None:
        color1 = bg_colors["grey"] + font_colors["black"]
    if color2 is None:
        color2 = font_decors["clear"]
        
    if style_counter % 2 == 0:
        return color1
    else:
        return color2

def get_keys_widthes(records_list, records_keys, max_width):
    # Повертає список ширини колонок таблиці
    keys_widthes = {}
    for key in records_keys:
        try:
            value_len = len(str(max(records_list, key=lambda record: len(str(record[key])))[key])) # Довжина контенту
        except Exception:
            value_len = 0
            # Якщо довжина контенту більша за максимальну ширину
            # то ширина дорівнює максимальній
        keys_widthes[key] = min(max(value_len, len(key)), max_width)
    return keys_widthes

def get_dict_both_side_key(my_dict):
    # Міняє значення на ключ
    return {key : key for key in my_dict.keys()}

def print_table(records_list=None, max_width = 13):
    # Виводиться таблиця з заголовком і списком
    if records_list is None:
        records_list = get_db()
    if len(records_list) > 0:
        my_keys = records_list[0]
    else:
        my_keys = {}
    records_keys = get_dict_both_side_key(my_keys) # Заголовок
    keys_widthes = get_keys_widthes(records_list, records_keys, max_width) # Ширини колонок
    
    second_style = bg_colors["grey"] + font_colors["black"] # Стиль для заголовку
    
    table_up_line = make_table_line(keys_widthes, "up") 
    table_title_line = make_table_content_line(records_keys, keys_widthes, second_style, "^")
    table_split_line = make_table_line(keys_widthes, "split")
    table_down_line = make_table_line(keys_widthes, "down")
    
    # Виведення заголовку
    print(style_text(table_up_line, second_style))
    print(style_text(table_title_line, second_style))
    print(style_text(table_split_line, second_style))
    
    # Виведення контенту
    table_style_counter = 1
    for record in records_list:
        cur_style = change_beetween_styles(table_style_counter)
        print(make_table_content_line(record, keys_widthes, cur_style))
        table_style_counter += 1
    
    # Виведення низу
    print(table_down_line)

def sum_by_key(key):
    # Сума значень записів за ключем
    total_of_key = 0
    records_list = get_db()
    for record in records_list:
        total_of_key += record[key]
    return total_of_key

def get_filter_value(filter_key):
    # Отримання даних за якими буде фільтрування
    clear()
    print_table()
    return input_and_convert_to("Введіть фільтруючі дані: ", employee_record_keys_with_types[filter_key])

def show_db_filtered_records(filter_key=None):
    # Меню фільтрування і одночасно фільтрування записів
    while True:
        clear()
        records_list = get_db()
        
        if filter_key is None:
            # Якщо в режимі меню
            filtered_records_list = records_list
            my_footer_text = None
        else:
            # Якщо в режимі фільтру
            filter_value = get_filter_value(filter_key)
            clear()
            filtered_records_list = [record for record in records_list if record[filter_key] == filter_value]
            my_footer_text = f"Поточний фільтр: Key:{filter_key}; Value:{filter_value};"
        
        # В залежності від того чи передавався ключ фільтрування виводяться
        # всі записи, або тільки відфільтровані
        print_table(filtered_records_list) 
        menu_options = []
        for key in employee_records_keys:
            menu_options.append((key, show_db_filtered_records, key))
        
        show_menu(menu_options, "Фільтрувати за", my_footer_text)
        return
        
        
def sort_records(sort_key, records_list=None):
    # Повертає відсортовані записи по ключу
    if records_list is None: #
        records_list = get_db()
    sorted_records_list = sorted(records_list, key=lambda record: record[sort_key])
    return sorted_records_list

def show_db_sorted_records(sort_key = None):
    # Меню сортування
    while True:
        clear()
        
        if sort_key is None: # Сортує по ID якщо перший запуск
            sort_key = employee_records_keys[0]
            
        sorted_records_list = sort_records(sort_key)
        print_table(sorted_records_list)
        
        menu_options = []
        for key in employee_records_keys:
            menu_options.append((key, show_db_sorted_records, key))
        
        my_footer_text = f"Поточне сортування: Key:{sort_key};"
        show_menu(menu_options, "Сортувати за", footer_text=my_footer_text)
        return


def show_db_records():
    # Виведення бази даних
    clear()
    print_table()
    press_enter_to_continue()
        
    
def show_menu(menu_options, header_text=None, footer_text=None):
    # Універсальне меню
    print_menu_options(menu_options, header_text, footer_text)
    return select_menu_option(menu_options)

def print_menu_options(menu_options, header_text=None, footer_text=None):
    # Виводить опції меню
    if header_text is not None:
        print(style_text(header_text.center(30), bg_colors["purple"]))
        
    for i in range(len(menu_options)):
        print(f"{i+1}. {menu_options[i][0]}")
    print("0. Вийти")
    
    if footer_text is not None:
        print(style_text(footer_text, font_colors["grey"]))


def select_menu_option(menu_options):
    # Запитує вибір опції, якщо вибрано 0, повертає False інакше True
    while True:
        choose = input_and_convert_to(f"Вибір: ", "+int")
        if choose < 0 or choose > len(menu_options):
            print(get_text_from_error(ValueError("NumberOutOfRange")))
        else:
            if choose == 0:
                return False
            menu_options[choose-1][1](*menu_options[choose-1][2:])
            return True

def main_menu():
    # Головне меню в якому відбувається вибір між функціями програми
    clear()
    print(style_text(program_name_text, font_colors[rand.choice(colors[1:])]))
    my_footer_text = "(Ctrl + C - Повернутись в головне меню)"
    return show_menu(main_menu_options, footer_text=my_footer_text)
    
def delete_record(id):
    # Видаляє запис відносно ID
    db = get_db()
    idx = None
    for i in range(len(db)):
        if db[i]["id"] == id:
            idx = i
            break
    if idx is None:
        return False
    db.pop(idx)
    write_db(db)
    return True

def show_delete_record():
    # Меню видалення записів
    while True:
        clear()
        print_table()
        while True: # Поки не введеться існуюче меню далі не пропускає
            id = input_and_convert_to("Введіть ID запису для видалення: ", "int")
            if get_record_by_value("id", id) is None:
                print(style_error_text("ID не знайдено!"))
            else:
                clear()
                print_table([get_record_by_value("id", id)])
                if show_warning("Ви впевнені що хочете видалити цей запис?"):
                    delete_record(id)
                break
                
def get_record_by_value(value_key, search_value):
    # Повертає значення по значенню ключа
    if value_key not in employee_records_keys:
        return None
    db = get_db()
    for record in db:
        if record[value_key] == search_value:
            return record
    return None

def get_records_by_few_values(*keys_and_values):
    # Повертає записи відносно кільком значень ключів у форматі
    # ((key1, value1), (key2, value2), ...)
    db = get_db()
    founded_vals = []
    for record in db:
        is_find = True
        for key, value in keys_and_values:
            if record[key] != value:
                is_find = False
                break
        if is_find:
            founded_vals.append(record)
    return founded_vals

def show_search_by_PIB():
    # Меню пошуку за ПІБ
    clear()
    print_table()
    name = input_and_convert_to("Введіть ім'я: ", "str")
    midname = input_and_convert_to("Введіть прізвище: ", "str")
    lastname = input_and_convert_to("Введіть по-батькові: ", "str")
    record = get_records_by_few_values(("midname", midname), ("name", name), ("lastname", lastname))
    clear()
    print_table(record)
    press_enter_to_continue()

def get_no_repeat_values_by_key(key):
    # Повертає значення записів по ключу без повторів
    db = get_db()
    values = []
    for record in db:
        if record[key] not in values:
            values.append(record[key])
    return values

def get_info_about_dapartments():
    # Повертає список записів з
    # Назвой відділу, бюджетом і кількістю працівників
    db = get_db()
    records_list = []
    
    departments = get_no_repeat_values_by_key("department")
    for department in departments:
        records_list.append({
            "department" : department,
            "capital" : 0,
            "count_employees": 0
            })
    
    for record in db:
        for department in records_list:
            if record["department"] == department["department"]:
                department["capital"] += record["salary"]
                department["count_employees"] += 1
                break
    return records_list

def show_departments_info():
    # Меню показу списку інформації про відділи
    clear()
    info_about_dapartments = get_info_about_dapartments()
    print_table(info_about_dapartments, max_width=30)
    press_enter_to_continue()

def make_table_list(keys_list, values_list):
    # Робить з списків ключів і заголовків, список записів 
    # ([key1, key2, ... n], [[value1, value2, ... n], [value1, value2, ... n], ... m])
    # n - кількість ключів
    # m - кількість записів
    records_list = [{} for i in range(len(values_list))]
    for i in range(len(values_list)):
        for j in range(len(keys_list)):
            records_list[i][keys_list[j]] = values_list[i][j]
        
    return records_list

def get_department_employees(department):
    # Повертає список записів що відносяться до заданого відділу
    db = get_db()
    records_list = []
    for record in db:
        if record["department"] == department:
            records_list.append(record)
    return records_list

def show_department_employees():
    # Меню покаку таблиці працівників що відносяться до заданого департаменту
    clear()
    departments = get_no_repeat_values_by_key("department")
    departments.sort()
    department_list = make_table_list(["department"], [[department] for department in departments])
    print_table(department_list)
    department = input_and_convert_to("Введіть назву відділу: ", "str")
    department_employees = get_department_employees(department)
    clear()
    print_table(department_employees)
    press_enter_to_continue()


def edit_record_by_id(id, key=None):
    # Змінення запису відповідно до ID
    if key is not None:
        db = get_db()
        for i in range(len(db)):
            if db[i]["id"] == id:
                while True: # Введення до поки не буде введено не існуючого ID або правильного формату даних
                    new_val = input_and_convert_to("Введіть нове значення: ", employee_record_keys_with_types[key])
                    if key == "id":
                        if is_id_exist(new_val):
                            print(style_error_text("Таке ID вже існує!"))
                        else:
                            break
                    else:
                        break
                db[i][key] = new_val
                if key == "id":
                    id = new_val # Зміна ID поточного перегляду запису щоб була можливість продовжувати редагувати
                write_db(db)
                clear()
                edit_record_by_id(id)
                return
    record = get_record_by_value("id", id)
    print_table([record])
    menu_options = []
    for key in employee_records_keys:
        menu_options.append((key, edit_record_by_id, id, key))
    if not show_menu(menu_options):
        return

def is_id_exist(id):
    # Перевірка на існування ID
    db = get_db()
    for record in db:
        if record["id"] == id:
            return True
    return False

def is_employee_key_exist(key):
    # Перевірка на існування ключа в списку ключів працівника
    return key in keys_types.keys()

def show_edit_records():
    # Меню зміни даних користувача
    clear()
    print_table()
    while True:
        id = input_and_convert_to("Введіть ID запису для редагування: ", "+int")
        if is_id_exist(id):
            break
        else:
            print(style_error_text("Такого ID не існує!"))
    clear()
    edit_record_by_id(id)
    
def show_table_report():
    # Меню подання важливих даних
    clear()
    records_list = get_db()
    sorted_records = sort_records("department", records_list)
    info_about_dapartments = get_info_about_dapartments()
    summary_list = make_table_list(["summary_count_employees", "summary_capital"], [[len(get_db()), sum_by_key("salary")]])
    print_table(sorted_records)
    print_table(info_about_dapartments, max_width=30)
    print_table(summary_list, max_width=40)
    press_enter_to_continue()




def make_style(code):
    # Робить стиль відносно коду
    return f"\033[{code}m"

# Кольори по назвам
colors = ["black", "red", "green", "yellow", "blue", "purple", "aqua", "white"]
font_colors = {}
bg_colors = {}
# Декорація тексту
font_decors = {
    "clear" : make_style(0),
    "bold" : make_style(1),
    "italic" : make_style(3),
    "underline" : make_style(4)
    }
decors = list(font_decors)

# Створення звичайних кольорів
for i in range(len(colors)):
    font_colors[colors[i]] = make_style(30 + i)
    bg_colors[colors[i]] = make_style(40 + i)

light_colors = ["grey"]
# Створення світлих кольорів
colors.extend(light_colors)
for i in range(len(light_colors)):
    font_colors[light_colors[i]] = make_style(90 + i)
    bg_colors[light_colors[i]] = make_style(100 + i)

# Таличні символи
table_chrs = {
    # hor - horizontal
    # ver - vertical
    # u - up
    # d - down
    # l - left
    # r - right
    # c - cross
    
    
    # Прямі лінії
    "hor": chr(9552),
    "ver": chr(9553),

    # Кутки
    "ul": chr(9556),
    "ur": chr(9559),
    "dl": chr(9562),
    "dr": chr(9565),

    # Лініх з поворотами
    "lc": chr(9568),
    "rc": chr(9571),
    "uc": chr(9574),
    "dc": chr(9577),
    "cc": chr(9580)
}

program_name_text =r''' _   _______       _                       _                        _   
| | | | ___ \     | |                     | |                      | |  
| |_| | |_/ /   __| | ___ _ __   __ _ _ __| |_ _ __ ___   ___ _ __ | |_ 
|  _  |    /   / _` |/ _ | '_ \ / _` | '__| __| '_ ` _ \ / _ | '_ \| __|
| | | | |\ \  | (_| |  __| |_) | (_| | |  | |_| | | | | |  __| | | | |_ 
\_| |_\_| \_|  \__,_|\___| .__/ \__,_|_|   \__|_| |_| |_|\___|_| |_|\__|
                         | |                                            
                         |_|                                            '''
    
text_button_for_main_menu = "(Ctrl + C - Головне меню)"
    
db_file_path = "database.json"

# Ключі працівників
employee_records_keys = [
    "id",
    "name",
    "midname",
    "lastname",
    "age",
    "department",
    "position",
    "phone_number",
    "salary"
]

# Ключи з їхніми типами даних
keys_types = {
    "id" : "+int",
    "name" : "str",
    "midname" : "str",
    "lastname" : "str",
    "age" : "age",
    "department" : "str",
    "position" : "str",
    "phone_number" : "tel",
    "salary" : "+float",
    "capital" : "+float",
    "count_employees" : "+int"
}

employee_record_keys_with_types = {key: keys_types[key] for key in employee_records_keys}

# Головні опції
main_menu_options = [
    ("Створити нову базу даних", show_create_new_empty_db),
    ("Додати записи", show_add_few_records_to_db),
    ("Редагувати записи", show_edit_records),
    ("Видалити запис", show_delete_record),
    ("Показити записи", show_db_records),
    ("Сортувати записи", show_db_sorted_records),
    ("Фільтрувати записи", show_db_filtered_records),
    ("Знайти записи за ПІБ", show_search_by_PIB),
    ("Інформація по відділам", show_departments_info),
    ("Працівники по відділам", show_department_employees),
    ("Табличний звіт", show_table_report),
]

# Цикл програми який повторюється доки користувач не вибере "Вихід"
while True:
    try:
        if not main_menu(): # Меню керування програмою
            break
    except KeyboardInterrupt: # KeyboardInterrupt використаний як повернення до головного меню
        continue