# coding: utf-8

from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os


def chinese_word_cloud():
    font = r'SourceHanSansCN-Light.otf'
    path = 'result/text'
    texts = os.listdir(path)
    for text in texts:
        file_path = path + '/' + text
        print(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if content:
                wc = WordCloud(collocations=False, font_path=font, width=1400, height=1400, margin=2).generate(content.lower())

                plt.imshow(wc)
                plt.axis("off")
                plt.show()
                text = text.split('.')[0]
                wc.to_file('result/image/{}.png'.format(text))  # 把词云保存下来

chinese_word_cloud()
