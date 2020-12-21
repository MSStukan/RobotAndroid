import time # do sleepa w komunikacji udp
from kivy.uix.widget import Widget
from kivy.uix.behaviors import DragBehavior
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from threading import Thread
from kivy.properties import NumericProperty, BooleanProperty, ReferenceListProperty, ObjectProperty
#################  For Udp transmission ################
import socket

global Data1, DataToSend, UDP_IP, UDP_PORT
UDP_IP = "192.168.43.168" # IP ESP
UDP_PORT = 4210
MESSAGE = b"Hello, mot*** fu****"
Data1 = [88, 44, 0, 11, 3, 8, 40, 155]   # tymczasowo do testów
DataToSend = bytes(Data1)                # convert na byte aby dało się wysłać
#print("UDP target IP: %s" % UDP_IP)
#("UDP target port: %s" % UDP_PORT)
#print("message: %s" % MESSAGE)
                        # Internet     # UDP
#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
###########################################################


global StopRunUDP, OnceRunUDP
StopRunUDP, OnceRunUDP = True, False
global WidX, HeiY, valXXY
global AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery, Temp
AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ = 0, 0, 0, 0, 0, 0
Battery, Temp = 0, 0
valXXY = NumericProperty
valXXY = 1

class Circle(DragBehavior, Widget):

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            tx, ty = touch.pos
            sx, sy = self.pos
        return super(Circle, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            #print("\tCircle.on_touch_up:")  # do usnięcia komentaz pogladowy do spr działania
            self.pos = WidX / 2 - self.width / 2, HeiY / 2 - self.height / 2
        return super(Circle, self).on_touch_up(touch)


class GUI(FloatLayout):

    ######   Global   Variables      ######


    global StopRunUDP, OnceRunUDP
    runOnce =BooleanProperty(False) # zmienna do jednorazowego pobrania wid/hei pod joystickiem

###################   Automatyczny updete pozycji #################3
    def __init__(self, **kwargs):
        super(GUI, self).__init__(**kwargs)
        Clock.schedule_interval(self.update, 1/30.0)
        Clock.schedule_interval(self.change_color, 1 / 1)  # !!!!!!!! TO DO ZMIANY
       # Clock.schedule_interval(self.change_color, 1 / 30.0) # !!!!!!!! TO DO ZMIANY
    # clock.schedule uruchamia w każdej wolnej chwili funkcje
    # dzieki temu automatycznie sa aktualizowane wartości label/ variables itd

    def update(self, *args): # args to pusty argument żeby się nie czepiał kompilator w sesie że nic nie robi , ale bez niego nie działa
        if not self.runOnce :
            self.WHJoy()
            self.runOnce=True

        pozX = self.ids.cir.pos[0]+25
        pozY = self.ids.cir.pos[1]+25
        pX, pY = self.calc_Joy(pozX, pozY)

    #
        self.ids.padX.text = ' pad X: %.2f' % pX
        self.ids.padY.text = ' pad Y: %.2f' % pY


    #   #### Updateing Data of Joystick ####
        self.Send_Pos_Joy(pX,pY)

    #   ####   Takeing half wid of showed reactangles ####
        WidRectangle = self.ids.GyXx.width-10
        HalfWidRe= WidRectangle/2
        self.Update_AccelGyro(HalfWidRe)




# ################## Pobranie szerokosci placu pod Joy.. ###############
    def WHJoy(self):  # uruchamiane jdnorazowo aby pobrac szerokość placu pod
                        # joystickiem by móc go wycentrować
        global WidX, HeiY
        WidX = self.ids.GridUnderJoy.size[0]
        HeiY = self.ids.GridUnderJoy.size[1]

#   ####       Updating posytion of joystick to send to ESP ####
    def Send_Pos_Joy(self, pozX, pozY):
        global Data1, DataToSend
        pXx = self.Map_Func(pozX, -50, 50, 0, 100)
        pYy = self.Map_Func(pozY, -50, 50, 0, 100)
        Data1[0] = int(pXx)
        Data1[1] = int(pYy)
        DataToSend = bytes(Data1)
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#  ####        Updateing value in kivy screen                      ####
    def Update_AccelGyro(self,HalfWID):

                # GyroX
        Gyrox = self.Map_Func(GyroX, -32768, 32768, -HalfWID, HalfWID)
        self.ids.valGyroX.text = '%d' % GyroX  # modyfikator tekst
        self.ids.GyroX.sGx = Gyrox
                # GyroY
        Gyroy = self.Map_Func(GyroY, -32768, 32768, -HalfWID, HalfWID)
        self.ids.valGyroY.text = '%d' % GyroY  # modyfikator tekst
        self.ids.GyroY.sGy = Gyroy
                # GyroZ
        Gyroz = self.Map_Func(GyroZ, -32768, 32768, -HalfWID, HalfWID)
        self.ids.valGyroZ.text = '%d' % GyroZ  # modyfikator tekst
        self.ids.GyroZ.sGz = Gyroz
                # AccelX
        Accelx = self.Map_Func(AccelX, -32768, 32768, -HalfWID, HalfWID)
        self.ids.valAccelX.text = '%d' % AccelX  # modyfikator tekst
        self.ids.AccelX.sAx = Accelx
                # AccelY
        Accely = self.Map_Func(AccelY, -32768, 32768, -HalfWID, HalfWID)
        self.ids.valAccelY.text = '%d' % AccelY  # modyfikator tekst
        self.ids.AccelY.sAy = Accely
                # AccelZ
        Accelz = self.Map_Func(AccelZ, -32768, 32768, -HalfWID, HalfWID)
        self.ids.valAccelZ.text = '%d' % AccelZ  # modyfikator tekst
        self.ids.AccelZ.sAz = Accelz
                #Battery
        Baatt = self.Map_Func(Battery, 0, 255, 0, HalfWID*2)
        BtPerCent = self.Map_Func(Battery, 0, 255, 0, 100)
        self.ids.valBattery.text = ' %d ' % BtPerCent + '%' # modyfikator tekst
        self.ids.BATT.sBt = Baatt
        #print(HalfWID*2)
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def change_color(self, *args):
        ww = Battery
        BatteryColor = (0, 0, 16 / 255, 1)
        if 191 < ww <= 255:  # 255-64
            BatteryColor = (94 / 255, 1, 0, 1)
        elif 128 < ww <= 191:
            BatteryColor = (221 / 255, 1, 0, 1)
        elif 64 < ww <= 128:
            BatteryColor = (1, 140 / 255, 0, 1)
        elif 0 <= ww <= 64:
            BatteryColor = (1, 64 / 255, 0, 1)
        self.ids.BATT.colOf = BatteryColor





# #### Calc position of joystick               #####
    def calc_Joy(self, pozX, pozY):

        if pozX >150: pozX = 150
        elif pozX<50: pozX = 50
        else: pozX = pozX
        UpDo = -(100-pozX)

        if pozY >150: pozY = 150
        elif pozY<50: pozY = 50
        else: pozY = pozY
        LeRi = -(100-pozY)

        return(UpDo,LeRi)
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    ###--------------------------- Dotąd jest G--------------------------###

            ################### map Function #################
    def Map_Func(self, x, minX, maxX, outMin, outMax):
        Out = (x - minX) * (outMax - outMin) / (maxX - minX) + outMin
        #  Out=    Y     *       Z            /      C       + outMin
        # Y/Z/C   ogarnąć zabezpiecznie  ( pamiętaj cholero nie dziel przez zero) , czy python to ogrania i uj z tym?
        return(Out)


############ !!!!!!!!!!!!!!!!!!!!!!!!FRAGMENT   PROBLEMATYCZNY!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#################
    def do_something(self):
        global StopRunUDP, OnceRunUDP
        #print(StopRunUDP)
        if not OnceRunUDP:
            StopRunUDP = True
            OnceRunUDP = True

       # print('after IF')
        #print(StopRunUDP)
        # create the thread to invoke other_func with arguments (2, 5)
        t1 = Thread(target=self.Communication_UDP_ESP)
        # set daemon to true so the thread dies when app is closed
        t1.daemon = True            # Jesli True -> background worker , if false
        # start the thread
        t1.start()


    def Stop_UDP(self):    # Z niewiadomych przyczyn nie uruchamia sie ...
        global StopRunUDP, OnceRunUDP           # próba przynajmniej zkończenia watku other_func
        #print(StopRunUDP)
        StopRunUDP = False
        OnceRunUDP = False
        #print('after StopUDP')
        #print(StopRunUDP)


    def Communication_UDP_ESP(self):
        global StopRunUDP,OnceRunUDP
        global Data1, DataToSend, UDP_IP, UDP_PORT
        global AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery, Temp
                                     # Internet     # UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Tworzenie / podlączenie socketa
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
        sock.settimeout(0.3) # najwyrażnej rozwiązło problem , (socket.setblocking)
                    # jesli false to nie mrozi progrmu w oczekiwaniu na dane jesli true , mrozi
        #lost = 1

        def Save_Data_From_ESP(Data):
            global AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, Battery, Temp
                        # Battery
            Battery = Data[0]
                        # Temp
            Temp = Data[1] << 8 | Data[2]
                        # Accel X
            AccelXx = Data[3] << 8 | Data[4]
            AccelX = self.Map_Func(AccelXx, 0, 65535, -32768, 32768)

                        # Accel Y
            AccelYy = Data[5] << 8 | Data[6]
            AccelY = self.Map_Func(AccelYy, 0, 65535, -32768, 32768)

                        # Accel Z
            AccelZz = Data[7] << 8 | Data[8]
            AccelZ = self.Map_Func(AccelZz, 0, 65535, -32768, 32768)

                        # Gyro X
            GyroXx = Data[9] << 8 | Data[10]
            GyroX = self.Map_Func(GyroXx, 0, 65500, -32750, 32750)

                        # Gyro Y
            GyroYy = Data[11] << 8 | Data[12]
            GyroY = self.Map_Func(GyroYy, 0, 65500, -32750, 32750)

                        # Gyro Z
            GyroZz = Data[13] << 8 | Data[14]
            GyroZ = self.Map_Func(GyroZz, 0, 65500, -32750, 32750)




        while StopRunUDP:
            # lost = lost+1     # for tests
            # print(lost)
            # if lost >90000 :
            #     lost = 0

            mili_Start = time.time()
            try:
                Data, addr = sock.recvfrom(16)  # buffer size is 15 bytes
            except:
                print("                                     error")

            if len(Data) > 0:  # jesli bufor wiekszy od zera ( linijak wyżej , albo bedzie , albo bedzie zero ....)
                Save_Data_From_ESP(Data)
               # print(Data)
                # print("received message: %s" % Data)  # wypisz dane
                Data = []  # zerowanie buforu , ale chyba niekonieczne
                sock.sendto(DataToSend, (UDP_IP, UDP_PORT))  # wysłanie wiadomości zwrotnej

            mili_Stop = time.time()
            TimeOut = mili_Stop - mili_Start
            #print(TimeOut)
            if TimeOut > 0.2 :
                print("Coś poszło nie tak, sprawdź połączenie")
                sock.sendto(DataToSend, (UDP_IP, UDP_PORT))  # wysłanie wiadomości zwrotnej

            #print()


        # def Print_Data_ESP_For_Check():
        #               # Battery
        #     Battery = Data[0]
        #     print("Battery: %x       " % Battery, end='')
        #     print("Battery in decimal: %d" % Battery)
        #               # Temp
        #     Temp = Data[1] << 8 | Data[2]
        #     print("Temp: %x       " % Temp, end='')
        #     print("Temp in decimal: %d" % Temp)
        #               # Accel X
        #     AccelXx = Data[3] << 8 | Data[4]
        #     AccelX = self.Map_Func(AccelXx, 0, 65535, -32768, 32768)
        #     print("AccelX: %x       " % AccelX, end='')
        #     print("AccelX in decimal: %d" % AccelX)
        #               # Accel Y
        #     AccelYy = Data[5] << 8 | Data[6]
        #     AccelY = self.Map_Func(AccelYy, 0, 65535, -32768, 32768)
        #     print("AccelY: %x       " % AccelY, end='')
        #     print("AccelY in decimal: %d" % AccelY)
        #               # Accel Z
        #     AccelZz = Data[7] << 8 | Data[8]
        #     AccelZ = self.Map_Func(AccelZz, 0, 65535, -32768, 32768)
        #     print("AccelZ: %x       " % AccelZ, end='')
        #     print("AccelZ in decimal: %d" % AccelZ)
        #               # Gyro X
        #     GyroXx = Data[9] << 8 | Data[10]
        #     GyroX = self.Map_Func(GyroXx, 0, 65500, -32750, 32750)
        #     print("GyroX: %x       " % GyroX, end='')
        #     print("GyroX in decimal: %d" % GyroX)
        #               # Gyro Y
        #     GyroYy = Data[11] << 8 | Data[12]
        #     GyroY = self.Map_Func(GyroYy, 0, 65500, -32750, 32750)
        #     print("GyroY: %x       " % GyroY, end='')
        #     print("GyroY in decimal: %d" % GyroY)
        #               # Gyro Z
        #     GyroZz = Data[13] << 8 | Data[14]
        #     GyroZ = self.Map_Func(GyroZz, 0, 65500, -32750, 32750)
        #     print("GyroZ: %x       " % GyroZ, end='')
        #     print("GyroZ in decimal: %d" % GyroZ)



class GUIApp(App):

    def build(self):

        return GUI()


if __name__ == '__main__':
    GUIApp().run()
