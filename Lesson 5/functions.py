

def count_words(lines: list[str]):
    words = {}
    for line in lines:
        _word, _, match_count, _ = line.split("\t")
        if _word in words:
            words[_word] += int(match_count)
        else:
            words[_word] = int(match_count)
    return words

def mp_count_words(lines: list[str], counter, lock):
    words_num = 0
    step = 10000
    words = {}
    for line in lines:
        _word, _, match_count, _ = line.split("\t")
        if _word in words:
            words[_word] += int(match_count)
        else:
            words[_word] = int(match_count)

        #monitoring
        words_num += 1
        if len(words) % step == 0:
            with lock:
                counter.value += 10000
    with lock:
        counter.value += words_num
        return words


    