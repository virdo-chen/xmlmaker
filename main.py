import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image

imgs = ["编程猫.png", "会移动的砖块.png", "探月兔.png", "兔年编程猫.png", "邪恶的敌人2.png", "游戏通关2.png",
        "障碍物.png", "brick4.png", "草灵灵.png", "蓝雀.png", "涂鸦狐.png", "小巴格.png", "邪恶的敌人3.png",
        "元宝0.png", "block.png", "brick5.png", "春节编程猫.png", "木叶龙.png", "兔年编程猫-拜年.png", "小黄鸡.png",
        "游戏过关1.png", "元宝1.png", "brick0.png", "brick6.png", "春节墙.png", "年兽.png", "兔年编程猫-舞龙.png",
        "小火熊.png", "游戏过关2.png", "元宝2.png", "brick1.png", "panda.png", "大黄鸡.png", "气泡鱼.png",
        "兔年编程猫-新春快乐.png", "小圆狸.png", "游戏过关3.png", "元宝3.png", "brick2.png", "鼓.png",
        "墙.png", "兔年编程猫-迎财神.png", "邪恶的敌人1.png", "游戏通关1.png", "元宝.png", "brick3.png"]

# 用来供给PIL库的使用（因为canvas似乎对tk本身的图片导入不太友好）
original_imgs = ["./imgs/编程猫.png", "./imgs/会移动的砖块.png", "./imgs/探月兔.png", "./imgs/兔年编程猫.png",
                 "./imgs/邪恶的敌人2.png", "./imgs/游戏通关2.png", "./imgs/障碍物.png", "./imgs/brick4.png",
                 "./imgs/草灵灵.png", "./imgs/蓝雀.png", "./imgs/涂鸦狐.png", "./imgs/小巴格.png",
                 "./imgs/邪恶的敌人3.png",
                 "./imgs/元宝0.png", "./imgs/block.png", "./imgs/brick5.png", "./imgs/春节编程猫.png", "./imgs/木叶龙.png",
                 "./imgs/兔年编程猫-拜年.png", "./imgs/小黄鸡.png", "./imgs/游戏过关1.png", "./imgs/元宝1.png",
                 "./imgs/brick0.png",
                 "./imgs/brick6.png", "./imgs/春节墙.png", "./imgs/年兽.png", "./imgs/兔年编程猫-舞龙.png",
                 "小火熊.png",
                 "./imgs/游戏过关2.png", "./imgs/元宝2.png", "./imgs/brick1.png", "./imgs/panda.png",
                 "./imgs/大黄鸡.png",
                 "./imgs/气泡鱼.png", "./imgs/兔年编程猫-新春快乐.png", "./imgs/小圆狸.png", "./imgs/游戏过关3.png",
                 "./imgs/元宝3.png", "./imgs/brick2.png", "./imgs/鼓.png", "./imgs/墙.png", "./imgs/兔年编程猫-迎财神.png",
                 "./imgs/邪恶的敌人1.png", "./imgs/游戏通关1.png", "./imgs/元宝.png", "./imgs/brick3.png"]

"""
canvas所需的图片对象必须是在一个全局变量里，且（起码在图片显示时）始终不发生改变（P事真tnnd多）
而为其空出600个变量是根本不可能的，所以只能出此下策
--------------
之前的方案有个缺点：每调用一次draw()，它就会新占用以下三个列表的后几个位置，如果一直调用，会导致这三个列表的位置被很快用完。
这个问题已得到解决(2023.10.03,National day in Wuwei)。理由是：以下这些变量只在类App()的方法draw()中被引用。显示功能也只在那里完成。
那么就可以在每一次调用draw()时，先初始化它们，这样就用不完了。
600从<累计在画板上显示的元素最大个数>变成了<同时在电脑上显示的元素最大个数>。
--------------
然而当我尝试着删除draw()方法中global全局声明对img,img_n以及im的声明以后，我意外发现：运行并点击加载按钮加载文件以后，素材只显示了一瞬间便消失了
经过仔细思忖，我认为是因为：draw()在其生命周期结束后会删除作为它的局部变量的img,img_n以及im，这导致图片也被删了。
所以它们必须作为全局变量。global不能删。既然如此，干脆把以下三行代码加回来，作为全局变量，有一个全局声明才是好习惯。
"""
img = [None for _ in range(300)]
img_n = 0
im = [None for _ in range(300)]

brick = [23, 31, 39, 46, 8, 16, 24]

img_selection = 1
kind_selection = None
k0_kind_part = None  # 1:高低；2:左右

"""
不一定只有一个moving_brick（事实上极有可能有多个）,故暂且使用列表来储存信息。
应为
[moving_brick组
    [a,b,c,d,e,f,g], 一个moving_brick
    [a1,b1,c1,d1,e1,f1,g1],
    [a2,b2,c2,d2,e2,f2,g2],...
]
这么一个离谱的列表。

对于一个moving_brick：[a,b,c,d,e,f,g]
a=0或1   0表示纵向平移，1表示横向平移
b:位移最小值
c:位移最大值
d:速度
e:初始位置x坐标
f:初始位置y坐标
g:素材图片编号
"""


