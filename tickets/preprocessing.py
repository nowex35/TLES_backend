import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib
import os

# 存在する列のみを削除する関数
def base_drop(df_name):
    columns_to_drop = ["Benefit", "Tax", "Total ticket price", "Wix service fee", "Ticket revenue", "Payment status", "Checked in"]
    existing_columns_to_drop = [col for col in columns_to_drop if col in df_name.columns]
    df_name.drop(columns=existing_columns_to_drop, inplace=True)
    
def ticket_drop(df_name):
    # Ticket numberの最後の一文字を除いた部分を新しい列に追加
    df_name['Ticket number base'] = df_name['Ticket number'].str[:-2]
    # Ticket number baseでグループ化し、重複している枚数分を新しい列「購入枚数」に格納
    df_name['重複枚数'] = df_name.groupby('Ticket number base')['Ticket number base'].transform('size')
    # 重複した行を削除（Ticket number baseで一意にする）
    df_name = df_name.drop_duplicates(subset='Ticket number base')
    df_name = df_name.drop(columns=['Ticket number base','Ticket number'])
    return df_name

def order_drop(df_name):
    # Order numberごとにチケット価格の合計を計算し、新しいカラム「合計チケット価格」に格納
    df_name['合計購入金額'] = df_name.groupby('Order number')['チケット価格'].transform('sum')
    # Order numberでグループ化し、重複している枚数分を新しい列「購入枚数」に格納
    df_name['購入枚数'] = df_name.groupby('Order number')['Order number'].transform('size')
    # 重複した行を削除（Order numberで一意にする）
    df_name = df_name.drop_duplicates(subset='Order number')
    df_name = df_name.drop(columns=['Ticket number base','Ticket number','チケット種類','座席種','チケット価格'])
    return df_name

def optional_drop(df_name):
    columns_to_drop = [
        "会場の様子を主催者等による広報で使用する場合があります/All photo will be used on SNS",
        "会場には駐車場がないので、近隣の有料駐車場を利用していただくか公共交通機関でお越しください/There is no parking available at the venue, so please use nearby paid parking facilities or consider using public transportation to get there。",
        "備考",
        "会場には駐車場がないので、近隣の有料駐車場を利用していただくか公共交通機関でお越しください/There is no parking available at the venue, so please use nearby paid parking facilities or consider using public transportation to get there.",
        "会場には駐車場がないので、公共交通機関でお越しください/No parking available",
        "居住地",
        "会場の様子は主催者等による広報で使用する場合があります/All photo will be used on SNS"
    ]
    existing_columns_to_drop = [col for col in columns_to_drop if col in df_name.columns]
    df_name.drop(columns=existing_columns_to_drop, inplace=True)
    

def full_drop(df_name):
    base_drop(df_name)
    optional_drop(df_name)

# 必要な列名を変更する関数
def base_rename(df_name):
    df_name.rename(columns={"Ticket type": "チケット種類", "Seat Information": "座席種", "Ticket price": "チケット価格", "カテゴリー/Category": "カテゴリー", "国籍/Country": "国籍", "学年/Grade": "学年","学年/Grade *筑波大生のみ必須/UT student MUST answer":"学年","学年（筑波大生のみ回答）/Grade(Only responses from Univ. of Tsukuba students)":"学年","学年/Grade※筑波大生のみ必須/UT student Must Answer":"学年","Order date":"購入日時","所属（学群生）/Affiliation *筑波大生のみ必須/UT student MUST answer":"所属","所属（学群生）/Affilliation※筑波大生のみ必須/UT student Must Answer":"所属","年代/Age":"年代","学群・学術院(筑波大生のみ回答)/Department・Graduate School":"所属","学群・学術院/Department・Graduate School":"所属"}, inplace=True)
    
