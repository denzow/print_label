#!/usr/bin/env python
# coding:utf-8
from __future__ import print_function, unicode_literals
import sys
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import csv
import re
# 設定系のサイズ
# はがきのサイズ
CANVAS_SIZE = (1480, 1000)
# 郵便はがき
VERTICAL_CANVAS_SIZE = (1000, 1480)
# 郵便番号のフォントサイズ
ADDRESS_NO_SIZE = 50
# 住所のフォントサイズの基準値
ADDRESS_SIZE = 60
# 宛名のフォントサイズの基準値
NAME_SIZE = 90

X_START_POSIT = 250
Y_START_POSIT = 300



class PrintLabel(object):
    """
    横書きのはがきや便箋に宛名を印刷するクラス
    """

    def __init__(self, address_data):
        # 住所データ
        self.address_data = address_data
        # ベース画像を真っ白で生成する
        self.img = PIL.Image.new("RGB", CANVAS_SIZE, (0xff, 0xff, 0xff))
        # レイヤ
        self.draw = PIL.ImageDraw.Draw(self.img)
        # 割とよく使うので先に取っておく
        self.img_size = list(self.img.size)
        # フォントファイルを取得
        self.font_file = "./font/Hannari.otf"
        # フォントを小さくする時の刻み幅
        self.decrement_size = 5
        # それぞれの文字のベースフォントサイズ
        # 文字長に応じて自動で縮小される
        self.address_no_size = ADDRESS_NO_SIZE
        self.address_size = ADDRESS_SIZE
        self.name_size = NAME_SIZE
        # 基準点
        self.write_posit = [X_START_POSIT, Y_START_POSIT]

    def print_label(self):
        """
        メインメソッド
        郵便番号、住所、宛名を描画するフロントメソッド
        :return:
        """
        self.print_address_no(self.address_no_size)
        self.print_address(self.address_size)
        self.print_name(self.name_size)
        return self.img

    def print_address_no(self, font_size):
        """
        郵便番号を描画する
        :param font_size:
        :return:
        """
        # 再帰処理なので、フォントが0未満になったら死ぬ
        if font_size < 0:
            raise Exception("Cannnot reduce size")
        # フォントを設定し、描画時の文字サイズを取得する
        self.draw.font = self.get_font(font_size)
        txt_size = list(self.draw.font.getsize(self.address_data["address_no"]))

        # もし横幅が足りないならサイズを下げてリトライ
        if self.write_posit[0] + txt_size[0] > self.img_size[0] - 30:
            return self.print_address_no(font_size - self.decrement_size)

        # 文字を書き込む
        self.draw.text(self.write_posit, self.address_data["address_no"], (0, 0, 0))
        # 書き込み位置を次に印刷する住所のためにずらす
        self.write_posit[0] += 50
        self.write_posit[1] += txt_size[1] + 10

    def print_address(self, font_size):
        """
        住所を描画する
        :param font_size:
        :return:
        """
        if font_size < 0:
            raise Exception("Cannnot reduce size")
        self.draw.font = self.get_font(font_size)
        txt_size = list(self.draw.font.getsize(self.address_data["address"]))
        # もし横幅が足りないならサイズを下げてリトライ
        if self.write_posit[0] + txt_size[0] > self.img_size[0] - 30:
            return self.print_address(font_size - self.decrement_size)

        self.draw.text(self.write_posit, self.address_data["address"], (0, 0, 0))
        # 書き込み位置を宛名のためにずらす。X軸はセンタリングするのでY軸だけ
        self.write_posit[1] += txt_size[1] + 10

    def print_name(self, font_size):
        """
        宛名を描画する
        :param font_size:
        :return:
        """
        if font_size < 0:
            raise Exception("Cannnot reduce size")
        self.draw.font = self.get_font(font_size)
        name_label = u"%s  %s 様" % (self.address_data["last_name"], self.address_data["first_name"])
        # 文字サイズの確認
        txt_size = list(self.draw.font.getsize(name_label))
        # センタリング
        pos = [(self.img_size[0] - txt_size[0]) / 2, (self.img_size[1] - txt_size[1]) / 2]
        # もし横幅が足りないならサイズを下げてリトライ
        if pos[0] + txt_size[0] > self.img_size[0] - 30:
            # 足りないならフォントサイズを下げてリトライ
            return self.print_name(font_size - self.decrement_size)

        # もし高さが足りないならサイズを下げてリトライ
        if pos[1] + txt_size[1] * (len(self.address_data["sub_first_name_list"]) + 1) > self.img_size[1] - 30:
            # 足りないならフォントサイズを5pt下げてリトライ
            return self.print_name(font_size - self.decrement_size)

        # Y軸はセンタリングしないのでX軸だけ上書きする
        self.write_posit[0] = pos[0]
        self.draw.text(self.write_posit, name_label, (0, 0, 0))
        # 次の行のために書きこみ位置をずらす
        self.write_posit[1] += txt_size[1] - 10
        # 連名の場合は苗字を省略するので
        last_name_spacer = re.sub(".", u"　", self.address_data["last_name"])
        for sub_name in self.address_data["sub_first_name_list"]:
            name_label = u"%s  %s 様" % (last_name_spacer, sub_name)
            self.draw.text(self.write_posit, name_label, (0, 0, 0))
            self.write_posit[1] += txt_size[1] - 10

    def get_font(self, size):
        """
        フォントとサイズを調整して戻す
        :param size:
        :return:
        """
        return PIL.ImageFont.truetype(self.font_file, size)


