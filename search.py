from bs4 import BeautifulSoup
from google import google
import requests
import wikipedia
import re


def get_videos(term, video_limit, duration_limit):  # Input paremeters for search, returns json data for videos

    restricted_links = ["googleadservices", "list", "channel"]  # Terms to filter out of links (ads and playlists)
    results = []  # Final list for dictionary elements

    query = "https://www.youtube.com/results?search_query={}".format(term.replace(" ", "+"))  # Format the term into a google search url
    page = requests.get(query).content  # Download the html of youtube page
    soup = BeautifulSoup(page, features="html.parser")  # Create bs4 object to parse html
    videos = soup.findAll("div", {'class': 'yt-lockup-content'})  # Find each video div
    print(query)
    count = 0  # Count for good videos to keep track for limit
    for video in videos:
        v_info = video.find("h3", {'class': 'yt-lockup-title'})  # Block to find title, duration, and link
        link = v_info.find("a")['href']  # Find the raw href of link (to filter out restrictions)
        
        if not any(rl in link for rl in restricted_links):  # Only parse if any of the restricted terms are NOT in the link

            link = link.split("v=")[1]  # Find video link after "v=" sign
            title = v_info.find("a").text  # Get video title
            channel = video.find("div", {'class': 'yt-lockup-byline'}).text  # Get channel name
            duration = v_info.find("span").text.split("Duration: ")[1][:-1]  # Parse the duration string and split/format to just get minute value
            
            result = {}  # Create empty dictionary for result and populate
            result['title'] = title
            result['channel'] = channel
            result['duration'] = duration
            result['link'] = link
            results.append(result)  # Append the populated dictionary to the result
    
            count += 1  # Increase the good counter by 1

            if count >= video_limit:  # One the limit is hit, stop the loop
                break

    return term, results  # Return term and the list of dictionaries


def get_summary(term):  # Input term, return summarized wikipedia entry of topic
    try:  # In case no wikipedia page is found
        term = term.replace(" ", "+")  # Set up query for wikipedia search
        query = "https://en.wikipedia.org/w/index.php?sort=relevance&search={}&title=Special%3ASearch&profile=advanced&fulltext=1&advancedSearch-current=%7B%7D&ns0=1".format(term)
        page = requests.get(query).content  # Fetch html and parse it
        soup = BeautifulSoup(page, features="html.parser")
        wiki_title = soup.find("div", {'class': 'mw-search-result-heading'}).text  # Find title of wiki page
        summary = wikipedia.WikipediaPage(title = wiki_title).summary  # Use wikipedia api to get summary
        summary = summary.partition('.')[0] + '.'  # Extract first setence
        return summary  # Return the summarized setence
    except:
        return ""  # If not found just return empty string (will be replaced with secondary sources)


# Test input (fake search data will become automated)
searches = [
"Human Center Design",
"Service Design",
"Fast Protoyping",
"Marketing Strategy"
]

with open("output.html", "w+", encoding="utf-8") as file:

    file.write("""
    <link rel="stylesheet" href="css/styles.css">
    <div class="review-container">\n
    """)

    for search in searches:
        term, videos = get_videos(search, 3, 10)

        summary = get_summary(term)

        iframes = ""
    
        for video in videos:
            iframes += '<iframe src="https://www.youtube.com/embed/{}"></iframe>'.format(video['link'])
            
        topic_string = """
        <div class="title">{}</div>
            <div class="summary">{}</div>
            <div class="videos">{}</div>
        """.format(term, summary, iframes)

        try:
            file.write(topic_string + "\n")
        except:
            pass

    file.write("""
    </div>\n
    """)

print("Completed and Saved results!")