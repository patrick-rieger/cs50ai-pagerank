import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    probability_distribution = dict()
    # If page has no outgoing links, then transition_model should return a probability distribution that chooses 
    # randomly among all pages with equal probability. 
    # (In other words, if a page has no links, we can pretend it has links to all pages in the corpus, including itself.)
    if not corpus[page]:
        d = 1 / len(corpus)
        for p in corpus:
            probability_distribution[p] = d
        return probability_distribution
    
    randomly_among_linked = damping_factor / len(corpus[page])
    randomly_among_all = (1 - damping_factor) / len(corpus)
    for p in corpus:
        probability_distribution[p] = randomly_among_all
    for p in corpus[page]:
        probability_distribution[p] += randomly_among_linked
    return probability_distribution

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Starting the dict
    PageRank = dict()
    for p in corpus:
        PageRank[p] = 0

    # Randomly choosing a page
    page = random.choice([key for key in corpus.keys()])

    count = n
    
    while count: # While n > 0
        PageRank[page] += 1
        population = []
        weights = []
        for (p, w) in transition_model(corpus, page, damping_factor).items():
            population.append(p)
            weights.append(w)

        page = random.choices(population, weights, k=1).pop()
        count -= 1
    
    # PageRank = dict((key, value/n) for (key,value) in PageRank)
    PageRank.update({key: PageRank[key] / n for key in PageRank.keys()})
    return PageRank

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    def formula(page):
        first_condition = (1 - damping_factor) / len(corpus)
        summation = 0
        for i in corpus:
            if corpus[i] != set():
                if page in corpus[i]:
                    NumLinks = len(corpus[i])
                    summation += PageRank[i] / NumLinks
            else:
                # A page that has no links should be interpreted as having 
                # one link for every page in the corpus (including itself).
                NumLinks = len(corpus)
                summation += PageRank[i] / NumLinks
        second_condition = damping_factor * summation
        return first_condition + second_condition

    PageRank = dict()
    new_PageRank = dict()
    N = len(corpus)
    # Begin by assigning each page a rank of 1 / N
    PageRank.update({p: 1 / N for p in corpus})
    
    new_PageRank.update({p: formula(p) for p in corpus})
    
    repeat = True
    while repeat:
        repeat = False
        PageRank = new_PageRank.copy()
        new_PageRank.update({page: formula(page) for page in corpus})
        # This process should repeat until no PageRank value changes by 
        # more than 0.001 between the current rank values and the new rank values
        if any(abs(PageRank[p] - new_PageRank[p]) >= 0.001 for p in corpus):
            repeat = True
    return PageRank


if __name__ == "__main__":
    main()
