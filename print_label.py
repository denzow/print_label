#!/usr/bin/env python
# coding:utf-8
import numpy
import sys
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import csv
import re
# 設定系のサイズ
# はがきのサイズ
CANVAS_SIZE = (1800, 1200)
# 郵便はがき
VERTICAL_CANVAS_SIZE = (1000, 1480)
# 郵便番号のフォントサイズ
ADDRESS_NO_SIZE = 50
# 住所のフォントサイズの基準値
ADDRESS_SIZE = 60
# 宛名のフォントサイズの基準値
NAME_SIZE = 90

left_start_posit = 250
top_start_posit = 200



class PrintLabel(object):

    def __init__(self, address_data):
        self.address_data = address_data
        self.img = PIL.Image.new("RGB", CANVAS_SIZE, (0xff, 0xff, 0xff))
        # レイヤ
        self.draw = PIL.ImageDraw.Draw(self.img)
        self.img_size = numpy.array(self.img.size)
        self.font_file = "./font/Hannari.otf"
        # フォントを小さくする時の刻み幅
        self.decrement_size = 5

        self.address_no_size = ADDRESS_NO_SIZE
        self.address_size = ADDRESS_SIZE
        self.name_size = NAME_SIZE
        # 基準点
        self.write_posit = [left_start_posit, top_start_posit]

    # フォントを割り当てるラッパー
    def get_font(self, size):
        return PIL.ImageFont.truetype(self.font_file, size)

    def print_label(self):
        self.print_address_no(self.address_no_size)
        self.print_address(self.address_size)
        self.print_name(self.name_size)
        return self.img

    def print_address_no(self, font_size):
        if font_size < 0:
            raise Exception("Cannnot reduce size")
        self.draw.font = self.get_font(font_size)
        txt_size = numpy.array(self.draw.font.getsize(self.address_data["address_no"]))

        # X軸の調整
        if self.write_posit[0] + txt_size[0] > self.img_size[0] - 30:
            return self.print_address_no(font_size - self.decrement_size)

        self.draw.text(self.write_posit, self.address_data["address_no"], (0, 0, 0))
        # 書き込み位置をずらす
        self.write_posit[0] += 50
        self.write_posit[1] += txt_size[1] + 10

    def print_address(self, font_size):
        if font_size < 0:
            raise Exception("Cannnot reduce size")
        self.draw.font = self.get_font(font_size)
        txt_size = numpy.array(self.draw.font.getsize(self.address_data["address"]))
        # X軸の調整
        if self.write_posit[0] + txt_size[0] > self.img_size[0] - 30:
            return self.print_address(font_size - self.decrement_size)

        self.draw.text(self.write_posit, self.address_data["address"], (0, 0, 0))
        # 書き込み位置をずらす
        self.write_posit[0] += 50
        self.write_posit[1] += txt_size[1] + 10

    def print_name(self, font_size):
        if font_size < 0:
            raise Exception("Cannnot reduce size")
        self.draw.font = self.get_font(font_size)
        name_label = u"%s  %s 様" % (self.address_data["last_name"], self.address_data["first_name"])
        # 文字サイズの確認
        txt_size = numpy.array(self.draw.font.getsize(name_label))
        # センタリング
        pos = (self.img_size - txt_size) / 2
        # 幅足りる？
        if pos[0] + txt_size[0] > self.img_size[0] - 30:
            # 足りないならフォントサイズを5pt下げてリトライ
            return self.print_name(font_size - self.decrement_size)

        # 高さ足りる？
        if pos[1] + txt_size[1] * (len(self.address_data["sub_first_name_list"]) + 1) > self.img_size[1] - 30:
            # 足りないならフォントサイズを5pt下げてリトライ
            return self.print_name(font_size - self.decrement_size)

        # Y軸はセンタリングしないのでX軸だけ上書きする
        self.write_posit[0] = pos[0]
        self.draw.text(self.write_posit, name_label, (0, 0, 0))
        self.write_posit[1] += txt_size[1] - 10
        # 連名処理
        last_name_spacer = re.sub(".", u"　", self.address_data["last_name"])
        for sub_name in self.address_data["sub_first_name_list"]:
            name_label = u"%s  %s 様" % (last_name_spacer, sub_name)
            self.draw.text(self.write_posit, name_label, (0, 0, 0))
            self.write_posit[1] += txt_size[1] - 10


