'''
@Author  :   Frank
@License :   (C) Copyright 2023-2028
@Contact :
@Software:   slot
@File    :   game20001.py
@Time    :   2023/2/24
@Desc    :   这是一个标准的3*5的pay lines游戏的例子
'''
import time
from tqdm import tqdm
import paylines_compute_win as compute_win
import paylines_create_tuan as create_tuan
import tools
from copy import copy, deepcopy
DEBUG_ON = True
PACKAGE_NAME = 'game5001'
from colored_logs.logger import Logger, LogType

def pprint(str):
    if DEBUG_ON:
        print(str)
##############  保存赔率概率表的excel ####################
GAME5001_EXCEL = r"C:\\u\\doc\\game20001.xlsx"
GAME5001_OUT_PUT = r"C:\\u\\doc\\game20001.txt"
# 【可改】 随机生成的图案矩阵的最终赔率是否满足需要
# 满足的条件是：它与赔率数组（excel中指定的所有赔率）中指定的某个元素对应的赔率相差不大
# 相差不大的条件是：在其0.8 - 1.2倍左右，具体是由PV_MIN 和 PV_MAX来定的
PV_MIN = 0.8
PV_MAX = 1.2
# 【必改】 定义图案的行数和列数
REEL_LENGTH = 3  # matrix的高度，rows 行数
REEL_NUM = 5    # matrix的宽度，cols 列数

#################  供生成图案用  ########################
# 所有的图案
# 'A':樱桃   'B':柠檬  'C':橙子  'D':西梅
# 'E':西瓜   'F':葡萄  'G':星星  'H':7
TUAN_LIST = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
# 每个REEL上面的图案出现的权重
QUANZHONG_LIST_REELS = ((20, 15, 10, 20, 25, 25, 12, 15),
                        (15, 15, 10, 20, 25, 25, 12, 15),
                        (10, 20, 20, 20, 25, 20, 10, 15),
                        (10, 20, 20, 20, 20, 25, 10, 5),
                        (10, 10, 20, 15, 15, 10, 10, 5))
#################  供生成图案用  ########################

#################  供计算中奖情况用  ########################
# 图案的赔率表
TUAN_PL_MAP = {
    'A' : [0, 0.2, 0.8, 2, 8],
    'B' : [0, 0, 0.8, 2, 8],
    'C' : [0, 0, 0.8, 2, 8],
    'D' : [0, 0, 0.8, 2, 8],
    'E' : [0, 0, 2, 8, 20],
    'F' : [0, 0, 2, 8, 20],
    'G' : [0, 0, 2, 10, 50],
    'H' : [0, 0, 4, 40, 200]
}

# 每条支付线对应的矩阵坐标位置
PAYLINES = [[(1, 0), (1, 1), (1, 2), (1, 3), (1, 4)],
            [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)],
            [(2, 0), (2, 1), (2, 2), (2, 3), (2, 4)],
            [(0, 0), (1, 1), (2, 2), (1, 3), (0, 4)],
            [(2, 0), (1, 1), (0, 2), (1, 3), (2, 4)],

            [(1, 0), (2, 1), (2, 2), (2, 3), (1, 4)],
            [(1, 0), (0, 1), (0, 2), (0, 3), (1, 4)],
            [(0, 0), (0, 1), (1, 2), (2, 3), (2, 4)],
            [(2, 0), (2, 1), (1, 2), (0, 3), (0, 4)],
            [(0, 0), (1, 1), (1, 2), (1, 3), (0, 4)],

            [(2, 0), (1, 1), (1, 2), (1, 3), (2, 4)],
            [(0, 0), (1, 1), (0, 2), (1, 3), (0, 4)],
            [(2, 0), (1, 1), (2, 2), (1, 3), (2, 4)],
            [(1, 0), (0, 1), (1, 2), (0, 3), (1, 4)],
            [(1, 0), (2, 1), (1, 2), (2, 3), (1, 4)],

            [(1, 0), (1, 1), (0, 2), (1, 3), (1, 4)],
            [(1, 0), (1, 1), (2, 2), (1, 3), (1, 4)],
            [(0, 0), (2, 1), (0, 2), (2, 3), (0, 4)],
            [(2, 0), (0, 1), (2, 2), (0, 3), (2, 4)],
            [(1, 0), (0, 1), (2, 2), (0, 3), (1, 4)],

            [(1, 0), (2, 1), (0, 2), (2, 3), (1, 4)],
            [(0, 0), (0, 1), (2, 2), (0, 3), (0, 4)],
            [(2, 0), (2, 1), (0, 2), (2, 3), (2, 4)],
            [(0, 0), (2, 1), (2, 2), (2, 3), (0, 4)],
            [(2, 0), (0, 1), (0, 2), (0, 3), (2, 4)],]
#################  供计算中奖情况用  ########################




if __name__ == '__main__':
    log = Logger(ID=PACKAGE_NAME)
    pl_list, gl_list, pl_need_num_list = tools.get_pl_from_excel(GAME5001_EXCEL)
    num = sum(pl_need_num_list) # 需要生成的组合总数
    pl_get_num_list = [0] * len(pl_need_num_list)  # 保存一下每个赔率得到了多少个组合
    log.success("main: 总共需要 " + str(num) + "个组合")
    progress_bar = tqdm(total = num)
    # 跑多少组组合，一般来讲，跑满需要的赔率需要10W次以上
    with open(GAME5001_OUT_PUT,'w') as f:
        for i in range(1000):
            all_tuan = create_tuan.create_tuan_matrix(TUAN_LIST, QUANZHONG_LIST_REELS, REEL_LENGTH, REEL_NUM)
            win_res = compute_win.compute_win_for_tuan_matrix(all_tuan, PAYLINES, TUAN_PL_MAP)
            #pprint("**package:"+PACKAGE_NAME + "  **funtion main:"+ str(win_res))
            result = [deepcopy(win_res), deepcopy(all_tuan)]
            log.success("main: 得到一局结果 ")
            pprint("main: 这一局的详细数据是 " + str(result))
            f.writelines(str(result) +'\n')
            total_win = win_res[0]
            # 如果这一局中奖了，要看这局的中奖结果要加到哪个赔率那里
            if total_win > 0 :
                for i, value in enumerate(pl_list):
                    if tools.pl_is_match(total_win, pl_list,i, PV_MIN, PV_MAX):
                        # 只有某个赔率没有满的时候，才需要添加
                        if pl_get_num_list[i] < pl_need_num_list[i]:
                            pl_get_num_list[i] = pl_get_num_list[i] + 1
                            # tools.save_to_php() 需要后续完善
                            log.success("main: 第" + str(
                                i) + "个赔率已生成组合数 " + str(pl_get_num_list[i]) + "/" + str(pl_need_num_list[i]))
                            progress_bar.update(1)  # 进度条加1
            else: # 没中奖，就加到赔率为0的列表里
                pl_get_num_list[0] = pl_get_num_list[0] + 1
                progress_bar.update(1)  # 进度条加1
                # tools.save_to_php() 需要后续完善
                #log.success("main: 第1个赔率已生成组合数 " + str(pl_get_num_list[0]) + "/" + str(pl_need_num_list[0]))

            # 如果已经生成了所有需要的组合，则退出程序
            if sum(pl_get_num_list) >= num:
                break




