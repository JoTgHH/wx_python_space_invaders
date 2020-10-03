import wx

""" Класс игры """
class Game(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title='My game, yo!')
        # Инициализация настроек
        self.settings = Settings()
        # Переменная счета игрока, а также помещения его в виджет панели, панель затем помещается в vbox.
        # Следом за панелью помещается кнопка 'Play!', вместо которой затем появится поле игры.
        self.score = 0
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.panel = wx.Panel(self, size=(self.settings.width, 50))
        self.score_table = wx.StaticText(self.panel)
        self.score_table.SetFont(wx.Font(20, wx.DEFAULT, wx.DEFAULT, wx.DEFAULT))
        self.score_table.SetLabel(f'Score: {self.score}')
        self.vbox.Add(self.panel)
        # Инициализация кнопки и виджетов для нее
        self.button = wx.Button(self, size=(self.settings.width, self.settings.height - 50))
        # Инициализация шрифта кнопки
        self.button.SetFont(wx.Font(35, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        # Задание текста кнопки
        self.button.SetLabelText('Play!')
        self.vbox.Add(self.button)
        # Указание vbox'а в качестве Sizer для основного окна
        self.SetSizer(self.vbox)
        # Привязка события кнопки к функции обработки нажатия на кнопку OnButtonClick
        self.Bind(wx.EVT_BUTTON, self.OnButtonClick, self.button)
        # Задание изначального, минимального и максимального размеров окна, т.е окно нельзя будет растянуть и сузить.
        self.SetSize((self.settings.width, self.settings.height))
        self.SetMinSize((self.settings.width, self.settings.height))
        self.SetMaxSize((self.settings.width, self.settings.height))
        # Привязка события прорисовки к функции прорисовки OnPaint
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        # Привязка события нажатия на клавишу к функции обработки OnKeyDown
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        # Привязка события отжатия клавиши к функции обработки OnKeyUp
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        # Инициализация таймера
        self.timer = wx.Timer(self, 1)
        # Центрирование главного окна
        self.Centre()
        # Переменная 'начата ли игра?'
        self.is_started = False
        # Переменная 'окончена ли игра?'
        self.is_finished = False
        # Переменная 'двигаться ли вправо?' ( нужна для плавного движения вправо )
        self.is_right_down = False
        # Переменная 'двигаться ли влево?' ( нужна для плавного движения влево )
        self.is_left_down = False
        # Инициализация начальных настроек игровых объектов
        self.InitDefault()
        # Привязка тика таймера к функции обработки
        self.Bind(wx.EVT_TIMER, self.TimerUpdate)

    """ Функция инициализации начальных игровых параметров """
    def InitDefault(self):
        # Счет
        self.score = 0
        # Прямоугольник корабля
        self.Rectangle = [int(self.settings.width / 2), self.settings.height - 100, 100, 100]
        # Список врагов
        self.enemies = []
        # Переменная скорости врагов
        self.enemy_speed = 1
        # Переменная вознаграждения за убийство одного врага
        self.enemy_regard = 100
        # Переменная напрвления движения врагов
        self.enemy_direction = 1
        # Список пуль
        self.bullets = []
        # Переменная скорости пуль
        self.bullet_speed = 10
        # Максимальное количество пуль
        self.max_bullets = 0
        # Заполнение списка врагов
        self.SpawnEnemies()

    """ Функция заполнения списка врагов """
    def SpawnEnemies(self):
        def SpawnRow(y):
            for i in range(1, 7):
                self.enemies.append([i*100, y, 50, 50])
        for y in range(1, 4):
            SpawnRow(y*100)

    """ Функция проверки столкновений пуль и врагов """
    def CheckCollisions(self):
        for enemy in self.enemies:
            for bullet in self.bullets:
                if (bullet[1] - enemy[1] - enemy[3]) <= -10 and bullet[0]+bullet[2] > enemy[0] and bullet[0]<enemy[0]+enemy[2]:
                    try:
                        self.enemies.remove(enemy)
                        self.bullets.remove(bullet)
                    except ValueError:
                        pass
                    self.score += self.enemy_regard * self.enemy_speed

    """ Функция обновления( одно за тик таймера) """
    def TimerUpdate(self, e):
        if self.is_started:
            # Обновление волны врагов
            if not self.enemies:
                self.SpawnEnemies()
                self.enemy_speed += self.settings.enemy_speed_multiplier
                self.max_bullets += 1
            # Обработка движения вправо, а также проверка на выход за экран
            if self.is_right_down and self.Rectangle[0]+self.Rectangle[2] < self.settings.width:
                self.Rectangle[0] += 20
            # Обработка движения влево, а также проверка на выход за экран
            if self.is_left_down and self.Rectangle[0] > 0:
                self.Rectangle[0] -= 20
            # Обновление прямоугольников пуль, а также удаление пуль, вышедших за экран
            for bullet in self.bullets:
                if bullet[1] == 0:
                    self.bullets.remove(bullet)
                bullet[1] -= self.bullet_speed
            # Обновление прямугольников врагов
            for enemy in self.enemies:
                # Проверка поражения ( враги опустились ниже корпуса корабля или столкнулись )
                if enemy[1]+enemy[3] >= self.Rectangle[1]:
                    self.timer.Stop()
                    self.is_started = False
                    self.button.Show()
                    self.is_finished = True
                # Спуск флота врагов, если вышли за экран справа
                if enemy[0]+enemy[2] >= self.settings.width:
                    for enemy in self.enemies:
                        enemy[0] -= 10
                        enemy[1] += 30
                    self.enemy_direction = -1
                # Спуск флота врагов, если вышли за экран слева
                elif enemy[0] <= 0:
                    for enemy in self.enemies:
                        enemy[0] += 10
                        enemy[1] += 30
                    self.enemy_direction = 1
                enemy[0] += self.enemy_direction * self.enemy_speed
            self.score_table.SetLabel(f'Score: {self.score}')
            self.CheckCollisions()
            self.Refresh(eraseBackground=False)

    """ Функция обаботки нажатия на кнопку 'Play!'(в меню) """
    def OnButtonClick(self, e):
        if not self.is_started:
            # Возврат к начальным игровым настройкам
            if self.is_finished:
                self.InitDefault()
            self.is_started = True
            self.is_finished = False
            # Спрятать кнопку 'Play!'
            self.button.Hide()
            # Явный вызов события и функции прорисовки OnPaint
            self.Refresh(eraseBackground=True)
            # Запуск таймера для начала обработки обновлений
            self.timer.Start(milliseconds=1)

    """ Функция обработки нажатий клавиш """
    def OnKeyDown(self, e):
        # Получение кода кнопки
        key = e.GetKeyCode()
        # Обработка нажатия на стрелку вправо
        if key == wx.WXK_RIGHT:
            self.is_right_down = True
        # Обработка нажатия на стрелку влево
        elif key == wx.WXK_LEFT:
            self.is_left_down = True
        # Обработка нажатия клавишу Q ( выход из игры )
        elif key == (wx.WXK_CONTROL_Q + 64):
            self.timer.Stop()
            self.enemies.clear()
            self.bullets.clear()
            self.Rectangle.clear()
            self.Close()
        # Обработка нажатия на клавишу P ( пауза )
        elif key == (wx.WXK_CONTROL_P + 64):
            self.timer.Stop()
            self.is_started = False
            self.button.Show()
            self.Refresh()
        # Обработка нажатия на пробел
        elif key == wx.WXK_SPACE and len(self.bullets) <= self.max_bullets:
            self.bullets.append([self.Rectangle[0]+int(self.Rectangle[2]/2), self.Rectangle[1], 3, 10])

    """ Функция обработки отжатий клавиш """
    def OnKeyUp(self, e):
        # Получение кода кнопки
        key = e.GetKeyCode()
        # Обработка отжатия стрелки вправо
        if key == wx.WXK_RIGHT:
            self.is_right_down = False
        # Обработка отжатия стрелки влево
        elif key == wx.WXK_LEFT:
            self.is_left_down = False

    """ Функция прорисовки корабля, массивов пуль и врагов """
    def OnPaint(self, e):
        if self.is_started:
            #dc = wx.PaintDC(self) -- вызывает мерцания на экране(среда рисования), wx.BufferedPaintDC не вызывает
            bdc = wx.BufferedPaintDC(self)
            # Прорисовка фона
            bdc.SetBrush(wx.Brush('#1ac500'))
            bdc.DrawRectangle(0, 0, self.settings.width, self.settings.height)
            # Прорисовка корабля
            bdc.SetBrush(wx.Brush('#c56c00'))
            bdc.DrawRectangle(*self.Rectangle)
            # Прорисовка пуль
            for bullet in self.bullets:
                bdc.SetBrush(wx.Brush('#ffffff'))
                bdc.DrawRectangle(*bullet)
            # Прорисовка врагов
            for enemy in self.enemies:
                bdc.SetBrush(wx.Brush('#ff0000'))
                bdc.DrawRectangle(*enemy)
        else:
            # Прорисовка кнопки
            self.button.Show()

""" Класс настроек """
class Settings:
    def __init__(self):
        # Ширина экрана в пикселях
        self.width = 900
        # Высота экрана в пикселях
        self.height = 700
        # Множитель сложности
        self.enemy_speed_multiplier = 1


if __name__ == '__main__':
    app = wx.App(False)
    frame = Game()
    frame.Show()
    app.MainLoop()