def optional_rename(df_name):
    df_name.rename(columns={"Coupon":"クーポン有無","普段のスポーツ実施頻度/How often do you play sports?": "スポーツ実施頻度","普段のスポーツ観戦頻度/How often do you watch sports?":"スポーツ観戦頻度", "今回のTSUKUBA LIVE!を知ったきっかけ？/Where did you know about this TSUKUBA LIVE! ?": "知ったきっかけ","本イベントを知ったきっかけ？/Where did you learn about us?":"知ったきっかけ","本イベントを知ったきっかけ？（複数回答可）/Where did you learn about us?(multiple responses allowed)":"知ったきっかけ","本イベントを知ったきっかけ/Where did you learn about us?":"知ったきっかけ", "普段のスポーツ観戦頻度/How often do you watch sports?": "スポーツ観戦頻度","普段のバレーボール観戦頻度/How often do you watch volleyball?":"スポーツ観戦頻度","TSUKUBA LIVE!にこれまで何回来場したことがありますか？/How many times have you attended TSUKUBA LIVE! so far?":"来場回数","TSUKUBA LIVE!の参加回数/This is my 〇〇 arrival at TSUKUBA LIVE!":"来場回数","本イベントを知ったきっかけを教えてください。（複数回答可）/Where did you learn about us?(multiple responses allowed)":"知ったきっかけ",}, inplace=True)
    df_name.rename(columns={"普段のバスケットボール観戦頻度/How often do you watch basketball?":"開催競技観戦頻度"},inplace=True)

def full_rename(df_name):
    base_rename(df_name)
    optional_rename(df_name)
    
# データ名の修正
def revise_price_data(df_name):
    if "チケット価格" in df_name.columns:
        df_name["チケット価格"] = df_name["チケット価格"].astype(str)  # 非文字列データを文字列に変換
        df_name["チケット価格"] = df_name["チケット価格"].str.replace("¥", "").str.replace(",", "").astype(int)
    
def revise_coupon_data(df_name):
    if "クーポン有無" in df_name.columns:
        df_name["クーポン有無"] = df_name["クーポン有無"].astype(str)  # 非文字列データを文字列に変換
        df_name["クーポン有無"] = df_name["クーポン有無"].str.replace(r"^¥500.*", "クーポンあり", regex=True)
        df_name["クーポン有無"] = df_name["クーポン有無"].str.replace("nan", "クーポンなし")
        df_name.loc[df_name["クーポン有無"].isna(), "クーポン有無"] = "クーポンなし"

def revise_Category_data(df_name):
    if "カテゴリー" in df_name.columns:
        df_name["カテゴリー"] = df_name["カテゴリー"].str.replace("筑波大学学生/Univ. of Tsukuba Student", "筑波大生")
        df_name["カテゴリー"] = df_name["カテゴリー"].str.replace("その他/Others", "その他")
        df_name["カテゴリー"] = df_name["カテゴリー"].str.replace("筑波大学教職員/Univ. of Tsukuba Faculty and Staff", "筑波大教職員")
        df_name["カテゴリー"] = df_name["カテゴリー"].str.replace("つくば市在住/ Residents of Tsukuba City", "つくば市在住")
        df_name["カテゴリー"] = df_name["カテゴリー"].str.replace("つくば市在勤/ Commute to Work in Tsukuba City", "つくば市在勤")
        df_name["カテゴリー"] = df_name["カテゴリー"].str.replace("筑波大学OB/Univ. of Tsukuba alumnus", "卒業生")
        df_name["カテゴリー"] = df_name["カテゴリー"].str.replace("アルバータ大学関係者/University of Alberta associate", "アウェーチーム関係者")
    
def revise_Grade_data(df_name):
    if "学年" in df_name.columns:
        df_name["学年"] = df_name["学年"].str.replace("修士課程/Master's Course", "Master")
        df_name["学年"] = df_name["学年"].str.replace("博士課程/Ph.D", "Ph.D")
        df_name["学年"] = df_name["学年"].str.replace("筑波大生ではない/Not UT student", "筑波大生でない")
        df_name["学年"] = df_name["学年"].str.replace("-", "筑波大生でない")
    