class Main_data_processor:
    def __init__(self):
        self.tree = None  # 读取文件时用的
        self.new_tree = None  # 编辑完成后写入新文件用的
        # 每个种类只需一个layer（甚至包括砖块）
        self.moving_bricks_data = [0 for _ in range(600)]
        self.killers_data = [0 for _ in range(600)]
        self.player_data = [0 for _ in range(600)]
        self.bricks_data = [0 for _ in range(600)]
        self.walls_data = [0 for _ in range(600)]

        self.load_for_init()

    def load_for_init(self):
        self.tree = ET.parse("./prototype.xml").getroot()
        for layer in self.tree.findall("layer"):
            if layer.get("name") == "障碍物":
                self.killers_data = eval("[" + layer.findtext("data") + "]")
            elif layer.get("name") == "玩家":
                self.player_data = eval("[" + layer.findtext("data") + "]")
            elif layer.get("name") == "砖块":
                self.bricks_data = eval("[" + layer.findtext("data") + "]")
            else:
                self.walls_data = eval("[" + layer.findtext("data") + "]")
        # moving_bricks:
        self.moving_bricks_data = []
        objects = self.tree.findall("objectgroup/object")
        for object in objects:
            c = [None for _ in range(7)]
            properties = object.find("properties").findall("property")
            if object.find("properties/property", {"name": ""}) is not None and \
                    object.find("properties/property", {"name": ""}).get("name") == "boundary_left":
                c[0] = 1
                for property_ in properties:
                    if property_.get("name") == "boundary_left":
                        c[1] = int(property_.get("value"))
                    elif property_.get("name") == "boundary_right":
                        c[2] = int(property_.get("value"))
                    else:
                        c[3] = int(property_.get("value"))
            else:
                c[0] = 0
                for property_ in properties:
                    if property_.get("name") == "boundary_bottom":  # 为统一度量衡
                        c[1] = 640 - int(property_.get("value"))
                    elif property_.get("name") == "boundary_top":
                        c[2] = 640 - int(property_.get("value"))
                    else:
                        c[3] = int(property_.get("value"))

            c[4] = int(float(object.get("x")))/2
            c[5] = int(float(object.get("y")))/2
            c[6] = int(object.get("gid"))
            self.moving_bricks_data.append(c)
        del objects

    def load(self):
        try:
            self.tree = ET.parse(filedialog.askopenfilename()).getroot()
        except Exception as E:
            return None
        for layer in self.tree.findall("layer"):
            if layer.get("name") == "障碍物":
                self.killers_data = eval("[" + layer.findtext("data") + "]")
            elif layer.get("name") == "玩家":
                self.player_data = eval("[" + layer.findtext("data") + "]")
            elif layer.get("name") == "砖块":
                self.bricks_data = eval("[" + layer.findtext("data") + "]")
            else:
                self.walls_data = eval("[" + layer.findtext("data") + "]")
        # moving_bricks:
        self.moving_bricks_data = []
        objects = self.tree.findall("objectgroup/object")
        for object in objects:
            c = [None for _ in range(7)]
            properties = object.find("properties").findall("property")
            if object.find("properties/property", {"name": ""}) is not None and \
                    object.find("properties/property", {"name": ""}).get("name") == "boundary_left":
                c[0] = 1
                for property_ in properties:
                    if property_.get("name") == "boundary_left":
                        c[1] = int(property_.get("value"))
                    elif property_.get("name") == "boundary_right":
                        c[2] = int(property_.get("value"))
                    else:
                        c[3] = int(property_.get("value"))
            else:
                c[0] = 0
                for property_ in properties:
                    if property_.get("name") == "boundary_bottom":  # 为统一度量衡
                        c[1] = 640 - int(property_.get("value"))
                    elif property_.get("name") == "boundary_top":
                        c[2] = 640 - int(property_.get("value"))
                    else:
                        c[3] = int(property_.get("value"))

            c[4] = int(float(object.get("x")))/2
            c[5] = int(float(object.get("y")))/2
            c[6] = int(object.get("gid"))
            self.moving_bricks_data.append(c)
        del objects


    def write_into_tree(self):
        self.new_tree = ET.parse("./prototype.xml").getroot()
        # write moving_bricks
        objectgroup = ET.Element("objectgroup", {"id": "0", "name": "移动的砖块"})
        for a in self.moving_bricks_data:
            obj = ET.Element("object", {"id": "1", "gid": str(a[6]), "x": str(a[4]*2), "y": str(a[5]*2), "width": "128",
                                        "height": "64"})
            properties = ET.Element("properties")
            if a[0]:
                # lr
                properties.append(ET.Element("property", {"name": "boundary_left", "type": "int", "value": str(a[1])}))
                properties.append(ET.Element("property", {"name": "boundary_right", "type": "int", "value": str(a[2])}))
                properties.append(ET.Element("property", {"name": "change_x", "type": "int", "value": str(a[3])}))
            else:
                # ud 同样为了统一度量衡而进行了改动
                properties.append(ET.Element("property", {"name": "boundary_bottom", "type": "int", "value": str(640-a[1])}))
                properties.append(ET.Element("property", {"name": "boundary_top", "type": "int", "value": str(640-a[2])}))
                properties.append(ET.Element("property", {"name": "change_y", "type": "int", "value": str(a[3])}))
            obj.append(properties)
            objectgroup.append(obj)
        self.new_tree.append(objectgroup)

        # write killers
        # 预备使用字符串拼接再导入的方法来解决无法写入文本元素的问题。ET.from...
        datastr = """<layer id="1" name="障碍物" width="30" height="20"><data encoding="csv">\n"""
        datastr += str(self.killers_data)[1:-1].replace(" ", "")
        datastr += "\n</data>\n</layer>\n"
        data = ET.fromstring(datastr)
        self.new_tree.append(data)

        # player
        datastr = """<layer id="2" name="玩家" width="30" height="20"><data encoding="csv">\n"""
        datastr += str(self.player_data)[1:-1].replace(" ", "")
        datastr += "\n</data>\n</layer>\n"
        data = ET.fromstring(datastr)
        self.new_tree.append(data)

        # bricks
        datastr = """<layer id="3" name="砖块" width="30" height="20"><data encoding="csv">\n"""
        datastr += str(self.bricks_data)[1:-1].replace(" ", "")
        datastr += "\n</data>\n</layer>\n"
        data = ET.fromstring(datastr)
        self.new_tree.append(data)

        # walls
        datastr = """<layer id="4" name="墙" width="30" height="20"><data encoding="csv">\n"""
        datastr += str(self.walls_data)[1:-1].replace(" ", "")
        datastr += "\n</data>\n</layer>\n"
        data = ET.fromstring(datastr)
        self.new_tree.append(data)

    def save(self):
        self.write_into_tree()
        self.new_tree = ET.ElementTree(self.new_tree)
        self.new_tree.write(filedialog.asksaveasfilename(), "UTF-8")

    def show_data(self):
        print("killers_data:\n", self.killers_data)
        print("\n\nplayer_data\n", self.player_data)
        print("\n\nbricks_data\n", self.bricks_data)
        print("\n\nwalls_data\n", self.walls_data)
        print("\n\nmoving_bricks_data:\n", self.moving_bricks_data)


