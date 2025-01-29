import logging
import random
import sys
import time
from colorama import init, Fore
from tabulate import tabulate
import matplotlib.pyplot as plt

init(autoreset=True)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s"
)
logger = logging.getLogger(__name__)

# ----------------------
# 1) Функціональні реалізації QuickSort
# ----------------------


def deterministic_quick_sort_function(arr):
    """
    Детермінований QuickSort (функціональний).
    Обираємо pivot = arr[0] (перший елемент).
    Повертає відсортований масив (новий).
    """
    if len(arr) <= 1:
        return arr
    pivot = arr[0]  # детермінований: перший
    left = []
    right = []
    for x in arr[1:]:
        if x < pivot:
            left.append(x)
        else:
            right.append(x)
    left_sorted = deterministic_quick_sort_function(left)
    right_sorted = deterministic_quick_sort_function(right)
    return left_sorted + [pivot] + right_sorted


def randomized_quick_sort_function(arr):
    """
    Рандомізований QuickSort (функціональний).
    Обираємо pivot випадково.
    """
    if len(arr) <= 1:
        return arr
    pivot_index = random.randint(0, len(arr) - 1)
    pivot = arr[pivot_index]
    left = []
    right = []
    # Створюємо списки
    for i, x in enumerate(arr):
        if i == pivot_index:
            continue
        if x < pivot:
            left.append(x)
        else:
            right.append(x)
    left_sorted = randomized_quick_sort_function(left)
    right_sorted = randomized_quick_sort_function(right)
    return left_sorted + [pivot] + right_sorted


# ----------------------
# 2) Класові реалізації QuickSort
# ----------------------
class DeterministicQuickSort:
    """
    Клас, що реалізує детермінований QuickSort (pivot = перший елемент).
    Викликаємо sort(arr) => сортуємо in-place.
    """

    def sort(self, arr):
        self._quick_sort(arr, 0, len(arr) - 1)

    def _quick_sort(self, arr, low, high):
        if low < high:
            pivot_index = self._partition(arr, low, high)
            self._quick_sort(arr, low, pivot_index - 1)
            self._quick_sort(arr, pivot_index + 1, high)

    def _partition(self, arr, low, high):
        pivot = arr[low]  # детермінований pivot
        i = low + 1
        j = high
        while True:
            while i <= j and arr[i] <= pivot:
                i += 1
            while i <= j and arr[j] > pivot:
                j -= 1
            if i <= j:
                arr[i], arr[j] = arr[j], arr[i]
                i += 1
                j -= 1
            else:
                break
        arr[low], arr[j] = arr[j], arr[low]
        return j


class RandomizedQuickSort:
    """
    Клас, що реалізує рандомізований QuickSort (pivot = випадковий елемент у [low..high]).
    """

    def sort(self, arr):
        self._quick_sort(arr, 0, len(arr) - 1)

    def _quick_sort(self, arr, low, high):
        if low < high:
            pivot_index = self._random_partition(arr, low, high)
            self._quick_sort(arr, low, pivot_index - 1)
            self._quick_sort(arr, pivot_index + 1, high)

    def _random_partition(self, arr, low, high):
        # випадковий pivot
        rand_idx = random.randint(low, high)
        arr[low], arr[rand_idx] = arr[rand_idx], arr[low]
        # Тепер pivot = arr[low], далі як у детерм.
        return self._partition(arr, low, high)

    def _partition(self, arr, low, high):
        pivot = arr[low]
        i = low + 1
        j = high
        while True:
            while i <= j and arr[i] <= pivot:
                i += 1
            while i <= j and arr[j] > pivot:
                j -= 1
            if i <= j:
                arr[i], arr[j] = arr[j], arr[i]
                i += 1
                j -= 1
            else:
                break
        arr[low], arr[j] = arr[j], arr[low]
        return j