def revise_reasons_data(df_name):
    if "知ったきっかけ" in df_name.columns:
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("前回のTSUKUBA LIVE!から知っていた/I knew it from the last TSUKUBA LIVE!", "前回から知っていた")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("前回のTSUKUBA LIVE!で知った/I knew it at the last TSUKUBA LIVE!", "前回のTL!で知った")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace(" 前回のTSUKUBA LIVE!の時から知っていた/knew from the last Home Game", "前回のTL!で知った")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("前回のTSUKUBA LIVE!の時から知っていた/knew from the last Home Game", "前回のTL!で知った")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("前回のTSUKUBA LIVE!から知っていた/I knew it from the latest TSUKUBA LIVE!", "前回のTL!で知った")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("家族・友人の紹介/from a friend・family", "家族・友人の紹介")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace(" 家族・友人の紹介/from a friend", "家族・友人の紹介")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("家族・友人の紹介/from a friend", "家族・友人の紹介")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("家族・友人の紹介/ from a friend・family", "家族・友人の紹介")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("選手の知り合い/friend of player", "選手の知人")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("女子バレーボール部員の紹介/Introduction from the women's volleyball team", "選手の知人")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("男子バレーボール部員の紹介/Introduction from the men's volleyball team", "選手の知人")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("男子バスケットボール部員の紹介/Introduction from the men's basketball team member", "選手の知人")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("男子バスケットボール部員の紹介/ Introduction from the men's basketball team member", "選手の知人")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("女子バスケットボール部員の紹介/Introduction from the women's basketball team member", "選手の知人")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("TSUKUBA LIVE! 運営スタッフの紹介/Introduction from the TSUKUBA LIVE! organizing staff", "クリエイターからの紹介")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("TSUKUBA LIVE! 運営スタッフの紹介/Introduction from the TSUKUBA LIVE! creators", "クリエイターからの紹介")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("TSUKUBA LIVE! 運営スタッフの紹介/ Introduction from the TSUKUBA LIVE! creators", "クリエイターからの紹介")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("メディアの記事を読んだ/from media", "メディアの記事")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("メディアの記事を読んだ/Read a media article", "メディアの記事")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("ポスター/poster", "ポスター")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("ポスター/ poster", "ポスター")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("チラシ/Flyer", "チラシ")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("チラシ/ Flyer", "チラシ")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("コズミくん/cosmicun", "コズミくん")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("コズミくん/ cosmicun", "コズミくん")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("SNS（コズミくん）/Cosmi-cun", "コズミくんSNS")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("SNS（コズミくん）/ Cosmi-cun", "コズミくんSNS")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("SNS (TSUKUBA LIVE!)", "TL!SNS")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace(" SNS（体育スポーツ局）/UT BPES", "スポーツ局SNS")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("SNS（体育スポーツ局）/UT BPES", "スポーツ局SNS")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("SNS (体育スポーツ局）/UT BPES", "スポーツ局SNS")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("コズミくんと会った/Met with Cosmicun.", "コズミくんと会った")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("今日オープンキャンパスで知った/Learned at today's Open Campus.", "オープンキャンパス")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace(" Twitter", "X")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("Twitter", "X")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("X (TSUKUBA LIVE! 公式)", "X")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("X（TSUKUBA LIVE! 公式）", "X")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("Instagram (TSUKUBA LIVE! 公式)", "Instagram")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("Instagram（TSUKUBA LIVE! 公式）", "Instagram")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("LINE (TSUKUBA LIVE! 公式)", "LINE")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("LINE（TSUKUBA LIVE! 公式）", "LINE")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("筑波大学女子バレボール部 公式SNS/Univ. of Tsukuba Women's Volleyball Team Official SNS", "チームSNS")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("筑波大学男子バスケットボール部 公式SNS/Univ. of Tsukuba men's basketball team official SNS", "チームSNS")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("筑波大学男子バスケットボール部 公式SNS/ Univ. of Tsukuba men's basketball team official SNS", "チームSNS")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("つくばユナイテッドSun GAIA 公式SNS/Tsukuba United Sun GAIA Official SNS", "スポンサー企業SNS")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("つくばユナイテッドSun GAIA関係者の紹介/Introduction from Tsukuba United Sun GAIA", "スポンサー企業からの紹介")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("カウントダウンボード/Countdown board", "カウントダウンボード")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("三角ポップ/Triangle pop-up sign", "三角ポップ")
        df_name["知ったきっかけ"] = df_name["知ったきっかけ"].str.replace("横断幕/Banner", "横断幕")
    
    
