import requests

from kivy.app import App

from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.core.clipboard import Clipboard
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition


from kivy.core.window import Window
Window.clearcolor = (0.9, 0.9, 1, 1)
# Next line is needed for debugging
#Window.size = 800/2.5, 1600/2.5

HEADERS = {
    'Accept': 'text/html, */*; q=0.01',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 YaBrowser/19.12.4.25 Yowser/2.5 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
    }

GROUPNAME = open('groupname.txt').read().lower()

OUTPUT = [] # Schedule screen uses it as data keeper

class Map(Screen):
    map = ObjectProperty()
    f = ObjectProperty()
    W = Window.size

    #def logo(self):
    #    self.map.source = './images/rea.jpg'

    def easter_egg(self):
        self.map.source = './images/paskhal_ochka.jpg'
        Clipboard.copy('https://vk.com/otsositefbi')

    def set_b(self, b_number):  # Sets building number
        self.b = b_number

    def set_fl(self, fl_number):  # Sets floor number
        self.fl = fl_number

    def kostyl(self, ne_stukai):  # Nu ne stukai, idk how to bind nothing
        pass

    def b12(self):  # Set buttons invisible and unbind(almost) them
        for i in self.f[0:4]:
            i.color = 1, 1, 1, 1
            i.background_color = 0.5, 0.5, 0.5, 1
            i.bind(on_release=self.open_map)
        for i in self.f[4:8]:
            i.color = 0, 0, 0, 0
            i.background_color = 0, 0, 0, 0
            i.bind(on_release=self.kostyl)

    def b36(self):  # Same but for buildings 3 & 6
        for i in self.f[1:8]:
            i.color = 1, 1, 1, 1
            i.background_color = 0.5, 0.5, 0.5, 1
            i.bind(on_release=self.open_map)
        self.f[0].color = 0, 0, 0, 0
        self.f[0].background_color = 0, 0, 0, 0
        self.f[0].bind(on_release=self.kostyl)

    def open_plan(self):
        self.map.source = './images/plan.jpg'

    def open_map(self, x):
        self.map.source = './images/%d-%d.png' % (self.b, self.fl)

def suka(self): # LOL, eto che?
        print(1)


class DesignedLabel(Label):
    pass


class LectionLabel(DesignedLabel):
    pass


class SeminarLabel(DesignedLabel):
    pass


class ExamLabel(DesignedLabel):
    pass


class ConsultationLabel(DesignedLabel):
    pass


class WeekDayLabel(DesignedLabel):
    pass

class LessonNumberLabel(DesignedLabel):
    pass


