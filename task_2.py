import logging
import time
from colorama import init, Fore
from tabulate import tabulate

init(autoreset=True)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s"
)
logger = logging.getLogger(__name__)


class Teacher:
    """
    Клас Teacher з полями:
    - first_name, last_name (ПІ)
    - age (вік)
    - email (електронна адреса)
    - can_teach_subjects (множина предметів, які може викладати)
    - assigned_subjects (множина предметів, призначених алгоритмом)
    """

    def __init__(self, first_name, last_name, age, email, can_teach_subjects):
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.email = email
        self.can_teach_subjects = set(can_teach_subjects)
        self.assigned_subjects = set()

    def __repr__(self):
        return f"Teacher({self.first_name}, {self.last_name}, age={self.age})"


class Scheduler:
    """
    Клас Scheduler реалізує жадібний алгоритм для задачі покриття множини предметів
    мінімальною кількістю викладачів.
    """

    def __init__(self, subjects, teachers):
        """
        :param subjects: (set) множина предметів, які треба покрити
        :param teachers: (list) список об'єктів Teacher
        """
        self.subjects = set(subjects)
        self.teachers = list(teachers)

    def create_schedule(self):
        """
        Жадібний алгоритм для покриття множини предметів:
        1. Поки є непокриті предмети:
           - шукаємо викладача, який покриває найбільше з непокритих предметів
           - за умови однакового покриття обираємо наймолодшого
           - якщо не знайшлося викладача з новим покриттям, повертаємо None
        2. Призначаємо йому предмети, які він може викладати і які ще непокриті
        3. Прибираємо ці предмети з непокритих
        4. Прибираємо викладача зі списку доступних (бо він уже "залучений")
        5. Продовжуємо, поки не покриємо всі предмети
        :return: (list[Teacher]) список призначених викладачів з оновленими assigned_subjects
                 або None, якщо покрити всі предмети неможливо
        """
        uncovered_subjects = set(self.subjects)
        chosen_teachers = []
        available_teachers = self.teachers[:]

        while uncovered_subjects:
            best_teacher = None
            best_coverage_size = 0

            for teacher in available_teachers:
                coverage = teacher.can_teach_subjects & uncovered_subjects
                coverage_size = len(coverage)

                # Жадібний вибір: найбільше покриття
                if coverage_size > best_coverage_size:
                    best_teacher = teacher
                    best_coverage_size = coverage_size
                elif coverage_size == best_coverage_size and coverage_size > 0:
                    # Якщо є "нічия", обираємо молодшого
                    if best_teacher and teacher.age < best_teacher.age:
                        best_teacher = teacher

            # Якщо ніхто не може покрити жодного нового предмета
            if best_teacher is None or best_coverage_size == 0:
                return None

            # Призначаємо предмети цьому викладачеві
            subjects_to_assign = best_teacher.can_teach_subjects & uncovered_subjects
            best_teacher.assigned_subjects = subjects_to_assign

            # Оновлюємо множину непокритих
            uncovered_subjects -= subjects_to_assign

            # Видаляємо вибраного викладача з подальшого розгляду
            available_teachers.remove(best_teacher)
            chosen_teachers.append(best_teacher)

        return chosen_teachers