def revise_sports_watch_data(df_name):
    if "スポーツ観戦頻度" in df_name.columns:
        df_name["スポーツ観戦頻度"] = df_name["スポーツ観戦頻度"].astype(str).str.replace("月に2~3回程度/few/month", "24~36回/年")
        df_name["スポーツ観戦頻度"] = df_name["スポーツ観戦頻度"].astype(str).str.replace("月に2~3回程度　few/month", "24~36回/年")
        df_name["スポーツ観戦頻度"] = df_name["スポーツ観戦頻度"].astype(str).str.replace("月に1回/1/month", "12回/年")
        df_name["スポーツ観戦頻度"] = df_name["スポーツ観戦頻度"].astype(str).str.replace("月に1回　1/month", "12回/年")
        df_name["スポーツ観戦頻度"] = df_name["スポーツ観戦頻度"].astype(str).str.replace("2~3ヶ月に1回程度/1/few months", "4~6回/年")
        df_name["スポーツ観戦頻度"] = df_name["スポーツ観戦頻度"].astype(str).str.replace("2-3か月に1回程度/ 1/few months", "4~6回/年")
        df_name["スポーツ観戦頻度"] = df_name["スポーツ観戦頻度"].astype(str).str.replace("2~3ヶ月に1回程度　1/few months", "4~6回/年")
        df_name["スポーツ観戦頻度"] = df_name["スポーツ観戦頻度"].astype(str).str.replace("半年に1回程度/1/6months", "2回/年")
        df_name["スポーツ観戦頻度"] = df_name["スポーツ観戦頻度"].astype(str).str.replace("半年に1回程度/ 1/ 6months", "2回/年")
        df_name["スポーツ観戦頻度"] = df_name["スポーツ観戦頻度"].astype(str).str.replace("半年に1回程度　1/6months", "2回/年")
        df_name["スポーツ観戦頻度"] = df_name["スポーツ観戦頻度"].astype(str).str.replace("1年に1回程度/1/year", "1回/年")
        df_name["スポーツ観戦頻度"] = df_name["スポーツ観戦頻度"].astype(str).str.replace("1年に一回程度/ 1/year", "1回/年")
        df_name["スポーツ観戦頻度"] = df_name["スポーツ観戦頻度"].astype(str).str.replace("それ未満/less than 1/year", "1-回/年")
        df_name["スポーツ観戦頻度"] = df_name["スポーツ観戦頻度"].astype(str).str.replace("それ未満/ less than 1/year", "1-回/年")
        df_name["スポーツ観戦頻度"] = df_name["スポーツ観戦頻度"].astype(str).str.replace("それ未満　less than 1/6months", "1-回/年")
        df_name["スポーツ観戦頻度"] = df_name["スポーツ観戦頻度"].astype(str).str.replace("それ未満/less than 1/6months", "1-回/年")
        df_name["スポーツ観戦頻度"] = df_name["スポーツ観戦頻度"].astype(str).str.replace("週に1回以上/1+/week", "1~2回/週")
        df_name["スポーツ観戦頻度"] = df_name["スポーツ観戦頻度"].astype(str).str.replace("週に1回以上/ 1+/week", "1~2回/週")
        df_name["スポーツ観戦頻度"] = df_name["スポーツ観戦頻度"].astype(str).str.replace("週に1~2回　few/week", "1~2回/週")
        df_name["スポーツ観戦頻度"] = df_name["スポーツ観戦頻度"].astype(str).str.replace("週に3回以上　more than 3/week ", "3+/回週")
        # カンマで区切られている場合、最初の選択肢だけを選ぶ
        df_name["スポーツ観戦頻度"] = df_name["スポーツ観戦頻度"].apply(lambda x: x.split(',')[0] if ',' in x else x)
    
