# coding: utf-8
import re
from datetime import datetime

import PySimpleGUI as sg
from timermute.db.MuteUserDB import MuteUserDB

from timermute.db.MuteWordDB import MuteWordDB


def popup_get_text(message, title=None, default_text='', password_char='', size=(None, None), button_color=None,
                   background_color=None, text_color=None, icon=None, font=None, no_titlebar=False,
                   grab_anywhere=False, keep_on_top=None, location=(None, None), relative_location=(None, None), image=None, modal=True):
    """sg.popup_get_text のラッパー

    Notes:
        テキストボックスにデフォルトでフォーカスをセットする
        image はサポートしていないので利用するときは追加すること
    """
    layout = [[sg.Text(message, auto_size_text=True, text_color=text_color, background_color=background_color)],
              [sg.Input(default_text=default_text, size=size, key="-INPUT-", password_char=password_char, focus=True)],
              [sg.Button("Ok", size=(6, 1), bind_return_key=True), sg.Button("Cancel", size=(6, 1))]]

    window = sg.Window(title=title or message, layout=layout, icon=icon, auto_size_text=True, button_color=button_color, no_titlebar=no_titlebar,
                       background_color=background_color, grab_anywhere=grab_anywhere, keep_on_top=keep_on_top, location=location, relative_location=relative_location, finalize=True, modal=modal, font=font)

    window["-INPUT-"].set_focus(True)

    button, values = window.read()
    window.close()
    del window
    if button != "Ok":
        return None
    else:
        path = values["-INPUT-"]
        return path


def update_mute_word_table(window: sg.Window, mute_word_db: MuteWordDB) -> None:
    """mute_word テーブルを更新する
    """
    # TODO::index保存

    # 画面表示更新
    mute_word_list = mute_word_db.select()
    mute_word_list_1 = [r for r in mute_word_list if r.status == "unmuted"]
    mute_word_list_2 = [r for r in mute_word_list if r.status == "muted"]

    def record_exclude_status(record):
        r_dict: dict = record.to_dict()
        del r_dict["status"]
        return list(r_dict.values())
    table_data = [record_exclude_status(r) for r in mute_word_list_1]
    window["-LIST_1-"].update(values=table_data)
    table_data = [record_exclude_status(r) for r in mute_word_list_2]
    window["-LIST_2-"].update(values=table_data)

    # 新着マイリストの背景色とテキスト色を変更する
    # update(values=list_data)で更新されるとデフォルトに戻る？
    # 強調したいindexのみ適用すればそれ以外はデフォルトになる
    # for i in include_new_index_list:
    #     window["-LIST-"].Widget.itemconfig(i, fg="black", bg="light pink")

    # indexをセットしてスクロール
    # scroll_to_indexは強制的にindexを一番上に表示するのでWidget.seeを使用
    # window["-LIST_1-"].Widget.see(index_1)
    # window["-LIST_1-"].update(set_to_index=index_1)
    return


def update_mute_user_table(window: sg.Window, mute_user_db: MuteUserDB) -> None:
    """mute_user テーブルを更新する
    """
    # TODO::index保存

    # 画面表示更新
    mute_user_list = mute_user_db.select()
    mute_user_list_1 = [r for r in mute_user_list if r.status == "unmuted"]
    mute_user_list_2 = [r for r in mute_user_list if r.status == "muted"]

    def record_exclude_status(record):
        r_dict: dict = record.to_dict()
        del r_dict["status"]
        return list(r_dict.values())
    table_data = [record_exclude_status(r) for r in mute_user_list_1]
    window["-LIST_3-"].update(values=table_data)
    table_data = [record_exclude_status(r) for r in mute_user_list_2]
    window["-LIST_4-"].update(values=table_data)

    # 新着マイリストの背景色とテキスト色を変更する
    # update(values=list_data)で更新されるとデフォルトに戻る？
    # 強調したいindexのみ適用すればそれ以外はデフォルトになる
    # for i in include_new_index_list:
    #     window["-LIST-"].Widget.itemconfig(i, fg="black", bg="light pink")

    # indexをセットしてスクロール
    # scroll_to_indexは強制的にindexを一番上に表示するのでWidget.seeを使用
    # window["-LIST_1-"].Widget.see(index_1)
    # window["-LIST_1-"].update(set_to_index=index_1)
    return