class SetCoverSchedulerDemo:
    """
    Клас-демонстрація виконує кілька тестових сценаріїв:
    1. "Успішний" — коли всі предмети можна покрити
    2. "Неуспішний" — коли частина предметів лишається непокритою
    """

    def measure_time(self, scheduler):
        """
        Вимірює час роботи методу create_schedule().
        :param scheduler: (Scheduler) екземпляр
        :return: (elapsed_time, schedule_result)
        """
        t0 = time.time()
        schedule = scheduler.create_schedule()
        t1 = time.time()
        elapsed_time = t1 - t0
        return elapsed_time, schedule

    def run_test_scenario(self, scenario_name, subjects, teachers):
        """
        Запускає один тестовий сценарій з переданими предметами та викладачами
        :param scenario_name: (str) ім'я сценарію для логування
        :param subjects: (set) множина предметів
        :param teachers: (list) список Teacher
        """
        logger.info(Fore.CYAN + f"=== Початок сценарію: {scenario_name} ===")

        scheduler = Scheduler(subjects, teachers)
        elapsed_time, schedule = self.measure_time(scheduler)

        if schedule is None:
            logger.error(
                Fore.RED
                + f"Сценарій [{scenario_name}]: Неможливо покрити всі предмети!"
            )
        else:
            logger.info(
                Fore.GREEN
                + f"Сценарій [{scenario_name}]: Розклад побудовано успішно! (За {elapsed_time:.6f} сек)"
            )
            # Підготуємо таблицю для виводу
            table_data = []
            for teacher in schedule:
                table_data.append(
                    [
                        f"{teacher.first_name} {teacher.last_name}",
                        teacher.age,
                        teacher.email,
                        (
                            ", ".join(teacher.assigned_subjects)
                            if teacher.assigned_subjects
                            else "-"
                        ),
                    ]
                )

            table_headers = ["Викладач", "Вік", "Email", "Призначені предмети"]
            table_str = tabulate(
                table_data, headers=table_headers, tablefmt="github", showindex=True
            )

            logger.info(Fore.CYAN + "=== РЕЗУЛЬТАТИ: ===")
            print(Fore.GREEN + table_str)

        logger.info(Fore.CYAN + f"=== Завершення сценарію: {scenario_name} ===\n")

    def run_all_tests(self):
        """
        Запускає два сценарії:
          1. Успішний.
          2. Неуспішний (коли бодай один предмет неможливо покрити)
        """

        # Сценарій 1: Успішний
        subjects_ok = {"Математика", "Фізика", "Хімія", "Інформатика", "Біологія"}
        teachers_ok = [
            Teacher(
                "Олександр",
                "Іваненко",
                45,
                "o.ivanenko@example.com",
                {"Математика", "Фізика"},
            ),
            Teacher(
                "Марія",
                "Петренко",
                38,
                "m.petrenko@example.com",
                {"Хімія"},
            ),
            Teacher(
                "Сергій",
                "Коваленко",
                50,
                "s.kovalenko@example.com",
                {"Інформатика", "Математика"},
            ),
            Teacher(
                "Наталія",
                "Шевченко",
                29,
                "n.shevchenko@example.com",
                {"Біологія", "Хімія"},
            ),
            Teacher(
                "Дмитро",
                "Бондаренко",
                35,
                "d.bondarenko@example.com",
                {"Фізика", "Інформатика"},
            ),
            Teacher(
                "Олена",
                "Гриценко",
                42,
                "o.grytsenko@example.com",
                {"Біологія"},
            ),
        ]
        self.run_test_scenario("Успішний сценарій", subjects_ok, teachers_ok)

        # Сценарій 2: Неуспішний (зробимо так, щоб "Біологія" була недоступна)
        subjects_fail = {"Математика", "Фізика", "Хімія", "Інформатика", "Біологія"}
        teachers_fail = [
            Teacher(
                "Олександр",
                "Іваненко",
                45,
                "o.ivanenko@example.com",
                {"Математика", "Фізика"},
            ),
            Teacher(
                "Марія",
                "Петренко",
                38,
                "m.petrenko@example.com",
                {"Хімія"},
            ),
            Teacher(
                "Сергій",
                "Коваленко",
                50,
                "s.kovalenko@example.com",
                {"Інформатика", "Математика"},
            ),
            Teacher(
                "Дмитро",
                "Бондаренко",
                35,
                "d.bondarenko@example.com",
                {"Фізика", "Інформатика"},
            ),
        ]
        self.run_test_scenario("Неуспішний сценарій", subjects_fail, teachers_fail)


def main():
    demo = SetCoverSchedulerDemo()
    demo.run_all_tests()


if __name__ == "__main__":
    main()