def revise_special_sports_watch_data(df_name):
    if "開催競技観戦頻度" in df_name.columns:
        df_name["開催競技観戦頻度"] = df_name["開催競技観戦頻度"].astype(str).str.replace("月に2~3回程度/few/month", "24~36回/年")
        df_name["開催競技観戦頻度"] = df_name["開催競技観戦頻度"].astype(str).str.replace("月に2~3回程度　few/month", "24~36回/年")
        df_name["開催競技観戦頻度"] = df_name["開催競技観戦頻度"].astype(str).str.replace("月に1回/1/month", "12回/年")
        df_name["開催競技観戦頻度"] = df_name["開催競技観戦頻度"].astype(str).str.replace("月に1回　1/month", "12回/年")
        df_name["開催競技観戦頻度"] = df_name["開催競技観戦頻度"].astype(str).str.replace("2~3ヶ月に1回程度/1/few months", "4~6回/年")
        df_name["開催競技観戦頻度"] = df_name["開催競技観戦頻度"].astype(str).str.replace("2-3か月に1回程度/ 1/few months", "4~6回/年")
        df_name["開催競技観戦頻度"] = df_name["開催競技観戦頻度"].astype(str).str.replace("2~3ヶ月に1回程度　1/few months", "4~6回/年")
        df_name["開催競技観戦頻度"] = df_name["開催競技観戦頻度"].astype(str).str.replace("半年に1回程度/1/6months", "2回/年")
        df_name["開催競技観戦頻度"] = df_name["開催競技観戦頻度"].astype(str).str.replace("半年に1回程度/ 1/ 6months", "2回/年")
        df_name["開催競技観戦頻度"] = df_name["開催競技観戦頻度"].astype(str).str.replace("半年に1回程度　1/6months", "2回/年")
        df_name["開催競技観戦頻度"] = df_name["開催競技観戦頻度"].astype(str).str.replace("1年に1回程度/1/year", "1回/年")
        df_name["開催競技観戦頻度"] = df_name["開催競技観戦頻度"].astype(str).str.replace("1年に一回程度/ 1/year", "1回/年")
        df_name["開催競技観戦頻度"] = df_name["開催競技観戦頻度"].astype(str).str.replace("それ未満/less than 1/year", "1-回/年")
        df_name["開催競技観戦頻度"] = df_name["開催競技観戦頻度"].astype(str).str.replace("それ未満/ less than 1/year", "1-回/年")
        df_name["開催競技観戦頻度"] = df_name["開催競技観戦頻度"].astype(str).str.replace("それ未満　less than 1/6months", "1-回/年")
        df_name["開催競技観戦頻度"] = df_name["開催競技観戦頻度"].astype(str).str.replace("週に1回以上/1+/week", "1~2回/週")
        df_name["開催競技観戦頻度"] = df_name["開催競技観戦頻度"].astype(str).str.replace("週に1回以上/ 1+/week", "1~2回/週")
        df_name["開催競技観戦頻度"] = df_name["開催競技観戦頻度"].astype(str).str.replace("週に1~2回　few/week", "1~2回/週")
        df_name["開催競技観戦頻度"] = df_name["開催競技観戦頻度"].astype(str).str.replace("週に3回以上　more than 3/week ", "3+/回週")
        # カンマで区切られている場合、最初の選択肢だけを選ぶ
        df_name["開催競技観戦頻度"] = df_name["開催競技観戦頻度"].apply(lambda x: x.split(',')[0] if ',' in x else x)
    
def revise_sports_play_data(df_name):
    if "スポーツ実施頻度" in df_name.columns:
        df_name["スポーツ実施頻度"] = df_name["スポーツ実施頻度"].astype(str)
        df_name["スポーツ実施頻度"] = df_name["スポーツ実施頻度"].str.replace("週に3回以上/more than 3/week", "3回+/週")
        df_name["スポーツ実施頻度"] = df_name["スポーツ実施頻度"].str.replace("週に3回以上　more than 3/week ", "3回+/週")
        df_name["スポーツ実施頻度"] = df_name["スポーツ実施頻度"].str.replace("週に1~2回/few/week", "1~2回/週")
        df_name["スポーツ実施頻度"] = df_name["スポーツ実施頻度"].str.replace("週に1~2回　few/week", "1~2回/週")
        df_name["スポーツ実施頻度"] = df_name["スポーツ実施頻度"].str.replace("月に1回/1/month", "1回/月")
        df_name["スポーツ実施頻度"] = df_name["スポーツ実施頻度"].str.replace("月に1回　1/month", "1回/月")
        df_name["スポーツ実施頻度"] = df_name["スポーツ実施頻度"].str.replace("2~3ヶ月に1回程度/1/few months", "1回/2~3カ月")
        df_name["スポーツ実施頻度"] = df_name["スポーツ実施頻度"].str.replace("2~3ヶ月に1回程度　1/few months", "1回/2~3カ月")
        df_name["スポーツ実施頻度"] = df_name["スポーツ実施頻度"].str.replace("それ未満/less than 1/few months", "1回-/2~3カ月")
        df_name["スポーツ実施頻度"] = df_name["スポーツ実施頻度"].str.replace("それ未満　less than 1/few months", "1回-/2~3カ月")
        # カンマで区切られている場合、最初の選択肢だけを選ぶ
        df_name["スポーツ実施頻度"] = df_name["スポーツ実施頻度"].apply(lambda x: x.split(',')[0] if ',' in x else x)
    