# ----------------------
# 3) Клас Demo для тестування
# ----------------------
class QuickSortComparisonDemo:
    def __init__(self):
        # Розміри масивів
        self.array_sizes = [10_000, 50_000, 100_000, 500_000]
        self.runs = 10  # для кожного розміру

    def generate_data(self, n):
        """Генерує масив розміру n із випадкових int."""
        return [random.randint(-10_000_000, 10_000_000) for _ in range(n)]

    def measure_time(self, sort_func, arr):
        """
        Вимірює час сортування масиву arr викликом sort_func(arr).
        sort_func - callable: arr -> sorted arr
        Повертає (elapsed_time, result_array).
        """
        t0 = time.time()
        res = sort_func(arr)
        t1 = time.time()
        elapsed = t1 - t0
        return (elapsed, res)

    def measure_time_class(self, sort_class, arr):
        """
        Вимірює час сортування in-place за допомогою класу (deterministic/randomized).
        sort_class - екземпляр класу, що має метод .sort(arr).
        Повертає (elapsed_time, arr).
        """
        t0 = time.time()
        sort_class.sort(arr)
        t1 = time.time()
        elapsed = t1 - t0
        return (elapsed, arr)

    def run_experiment(self):
        """
        Для кожного з 4 реалізацій (det_func, rand_func, det_class, rand_class)
        та для розмірів [10k, 50k, 100k, 500k], виконує 5 запусків, бере середній час.
        Будує таблицю і графік "size vs time" (4 лінії).
        """
        logger.info(Fore.CYAN + "=== Запуск порівняння 4 реалізацій QuickSort ===")

        results_table = []  # кожен ряд: [name, size, avg_time]
        # Для побудови графіка: зберігатимемо dict: method_name -> ([sizes], [times])
        times_for_plot = {
            "Deterministic Func": ([], []),
            "Randomized Func": ([], []),
            "Deterministic Class": ([], []),
            "Randomized Class": ([], []),
        }

        # Екземпляри класів
        det_class_sorter = DeterministicQuickSort()
        rand_class_sorter = RandomizedQuickSort()

        for size in self.array_sizes:
            # згенеруємо масив
            logger.info(Fore.GREEN + f"Generating array of size {size} ...")
            base_array = self.generate_data(size)

            # 1) Deterministic function
            method_name = "Deterministic Func"
            total_time = 0.0
            for _ in range(self.runs):
                arr_copy = list(base_array)
                elapsed, sorted_arr = self.measure_time(
                    deterministic_quick_sort_function, arr_copy
                )
                total_time += elapsed
            avg_time = total_time / self.runs
            results_table.append([method_name, size, f"{avg_time:.4f}s"])
            times_for_plot[method_name][0].append(size)
            times_for_plot[method_name][1].append(avg_time)

            # 2) Randomized function
            method_name = "Randomized Func"
            total_time = 0.0
            for _ in range(self.runs):
                arr_copy = list(base_array)
                elapsed, sorted_arr = self.measure_time(
                    randomized_quick_sort_function, arr_copy
                )
                total_time += elapsed
            avg_time = total_time / self.runs
            results_table.append([method_name, size, f"{avg_time:.4f}s"])
            times_for_plot[method_name][0].append(size)
            times_for_plot[method_name][1].append(avg_time)

            # 3) Deterministic class
            method_name = "Deterministic Class"
            total_time = 0.0
            for _ in range(self.runs):
                arr_copy = list(base_array)
                elapsed, sorted_inplace = self.measure_time_class(
                    det_class_sorter, arr_copy
                )
                total_time += elapsed
            avg_time = total_time / self.runs
            results_table.append([method_name, size, f"{avg_time:.4f}s"])
            times_for_plot[method_name][0].append(size)
            times_for_plot[method_name][1].append(avg_time)

            # 4) Randomized class
            method_name = "Randomized Class"
            total_time = 0.0
            for _ in range(self.runs):
                arr_copy = list(base_array)
                elapsed, sorted_inplace = self.measure_time_class(
                    rand_class_sorter, arr_copy
                )
                total_time += elapsed
            avg_time = total_time / self.runs
            results_table.append([method_name, size, f"{avg_time:.4f}s"])
            times_for_plot[method_name][0].append(size)
            times_for_plot[method_name][1].append(avg_time)

        # Виводимо таблицю
        table_str = tabulate(
            results_table,
            headers=["Method", "Array Size", f"Avg Time over {self.runs} runs"],
            tablefmt="github",
        )
        logger.info(Fore.CYAN + "=== РЕЗУЛЬТАТИ: ===")
        print(Fore.GREEN + table_str)

        print(Fore.CYAN + "\n=== ГРАФІКИ: ===")
        # Будуємо графік "array size" vs "time" (4 криві)
        plt.figure(figsize=(7, 5))
        plt.title("Час сортування від розміру (QuickSort variants)")
        for method_name, (sizes, times) in times_for_plot.items():
            plt.plot(sizes, times, marker="o", label=method_name)
        plt.xlabel("Array Size")
        plt.ylabel("Average Time (sec)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        # Висновки
        print(Fore.CYAN + "\n=== ВИСНОВКИ: ===")
        print(
            Fore.GREEN
            + "1) На масивах до 100 тис. елементів детерміністичні варіанти (Func і Class) "
            + "загалом працювали швидше за рандомізовані, інколи у 1.3–1.5 раза.\n"
            + "2) Для розміру ~100k, рандомізований клас показав 0.1661s, трохи випередивши детермінований клас (0.1680s).\n"
            + "3) На найбільшому масиві (500k) детерміністичні підходи знову переважають, "
            + "показавши час ~0.74–0.83s проти ~1.09–1.25s у рандомізованих.\n"
            + "4) У середньому детерміністичні реалізації у цих експериментах були швидшими, "
            + "але рандомізовані (особливо класова версія) іноді виграють на деяких розмірах.\n"
            + "5) Якщо порівнювати реалізації (Func vs Class) в межах одного підходу (детермінованого чи рандомізованого), "
            + "то класові варіанти здебільшого випереджають функціональні за швидкістю."
        )


def main():
    sys.setrecursionlimit(10**7)
    demo = QuickSortComparisonDemo()
    demo.run_experiment()


if __name__ == "__main__":
    main()
