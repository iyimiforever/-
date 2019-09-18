"""
python3.6
env window10
"""
import sys
import time


# 模型
class Model(object):
    def __init__(self):
        self.start_time = time.time()
        self.end_time = None
        self.dim = None
        self.people_set = set()
        self.computer_set = set()
        self.people_color = None
        self.computer_color = None
        self.R_LIST = [(i, j) for i in range(-1, 2) for j in range(-1, 2)]
        self.R_LIST.remove((0, 0))  # 八个方向元组组成的列表


# 逻辑
class Controller(object):
    def __init__(self):
        self.model = Model()
        self.people_draw_or_not = 1
        self.computer_draw_or_not = 1

    def computer_turn(self):
        if len(self.model.people_set) + len(self.model.computer_set) == self.model.dim ** 2:
            self.__game_over()
        right_place = self.__legal_position(self.model.computer_set, self.model.people_set)
        if not right_place:
            if self.people_draw_or_not == 0:
                self.__game_over()
            else:
                self.computer_draw_or_not = 0
                print("电脑没有可以落子的位置")
                self.people_turn()
        position = tuple()
        turn_position = set()
        for key, value in right_place.items():
            if len(value) > len(turn_position):
                position = key
                turn_position = value
        self.__update_set("computer", position, right_place[position])
        self.computer_draw_or_not = 1
        self.print_table(position)
        self.people_turn()

    def people_turn(self):
        if len(self.model.people_set) + len(self.model.computer_set) == self.model.dim * self.model.dim:
            self.__game_over()
        right_place = self.__legal_position(self.model.people_set, self.model.computer_set)
        if not right_place:
            self.people_draw_or_not = 0
            if self.computer_draw_or_not == 0:
                self.__game_over()
            self.people_draw_or_not = 0
            print("玩家没有可以落子的位置")
            self.computer_turn()
        else:
            print("可落子的位置：", end="")
            for item in right_place:
                print(self.__turn_position_into_game(item), end=" ")
            print()
            chance = input("请输入下棋的位置:")
            position = self.__calculate_position(chance)
            if position not in right_place:
                self.people_turn()
            self.__update_set("people", position, right_place[position])
            self.people_draw_or_not = 1
            self.print_table()
            self.computer_turn()

    def __game_over(self):
        self.model.end_time = time.time()
        computer_number = len(self.model.computer_set)
        people_number = len(self.model.people_set)
        if computer_number > people_number:
            result = "玩家%d个棋子，电脑%d个棋子，电脑胜" % (people_number, computer_number)
        elif computer_number < people_number:
            result = "玩家%d个棋子，电脑%d个棋子，玩家胜" % (people_number, computer_number)
        else:
            result = "玩家%d个棋子，电脑%d个棋子，平局" % (people_number, computer_number)
        print(result)
        with open("黑白棋结果.txt", "a", encoding="utf-8") as f:
            f.write("游戏维度%d*%d\n" % (self.model.dim, self.model.dim))
            f.write("游戏开始时间：%s\n" % time.ctime(self.model.start_time))
            f.write("游戏持续时间：%d秒\n" % (self.model.end_time - self.model.start_time))
            f.write(result + "\n\n")
        sys.exit(0)

    def print_table(self, specious=None):
        for i in range(self.model.dim + 1):
            if i == 0:
                print("   ", end='')
                print(' '.join([str(chr(97 + x)) for x in range(self.model.dim)]))
            else:
                for j in range(self.model.dim + 1):
                    if j == 0 and i < 10:
                        print(" " + str(i), end=' ')
                    elif j == 0 and i >= 10:
                        print(i, end=' ')
                    else:
                        if (i, j) in self.model.people_set:
                            print(self.model.people_color, end=' ')
                        elif (i, j) in self.model.computer_set:
                            if (i, j) == specious:
                                print("\033[31m" + self.model.computer_color + "\033[0m", end=' ')
                                continue
                            print(self.model.computer_color, end=' ')
                        else:
                            print('.', end=' ')
                print()

    def __update_set(self, player, position, turn_position_list):
        if player == "people":
            self.model.people_set.add(position)
            self.model.people_set = self.model.people_set | set(turn_position_list)
            self.model.computer_set -= set(turn_position_list)
        else:
            self.model.computer_set.add(position)
            self.model.computer_set = self.model.computer_set | set(turn_position_list)
            self.model.people_set -= set(turn_position_list)

    def __calculate_position(self, chance):
        # "1a"->(1, 1)
        return (int(chance[:-1]), ord(chance[-1:]) - 96)

    def __turn_position_into_game(self, position):
        # (1, 1) -> "1a"
        return str(position[0]) + chr((96 + position[1]))

    def __legal_position(self, player, oppoplayer):
        """
        :param player: {}
        :param oppoplayer: {}
        :return: 字典 {可以落子位置：反转对手子的位置}
        """
        kong = [(i, j) for i in range(1, self.model.dim + 1) for j in range(1, self.model.dim + 1)]
        kong = set(kong) - self.model.computer_set - self.model.people_set
        p_player_list_in = {}  # 如果落在p，会有的夹在中间的反色子集合
        for p in kong:
            all_r_players_list_in = []  # 所有方向的反色夹在中间子的集合
            for r in self.model.R_LIST:
                _players_list_in = []  # 某一方向夹在中间反色子的集合
                i = 1
                lst = []
                while True:
                    if (p[0] + i * r[0], p[1] + i * r[1]) in oppoplayer:
                        lst.append(tuple([p[0] + i * r[0], p[1] + i * r[1]]))
                        i += 1
                        if (p[0] + i * r[0], p[1] + i * r[1]) in player:
                            _players_list_in += lst
                            break
                        if i > self.model.dim + 1:
                            break
                    else:
                        break
                if _players_list_in:  # 如果这个方向有夹在中间的反色子
                    all_r_players_list_in += _players_list_in
            if all_r_players_list_in:  # 如果落在p，会夹在中间的反色子集合[]
                p_player_list_in[p] = all_r_players_list_in
        return p_player_list_in