main_data_processor = Main_data_processor()


class Left_button:
    def __init__(self):
        self.Btn = None
        self.num = None

    def set(self, root, img, num):
        self.num = num
        self.Btn = tk.Button(root, image=img, width=190, height=100, command=self.reply_press)

    def place(self, x, y):
        self.Btn.place(x=x, y=y)

    def reply_press(self):
        global img_selection
        img_selection = self.num


# 怎么讲。。。编写self.init的时候发现它实在是太长了，所以为了给程序分清次序，把函数拆成很多小部分(main1,main2什么的)
class App:
    def __init__(self):
        # self.mouse_in_L = False
        self.main_window = tk.Tk()
        self.main_window.title("TMX Maker")
        self.main_window.geometry("800x600")

        self.main1()

        self.main2_1()

        self.main2_2()

        self.main2_3()

        self.main2_4()

        self.main3()

        self.pos_xy_showVar = tk.StringVar()
        self.pos_xy_showVar.set("1145, 1411")
        self.pos_xy_show = tk.Label(self.main_window, textvariable=self.pos_xy_showVar,
                                    background="skyblue")
        self.pos_xy_show.place(x=200, y=0)

        self.main_window.update()
        self.main_window.mainloop()


    # 重置work_part大小
    def resize_work(self, event):
        self.work_part.config(width=self.main_window.winfo_width() - 200, height=self.main_window.winfo_height())
        self.work_part.place(x=200, y=0)
        self.main_window.update()

    # 加载/重置k0的上下/左右区域的布局
    def reset_k0_kind_part(self, mode_num):
        global k0_kind_part
        # 打扫干净屋子
        self.k0_tmLbl.place_forget()
        self.k0_tmEty.place_forget()

        self.k0_bmLbl.place_forget()
        self.k0_bmEty.place_forget()

        self.k0_lmLbl.place_forget()
        self.k0_lmEty.place_forget()

        self.k0_rmLbl.place_forget()
        self.k0_rmEty.place_forget()

        # 再请客
        if mode_num == 1:
            self.k0_tmLbl.place(relx=0, rely=1 / 5, relwidth=1, relheight=1 / 10)
            self.k0_tmEty.place(relx=0, rely=3 / 10, relwidth=1, relheight=1 / 20)
            self.k0_bmLbl.place(relx=0, rely=7 / 20, relwidth=1, relheight=1 / 20)
            self.k0_bmEty.place(relx=0, rely=2 / 5, relwidth=1, relheight=1 / 20)
        elif mode_num == 2:
            self.k0_lmLbl.place(relx=0, rely=1 / 5, relwidth=1, relheight=1 / 10)
            self.k0_lmEty.place(relx=0, rely=3 / 10, relwidth=1, relheight=1 / 20)
            self.k0_rmLbl.place(relx=0, rely=7 / 20, relwidth=1, relheight=1 / 20)
            self.k0_rmEty.place(relx=0, rely=2 / 5, relwidth=1, relheight=1 / 20)
        k0_kind_part = mode_num

    # 加载/重置5种kind的布局
    def reset_kind_part(self, mode_num):
        # 打扫干净屋子
        self.k0_select_tb.place_forget()
        self.k0_select_lr.place_forget()

        self.k0_tmLbl.place_forget()
        self.k0_tmEty.place_forget()
        self.k0_bmLbl.place_forget()
        self.k0_bmEty.place_forget()

        self.k0_lmLbl.place_forget()
        self.k0_lmEty.place_forget()
        self.k0_rmLbl.place_forget()
        self.k0_rmEty.place_forget()

        self.k0_speed_ask.place_forget()
        self.k0_speed_get.place_forget()

        self.k0_start_pos_ask.place_forget()
        self.k0_x_get.place_forget()
        self.k0_y_get.place_forget()

        self.k1_askLbl_x.place_forget()
        self.k1_x_Entry.place_forget()
        self.k1_askLbl_y.place_forget()
        self.k1_y_Entry.place_forget()

        self.k2_askLbl_x.place_forget()
        self.k2_x_Entry.place_forget()
        self.k2_askLbl_y.place_forget()
        self.k2_y_Entry.place_forget()

        self.k3_askLbl_x.place_forget()
        self.k3_x_Entry.place_forget()
        self.k3_askLbl_y.place_forget()
        self.k3_y_Entry.place_forget()
        self.k3_askLbl_life.place_forget()
        self.k3_life_Entry.place_forget()

        self.k4_askLbl_x.place_forget()
        self.k4_x_Entry.place_forget()
        self.k4_askLbl_y.place_forget()
        self.k4_y_Entry.place_forget()

        # 再请客
        if mode_num == 0:
            self.k0_select_tb.place(relx=0, rely=1 / 20, relwidth=1 / 2, relheight=1 / 10)
            self.k0_select_lr.place(relx=1 / 2, rely=1 / 20, relwidth=1 / 2, relheight=1 / 10)
            self.k0_speed_ask.place(relx=0, rely=13 / 20, relwidth=1, relheight=1 / 20)
            self.k0_speed_get.place(relx=0, rely=7 / 10, relwidth=1, relheight=1 / 20)
            self.k0_start_pos_ask.place(relx=0, rely=15 / 20, relwidth=1, relheight=1 / 20)
            self.k0_x_get.place(relx=0, rely=4 / 5, relwidth=1 / 2, relheight=1 / 20)
            self.k0_y_get.place(relx=1 / 2, rely=4 / 5, relwidth=1 / 2, relheight=1 / 20)
        elif mode_num == 1:
            self.k1_askLbl_x.place(relx=0, rely=1 / 10, relwidth=1, relheight=1 / 10)
            self.k1_x_Entry.place(relx=0, rely=1 / 5, relwidth=1, relheight=1 / 10)
            self.k1_askLbl_y.place(relx=0, rely=2 / 5, relwidth=1, relheight=1 / 10)
            self.k1_y_Entry.place(relx=0, rely=1 / 2, relwidth=1, relheight=1 / 10)
        elif mode_num == 2:
            self.k2_askLbl_x.place(relx=0, rely=1 / 10, relwidth=1, relheight=1 / 10)
            self.k2_x_Entry.place(relx=0, rely=1 / 5, relwidth=1, relheight=1 / 10)
            self.k2_askLbl_y.place(relx=0, rely=2 / 5, relwidth=1, relheight=1 / 10)
            self.k2_y_Entry.place(relx=0, rely=1 / 2, relwidth=1, relheight=1 / 10)
        elif mode_num == 3:
            self.k3_askLbl_x.place(relx=0, rely=1 / 10, relwidth=1, relheight=1 / 10)
            self.k3_x_Entry.place(relx=0, rely=1 / 5, relwidth=1, relheight=1 / 10)
            self.k3_askLbl_y.place(relx=0, rely=2 / 5, relwidth=1, relheight=1 / 10)
            self.k3_y_Entry.place(relx=0, rely=1 / 2, relwidth=1, relheight=1 / 10)
            self.k3_askLbl_life.place(relx=0, rely=7 / 10, relwidth=1, relheight=1 / 10)
            self.k3_life_Entry.place(relx=0, rely=4 / 5, relwidth=1, relheight=1 / 10)
        elif mode_num == 4:
            self.k4_askLbl_x.place(relx=0, rely=1 / 10, relwidth=1, relheight=1 / 10)
            self.k4_x_Entry.place(relx=0, rely=1 / 5, relwidth=1, relheight=1 / 10)
            self.k4_askLbl_y.place(relx=0, rely=2 / 5, relwidth=1, relheight=1 / 10)
            self.k4_y_Entry.place(relx=0, rely=1 / 2, relwidth=1, relheight=1 / 10)

        global kind_selection
        kind_selection = mode_num
        self.main_window.update()

    # 这一部分完成左边选择栏的定义，设置和显示
    # noinspection PyAttributeOutsideInit
    def main1(self):
        # <插入：对img[i]的类型转换  (str)path => (tk.PhotoImage)obj>
        for i in range(len(imgs)):
            imgs[i] = tk.PhotoImage(file="./imgs/" + imgs[i])
        # </插入：对img[i]的类型转换  (str)path => (tk.PhotoImage)obj>

        self.canvasL = tk.Canvas(self.main_window, width=200, scrollregion=(0, 0, 200, 4830))  # 创建canvas
        self.frameL = tk.Frame(self.canvasL, width=200, height=4830)  # 把frame放在canvas里
        self.vbarL = tk.Scrollbar(self.canvasL, orient=tk.VERTICAL)  # 竖直滚动条

        self.vbarL.configure(command=self.canvasL.yview)
        self.canvasL.config(yscrollcommand=self.vbarL.set)  # 设置

        self.canvasL.place(anchor="nw", relx=0, rely=0, relheight=1)  # 放置canvas的位置
        self.vbarL.place(relx=0.9, width=20, relheight=1)
        self.canvasL.create_window((100, 2415), window=self.frameL)  # create_self.main_window (100, 2415)是指window的中心点坐标

        self.left_btns = [Left_button() for _ in range(len(imgs))]
        for i in range(len(imgs)):
            self.left_btns[i].set(root=self.frameL, img=imgs[i], num=i + 1)
            self.left_btns[i].place(x=0, y=105 * i)

    # 这一部分完成work_part除kind_part外所有部分的定义
    # noinspection PyAttributeOutsideInit
    def main2_1(self):
        # part 2:the work_part——the most of the window
        self.work_part = tk.Frame(self.main_window, width=600, height=600)
        self.right_part = tk.Frame(self.work_part)
        self.save_load_part = tk.Frame(self.right_part)
        self.control_part = tk.Frame(self.right_part)
        self.load_Btn = tk.Button(self.save_load_part, text="加载", command=self.load)
        self.save_Btn = tk.Button(self.save_load_part, text="保存", command=main_data_processor.save)
        self.control_part_Lbl = tk.Label(self.control_part, text="控件编辑")
        self.kind0 = tk.Button(self.control_part, text="移动的砖块")
        self.kind1 = tk.Button(self.control_part, text="障碍物")
        self.kind2 = tk.Button(self.control_part, text="玩家")
        self.kind3 = tk.Button(self.control_part, text="砖块")
        self.kind4 = tk.Button(self.control_part, text="墙")
        self.del_Btn = tk.Button(self.control_part, text="删除", command=self.del_Btn_clicked)
        self.fill_Btn = tk.Button(self.control_part, text="确定", command=self.fill_Btn_clicked)

    # 这一部分完成对kind_part的5种kind的所有布局的定义和设置（其显示是由reset_kind_part， reset_k0_kind_part负责的）
    # noinspection PyAttributeOutsideInit
    def main2_2(self):
        self.kind_part = tk.Frame(self.control_part)
        # kind0
        self.k0_select_tb = tk.Button(self.kind_part, text="纵向平移", command=lambda: self.reset_k0_kind_part(1))
        self.k0_select_lr = tk.Button(self.kind_part, text="横向平移", command=lambda: self.reset_k0_kind_part(2))

        self.k0_tmLbl = tk.Label(self.kind_part, text="（以坐标记）\n纵向平移的最高端")
        self.k0_tmVar = tk.StringVar()  # 获得纵向平移的最高值
        self.k0_tmEty = tk.Entry(self.kind_part, textvariable=self.k0_tmVar)

        self.k0_bmLbl = tk.Label(self.kind_part, text="纵向平移的最低端")
        self.k0_bmVar = tk.StringVar()  # 获得纵向平移的最低值
        self.k0_bmEty = tk.Entry(self.kind_part, textvariable=self.k0_bmVar)

        self.k0_lmLbl = tk.Label(self.kind_part, text="（以坐标记）\n横向平移的最左端")
        self.k0_lmVar = tk.StringVar()  # 获得横向平移的最左值
        self.k0_lmEty = tk.Entry(self.kind_part, textvariable=self.k0_lmVar)

        self.k0_rmLbl = tk.Label(self.kind_part, text="横向平移的最右端")
        self.k0_rmVar = tk.StringVar()  # 获得横向平移的最右值
        self.k0_rmEty = tk.Entry(self.kind_part, textvariable=self.k0_rmVar)

        self.k0_speed_ask = tk.Label(self.kind_part, text="速度（可为负）:")
        self.k0_speed_getVar = tk.StringVar()
        self.k0_speed_get = tk.Entry(self.kind_part, textvariable=self.k0_speed_getVar)

        self.k0_start_pos_ask = tk.Label(self.kind_part, text="初始位置:")
        self.k0_x_getVar = tk.StringVar()
        self.k0_x_get = tk.Entry(self.kind_part, textvariable=self.k0_x_getVar)
        self.k0_y_getVar = tk.StringVar()
        self.k0_y_get = tk.Entry(self.kind_part, textvariable=self.k0_y_getVar)

        # kind1
        self.k1_x_var = tk.StringVar()
        self.k1_x_Entry = tk.Entry(self.kind_part, textvariable=self.k1_x_var)
        self.k1_y_var = tk.StringVar()
        self.k1_y_Entry = tk.Entry(self.kind_part, textvariable=self.k1_y_var)
        self.k1_askLbl_x = tk.Label(self.kind_part, text="（以格数计）\n此障碍物的x坐标是：")
        self.k1_askLbl_y = tk.Label(self.kind_part, text="此障碍物的y坐标是：")

        # kind2
        self.k2_x_var = tk.StringVar()
        self.k2_x_Entry = tk.Entry(self.kind_part, textvariable=self.k2_x_var)
        self.k2_y_var = tk.StringVar()
        self.k2_y_Entry = tk.Entry(self.kind_part, textvariable=self.k2_y_var)
        self.k2_askLbl_x = tk.Label(self.kind_part, text="（以格数计）\n玩家的x坐标是：")
        self.k2_askLbl_y = tk.Label(self.kind_part, text="玩家的y坐标是：")

        # kind3
        self.k3_askLbl_x = tk.Label(self.kind_part, text="（以格数计）\n砖块的x坐标是：")
        self.k3_x_var = tk.StringVar()
        self.k3_x_Entry = tk.Entry(self.kind_part, textvariable=self.k3_x_var)

        self.k3_askLbl_y = tk.Label(self.kind_part, text="砖块的y坐标是：")
        self.k3_y_var = tk.StringVar()
        self.k3_y_Entry = tk.Entry(self.kind_part, textvariable=self.k3_y_var)

        self.k3_askLbl_life = tk.Label(self.kind_part, text="砖块的生命值是")
        self.k3_life_var = tk.StringVar()
        self.k3_life_Entry = tk.Entry(self.kind_part, textvariable=self.k3_life_var)

        # kind4
        self.k4_x_var = tk.StringVar()
        self.k4_x_Entry = tk.Entry(self.kind_part, textvariable=self.k4_x_var)
        self.k4_y_var = tk.StringVar()
        self.k4_y_Entry = tk.Entry(self.kind_part, textvariable=self.k4_y_var)
        self.k4_askLbl_x = tk.Label(self.kind_part, text="（以格数计）\n墙的x坐标是：")
        self.k4_askLbl_y = tk.Label(self.kind_part, text="墙的y坐标是：")

    # 完成work_part除kind_part外所有部分的设置
    # noinspection PyAttributeOutsideInit
    def main2_3(self):
        self.main_window.bind("<Configure>", self.resize_work)  # 绑定改变窗口大小事件以实时调整窗口大小
        self.kind0.config(command=lambda: self.reset_kind_part(0))
        self.kind1.config(command=lambda: self.reset_kind_part(1))
        self.kind2.config(command=lambda: self.reset_kind_part(2))
        self.kind3.config(command=lambda: self.reset_kind_part(3))
        self.kind4.config(command=lambda: self.reset_kind_part(4))

    # 完成work_part除kind_part外所有部分的显示
    # noinspection PyAttributeOutsideInit
    def main2_4(self):
        self.work_part.place(x=205, y=5)
        self.right_part.place(relx=4 / 5, y=0, relwidth=1 / 5, relheight=1)
        self.save_load_part.place(x=0, y=0, relwidth=1, relheight=1 / 12)
        self.load_Btn.place(x=0, y=0, relwidth=1 / 2, relheight=1)
        self.save_Btn.place(relx=1 / 2, y=0, relwidth=1 / 2, relheight=1)
        self.control_part.place(x=0, rely=1 / 12, relwidth=1, relheight=11 / 12)
        self.control_part_Lbl.place(x=0, y=0, relwidth=1, relheight=1 / 10)
        self.kind0.place(relx=0, rely=1 / 10, relwidth=1 / 2, relheight=1 / 20)
        self.kind1.place(relx=1 / 2, rely=1 / 10, relwidth=1 / 2, relheight=1 / 20)
        self.kind2.place(relx=0, rely=3 / 20, relwidth=1 / 3, relheight=1 / 20)
        self.kind3.place(relx=1 / 3, rely=3 / 20, relwidth=1 / 3, relheight=1 / 20)
        self.kind4.place(relx=2 / 3, rely=3 / 20, relwidth=1 / 3, relheight=1 / 20)
        self.del_Btn.place(relx=0, rely=9 / 10, relwidth=1 / 2, relheight=1 / 10)
        self.fill_Btn.place(relx=1 / 2, rely=9 / 10, relwidth=1 / 2, relheight=1 / 10)

        self.kind_part.place(relx=0, rely=1 / 5, relwidth=1, relheight=7 / 10)

    # 完成中间地图部分
    # noinspection PyAttributeOutsideInit
    def main3(self):
        self.map_part = tk.Canvas(self.work_part, scrollregion=(0, 0, 1500, 1000), bg="skyblue")
        self.map_part.bind("<Button-1>", self.click_to_choose_xy)
        self.map_part.bind("<Motion>", self.motion)


        self.vbar_mp_R = tk.Scrollbar(self.map_part, orient=tk.VERTICAL)  # 竖直滚动条:Right
        self.vbar_mp_B = tk.Scrollbar(self.map_part, orient=tk.HORIZONTAL)  # 水平滚动条:Bottom

        self.vbar_mp_R.config(command=self.map_part.yview)
        self.vbar_mp_B.config(command=self.map_part.xview)
        self.map_part.config(yscrollcommand=self.vbar_mp_R.set, xscrollcommand=self.vbar_mp_B.set)

        self.map_part.place(x=0, y=0, relwidth=4 / 5, relheight=1)
        self.vbar_mp_R.place(anchor="ne", relx=1, rely=0, width=20, relheight=1)
        self.vbar_mp_B.place(anchor="sw", relx=0, rely=1, height=20, relwidth=1)
        self.draw()

    # 处理加载按钮被按下的情况
    def load(self):
        main_data_processor.load()
        self.draw()

    # 向main_data_processor写入一个方块
    def write_in_a_block(self):
        if kind_selection == 0:
            if k0_kind_part == 1:
                main_data_processor.moving_bricks_data.append(
                    [0, int(self.k0_bmEty.get()), int(self.k0_tmEty.get()), int(self.k0_speed_get.get()), int(self.k0_x_get.get()), int(self.k0_y_get.get()), img_selection]
                )
            elif k0_kind_part == 2:
                main_data_processor.moving_bricks_data.append(
                    [1, int(self.k0_lmEty.get()), int(self.k0_rmEty.get()), int(self.k0_speed_get.get()), int(self.k0_x_get.get()), int(self.k0_y_get.get()), img_selection]
                )
        elif kind_selection == 1:
            main_data_processor.killers_data[
                int(self.k1_x_Entry.get()) + int(self.k1_y_Entry.get()) * 30] = img_selection
        elif kind_selection == 2:
            main_data_processor.player_data[
                int(self.k2_x_Entry.get()) + int(self.k2_y_Entry.get()) * 30] = img_selection
        elif kind_selection == 3:
            main_data_processor.bricks_data[int(self.k3_x_Entry.get()) + int(self.k3_y_Entry.get()) * 30] = brick[
                int(self.k3_life_Entry.get()) - 1]
        elif kind_selection == 4:
            main_data_processor.walls_data[int(self.k4_x_Entry.get()) + int(self.k4_y_Entry.get()) * 30] = img_selection

    # 从main_data_processor删除一个方块
    def delete_a_block(self):
        if kind_selection == 0:
            del main_data_processor.moving_bricks_data[int(self.k0_x_get.get())]
        elif kind_selection == 1:
            main_data_processor.killers_data[int(self.k1_x_Entry.get()) + int(self.k1_y_Entry.get()) * 30] = 0
        elif kind_selection == 2:
            main_data_processor.player_data[int(self.k2_x_Entry.get()) + int(self.k2_y_Entry.get()) * 30] = 0
        elif kind_selection == 3:
            main_data_processor.bricks_data[int(self.k3_x_Entry.get()) + int(self.k3_y_Entry.get()) * 30] = 0
        elif kind_selection == 4:
            main_data_processor.walls_data[int(self.k4_x_Entry.get()) + int(self.k4_y_Entry.get()) * 30] = 0

    # 处理确定按钮被按下的情况
    def fill_Btn_clicked(self):
        try:
            self.write_in_a_block()
        except ValueError:
            print("再常见不过的ValueError（这通常是因为用户的某一个对话框没有填）")
        self.draw()

    # 处理删除按钮按下的情况
    def del_Btn_clicked(self):
        try:
            self.delete_a_block()
        except ValueError:
            print("再常见不过的ValueError（这通常是因为用户的某一个对话框没有填）")
        self.draw()

    # 处理鼠标点击work_part选取坐标，以及标记选区（选位）
    def click_to_choose_xy(self, event):
        global kind_selection
        self.draw()
        # 以下代码来自https://blog.csdn.net/qq_41556318/article/details/85272026
        canvas = event.widget
        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        # 以上代码来自https://blog.csdn.net/qq_41556318/article/details/85272026
        if kind_selection == 0:
            self.k0_x_getVar.set(str(int(x/50*32)))
            self.k0_y_getVar.set(str(int(y/50*32)))
            self.map_part.create_oval(x-2, y-2, x+2, y+2, width=0, fill="red")
            return None  # 剩下的四种kind都绘制方块位置，故绘制放在大判断后。又为了不让此case也绘制方块，故强制停止
        elif kind_selection == 1:
            self.k1_x_var.set(str(
                int(x/1500*30)
            ))
            self.k1_y_var.set(str(
                int(y/1000*20)
            ))

        elif kind_selection == 2:
            self.k2_x_var.set(str(
                int(x / 1500 * 30)
            ))
            self.k2_y_var.set(str(
                int(y / 1000 * 20)
            ))
        elif kind_selection == 3:
            self.k3_x_var.set(str(
                int(x / 1500 * 30)
            ))
            self.k3_y_var.set(str(
                int(y / 1000 * 20)
            ))
        elif kind_selection == 4:
            self.k4_x_var.set(str(
                int(x / 1500 * 30)
            ))
            self.k4_y_var.set(str(
                int(y / 1000 * 20)
            ))
        self.map_part.create_rectangle(x//50*50, y//50*50, x//50*50+50, y//50*50+50, fill="red")

    # 处理鼠标移动的情况，并实时显示鼠标坐标
    def motion(self, event):
        # 以下代码来自https://blog.csdn.net/qq_41556318/article/details/85272026
        canvas = event.widget
        x = int(canvas.canvasx(event.x))
        x = int(x/50*32)
        y = int(canvas.canvasy(event.y))
        y = int(y/50*32)
        # 以上代码来自https://blog.csdn.net/qq_41556318/article/details/85272026
        self.pos_xy_showVar.set(str(x) + ", " + str(y))

    # 主画板显示
    def draw(self):
        global original_imgs, img, im, img_n
        img = [None for _ in range(300)]
        img_n = 0
        im = [None for _ in range(300)]

        self.map_part.delete("all")
        self.map_part.config(bg="Skyblue")
        for i in range(30):
            self.map_part.create_line(i * 50, 0, i * 50, 1000)
        for i in range(20):
            self.map_part.create_line(0, i * 50, 1500, i * 50)

        # moving bricks
        id = 0
        for i in main_data_processor.moving_bricks_data:
            # 绘制初始位置
            img[img_n] = Image.open(original_imgs[i[6] - 1]).resize((50, 50))
            im[img_n] = ImageTk.PhotoImage(img[img_n])
            self.map_part.create_image(i[4] / 960 * 1500 + 25, i[5] / 640 * 1000 + 25,
                                       image=im[img_n])
            # 标上方便（删除）的ID
            self.map_part.create_text(i[4] / 960 * 1500 + 25, i[5] / 640 * 1000 + 25,
                                      text="ID:"+str(id)
                                      )
            if i[0] == 1:
                # lr
                # 绘制标明位置的线段
                if i[3] > 0:
                    self.map_part.create_line(i[4] / 960 * 1500 + 25, i[5] / 640 * 1000 + 25,
                                              i[2] / 960 * 1500 + 25, i[5] / 640 * 1000 + 25, fill="red")
                    self.map_part.create_line(i[4] / 960 * 1500 + 25, i[5] / 640 * 1000 + 25,
                                              i[1] / 960 * 1500 + 25, i[5] / 640 * 1000 + 25, fill="blue")
                else:
                    self.map_part.create_line(i[4] / 960 * 1500 + 25, i[5] / 640 * 1000 + 25,
                                              i[2] / 960 * 1500 + 25, i[5] / 640 * 1000 + 25, fill="blue")
                    self.map_part.create_line(i[4] / 960 * 1500 + 25, i[5] / 640 * 1000 + 25,
                                              i[1] / 960 * 1500 + 25, i[5] / 640 * 1000 + 25, fill="red")
            else:
                # ud
                # 绘制标明位置的线段
                if i[3] > 0:
                    self.map_part.create_line(i[4] / 960 * 1500 + 25, i[5] / 640 * 1000 + 25,
                                              i[4] / 960 * 1500 + 25, i[2] / 640 * 1000 + 25, fill="red")
                    self.map_part.create_line(i[4] / 960 * 1500 + 25, i[5] / 640 * 1000 + 25,
                                              i[4] / 960 * 1500 + 25, i[1] / 640 * 1000 + 25, fill="blue")
                else:
                    self.map_part.create_line(i[4] / 960 * 1500 + 25, i[5] / 640 * 1000 + 25,
                                              i[4] / 960 * 1500 + 25, i[2] / 640 * 1000 + 25, fill="blue")
                    self.map_part.create_line(i[4] / 960 * 1500 + 25, i[5] / 640 * 1000 + 25,
                                              i[4] / 960 * 1500 + 25, i[1] / 640 * 1000 + 25, fill="red")
            img_n += 1
            id += 1
        del id

        # killer
        for i in range(600):
            if not main_data_processor.killers_data[i] == 0:
                img[img_n] = Image.open(original_imgs[main_data_processor.killers_data[i] - 1]).resize((50, 50))
                im[img_n] = ImageTk.PhotoImage(img[img_n])
                self.map_part.create_image(i % 30 * 50 + 25, i // 30 * 50 + 25, image=im[img_n])
                img_n += 1
        # player
        for i in range(600):
            if not main_data_processor.player_data[i] == 0:
                img[img_n] = Image.open(original_imgs[main_data_processor.player_data[i] - 1]).resize((50, 50))
                im[img_n] = ImageTk.PhotoImage(img[img_n])
                self.map_part.create_image(i % 30 * 50 + 25, i // 30 * 50 + 25, image=im[img_n])
                img_n += 1
        # bricks
        for i in range(600):
            if not main_data_processor.bricks_data[i] == 0:
                img[img_n] = Image.open(original_imgs[main_data_processor.bricks_data[i] - 1]).resize((100, 50))
                im[img_n] = ImageTk.PhotoImage(img[img_n])
                self.map_part.create_image(i % 30 * 50 + 50, i // 30 * 50 + 25, image=im[img_n])
                img_n += 1
        # walls
        for i in range(600):
            if not main_data_processor.walls_data[i] == 0:
                img[img_n] = Image.open(original_imgs[main_data_processor.walls_data[i] - 1]).resize((50, 50))
                im[img_n] = ImageTk.PhotoImage(img[img_n])
                self.map_part.create_image(i % 30 * 50 + 25, i // 30 * 50 + 25, image=im[img_n])
                img_n += 1

        self.main_window.update()


if __name__ == '__main__':
    app = App()