def update_all_table(window: sg.Window, mute_word_db, mute_user_db) -> None:
    """すべてのテーブルを更新する
    """
    # 現在選択中のマイリストがある場合そのindexを保存
    index = 0
    if window["-LIST-"].get_indexes():
        index = window["-LIST-"].get_indexes()[0]

    # マイリスト画面表示更新
    NEW_MARK = "*:"
    list_data = window["-LIST-"].Values
    m_list = mylist_db.select()
    include_new_index_list = []
    for i, m in enumerate(m_list):
        if m["is_include_new"]:
            m["showname"] = NEW_MARK + m["showname"]
            include_new_index_list.append(i)
    list_data = [m["showname"] for m in m_list]
    window["-LIST-"].update(values=list_data)

    # 新着マイリストの背景色とテキスト色を変更する
    # update(values=list_data)で更新されるとデフォルトに戻る？
    # 強調したいindexのみ適用すればそれ以外はデフォルトになる
    for i in include_new_index_list:
        window["-LIST-"].Widget.itemconfig(i, fg="black", bg="light pink")

    # indexをセットしてスクロール
    # scroll_to_indexは強制的にindexを一番上に表示するのでWidget.seeを使用
    # window["-LIST-"].update(scroll_to_index=index)
    window["-LIST-"].Widget.see(index)
    window["-LIST-"].update(set_to_index=index)
    return 0


def update_table_pane(window: sg.Window, mylist_db, mylist_info_db, mylist_url: str = "") -> int:
    """テーブルリストペインの表示を更新する

    Args:
        window (sg.Window): pysimpleguiのwindowオブジェクト
        mylist_db (MylistDBController): マイリストDBコントローラー
        mylist_info_db (MylistInfoDBController): 動画情報DBコントローラー
        mylist_url (str): 表示対象マイリスト

    Returns:
        int: 成功時0, エラー時-1
    """
    # 表示対象マイリストが空白の場合は
    # 右上のテキストボックスに表示されている現在のマイリストURLを設定する(window["-INPUT1-"])
    if mylist_url == "":
        mylist_url = window["-INPUT1-"].get()

    index = 0
    def_data = []
    table_cols_name = ["No.", "動画ID", "動画名", "投稿者", "状況", "投稿日時", "登録日時", "動画URL", "所属マイリストURL", "マイリスト表示名", "マイリスト名"]
    if mylist_url == "":
        # 引数も右上のテキストボックスも空白の場合
        # 現在表示しているテーブルの表示をリフレッシュする処理のみ行う
        def_data = window["-TABLE-"].Values  # 現在のtableの全リスト

        # 現在選択中のマイリストがある場合そのindexを保存
        index = 0
        if window["-LIST-"].get_indexes():
            index = window["-LIST-"].get_indexes()[0]
    else:
        # 現在のマイリストURLからlistboxのindexを求める
        m_list = mylist_db.select()
        mylist_url_list = [m["url"] for m in m_list]
        for i, url in enumerate(mylist_url_list):
            if mylist_url == url:
                index = i
                break

        # 現在のマイリストURLからテーブル情報を求める
        records = mylist_info_db.select_from_mylist_url(mylist_url)
        for i, m in enumerate(records):
            a = [i + 1, m["video_id"], m["title"], m["username"], m["status"], m["uploaded_at"], m["registered_at"], m["video_url"], m["mylist_url"]]
            def_data.append(a)

    # 画面更新
    # window["-LIST-"].update(set_to_index=index)
    window["-LIST-"].Widget.see(index)
    window["-TABLE-"].update(values=def_data)
    if len(def_data) > 0:
        window["-TABLE-"].update(select_rows=[0])
    # 1行目は背景色がリセットされないので個別に指定してdefaultの色で上書き
    window["-TABLE-"].update(row_colors=[(0, "", "")])
    return 0


if __name__ == "__main__":
    from timermute.ui.MainWindow import MainWindow
    mw = MainWindow()
    mw.run()