# 视图
class View(object):
    def __init__(self):
        self.controller = Controller()

    def main(self):
        self.__start()

    def __get_dim(self):
        self.controller.model.dim = int(input("请选择要棋盘的维度（偶数）："))
        if self.controller.model.dim % 2 == 1:
            self.__get_dim()
        return self.controller.model.dim

    def __get_first_or_not(self):
        turn = input("请选择先后顺序：\n0 表示玩家执白O先行，电脑执黑X后行\n1 表示电脑执白O先行，玩家执黑X后行\n")
        if turn == "0":
            self.controller.model.people_color = "O"
            self.controller.model.computer_color = "X"
            self.__qizi_init("O")
            self.controller.print_table()
            self.controller.people_turn()
        elif turn == "1":
            self.controller.model.people_color = "O"
            self.controller.model.computer_color = "X"
            self.__qizi_init("X")
            self.controller.computer_turn()

    def __qizi_init(self, color):
        if color == "O":
            self.controller.model.people_set = {(self.controller.model.dim/2+1, self.controller.model.dim/2), (self.controller.model.dim/2, self.controller.model.dim/2+1)}
            self.controller.model.computer_set = {(self.controller.model.dim/2, self.controller.model.dim/2), (self.controller.model.dim/2+1, self.controller.model.dim/2+1)}
        else:
            self.controller.model.people_set = {(self.controller.model.dim/2, self.controller.model.dim/2), (self.controller.model.dim/2+1, self.controller.model.dim/2+1)}
            self.controller.model.computer_set = {(self.controller.model.dim/2+1, self.controller.model.dim/2), (self.controller.model.dim/2, self.controller.model.dim/2+1)}

    def __start(self):
        self.controller.model.dim = self.__get_dim()
        self.__get_first_or_not()


if __name__ == '__main__':
    view = View()
    view.main()

"""
步骤：
初始化
人没下过 = 1
电脑没下过 = 1
选择棋盘的维度，需要是偶数：
选择先后顺序
选择人先，则people_set={}，集合中给people_color="O"
            computer_set={},集合中给computer_color="X"
            在people_set中添加（((x+1)/2,x/2),(x/2,(x+1)/2)）
            在computer_set中添加（(x/2,x/2),((x+1)/2,(x+1)/2)）
            打印
            人的回合
选择人后，则computer_set={},集合中给O
            people_set={}，集合中给X
            computer_set={},集合添加 （((x+1)/2,x/2),(x/2,(x+1)/2)）
            people_set={}，集合中添加（(x/2,x/2),((x+1)/2,(x+1)/2)）
            打印
            电脑回合


人的回合：
    if len(people_set)+len(computer_set)==维度**2：
        结束游戏
    判断人是否有位置可以下，（推荐位置）
    if 没有：
        人没下过 = 0
        if 电脑没下过 = 0
            结束游戏
        电脑的回合
    人下棋，是否在推荐位置中
    if 不是：
        重新下
    （计算需要翻转的棋子）
    更新人棋子
    人没下过=1
    打印棋盘

电脑回合
    if len(people_set)+len(computer_set)==维度**2：
        结束游戏
    判断电脑是否有位置可以下
    if 没有：
        电脑下过 = 0
        if 人没下过 = 0
            结束游戏
    列出位置
    计算各位置会翻转的棋子的个数｛（）：翻转个数｝
    选择翻转棋子最多的位置
    更新电脑棋子
    电脑没下过 = 1
    打印棋盘

游戏结束
    统计两个集合中元素的个数
    判断胜负
    打印游戏时间
"""
