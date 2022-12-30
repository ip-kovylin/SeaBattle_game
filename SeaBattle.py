from random import randint


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за пределы поля!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "В данную клетку уже был совершен выстрел! Есть еще одна попытка!"

class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class Ship:
    def __init__(self, bow, len, o):
        self.bow = bow
        self.len = len
        self.o = o
        self.lives = len

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.len):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = [[" "] * size for i in range(size)]

        self.busy = []
        self.ships = []

    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "*"
                    self.busy.append(cur)

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "T"
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        a = self.board.field.__len__()
        d = Dot(randint(0, a-1), randint(0, a-1))
        print(f"Компьютер выстрелил в координату ({d.x + 1}, {d.y + 1})")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Введите координаты x y: ").split()

            if len(cords) != 2:
                print("Введите координаты в формате 'x' 'y' (x - строка, y - cтолбец)")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print("Введите целые числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        self.co_hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print('Добро пожаловать в игру "Морской бой"! ')
        print("-------------------")
        print("Краткие правила игры:")
        print("1. Формат ввода: x y, где x - номер строки, y - номер столбца")
        print("2. Не стреляем за пределы поля!")
        print("3. Не стреляем в одну и ту же клетку несколько раз!")

    def __str__(self):
        res = ""
        res0 = ""
        for i in range(self.size):
            if i == 0:
                res0 += "  |" + f" {i+1} "
            else:
                res0 += "|" + f" {i + 1} "
            if i == self.size - 1:
                for j in range(self.size):
                    if j == 0:
                        res0 += "| \t\t  |" + f" {j + 1} "
                    else:
                        res0 += "|" + f" {j + 1} "
                    if j == self.size - 1:
                        res0 += "|"
                        print(res0)
        for i in range(self.size):
            res1, res2 = "", ""
            res1 = f"{i + 1} | " + " | ".join(self.us.board.field[i]) + " | " + f"{i + 1}"
            res2 = f"\t\t{i + 1} | " + " | ".join(self.ai.board.field[i]) + " | " + f"{i + 1}"
            if self.co_hid:
                res2 = res2.replace("■", " ")
                res = res1 + res2
                print(res)
            else:
                res = res1 + res2
                print(res)
        return res0

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print(" " * 1 * self.size + "Поле пользователя" + " " * 3 * self.size + " Поле компьютера")
            print(self.__str__())
            if num % 2 == 0:
                print("-" * 20)
                print("Ваш ход.", end=' ')
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ход компьютера.", end=" ")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Вы выиграли!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

    def end(self):
        return 'Спасибо за игру! Возвращайтесь еще!'

g = Game()
g.start()
