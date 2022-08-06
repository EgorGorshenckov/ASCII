from PIL import Image
import requests
import time
import os

GRADIENT: str = " .:!/r(l1Z9$@"
GRADIENT_NUM: int = len(GRADIENT)


def get_terminal_size():
    try:
        return tuple(map(lambda x: int(x), os.popen('stty size', 'r').read().split()))[::-1]
    except OSError as ex:
        if ex is OSError:
            exit('''
Простите, произошла ошибка.
Вам требуется выполнить данное действие в предустановленном терминале терминале компьютера,
а не в программном.''')
        else:
            print('Простите, возникла ошибка', ex.__class__.__name__)
            exit()


class IMG:
    def __init__(self, internet_or_computer: bool, url: str):
        self.url: str = url

        if internet_or_computer:
            self.path = self.get_path()
        else:
            self.path = self.url

        img = Image.open(self.path)
        self.pix = img.load()
        self.size = img.size
        self.t_size = get_terminal_size()

        self.quality_x = 1
        self.quality_y = 2

        if self.size[1] > self.t_size[1]:
            self.quality_y = self.size[1] // self.t_size[1]
            self.quality_x = self.quality_y // 2
        if self.size[0] // self.quality_x > self.t_size[0]:
            self.quality_x = self.size[0] // self.t_size[0]
            self.quality_y = self.quality_y * 2

    def get_path(self):
        with open(f'{os.path.abspath(".")}/photo/{self.photo_name()}', 'wb') as file:
            ph = requests.get(self.url).content
            file.write(ph)
        return f'{os.path.abspath(".")}/photo/{self.photo_name()}'

    def __str__(self) -> str:
        returner = []
        for y in range(self.size[1]):
            r = ''
            if not y % self.quality_y:
                for x in range(self.size[0]):
                    if not x % self.quality_x:
                        r += GRADIENT[self.symbol(sum(self.pix[x, y]) / 3)]

                if len(r) < self.t_size[0]:
                    r = ' ' * ((self.t_size[0] - len(r)) // 2) + r + ' ' * ((self.t_size[0] - len(r)) // 2)
                returner.append(r[:self.t_size[0]])

        if len(returner) < self.t_size[1]:
            const = self.t_size[1] - len(returner)
            senter = [' ' * self.t_size[0]]
            returner = senter * (const // 2 + const % 2) + returner + senter * (const // 2)
        return '\n'.join(returner[:self.t_size[1]])

    def photo_name(self):
        return self.url.split('/')[-1]

    @staticmethod
    def symbol(bright):
        for i in range(GRADIENT_NUM):
            if bright <= (i + 1) * 255 / GRADIENT_NUM:
                return i
        return 0


def main():
    try:
        i = IMG(bool(int(input('Комп - 0, Интернет - 1: '))), input('Введите ссылку / путь: '))
        t = time.time()
        print(i)
        print(time.time() - t)
    except Exception as ex:
        print('\n' * 2 + '+' + '-' * len(ex.__str__()) + '+')
        print('|' + ex.__str__() + '|')
        print('+' + '-' * len(ex.__str__()) + '+')


if __name__ == '__main__':
    main()
