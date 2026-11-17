import json
import os
from datetime import date, datetime

import matplotlib.pyplot as plt

DATA_FILE = "tracker_data.json"
REPORT_FILE = "report.txt"
CHART_FILE = "mood_chart.png"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def ask_int(prompt, low, high):
    while True:
        text = input(prompt).strip()
        if text.isdigit() and low <= int(text) <= high:
            return int(text)
        print(f"Нужно целое число от {low} до {high}, попробуйте ещё раз.")


def ask_date():
    while True:
        text = input("Дата (ГГГГ-ММ-ДД, Enter - сегодня): ").strip()
        if text == "":
            return str(date.today())
        try:
            datetime.strptime(text, "%Y-%m-%d")
            return text
        except ValueError:
            print("Неверный формат даты, пример: 2026-11-16")


def get_day(data, day):
    if day not in data:
        data[day] = {"mood": None, "note": "", "pills": []}
    return data[day]


def mood_smile(mood):
    if mood is None:
        return "  -  "
    if mood <= 3:
        return ":(  "
    elif mood <= 7:
        return ":|  "
    else:
        return ":)  "


def add_mood(data):
    day = ask_date()
    mood = ask_int("Оцените настроение от 1 до 10: ", 1, 10)
    note = input("Короткая заметка (можно пропустить): ").strip()
    record = get_day(data, day)
    record["mood"] = mood
    record["note"] = note.capitalize()
    save_data(data)
    print(f"Записано: {day}, настроение {mood}/10")


def add_pills(data):
    day = ask_date()
    text = input("Какие таблетки приняли? (через запятую): ")
    names = text.split(",")
    record = get_day(data, day)

    taken = set(record["pills"])
    for name in names:
        name = name.strip().title()
        if name != "":
            taken.add(name)

    record["pills"] = sorted(taken)
    save_data(data)
    if record["pills"]:
        print("Приём отмечен: " + ", ".join(record["pills"]))
    else:
        print("Вы ничего не ввели.")


def show_history(data):
    if not data:
        print("Записей пока нет.")
        return
    print("\n  Дата        Настр.   Таблетки / заметка")
    print("-" * 55)
    for day in sorted(data):
        rec = data[day]
        mood = rec["mood"] if rec["mood"] is not None else "-"
        pills = ", ".join(rec["pills"]) if rec["pills"] else "не отмечены"
        print(f"  {day}  {str(mood):>3} {mood_smile(rec['mood'])} {pills}")
        if rec["note"]:
            print(f"                       заметка: {rec['note']}")


def show_stats(data):
    moods = {}
    pill_count = {}
    days_without_pills = []

    for day, rec in data.items():
        if rec["mood"] is not None:
            moods[day] = rec["mood"]
            if not rec["pills"]:
                days_without_pills.append(day)
        for pill in rec["pills"]:
            pill_count[pill] = pill_count.get(pill, 0) + 1

    if not moods:
        print("Недостаточно данных для статистики.")
        return

    average = sum(moods.values()) / len(moods)
    best_day = max(moods, key=moods.get)
    worst_day = min(moods, key=moods.get)

    print("\n--- Статистика ---")
    print(f"Дней с записью настроения: {len(moods)}")
    print(f"Среднее настроение: {average:.1f}/10")
    print(f"Лучший день: {best_day} ({moods[best_day]}/10)")
    print(f"Худший день: {worst_day} ({moods[worst_day]}/10)")

    if pill_count:
        print("Принято таблеток:")
        for pill, count in pill_count.items():
            print(f"  {pill}: {count} дн.")
    if days_without_pills:
        print("Дни без отметки о таблетках: " + ", ".join(sorted(days_without_pills)))

    if average < 4:
        print("Настроение в среднем низкое. Если это длится долго - "
              "стоит поговорить с близкими или врачом.")


def plot_mood(data):
    days = [d for d in sorted(data) if data[d]["mood"] is not None]
    if len(days) < 2:
        print("Для графика нужно минимум 2 записи настроения.")
        return
    moods = [data[d]["mood"] for d in days]

    plt.figure(figsize=(9, 4))
    plt.plot(days, moods, marker="o", color="tab:blue", label="Настроение")

    pill_days = [d for d in days if data[d]["pills"]]
    pill_moods = [data[d]["mood"] for d in pill_days]
    plt.scatter(pill_days, pill_moods, color="red", s=90, zorder=3,
                label="Приём таблеток")

    plt.ylim(0, 10.5)
    plt.title("График настроения")
    plt.xlabel("Дата")
    plt.ylabel("Настроение (1-10)")
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(CHART_FILE)
    print(f"График сохранён в файл {CHART_FILE}")
    plt.show()


def export_report(data):
    if not data:
        print("Нечего выгружать - записей нет.")
        return
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("ОТЧЁТ ПО ТРЕКЕРУ НАСТРОЕНИЯ\n")
        f.write("=" * 40 + "\n")
        for day in sorted(data):
            rec = data[day]
            mood = rec["mood"] if rec["mood"] is not None else "нет данных"
            pills = ", ".join(rec["pills"]) if rec["pills"] else "не отмечены"
            f.write(f"{day} | настроение: {mood} | таблетки: {pills}\n")
            if rec["note"]:
                f.write(f"    заметка: {rec['note']}\n")
    print(f"Отчёт сохранён в файл {REPORT_FILE}")


def print_menu():
    print("\n=== ТРЕКЕР НАСТРОЕНИЯ ===")
    print("1 - Записать настроение")
    print("2 - Отметить приём таблеток")
    print("3 - Показать историю")
    print("4 - Статистика")
    print("5 - График настроения")
    print("6 - Выгрузить отчёт в файл")
    print("0 - Выход")


def main():
    data = load_data()
    actions = {
        "1": add_mood,
        "2": add_pills,
        "3": show_history,
        "4": show_stats,
        "5": plot_mood,
        "6": export_report,
    }
    running = True
    while running:
        print_menu()
        choice = input("Выберите пункт: ").strip()
        if choice == "0":
            print("До свидания! Берегите себя.")
            running = False
        elif choice in actions:
            actions[choice](data)
        else:
            print("Нет такого пункта меню.")


if __name__ == "__main__":
    main()
