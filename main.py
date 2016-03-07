#!/usr/bin/env python
# coding:utf-8
import numpy
import sys
import os
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import csv
import re
# 設定系のサイズ
canvas_size = (1800, 1200)
address_no_size = 50
address_size = 60
name_size = 90

left_start_posit = 250
top_start_posit = 300


# フォントを割り当てるラッパー
def get_font(size):
    return PIL.ImageFont.truetype("./font/Hannari.otf", size)


# 文字を画像として重ねる
# 郵便番号とアドレス用
def draw_text(draw, text, font_size, posit, img_size):
    if font_size < 0:
        raise Exception("Cannnot reduce size")
    draw.font = get_font(font_size)
    txt_size = numpy.array(draw.font.getsize(text))
    #print txt_size
    # 幅足りる？
    if posit[0] + txt_size[0] > img_size[0] - 30:
        draw_text(draw, text, font_size - 5 , posit, img_size)

    draw.text(posit, text, (0, 0, 0))

# 名前を描画する
def draw_name(draw, text, font_size, posit, img_size):
    if font_size < 0:
        raise Exception("Cannnot reduce size")
    draw.font = get_font(font_size)
    # 文字サイズの確認
    txt_size = numpy.array(draw.font.getsize(text))
    #print txt_size
    # センタリング
    pos = (img_size - txt_size) / 2
    # 幅足りる？
    if pos[0] + txt_size[0] > img_size[0]:
        # 足りないならフォントサイズを5pt下げてリトライ
        draw_text(draw, text, font_size - 5, posit, img_size)
    pos[1] = posit[1]
    draw.text(pos, text, (0, 0, 0))
    return pos

# 宛名全部を描画する関数。
# 内部では↑の関数を読んでいる
def draw_address(address_no, address, first_name, last_name, sub_name, sub_sub_name):
    img = PIL.Image.new("RGB", canvas_size, (0xff, 0xff, 0xff))
    draw = PIL.ImageDraw.Draw(img)
    # はがきのサイズ
    img_size = numpy.array(img.size)
    draw_text(draw, address_no, address_no_size, (left_start_posit, top_start_posit), img_size)
    draw_text(draw, address, address_size, (left_start_posit, top_start_posit + 90), img_size)
    name_pos = draw_name(draw, first_name + u"　" + last_name + u" 様", name_size, (left_start_posit, top_start_posit + 250), img_size)
    if sub_name:
        # 苗字をぜんぶ全角スペースに置換
        spacer = re.sub(".", u"　", first_name)
        name_pos[1] += 120
        draw_text(draw, spacer + u"　" + sub_name + u" 様", name_size, name_pos, img_size)
    if sub_sub_name:
        # 苗字をぜんぶ全角スペースに置換
        spacer = re.sub(".", u"　", first_name)
        name_pos[1] += 120
        draw_name(draw, spacer + u"　" + sub_sub_name + u" 様", name_size, name_pos, img_size)
    return img


# CSV読んでそれっぽいデータに整形して戻す
def read_csv(csv_file):
    reader = csv.reader(csv_file)
    address_list = []
    for line in reader:
        # 同上チェック
        # print line[2]
        # print line
        if line[2] == "同上":
            # 一人前の併記として処理する
            if not address_list[-1]["name3"]:
                address_list[-1]["name3"] = line[1].decode("utf-8")
            else:
                address_list[-1]["name4"] = line[1].decode("utf-8")
            continue
        # ひでぇ構造だ
        tmp_dict = {
            "name1": line[0].decode("utf-8"),
            "name2": line[1].decode("utf-8"),
            "name3": None,
            "name4": None,
            "address_no": line[2].decode("utf-8"),
            "address": line[3].decode("utf-8"),
        }
        address_list.append(tmp_dict)
    return address_list


# メイン
def do_main():
    target_file = sys.argv[1]
    dest_dir = sys.argv[2]
    # はがきのサイズ
    f = open(target_file)
    address_list = read_csv(f)
    for address in address_list:
        print(address["name1"] + address["name2"])
        img = draw_address(address["address_no"], address["address"], address["name1"], address["name2"], address["name3"], address["name4"])
        img.save(dest_dir+os.sep+address["name1"] + address["name2"]+".png")

if __name__ == "__main__":
    do_main()

