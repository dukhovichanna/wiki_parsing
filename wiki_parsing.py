from bs4 import BeautifulSoup
import re
import os
import queue

file_path = 'C:\\Users\\Anna\\PycharmProjects\\wiki_parse\\soup_sample\\wiki'
regex = re.compile(r'^/wiki/[\w\d_()]*$')


# Getting all the /wiki/... links from the page and returning in sorted order
def get_links(file):
    links = []
    with open(file, 'r', encoding="utf-8") as f:
        soup = BeautifulSoup(f, 'lxml')
        for link in soup.find_all('a'):
            match = regex.search(str(link.get('href')))
            if match:
                file_name = str(link.get('href')).split('/')[-1]
                if file_name not in links and os.path.isfile(file_name) and file_name != file:
                    links.append(file_name)
    return sorted(links)


# Building the shortest path between 2 pages by traversing the other pages in the folder
def shortest_path(start, end):
    q = queue.Queue(maxsize=0)
    path = []
    already_visited = {}
    parents = {}
    found = False
    # Adding start to queue'
    q.put(start)
    # Adding start to already visited
    already_visited.update({start: get_links(start)})
    # Searching for end in already_visited
    if end not in already_visited[start]:
        while not found:
            parent = q.get()
            links = get_links(parent)
            for link in links:
                if link not in parents:
                    parents.update({link: parent})
            for item in links:
                if item not in already_visited:
                    # Adding item to queue
                    q.put(item)
                    # Adding item to already visited
                    already_visited.update({item: get_links(item)})
                    # Searching for end in already_visited
                    if end in already_visited[item]:
                        found = True
                        path = build_path(start, end, item, parents)
                        break
    return path


# Building the shortest path
def build_path(start, end, current_node, parents):
    path = [end, current_node]
    while path[-1] != start:
        parent = parents.get(current_node)
        path.append(parent)
        current_node = parent
    return list(reversed(path))


# Get all images with width >=200
def get_images(div):
    counter = 0
    tags = div.find_all('img')
    for tag in tags:
        if tag.has_attr('width') and int(tag['width']) >= 200:
            counter +=1
    return counter


# Get all headers that start with C,T or E
def get_headers(div):
    counter = 0
    tags = div.find_all(name=re.compile(r'^h\d$'))
    pattern = re.compile(r'[CTE]+')
    for tag in tags:
        if tag.get_text() and pattern.match(tag.get_text()):
            counter +=1

    return counter


# Get a longest chain of links
def get_chain_links(div):
    counter = 0
    tags = div.find_all('a')
    # Setting a counter to one as a chain has at least one link by default
    local_counter = 1
    for tag in tags:
        next_a_sibling = tag.find_next_sibling("a")
        # Checking if the next sibling is a link
        if next_a_sibling and next_a_sibling.find_previous_sibling() == tag:
            local_counter += 1
            if local_counter > counter:
                counter = local_counter
            continue
        local_counter = 1
    return counter


# Get lists that don't have other lists inside them
def get_unnested_lists(div):
    counter = 0
    tags_ul = div.find_all('ul')
    tags_ol = div.find_all('ol')
    tags = tags_ol + tags_ul
    for tag in tags:
        if not tag.find_parents("ol") and not tag.find_parents("ul"):
            counter +=1
    return counter


# Getting the final stats for a single page
def stats(file):
    with open(file, 'r', encoding="utf-8") as f:
        soup = BeautifulSoup(f, 'lxml')
        div = soup.find("div", id="bodyContent")
        stats = [get_images(div), get_headers(div), get_chain_links(div), get_unnested_lists(div)]
    return stats


# Creating a dict with stats for all pages in the shortest path
def shortest_path_with_stats(start, end):
    list_of_pages = shortest_path(start, end)
    dict_with_stats = {}
    for page in list_of_pages:
        dict_with_stats[page] = stats(page)
    return dict_with_stats


# Main function to get it put things together
def parse(start, end, path):
    os.chdir(path)
    return shortest_path_with_stats(start, end)