class Schedule(Screen):
    global GROUPNAME, HEADERS, OUTPUT

    weeknum = ObjectProperty()
    schedulebackground = ObjectProperty()

    WEEKDAYS = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота']

    def check_group_number(self):
        if GROUPNAME != '':
            self.reload()
            self.reload_weeknum()
            self.show_week()
        else:
            self.schedulebackground.add_widget(Label(text='\n\n\nВыберите номер группы в установках', color=(0, 0, 0, 1)))

    def reload(self):
        global GROUPNAME, OUTPUT

        weekschedule = self.week_request(GROUPNAME, self.weeknum.text)

        OUTPUT = []
        for i in weekschedule:
            OUTPUT.append(self.show_lesson_text(GROUPNAME, i[0], i[1]))
        self.show_week()

        return OUTPUT

    def show_week(self):
        self.schedulebackground.clear_widgets()
        for i in self.WEEKDAYS:
            self.schedulebackground.add_widget(WeekDayLabel(text='[b]' + i.capitalize() + '[/b]'))
            self.show_day(i, False)

    def show_day(self, day, notweek=True):
        global OUTPUT

        if notweek:
            self.schedulebackground.clear_widgets()

        localoutput = []

        for lesson in OUTPUT:
            for i in lesson:
                if day in i[1]:
                    localoutput.append(i)
                    for widget in self.schedulebackground.children:
                        if day in widget.text.lower() and '\n' not in widget.text:
                            date = i[1][i[1].find(',')+2: i[1].rfind(',')-5]
                            widget.text = widget.text + '\n' + date

        for i in range(len(localoutput)):
            if localoutput[i][1] != localoutput[i-1][1]:
                self.schedulebackground.add_widget(LessonNumberLabel(text=str(localoutput[i][1][-6:])))
            if 'Практическое занятие' in localoutput[i][3]:
                self.schedulebackground.add_widget(SeminarLabel(text=str(localoutput[i][0])))
            elif 'Консультации' in localoutput[i][3]:
                self.schedulebackground.add_widget(ConsultationLabel(text=str(localoutput[i][0])))
            elif 'зачёт' in localoutput[i][3].lower() or 'Экзамен' in localoutput[i][3]:
                self.schedulebackground.add_widget(ExamLabel(text=str(localoutput[i][0])))
            else:
                self.schedulebackground.add_widget(LectionLabel(text=str(localoutput[i][0])))

    def show_lesson_text(self, groupname, date, time, calledoutside=False):
        global HEADERS

        requesturl = 'https://rasp.rea.ru/Schedule/GetDetails?selection={}&date={}&timeSlot={}'.format(groupname, date, time)

        request = requests.get(url=requesturl, headers = HEADERS)
        requesttext = request.text.split('\n')
        localoutput = []
        for i in range(len(requesttext)//23):
            if calledoutside:
                localoutput.append(self.clean_text(Schedule, requesttext[6*(1+4*i)-1:6*(1+4*i)+16], calledoutside=True))
            else:
                localoutput.append(self.clean_text(requesttext[6*(1+4*i)-1:6*(1+4*i)+16]))
        return localoutput

    def clean_text(self, text, calledoutside=False):
        '''
        Makes parsed text easy to read
        '''
        date = text[2].lstrip()[:-7]
        group = text[8][:-1].lstrip()
        text = [text[0]] + [text[1]] + [text[3]] + [text[12]] + [text[15]]
        for i in range(len(text)):
            text[i] = text[i].lstrip()

        if calledoutside:
            return text[2][11:-7]
        text[0] = '[b]' + text[0][4:-6] + '[/b]' # Lesson name
        text[1] = '[i]' + text[1][8:-16] + '[/i]' # Lesson type
        if 'чет' in text[1]:
            text[1] = text[1].replace('чет', 'чёт')
        text[2] = text[2][:-7] # Room
        text[3] = text[3][:-1] # Teacher
        text[4] = text[4][text[4].rfind('</i>')+5:-5] # Teacher's name
        if ')' in group:
            text = text[:3] + [str('Подгруппа: ' + group[-2])] + text[3:]
        lessontype = text[1]
        return ['\n'.join(text), date, group, lessontype]

    def week_request(self, groupname, weeknum):
        '''
        Requests weekly list of lessons

        Returns list of dates and numbers of lessons
        '''

        global HEADERS

        starturl = 'https://rasp.rea.ru/Schedule/ScheduleCard?selection={}&weekNum={}&catfilter=0'.format(groupname, weeknum)
        request = requests.get(url=starturl, headers=HEADERS)

        parse = request.text.split('\n')

        lessonlist = []

        for line in parse:
            if 'updateTimeslotInfo' in line:
                lessonlist.append([line[270:280], line[284]])

        return lessonlist

    def weeknum_request(self, groupname):
        global HEADERS

        requrl = 'https://rasp.rea.ru/Schedule/ScheduleCard?selection={}&weekNum=-1&catfilter=0'.format(groupname)
        request = requests.get(url=requrl, headers=HEADERS)

        ans = request.text.split('\n')
        return ans[2][41:43]

    def reload_weeknum(self):
        global GROUPNAME

        self.weeknum.text = self.weeknum_request(GROUPNAME)

    def next_week(self):
        self.weeknum.text = str(int(self.weeknum.text) + 1)

    def prev_week(self):
        self.weeknum.text = str(int(self.weeknum.text) - 1)


class Empty(Screen):
    rooms = ObjectProperty()

    def load(self):
        occupiedroomslist = []
        # grouplist = open('grouplist.txt').read().lower().split('\n')
        grouplist = [open('groupname.txt').read().lower()]
        roomslist = open('roomlist.txt').read().split('\n')
        for group in grouplist:
            occupiedroomslist.append(Schedule.show_lesson_text(Schedule, group, self.date.text, self.lessonnumber.text, calledoutside=True)[0]) # Returns room
        occupiedroomslist = set(occupiedroomslist)
        print(occupiedroomslist)
        '''
        for room in occupiedroomslist:
            roomslist.remove(room)
        self.rooms.text = ''
        for room in roomslist:
            self.rooms.text = self.rooms.text + room + '\n'
        '''


class Sets(Screen):
    faculty = ObjectProperty()
    course = ObjectProperty()
    level = ObjectProperty()
    group = ObjectProperty()
    department = ObjectProperty()
    teacher = ObjectProperty()
    shower = ObjectProperty()

    facultyvalues = open('faculties.txt').read().split('\n') # Too long to be here
    coursevalues = ['1-й курс', '2-й курс', '3-й курс', '4-й курс', '5-й курс']
    levelvalues = ['Бакалавр', 'Магистр', 'Специалист']
    departmentvalues = open('departments.txt').read().split('\n') # 66 rows, fuck it

    def show(self):
        global GROUPNAME

        self.faculty.text = 'Факультет'
        self.faculty.values = self.facultyvalues
        self.course.text = 'Курс'
        self.course.values = self.coursevalues
        self.level.text = 'Уровень'
        self.level.values = self.levelvalues
        self.group.text = 'Группа'
        self.department.text = 'Кафедра'
        self.department.values = self.departmentvalues
        self.teacher.text = 'Преподаватель'
        self.shower.text = GROUPNAME

    def load_groups(self):
        global HEADERS

        if self.faculty.text != 'Факультет' and self.course.text != 'Курс' and self.level.text != 'Уровень':
            data = {'Faculty': self.faculty.text,
                    'Course': self.course.text,
                    'Type': self.level.text,
                    'Cathedra': 'na',
                    'ChangedNode': 'Type',
                    'ChangedValue': self.level.text}
            req = requests.post(url='https://rasp.rea.ru/Schedule/Navigator', headers=HEADERS, data=data)
            groups = req.text.split('\n')
            groups = groups[33].split('</option>')[:-1]
            for group in range(len(groups)):
                groups[group] = groups[group].split('>')[1]
            self.group.values = groups
            print(groups)


    def load_teachers(self):
        global HEADERS

        if self.department.text != 'Кафедра':
            data = {'Faculty': 'na',
                    'Cathedra': self.department.text,
                    'ChangedNode': 'Cathedra',
                    'ChangedValue': self.department.text}
            req = requests.post(url='https://rasp.rea.ru/Schedule/Navigator', headers=HEADERS, data=data)
            teachers = req.text.split('\n')
            teachers = teachers[47].split('</option>')[:-1]
            for teacher in range(len(teachers)):
                teachers[teacher] = teachers[teacher].split('>')[1]
            self.teacher.values = teachers


    def save(self, choose):
        global GROUPNAME

        if choose.text != 'Преподаватель' and choose.text != 'Группа':
            GROUPNAME = choose.text.lower()
            open('groupname.txt', 'w').write(GROUPNAME)
            self.shower.text = GROUPNAME


class BottomMenu(BoxLayout):
    pass


class Container(ScreenManager):
    pass


class sApp(App):

    def build(self):
        return Container()


if __name__ == '__main__':
    sApp().run()
