# Bookmarklet

The project was inspired by the following [blog post][1] which the author
recorded all the articles read. This quickly gets my attention. Knowing myself
probably spend most of my time reading stuffs on the internet and forgets them
quickly later on, this is an approach to record them down. These materials
might serves as the source of inspiration in the future. The complete project
should,

1. record the url in a fairly simple manner,
1. record the inner HTML for future referrence

the 2nd requirement is particularly important as I lookback at my bookmark
list, which more than half of the content are no longer available. The
bookmarklet project that I came by helps on the 1st requirement but not the 2nd
.

## Bookmarklet?

Bookmarklet is a bookmark stored in web browser that contants JavaScript
commands that add new features to the browser [ref][2]. Bookmarklet can be
created easily on Chrome by going to the bookmark manager (windows ctrl+shift+o
) and adding a new bookmark. A snippet of JavaScript is provided instead of an
ordinary url. Below is a working example,

```javascript
javascript:(() => {console.log("hello world!")})();
```

A few use cases for bookmarklet including button clicking, modifying HTML
content, data scraping etc. Bookmarklet are not limited to the context of HTML.

## Scraping or more bookmarklet?

Recall on the 2nd requirement to record the inner HTML for future referrence,
there are two approach to achieve it,

1. automating it with web scraping technologies
1. using a modified bookmarklet script

If only the web is still full of static sites, then without a doubt option 1
with python `requests` library would be the easiest way to go by. However, the
web's is a mix of static sites and single page applications (JavaScript
frontend frameworks). The latter makes web scrapping a little complicated,
browser automation technologies like `Selenium` is needed instead of a simple
post request. Oh! Don't forget about logins! It definitely is a interesting
approach to pursue to have asynchronous workes e.g. `celery` or `rq` and does
the necessary web scrapping or alternatively, modify the bookmarklet script to
does exactly that.

> Warning, it does requires some manual input however the tradeoff is
> worthwhile, trust me!

```javascript
/* asking for xpath */
```

## Some data analysis...

data collection in progress - no analysis yet.

reading behavior?

favorite sites?

## Some problems with current approach...

The bookmarklet uses http GET method with token as one of the search parameters
, which can be a security risk. a previous attempt to convert to post request
encounters some bugs which was not able to be resolve at that point of time.
Currently this is addressed by setting a short enough token exipration to
prevent token abuse.


[1]: https://www.tdpain.net/blog/a-year-of-reading
[2]: https://en.wikipedia.org/wiki/Bookmarklet