def revise_OrderDate_data(df_name):
    df_name["購入日時"] = pd.to_datetime(df_name["購入日時"]).dt.strftime('%Y/%m/%d %H:%M')
    
def additional_revise(df_name):
    if "性別" in df_name.columns:
        df_name["性別"] = df_name["性別"].str.replace("女性/Woman", "女性")
        df_name["性別"] = df_name["性別"].str.replace("男性/Man", "男性")
        df_name["性別"] = df_name["性別"].str.replace("男性, 女性", "その他")
        df_name["性別"] = df_name["性別"].str.replace("女性, 男性", "その他")
        df_name["性別"] = df_name["性別"].str.replace("その他/Others", "その他")
    if "カテゴリー" in df_name.columns:
        df_name["カテゴリー"] = df_name["カテゴリー"].astype(str)
        df_name["カテゴリー"] = df_name["カテゴリー"].apply(lambda x: "筑波大生" if "筑波大生" in x else x)
        df_name["カテゴリー"] = df_name["カテゴリー"].apply(lambda x: "筑波大教職員" if "筑波大教職員" in x else x)
        df_name["カテゴリー"] = df_name["カテゴリー"].apply(lambda x: "つくば市在住" if "つくば市在住" in x else x)
        df_name["カテゴリー"] = df_name["カテゴリー"].apply(lambda x: "つくば市在勤" if "つくば市在勤務" in x else x)
    df_name["座席種"] = df_name["座席種"].str.replace("Area: ", "")

    # df_name["カテゴリー"] = df_name["カテゴリー"].str.replace("筑波大教職員, つくば市在住", "筑波大教職員")#筑波大生＞筑波大教職員＞つくば市在住＞つくば市在勤＞その他
    if "学年" in df_name.columns:
        df_name["学年"] = df_name["学年"].str.replace("1年, 筑波大生でない", "他大生")
        df_name["学年"] = df_name["学年"].str.replace("2年, 筑波大生でない", "他大生")
        df_name["学年"] = df_name["学年"].str.replace("3年, 筑波大生でない", "他大生")
        df_name["学年"] = df_name["学年"].str.replace("4年, 筑波大生でない", "他大生")
        df_name["学年"] = df_name["学年"].str.replace("U1", "1年")
        df_name["学年"] = df_name["学年"].str.replace("1年/Freshman", "1年")
        df_name["学年"] = df_name["学年"].str.replace("1年/Freshman", "1年")
        df_name["学年"] = df_name["学年"].str.replace("U2", "2年")
        df_name["学年"] = df_name["学年"].str.replace("2年/Sophomore", "2年")
        df_name["学年"] = df_name["学年"].str.replace("U3", "3年")
        df_name["学年"] = df_name["学年"].str.replace("3年/Junior", "3年")
        df_name["学年"] = df_name["学年"].str.replace("U4", "4年")
        df_name["学年"] = df_name["学年"].str.replace("4年/Senior", "4年")
        df_name["学年"] = df_name["学年"].str.replace("M1", "Master")
        df_name["学年"] = df_name["学年"].str.replace("M2", "Master")
        df_name["学年"] = df_name["学年"].str.replace("D(博士課程）", "Ph.D")
        df_name["学年"] = df_name["学年"].str.replace("D1", "Ph.D")
        df_name["学年"] = df_name["学年"].str.replace("D2", "Ph.D")
        df_name["学年"] = df_name["学年"].apply(lambda x: "Master" if "Master" in x else x)
        if "カテゴリー" in df_name.columns:
            df_name['学年'] = df_name.apply(lambda row: "筑波大生でない" if (row['カテゴリー'] != "筑波大生") else row['学年'],axis=1)
        df_name["学年"] = df_name["学年"].apply(lambda x: x.split(',')[0] if ',' in x else x)
    
    if "所属" in df_name.columns:
        df_name["所属"] = df_name["所属"].str.replace("-", "筑波大生でない")
        df_name["所属"] = df_name["所属"].str.replace("筑波大生ではない/Not UT student", "筑波大生でない")
        df_name["所属"] = df_name["所属"].str.replace("人文・文化学群/School of Humanities and Culture", "人文・文化学群")
        df_name["所属"] = df_name["所属"].str.replace("社会・国際学群/School of Social and International Studies", "社会・国際学群")
        df_name["所属"] = df_name["所属"].str.replace("人間学群/ School of Human Sciences", "人間学群")
        df_name["所属"] = df_name["所属"].str.replace("生命環境学群/School of Life and Environmental Sciences", "生命環境学群")
        df_name["所属"] = df_name["所属"].str.replace("理工学群/School of Science and Engineering", "理工学群")
        df_name["所属"] = df_name["所属"].str.replace("情報学群/School of Informatics", "情報学群")
        df_name["所属"] = df_name["所属"].str.replace("医学群/School of Medicine and Medical Sciences", "医学群")
        df_name["所属"] = df_name["所属"].str.replace("体育専門学群/School of Health and Physical Education", "体育専門学群")
        df_name["所属"] = df_name["所属"].str.replace("芸術専門学群/School of Art and Design", "芸術専門学群")
        df_name["所属"] = df_name["所属"].str.replace("総合学域群/School of Comprehensive Studies", "総合学域群")
        df_name["所属"] = df_name["所属"].str.replace("人文社会ビジネス科学学術院/Graduate School of Business Sciences, Humanities and Social Sciences", "人文社会ビジネス科学学術院")
        df_name["所属"] = df_name["所属"].str.replace("人文社会ビジネス科学学術院/Graduate School of Business Sciences Humanities and Social Sciences", "人文社会ビジネス科学学術院")
        df_name["所属"] = df_name["所属"].str.replace("理工情報生命学術院/Graduate School of Science and Technology", "理工情報生命学術院")
        df_name["所属"] = df_name["所属"].str.replace("人間総合科学学術院/Graduate School of Comprehensive Human Sciences", "人間総合科学学術院")
        df_name["所属"] = df_name["所属"].str.replace("グローバル教育院/School of Integrative and Global Majors", "グローバル教育院")
        # カンマで区切られている場合、最初の選択肢だけを選ぶ
        df_name["所属"] = df_name["所属"].fillna("").apply(lambda x: x.split(',')[0] if ',' in x else x)
        
    # スポーツ観戦頻度の列で、コンマで区切られた最初の選択肢のみを取得
    if "スポーツ観戦頻度" in df_name.columns:
        df_name["スポーツ観戦頻度"] = df_name["スポーツ観戦頻度"].apply(lambda x: x.split(',')[0])
    # スポーツ実施頻度の列で、コンマで区切られた最初の選択肢のみを取得
    if "スポーツ実施頻度" in df_name.columns:
        df_name["スポーツ実施頻度"] = df_name["スポーツ実施頻度"].apply(lambda x: x.split(',')[0])
    if "来場回数" in df_name.columns:
        df_name["来場回数"] = df_name["来場回数"].str.replace("1月2日","1~2")
        df_name["来場回数"] = df_name["来場回数"].str.replace("3月4日","3~4")
        df_name["来場回数"] = df_name["来場回数"].str.replace("5月6日","5~6")
        