class PrintLabelVertical(object):

    def __init__(self, address_data):
        self.address_data = address_data
        self.img = PIL.Image.new("RGB", VERTICAL_CANVAS_SIZE, (0xff, 0xff, 0xff))
        # レイヤ
        self.draw = PIL.ImageDraw.Draw(self.img)
        self.img_size = numpy.array(self.img.size)
        self.font_file = "./font/Hannari.otf"
        # フォントを小さくする時の刻み幅
        self.decrement_size = 5
        # はがきの郵便番号開始位置
        self.address_no_start_posit = (self.img_size[0] - 557, 120)

        self.address_size = ADDRESS_SIZE
        self.name_size = NAME_SIZE
        # 基準点
        self.write_posit = [0, 0]

    # フォントを割り当てるラッパー
    def get_font(self, size):
        return PIL.ImageFont.truetype(self.font_file, size)

    def print_label(self):
        self.print_frame()
        self.print_address_no()
        #self.print_address(self.address_size)
        #self.print_name(self.name_size)
        return self.img

    def print_frame(self):
        """
        はがきのフレームを描画する
        :return:
        """
        # http://www.post.japanpost.jp/zipcode/zipmanual/p05.html
        # http://www.toryokohsoku.com/press/papersize/266.html
        # rectangle((左上点,右下点),塗つぶし色,線色)
        # 557,120
        start_x = self.address_no_start_posit[0]
        start_y = self.address_no_start_posit[1]
        for i in range(7):
            self.draw.rectangle((start_x, start_y, start_x+57, start_y+80), fill=None, outline=(255, 0, 0))
            start_x += 70
            if i == 2:
                start_x + 6

    def print_address_no(self):
        # フォントサイズ固定
        self.draw.font = self.get_font(80)
        write_posit = list(self.address_no_start_posit)
        write_posit[0] += 5
        for i, no in enumerate(self.address_data["address_no"].replace("-", "")):
            self.draw.text(write_posit, no, (0, 0, 0))
            write_posit[0] += 70
            if i == 2:
                write_posit[0] += 6

    def print_address(self, font_size):
        if font_size < 0:
            raise Exception("Cannnot reduce size")
        self.draw.font = self.get_font(font_size)
        txt_size = numpy.array(self.draw.font.getsize(self.address_data["address"]))
        # X軸の調整
        if self.write_posit[0] + txt_size[0] > self.img_size[0] - 30:
            return self.print_address(font_size - self.decrement_size)

        self.draw.text(self.write_posit, self.address_data["address"], (0, 0, 0))
        # 書き込み位置をずらす
        self.write_posit[0] += 50
        self.write_posit[1] += txt_size[1] + 10

    def print_name(self, font_size):
        if font_size < 0:
            raise Exception("Cannnot reduce size")
        self.draw.font = self.get_font(font_size)
        name_label = u"%s  %s 様" % (self.address_data["last_name"], self.address_data["first_name"])
        # 文字サイズの確認
        txt_size = numpy.array(self.draw.font.getsize(name_label))
        # センタリング
        pos = (self.img_size - txt_size) / 2
        # 幅足りる？
        if pos[0] + txt_size[0] > self.img_size[0] - 30:
            # 足りないならフォントサイズを5pt下げてリトライ
            return self.print_name(font_size - self.decrement_size)

        # 高さ足りる？
        if pos[1] + txt_size[1] * (len(self.address_data["sub_first_name_list"]) + 1) > self.img_size[1] - 30:
            # 足りないならフォントサイズを5pt下げてリトライ
            return self.print_name(font_size - self.decrement_size)

        # Y軸はセンタリングしないのでX軸だけ上書きする
        self.write_posit[0] = pos[0]
        self.draw.text(self.write_posit, name_label, (0, 0, 0))
        self.write_posit[1] += txt_size[1] - 10
        # 連名処理
        last_name_spacer = re.sub(".", u"　", self.address_data["last_name"])
        for sub_name in self.address_data["sub_first_name_list"]:
            name_label = u"%s  %s 様" % (last_name_spacer, sub_name)
            self.draw.text(self.write_posit, name_label, (0, 0, 0))
            self.write_posit[1] += txt_size[1] - 10

    def write_vertical(self, text, font_size):
        pass


def read_csv(csv_file_path):
    """
    utf-8のCSVファイルを開いてデータを整える
    :param csv_file_path:
    :return:
    """
    reader = csv.reader(open(csv_file_path))
    address_list = []
    """
    データ型
    address_data = {
        "last_name": "", # 苗字
        "first_name": "", # 名前
        "sub_first_name_list": [], # 子供などの連名用
        "address_no": "",
        "address":"",

    }
    """


    # 苗字,名前,郵便番号, 住所
    # 山田,一郎,999-999, 東京都千代田区1-1-1
    for line in reader:
        # 郵便番号の欄が同上かの判定
        if line[2] == "同上":
            # 一人前の併記として処理する
            address_list[-1]["sub_first_name_list"].append(line[1].decode("utf-8"))
            continue

        tmp_address_data = {
            "last_name": line[0].decode("utf-8"),
            "first_name": line[1].decode("utf-8"),
            "sub_first_name_list": [],
            "address_no": line[2].decode("utf-8"),
            "address": line[3].decode("utf-8"),
        }

        address_list.append(tmp_address_data)
    return address_list


# メイン
def do_main():
    # 引数処理
    if len(sys.argv) < 3:
        print ""
        print "usage:print_label.py <src_csv> <dest_dir>"
        print ""
        sys.exit(1)

    target_file = sys.argv[1]
    dest_dir = sys.argv[2]

    address_list = read_csv(target_file)
    for address_data in address_list:
        label = PrintLabelVertical(address_data)
        label.print_label().show()
        break


if __name__ == u"__main__":
    do_main()

