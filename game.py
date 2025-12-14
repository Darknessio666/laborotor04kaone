"""
Простая 2D-игра на tkinter без использования pygame.
Управление: W/A/S/D для движения, ESC для выхода.
"""

import tkinter as tk
from tkinter import messagebox


class Game:
    """Основной класс игры."""

    def __init__(self):
        """Инициализация игры."""
        self.root = tk.Tk()
        self.root.title("2D Game")
        self.root.resizable(False, False)

        # Карта игры (0 - пусто, 1 - стена, C - коллекционный предмет,
        # E - выход, P - игрок, X - патруль)
        self.map_data = [
            "111110001111111",
            "100000X00000001",
            "1000111111000",
            "1P0000E0000C0X",
            "111111111111111"
        ]

        # Параметры игры
        self.cell_size = 40
        self.moves = 0
        self.collected = 0
        self.total_collectibles = 0
        self.player_pos = None
        self.patrols = []
        self.game_over = False
        self.won = False
        self.animation_frame = 0  # Для анимации спрайтов

        # Найти позицию игрока и подсчитать коллекционные предметы
        self._initialize_map()

        # Создать canvas
        self.canvas = tk.Canvas(
            self.root,
            width=len(self.map_data[0]) * self.cell_size,
            height=len(self.map_data) * self.cell_size + 50,
            bg="lightblue"
        )
        self.canvas.pack()

        # Привязать события клавиатуры
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.focus_set()

        # Привязать закрытие окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Отобразить начальное состояние
        self.draw_map()
        self.update_move_counter()

        # Запустить анимацию
        self.animate()

    def _initialize_map(self):
        """Инициализировать карту и найти позиции элементов."""
        for y, row in enumerate(self.map_data):
            for x, cell in enumerate(row):
                if cell == 'P':
                    self.player_pos = [x, y]
                elif cell == 'C':
                    self.total_collectibles += 1
                elif cell == 'X':
                    self.patrols.append([x, y])

    def draw_map(self):
        """Отрисовать карту."""
        self.canvas.delete("all")

        # Отрисовка карты
        for y, row in enumerate(self.map_data):
            for x, cell in enumerate(row):
                x1 = x * self.cell_size
                y1 = y * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                if cell == '1':
                    # Стена - зеленый квадрат
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill="green", outline="darkgreen", width=2
                    )
                elif cell == '0':
                    # Пустое место - светло-серый
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill="lightgray", outline="gray"
                    )
                elif cell == 'C':
                    # Коллекционный предмет - желтая звезда с анимацией
                    center_x = x1 + self.cell_size // 2
                    center_y = y1 + self.cell_size // 2
                    # Пульсирующий размер для анимации
                    pulse = 1.0 + 0.2 * abs(
                        (self.animation_frame % 20) / 10.0 - 1.0
                    )
                    size = int(self.cell_size // 3 * pulse)
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill="lightgray", outline="gray"
                    )
                    self.canvas.create_polygon(
                        center_x, center_y - size,
                        center_x + size * 0.3, center_y - size * 0.3,
                        center_x + size, center_y,
                        center_x + size * 0.3, center_y + size * 0.3,
                        center_x, center_y + size,
                        center_x - size * 0.3, center_y + size * 0.3,
                        center_x - size, center_y,
                        center_x - size * 0.3, center_y - size * 0.3,
                        fill="yellow", outline="orange", width=2
                    )
                elif cell == 'E':
                    # Выход - коричневая арка
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill="lightgray", outline="gray"
                    )
                    self.canvas.create_arc(
                        x1 + 5, y1 + 5, x2 - 5, y2 - 5,
                        start=0, extent=180, fill="brown", outline="#654321"
                    )
                elif cell == 'X':
                    # Патруль - фиолетовый круг с анимацией
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill="lightgray", outline="gray"
                    )
                    center_x = x1 + self.cell_size // 2
                    center_y = y1 + self.cell_size // 2
                    # Пульсирующий размер для анимации
                    pulse = 1.0 + 0.15 * abs(
                        (self.animation_frame % 16) / 8.0 - 1.0
                    )
                    radius = int(12 * pulse)
                    self.canvas.create_oval(
                        center_x - radius, center_y - radius,
                        center_x + radius, center_y + radius,
                        fill="purple", outline="#4B0082"
                    )

        # Отрисовка игрока с анимацией
        if self.player_pos:
            px = self.player_pos[0] * self.cell_size
            py = self.player_pos[1] * self.cell_size
            center_x = px + self.cell_size // 2
            center_y = py + self.cell_size // 2

            # Легкая анимация дыхания для игрока
            breath = 1.0 + 0.05 * abs(
                (self.animation_frame % 30) / 15.0 - 1.0
            )

            # Тело игрока - коричневый круг
            body_size = int(10 * breath)
            self.canvas.create_oval(
                center_x - body_size, center_y - body_size,
                center_x + body_size, center_y + body_size,
                fill="tan", outline="brown", width=2
            )
            # Голова
            head_size = int(6 * breath)
            self.canvas.create_oval(
                center_x - head_size, center_y - 15,
                center_x + head_size, center_y - 3,
                fill="tan", outline="brown"
            )

        # Отображение счетчика ходов на экране (бонус)
        self.canvas.create_text(
            len(self.map_data[0]) * self.cell_size // 2,
            len(self.map_data) * self.cell_size + 25,
            text=f"MOVES: {self.moves}",
            font=("Arial", 16, "bold"),
            fill="white"
        )

    def update_move_counter(self):
        """Обновить счетчик ходов в консоли."""
        print(f"MOVES: {self.moves}")

    def can_move(self, new_x, new_y):
        """Проверить, можно ли переместиться в новую позицию."""
        if new_y < 0 or new_y >= len(self.map_data):
            return False
        if new_x < 0 or new_x >= len(self.map_data[new_y]):
            return False
        cell = self.map_data[new_y][new_x]
        return cell != '1'  # Нельзя идти в стену

    def move_player(self, dx, dy):
        """Переместить игрока."""
        if self.game_over or self.won:
            return

        new_x = self.player_pos[0] + dx
        new_y = self.player_pos[1] + dy

        if not self.can_move(new_x, new_y):
            return

        # Обновить позицию игрока на карте
        old_row = list(self.map_data[self.player_pos[1]])
        old_row[self.player_pos[0]] = '0'
        self.map_data[self.player_pos[1]] = ''.join(old_row)

        # Проверить, что находится в новой позиции
        new_cell = self.map_data[new_y][new_x]

        # Проверить столкновение с патрулем
        if new_cell == 'X':
            self.game_over = True
            self.draw_map()
            messagebox.showinfo("Game Over", "Вы коснулись патруля! Игра окончена.")
            self.root.quit()
            return

        # Собрать коллекционный предмет
        if new_cell == 'C':
            self.collected += 1
            new_row = list(self.map_data[new_y])
            new_row[new_x] = '0'
            self.map_data[new_y] = ''.join(new_row)

        # Проверить выход
        if new_cell == 'E':
            if self.collected >= self.total_collectibles:
                self.won = True
                self.draw_map()
                messagebox.showinfo("Победа!", "Вы собрали все предметы и достигли выхода!")
                self.root.quit()
                return
            else:
                messagebox.showinfo(
                    "Выход заблокирован",
                    f"Соберите все предметы! ({self.collected}/{self.total_collectibles})"
                )

        # Обновить позицию игрока
        self.player_pos = [new_x, new_y]
        self.moves += 1
        self.update_move_counter()
        self.draw_map()

    def on_key_press(self, event):
        """Обработка нажатий клавиш."""
        if event.keysym == 'Escape':
            self.root.quit()
            return

        if event.keysym.lower() == 'w':
            self.move_player(0, -1)
        elif event.keysym.lower() == 's':
            self.move_player(0, 1)
        elif event.keysym.lower() == 'a':
            self.move_player(-1, 0)
        elif event.keysym.lower() == 'd':
            self.move_player(1, 0)

    def on_closing(self):
        """Обработка закрытия окна."""
        self.root.quit()

    def animate(self):
        """Обновить анимацию спрайтов."""
        if not self.game_over and not self.won:
            self.animation_frame += 1
            self.draw_map()
            self.root.after(50, self.animate)  # Обновление каждые 50мс

    def run(self):
        """Запустить игру."""
        self.root.mainloop()


def main():
    """Главная функция."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
