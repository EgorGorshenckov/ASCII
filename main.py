from PIL import Image
from inspect import getsourcefile
import requests
import time
import os
import cv2


# Яркость
GRADIENT: str = " .:!/r(l1Z9$@"
# Количество возможных яркостей
GRADIENT_NUM: int = len(GRADIENT)
# Име папки в которой находится файл с репозиторием
FOLDER_AP = os.path.abspath(getsourcefile(lambda: 0) + "/..")


def error_printer(ex: Exception):
    """ Красивый вывод ошибок """
    returner = '\n' * 2 + '+' + '-' * len(ex.__str__()) + '+\n'
    returner += '|' + ex.__str__() + '|\n'
    returner += '+' + '-' * len(ex.__str__()) + '+\n'
    print(returner)


def get_terminal_size() -> tuple[int]:
    """
    Получение размеров терминала в символах
    :return (столбцы, строки):
    """
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

    """ Класс изображения, для превращения в символы и вывода в терминал """

    def __init__(self, internet_or_computer: bool, url: str):
        self.url: str = url

        if internet_or_computer:
            self.path: str = self.get_path()
        else:
            self.path: str = self.url

        img = Image.open(self.path)
        self.pix = img.load()
        self.size = img.size
        self.t_size: tuple[int] = get_terminal_size()

        # В случае плохого вывода изображения поиграйтесь с quality_x и quality_y
        # !! quality_x / quality_y = 0.5 !!
        self.quality_x: int = 1
        self.quality_y: int = 2

        if self.size[1] > self.t_size[1]:
            self.quality_y = self.size[1] // self.t_size[1]
            self.quality_x = self.quality_y // 2
        if self.size[0] // self.quality_x > self.t_size[0]:
            self.quality_x = self.size[0] // self.t_size[0]
            self.quality_y = self.quality_y * 2

    def get_path(self) -> str:
        """
        В случае загрузки изображения из интернета,
        метод загружает изображение в отдельный файл и возвращает путь до него
        :return [абсолютный путь до файла]:
        """
        with open(f'{FOLDER_AP}/photo/{self.photo_name()}', 'wb') as file:
            ph = requests.get(self.url).content
            file.write(ph)
        return f'{FOLDER_AP}/photo/{self.photo_name()}'

    def __str__(self) -> str:
        """
        Главный метод для вывода изображения в консоль
        :return [изменённое изображение в формате ASCII]:
        """
        returner = []
        for y in range(self.size[1]):
            r = ''
            if not y % self.quality_y:
                for x in range(self.size[0]):
                    if not x % self.quality_x:
                        r += GRADIENT[self.symbol(sum(self.pix[x, y]) / 3)]

                returner.append(self._center_Ox(r)[:self.t_size[0]])

        return '\n'.join(self._center_Oy(returner)[:self.t_size[1]])

    def _center_Ox(self, r: str):
        """
        Метод центровки строк
        :param [строка]:
        :return:
        """
        if len(r) < self.t_size[0]:
            return ' ' * ((self.t_size[0] - len(r)) // 2) + r + ' ' * ((self.t_size[0] - len(r)) // 2)
        return r

    def _center_Oy(self, returner: list[str]):
        """
        Метод центровки столбцов
        :param [изображение в формате ASCII]:
        :return:
        """
        if len(returner) < self.t_size[1]:
            const = self.t_size[1] - len(returner)
            senter = [' ' * self.t_size[0]]
            return senter * (const // 2 + const % 2) + returner + senter * (const // 2)
        return returner

    def photo_name(self) -> str:
        """ Метод получения имени фотографии """
        return self.url.split('/')[-1]

    @staticmethod
    def symbol(bright):
        """ Метод определения яркости символа """
        for i in range(GRADIENT_NUM):
            if bright <= (i + 1) * 255 / GRADIENT_NUM:
                return i
        return 0


class MP4:

    """ Класс видио """

    def __init__(self, internet_or_computer: bool, url: str, FPS: int = 24):
        self.url: str = url

        if internet_or_computer:
            self.path = self.get_path()
        else:
            self.path = self.url

        self.timing: int = 0
        self.frames: list[IMG] = []
        self.FPS: int = min(60, FPS)
        self.saved_frame_name = 0

        self.redding()

    def redding(self):
        """  По-кадровое сохранение видио в файл 'video' """
        try:
            video_capture = cv2.VideoCapture(self.path)
            video_capture.set(cv2.CAP_PROP_FPS, self.FPS)
            os.mkdir(f'{FOLDER_AP}/video/{self.video_name()}')
            frame_count = video_capture.get(cv2.CAP_PROP_FRAME_COUNT)

            while video_capture.isOpened():
                frame_is_read, frame = video_capture.read()
                if frame_is_read:
                    cv2.imwrite(
                        f"{FOLDER_AP}/video/{self.video_name()}/{str(self.saved_frame_name)}.jpg",
                        frame)
                    self.saved_frame_name += 1
                elif self.saved_frame_name >= frame_count:
                    break
        except FileExistsError:
            self.saved_frame_name = len(os.listdir(f"{FOLDER_AP}/video/{self.video_name()}/"))

    def __str__(self) -> str:
        """ Покадровый вывод видео """
        video = []

        for i in range(self.saved_frame_name):
            video.append(IMG(False, f'{FOLDER_AP}/video/{self.video_name()}/{i}.jpg'))

        for i in video:
            print(i)
            time.sleep(1 / self.FPS)

        return 'Done'

    def video_name(self) -> str:
        """ Получение имени видео """
        return self.url.split('/')[-1].split('.')[0]

    def get_path(self) -> str:
        """ Загружает и возвращает путь до загруженого файла """
        import urllib.request
        fool_path = FOLDER_AP + '/loaded_videos/' + self.url.split('/')[-1]
        urllib.request.urlretrieve(self.url, fool_path)
        return fool_path


def main():
    try:
        i = MP4(False, input('Введите путь: '), int(input('FPS - не больше 30:')))
        t = time.time()
        print(i)
        print(time.time() - t)
    except Exception as ex:
        error_printer(ex)


if __name__ == '__main__':
    main()
