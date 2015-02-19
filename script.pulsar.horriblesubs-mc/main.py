from pulsar import provider
import common
import re

# this read the settings
settings = common.Settings()
# define the browser
browser = common.Browser()
# create the filters
filters = common.Filtering()


# using function from Steeve to add Provider's name and search torrent
def extract_magnets(data):
    try:
        filters.information()  # print filters settings
        data = common.clean_html(data)
        lname = re.findall('.HorribleSubs.(.*?)<', data)  # list the names
        cont = 0
        for cm, magnet in enumerate(re.findall(r'magnet:\?[^\'"\s<>\[\]]+', data)):
            name = lname[cm] + ' - ' + settings.name_provider
            if filters.verify(name, None):
                    yield {"name": name, "uri": magnet}  # return le torrent
                    cont += 1
            else:
                provider.log.warning(filters.reason)
            if cont == settings.max_magnets:  # limit magnets
                break
        provider.log.info('>>>>>>' + str(cont) + ' torrents sent to Pulsar<<<<<<<')
    except:
        provider.log.error('>>>>>>>ERROR parsing data<<<<<<<')
        provider.notify(message='ERROR parsing data', header=None, time=5000, image=settings.icon)


def search(query):
    global filters
    filters.title = query  # to do filtering by name
    if settings.time_noti > 0: provider.notify(message="Searching: " + query.title() + '...', header=None, time=settings.time_noti, image=settings.icon)
    url_search = "%s/lib/search.php?value=%s" % (settings.url,query.replace(' ','%20'))  # change in each provider
    provider.log.info(url_search)
    if browser.open(url_search):
        results = extract_magnets(browser.content)
    else:
        provider.log.error('>>>>>>>%s<<<<<<<' % browser.status)
        provider.notify(message=browser.status, header=None, time=5000, image=settings.icon)
        results = []
    return results


def search_movie(info):
    return []


def search_episode(info):
    info['title'] = common.exception(info['title'])
    filters.use_TV()
    query = info['title'] + ' %02d' % info['absolute_number']  # define query
    results = []
    if info['absolute_number'] != 0:
        results = search(query)
    return results

# This registers your module for use
provider.register(search, search_movie, search_episode)