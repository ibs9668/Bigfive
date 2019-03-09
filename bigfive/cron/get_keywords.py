from textrank4zh import TextRank4Keyword, TextRank4Sentence

# key_words
def text_rank_keywords(text, keywords_num=5):
    keywords = []
    tr4w = TextRank4Keyword()
    tr4w.analyze(text=text.encode('utf-8', 'ignore'), lower=True, window=2)   # py2中text必须是utf8编码的str或者unicode对象，py3中必须是utf8编码的bytes或者str对象
    for item in tr4w.get_keywords(keywords_num, word_min_len= 1):
        keywords.append(item.word)

    return keywords

if __name__ == "__main__":
    text_rank_keywords("今天是个好日子，心想的事儿都能成！", 5)