def revise_age_data(df_name):
    if "年代" in df_name.columns:
        df_name["年代"] = df_name["年代"].str.replace("18歳以下/Under18", "18歳以下")
        df_name["年代"] = df_name["年代"].str.replace("18歳以下/Under 18", "18歳以下")
        df_name["年代"] = df_name["年代"].str.replace("10 - 19歳", "18歳以下")
        df_name["年代"] = df_name["年代"].str.replace("10代", "18歳以下")
        df_name["年代"] = df_name["年代"].str.replace("20代", "19&20代")
        df_name["年代"] = df_name["年代"].str.replace("20 - 29歳", "19&20代")
        df_name["年代"] = df_name["年代"].str.replace("19歳・20代/19 - 20s", "19&20代")
        df_name["年代"] = df_name["年代"].str.replace("30 - 39歳", "30代")
        df_name["年代"] = df_name["年代"].str.replace("30代/30s", "30代")
        df_name["年代"] = df_name["年代"].str.replace("40 - 49歳", "40代")
        df_name["年代"] = df_name["年代"].str.replace("40代/40s", "40代")
        df_name["年代"] = df_name["年代"].str.replace("50 - 59歳", "50代")
        df_name["年代"] = df_name["年代"].str.replace("50代/50s", "50代")
        df_name["年代"] = df_name["年代"].str.replace("50代/50s", "50代")
        df_name["年代"] = df_name["年代"].str.replace("60 - 69歳", "60代")
        df_name["年代"] = df_name["年代"].str.replace("60代/60s", "60代")
        df_name["年代"] = df_name["年代"].str.replace("70代以上/70 and over", "70代以上")
        df_name["年代"] = df_name["年代"].str.replace("70 歳以上", "70代以上")
        df_name["年代"] = df_name["年代"].str.replace("18歳以下, 50代", "50代")
        df_name["年代"] = df_name["年代"].str.replace("19歳・20代/19 - 20s, 18歳以下", "19&20代")
        df_name["年代"] = df_name["年代"].str.replace("18歳以下, 19歳・20代/19 - 20s,", "19&20代")
        df_name["年代"] = df_name["年代"].str.replace("30代, 18歳以下", "30代")
        df_name["年代"] = df_name["年代"].str.replace("40代, 18歳以下", "40代")
        df_name["年代"] = df_name["年代"].str.replace("50代, 18歳以下", "50代")
        df_name["年代"] = df_name["年代"].str.replace("60代, 18歳以下", "60代")
        df_name["年代"] = df_name["年代"].str.replace("70代, 18歳以下", "70代")
        df_name["年代"] = df_name["年代"].str.replace("18歳以下/Under18, 19歳・20代/19 - 20s", "19&20代")
        df_name["年代"] = df_name["年代"].str.replace("18歳以下, 30代", "30代")
        df_name["年代"] = df_name["年代"].str.replace("18歳以下, 40代", "40代")
        df_name["年代"] = df_name["年代"].str.replace("18歳以下, 60代", "60代")
        df_name["年代"] = df_name["年代"].str.replace("18歳以下, 70代", "70代")
        df_name["年代"] = df_name["年代"].str.replace("18歳以下, 70代以上", "70代以上")
        df_name.loc[df_name["年代"].str.contains("19&20代", na=False), "年代"] = "19&20代"


def full_revise(df_name):
    revise_price_data(df_name)
    revise_coupon_data(df_name)
    revise_Category_data(df_name)
    revise_Grade_data(df_name)
    if "購入日時" in df_name.columns:
        revise_OrderDate_data(df_name)
    revise_reasons_data(df_name)
    revise_sports_watch_data(df_name)
    revise_special_sports_watch_data(df_name)
    revise_sports_play_data(df_name)
    revise_age_data(df_name)

# データフレームの操作
def allpreprocessing(df_name):
    full_drop(df_name)
    full_rename(df_name)
    full_revise(df_name)
    additional_revise(df_name)
    df_name = ticket_drop(df_name)
    return df_name

# データフレームの操作
def allpreprocessing_full(df_name):
    full_drop(df_name)
    full_rename(df_name)
    full_revise(df_name)
    additional_revise(df_name)
    return df_name

def allpreprocessing_customer(df_name):
    full_drop(df_name)
    full_rename(df_name)
    full_revise(df_name)
    additional_revise(df_name)
    df_name = order_drop(df_name)
    return df_name
