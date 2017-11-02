# -*- coding: UTF-8 -*-

import re

f = open('result.txt','r')
item = f.read()

pattern_trendinggames = re.compile(r'<table id="trendinggames".*?>(.*?)</table>', re.S)
pattern_tr = re.compile(r'<tr>(.*?)</tr>', re.S)
pattern_td = re.compile(r'<td.*?>(.*?)</td>')
trendinggames = re.findall(pattern_trendinggames, item)[0]
games = re.findall(pattern_tr, trendinggames)

count = 0

game_list = []
game_dict = {}

for game in games:
    info = re.findall(pattern_td, game)
    print(info,game)
    if info != '':
        break
    game_info = []
    game_list.append(game_info)



print(len(game_list))

with open('result-item.txt','wt') as f:
    print(game_list,file=f)


    """<td>29</td>
<td data-order="Guardians of Ember"><a href=/app/463680><img src="http://cdn.akamai.steamstatic.com/steam/apps/463680/capsule_184x69.jpg" class="img-ss-list"> Guardians of Ember</a></td>
<td class="" data-order="2017-09-20">Sep 20, 2017</td>
<td data-order="1004">$10.04</td><td class="t768" data-order="15">15% (59%)</td><td class="t1024" data-order="44169">44,169 <font class="small">&plusmn;6,185</font></td><td class="t1300" data-order="4530.1283082077">4,530 <font class="small">&plusmn;1,981</font></td><td class="t1500" data-order="330">05:30 (02:15)</td></tr>
"""

    """1
<a href=/app/594570><img src="http://cdn.akamai.steamstatic.com/steam/apps/594570/capsule_184x69.jpg" class="img-ss-list"> Total War: WARHAMMER II</a>
Sep 28, 2017
$59.99
74% (90%/87%)
204,988 <font class="small">&plusmn;13,323</font>
23,330 <font class="small">&plusmn;4,495</font>
02:51 (10:52)


#	GAME	RELEASE DATE	
PRICE
SCORE RANK
(USERSCORE / METASCORE)
OWNERS
PLAYERS
1	PLAYERUNKNOWN'S BATTLEGROUNDS	Mar 23, 2017	$29.99	33% (73%)	12,550,720 ±102,839	9,605,005 ±90,260


"""