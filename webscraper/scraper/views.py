from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from .forms import ScrapeForm
from .models import ScrapedResult
from textblob import TextBlob
from urllib.parse import urljoin
import re
from collections import Counter
import time
import spacy

nlp = spacy.load("en_core_web_sm")

def categorize_content(text):
    text = text.lower()
    if "stock" in text or "investment" in text or "share price" in text:
        return "Finance"
    elif "health" in text or "medicine" in text or "disease" in text:
        return "Health"
    elif "university" in text or "college" in text:
        return "Education"
    elif "software" in text or "programming" in text or "ai" in text:
        return "Technology"
    else:
        return "Other"

def scrape_view(request):
    data = {}
    error = None

    if request.method == 'POST':
        form = ScrapeForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            max_attempts = 3
            attempt = 0
            response = None

            while attempt < max_attempts:
                try:
                    response = requests.get(url, timeout=20)
                    break
                except requests.exceptions.Timeout:
                    attempt += 1
                    print(f"[Attempt {attempt}] Timeout occurred for URL: {url}")
                    if attempt < max_attempts:
                        time.sleep(1)
                except Exception as e:
                    error = f"An error occurred while fetching the URL: {e}"
                    print(f"[Error] {e}")
                    break

            if response and response.status_code == 200:
                try:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    title = soup.title.string.strip() if soup.title else 'No title found'
                    links = [link['href'] for link in soup.find_all('a', href=True)]
                    images = [urljoin(url, img['src']) for img in soup.find_all('img', src=True)]

                    meta_desc = soup.find('meta', attrs={'name': 'description'})
                    meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
                    description = meta_desc['content'] if meta_desc else 'No description'
                    keywords = meta_keywords['content'] if meta_keywords else 'No keywords'

                    content = soup.get_text()

                    # Run NER here
                    doc = nlp(content)
                    entities = [(ent.text, ent.label_) for ent in doc.ents]

                    # Categorize content
                    category = categorize_content(content)

                    # Sentiment Analysis
                    blob = TextBlob(content)
                    polarity = blob.sentiment.polarity

                    if polarity >= 0.6:
                        sentiment = "Very Positive 😊"
                    elif polarity >= 0.2:
                        sentiment = "Positive 🙂"
                    elif polarity > -0.2:
                        sentiment = "Neutral 😐"
                    elif polarity > -0.6:
                        sentiment = "Negative 🙁"
                    else:
                        sentiment = "Very Negative 😠"

                    words = re.findall(r'\b\w{5,}\b', content.lower())
                    common_words = Counter(words).most_common(10)
                    keywords_ai = [word for word, _ in common_words]

                    ScrapedResult.objects.create(
                        url=url,
                        title=title,
                        meta_description=description,
                        meta_keywords=keywords,
                        links=",".join(links),
                        images=",".join(images)
                    )

                    data = {
                        'title': title,
                        'links': links,
                        'images': images,
                        'meta_description': description,
                        'meta_keywords': keywords,
                        'sentiment': sentiment,
                        'polarity_score': polarity,
                        'keywords_ai': keywords_ai,
                        'entities': entities,
                        'category': category,
                    }

                except Exception as e:
                    error = f"Error while parsing content: {e}"
                    print(f"[Parse Error] {e}")

            elif not response:
                error = "Website did not respond in time after multiple attempts."
    else:
        form = ScrapeForm()

    return render(request, 'scraper/scrape.html', {'form': form, 'data': data, 'error': error})