class PrintLabelVertical(object):
    """
    縦書きでハガキに宛名書きを行なうクラス
    """

    def __init__(self, address_data):
        self.address_data = address_data
        self.img = PIL.Image.new("RGB", VERTICAL_CANVAS_SIZE, (0xff, 0xff, 0xff))
        # レイヤ
        self.draw = PIL.ImageDraw.Draw(self.img)
        self.img_size = list(self.img.size)
        self.font_file = "./font/Hannari.otf"
        # フォントを小さくする時の刻み幅
        self.decrement_size = 5
        # はがきの郵便番号開始位置
        self.address_no_start_posit = (self.img_size[0] - 557, 120)

        self.address_size = ADDRESS_SIZE
        self.name_size = NAME_SIZE
        # 基準点
        self.write_posit = [VERTICAL_CANVAS_SIZE[0] - 100, 250]

    # フォントを割り当てるラッパー
    def get_font(self, size):
        return PIL.ImageFont.truetype(self.font_file, size)

    def print_label(self):
        self.print_frame()
        self.print_address_no()
        self.print_address(self.address_size)
        self.print_name(self.name_size)
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
        # 各枠は57 * 80 、間隔は13
        start_x = self.address_no_start_posit[0]
        start_y = self.address_no_start_posit[1]
        for i in range(7):
            self.draw.rectangle((start_x, start_y, start_x+57, start_y+80), fill=None, outline=(255, 0, 0))
            start_x += 70
            # 定義上、郵便番号の下4桁との間は少し開く
            if i == 2:
                start_x + 6

    def print_address_no(self):
        """
        郵便番号を枠に合わせて書き込む
        :return:
        """
        # フォントサイズは固定
        self.draw.font = self.get_font(80)
        write_posit = list(self.address_no_start_posit)
        write_posit[0] += 5
        for i, no in enumerate(self.address_data["address_no"].replace("-", "")):
            self.draw.text(write_posit, no, (0, 0, 0))
            # 1文字ずつずらして書いていく
            write_posit[0] += 70
            # 定義上、郵便番号の下4桁との間は少し開く
            if i == 2:
                write_posit[0] += 6

    def print_address(self, font_size):
        """
        住所を縦書きにする。書きこみ位置は右端
        :param font_size:
        :return:
        """
        self.write_vertical(self.address_data["address"], font_size, self.write_posit)

    def print_name(self, font_size):
        """
        名前を縦書きにする。書きこみ位置はセンター
        :param font_size:
        :return:
        """
        self.draw.font = self.get_font(font_size)
        name_label_list = []
        name_label = u"%s  %s 様" % (self.address_data["last_name"], self.address_data["first_name"])
        name_label_list.append(name_label)

        last_name_spacer = re.sub(".", u"　", self.address_data["last_name"])
        for sub_name in self.address_data["sub_first_name_list"]:
            sub_name_label = u"%s  %s 様" % (last_name_spacer, sub_name)
            name_label_list.append(sub_name_label)

        self.write_vertical_center(name_label_list, font_size, start_posit_y=self.write_posit[1] + 30)

    def write_vertical(self, text, font_size, start_posit):
        """
        文字を縦書きする
        :param text:
        :param font_size:
        :param start_posit:
        :return:
        """
        total_size = [0, 0]
        # 横棒は縦書きにできないのでそれっぽいのに置き換える
        text = text.replace("-", "丨").replace(u"ー", "丨")
        self.draw.font = self.get_font(font_size)
        write_posit = list(start_posit)
        # 縦書きした際の高さをチェック
        for character in text:
            txt_size = list(self.draw.font.getsize(character))
            # 文字列の高さと文字列の間の幅を加算していく
            total_size[1] += txt_size[1] - (font_size * 0.1)
            # 文字幅の最大長を取得
            if total_size[0] < txt_size[0]:
                total_size[0] = txt_size[0]

        # 高さ足りてる？
        if start_posit[1] + total_size[1] > self.img_size[1] - 30:
            return self.write_vertical(text, font_size - 5, start_posit)

        # サイズチェックをパスしたら実際に書く
        # 書きこみ位置をリセット
        write_posit = list(start_posit)
        for character in text:
            txt_size = list(self.draw.font.getsize(character))
            # 半角文字がずれるので幅みてずらす
            if total_size[0] > txt_size[0]:
                tmp_write_posit = write_posit[:]
                # 差分の半分だけX軸ずらせばセンタリングになる
                tmp_write_posit[0] += (total_size[0] - txt_size[0]) / 2
                self.draw.text(tmp_write_posit, character, (0, 0, 0))
            else:
                self.draw.text(write_posit, character, (0, 0, 0))
            # 次の文字のためずらす
            write_posit[1] += txt_size[1] - (font_size * 0.1)

        return total_size

    def write_vertical_center(self, text_list, font_size, start_posit_y):
        """
        センタリングして縦書きする
        :param text_list:
        :param font_size:
        :param start_posit_y:
        :return:
        """

        self.draw.font = self.get_font(font_size)
        # 最大の高さを確認スル
        max_str_length = max([len(text) for text in text_list])
        one_char_size = list(self.draw.font.getsize("　"))

        # 連名の場合もあるのでそのぶんを踏まえてセンタリング
        center_x = (self.img_size[0] - one_char_size[0] * len(text_list)) / 2
        # これは左端なので連名の場合は連名者からはじめる必要がある
        write_posit = [center_x, start_posit_y]

        # 高さ足りてる？
        if start_posit_y + one_char_size[1] * max_str_length > self.img_size[1] - 30:
            return self.write_vertical_center(text_list, font_size - 5, start_posit_y)

        for name in reversed(text_list):
            start_write_posit = write_posit[:]
            for character in name:
                txt_size = list(self.draw.font.getsize(character))
                # 半角文字がずれるので幅みてずらす
                if one_char_size[0] > txt_size[0]:
                    tmp_write_posit = start_write_posit[:]
                    # 差分の半分だけX軸ずらせばセンタリングになる
                    tmp_write_posit[0] += (one_char_size[0] - txt_size[0]) / 2
                    self.draw.text(tmp_write_posit, character, (0, 0, 0))
                else:
                    self.draw.text(start_write_posit, character, (0, 0, 0))

                start_write_posit[1] += txt_size[1] - (font_size * 0.1)

            write_posit[0] += one_char_size[0] - (font_size * 0.1)


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
        if line[2].decode("utf-8") == "同上":
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
        print("")
        print("usage:print_label.py <src_csv> <dest_dir> <mode: horizontal or vertical> ")
        print("")

        sys.exit(1)

    target_file = sys.argv[1]
    dest_dir = sys.argv[2]
    mode = "horizontal"

    if len(sys.argv) > 3:
        mode = sys.argv[3]
        if mode not in ["vertical", "horizontal"]:
            print("invalid mode")
            sys.exit(1)

    address_list = read_csv(target_file)
    for address_data in address_list:
        if mode == "horizontal":
            label = PrintLabel(address_data)
        else:
            label = PrintLabelVertical(address_data)

        label.print_label().show()
        break

if __name__ == u"__main__":
    do_main()

