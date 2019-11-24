from bs4 import BeautifulSoup
import requests


def get_videos(term, video_limit, duration_limit):  # Input paremeters for search, returns json data for videos

    restricted_links = ["googleadservices", "list"]  # Terms to filter out of links (ads and playlists)
    results = []  # Final list for dictionary elements

    query = "https://www.youtube.com/results?search_query={}".format(term.replace(" ", "+"))  # Format the term into a google search url
    page = requests.get(query).content  # Download the html of youtube page
    soup = BeautifulSoup(page, features="html.parser")  # Create bs4 object to parse html
    videos = soup.findAll("div", {'class': 'yt-lockup-content'})  # Find each video div

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




# Test input (fake search data will become automated)
searches = [
"Industrial Revolution APUSH",
"5.6 The Fundamental Theorem of Calculus",
"5.3 Integration By Substitution",
"5.9 Definite Integrals by Substitution",
"5.7 Total Change Theorem",
"5.4 Area as Limit/Riemann Sums; Sigma",
"7.7 The Trapezoid Rule",
"APUSH Period 3 Review"
]

with open("output.html", "w+") as file:
    for search in searches:
        term, videos = get_videos(search, 5, 10)
        iframes = ""

        for video in videos:
            iframes += '<iframe src="https://www.youtube.com/embed/{}"></iframe>'.format(video['link'])
            
        topic_string = """
        <div class="topic">
            <h1>{}</h1>
            {}
        </div>
        """.format(term, iframes)

        file.write(topic_string + "\n")

print("Completed and Saved results!")
    
        