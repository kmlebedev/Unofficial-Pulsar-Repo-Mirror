__author__ = 'Ruben'
def uncode_name(name):  # convert all the &# codes to char, remove extra-space and normalize
    from HTMLParser import HTMLParser
    from unicodedata import normalize
    if type(name) is unicode:
        normalize_name = normalize('NFKD', name)
        name = normalize_name.encode('ascii', 'replace')
    name = ' '.join(name.split())
    name = name.replace('<![CDATA[', '').replace(']]', '')
    name = HTMLParser().unescape(name)
    return name


def safe_name(value):  # make the name directory and filename safe
    value = uncode_name(value)
    keys = {'"': ' ', '*': ' ', '/': ' ', ':': ' ', '<': ' ', '>': ' ', '?': ' ', '|': ' '}
    for key in keys.keys():
        value = value.replace(key, keys[key])
    return value


def format_title(value=''):
    import re
    value = value.replace('.', ' ').replace(')', ' ').replace('(', ' ').replace('[', ' ').replace(']', ' ')
    value = safe_name(value).lower()
    formats = ['s[0-9]+e[0-9]+', 's[0-9]+ e[0-9]+', '[0-9]+x[0-9]+', '[0-9][0-9][0-9][0-9] [0-9][0-9] [0-9][0-9]',
               'season [0-9]+', 'season[0-9]+', 's[0-9][0-9]']
    for format in formats:
        sshow = re.search(format, value) # format shows
        if sshow is not None:
            break
    if sshow is None:
        # it is a movie
        value += ' 0000 '  # checking year
        syear = re.search(' [0-9][0-9][0-9][0-9] ', value)
        year = syear.group(0).strip()
        pos = value.find(year)
        if pos > 0:
            title = value[:pos].strip()
            rest =  value[pos + 5:].strip().replace('0000', '')
        else:
            title = value.replace('0000', '')
            rest = ''
        keywords = ['en 1080p', 'en 720p', 'en dvd', 'en dvdrip', 'en hdtv', 'en bluray', 'en blurayrip', 'en web', 'en rip']
        keywords += ['1080p', '720p', 'dvd', 'dvdrip', 'hdtv', 'bluray', 'blurayrip', 'web', 'rip']
        while pos != -1:  # loop until doesn't have any keyword in the title
            value = title
            for keyword in keywords:  # checking keywords
                pos = value.find(keyword)
                if pos > 0:
                    title = value[:pos - 1].strip()
                    rest =  value[pos:].strip() + ' ' + rest
                    break
        #title = title.strip()
        clean_title = title
        if '0000' not in year:
            title += ' (' + year.strip() + ')'
        title = title.title().replace('Of', 'of')
        clean_title = clean_title.title().replace('Of', 'of')
        folder = title
        return {'title': title, 'folder': folder, 'rest': rest.strip(), 'type': 'MOVIE', 'clean_title': clean_title, 'year': year}
    else:
        # it is a show
        episode = sshow.group(0)
        title = value[:value.find(episode)].strip()
        rest =  value[value.find(episode) + len(episode):].strip()
        title = title.strip()
        if 'x' in episode:
            episode = 's' + episode.replace('x', 'e')
        episode = episode.replace(' ', '')  # remove spaces in the episode format
        folder = title.title().replace('Of', 'of')
        clean_title = folder
        title = folder + ' ' + episode.upper()
        year = 0000
        return {'title': title, 'folder': folder, 'rest': rest, 'type': 'SHOW', 'clean_title': clean_title, 'year': year}


print format_title('Placeres Vespertinos (1800)')