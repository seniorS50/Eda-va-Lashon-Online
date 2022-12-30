# This helps to print Hebrew correctly in terminal for debugging. Not necessary for running server
from bidi.algorithm import get_display
import json
from xml.dom import minidom

with open('filenames.json') as f:
    data = json.load(f)

# Pre-load dictionary of city locations from JSON
with open('static/city_locs.json') as f:
    cities = json.load(f)

# Switch from full string (which the filenames pass in from the JSON) to the abbreviations present in the English JPS 1917 edition
# JPS used because it is open source and so that chapters and verses match
def book_to_abbr(book_name):
    match book_name.replace("_", " "):
        case 'Genesis': return ( 'GEN')
        case 'Exodus': return ( 'EXO')
        case 'Leviticus': return ( 'LEV')
        case 'Numbers': return ( 'NUM')
        case 'Deuteronomy': return ( 'DEU')
        case 'Joshua': return ( 'JOS')
        case 'Judges': return ( 'JDG')
        case 'Ruth': return ( 'RUT')
        case 'Samuel 1': return ( '1SA')
        case '1 Samuel': return ( '1SA')
        case '2 Samuel': return ( '2SA')
        case 'Samuel 2': return ( '1SA')
        case '1 Kings', 'Kings 1': return ( '1KI')
        case '2 Kings', 'Kings 2': return ( '2KI')
        case '1 Chronicles', 'Chronicles 1': return ( '1CH')
        case '2 Chronicles', 'Chronicales 2': return ( '2CH')
        case 'Ezra': return ( 'EZR')
        case 'Nehemiah': return ( 'NEH')
        case 'Esther': return ( 'EST')
        case 'Job': return ( 'JOB')
        case 'Psalms': return ( 'PSA')
        case 'Proverbs': return ( 'PRO')
        case 'Ecclesiastes': return ( 'ECC')
        case 'Song of Songs': return ( 'SNG')
        case 'Isaiah': return ( 'ISA')
        case 'Jeremiah': return ( 'JER')
        case 'Lamentations': return ( 'LAM')
        case 'Ezekiel': return ( 'EZK')
        case 'Daniel': return ( 'DAN')
        case 'Hosea': return ( 'HOS')
        case 'Joel': return ( 'JOL')
        case 'Amos': return ( 'AMO')
        case 'Obadiah': return ( 'OBA')
        case 'Jonah': return ( 'JON')
        case 'Micah': return ( 'MIC')
        case 'Nahum': return ( 'NAM')
        case 'Habakkuk': return ( 'HAB')
        case 'Zepheniah': return ( 'ZEP')
        case 'Haggai': return ( 'HAG')
        case 'Zecheriah': return ( 'ZEC')
        case 'Malachi': return ( 'MAL')
    return("Error")


def get_book_index():
    # Get info from the index
    doc = minidom.parse("Books/TanachIndex.xml")
    index = doc.getElementsByTagName("book")
    book_info = []
    for book in index:
        name = book.getElementsByTagName("name")[0].firstChild.data
        abbrev = book.getElementsByTagName("abbrev")[0].firstChild.data
        filename = book.getElementsByTagName("filename")[0].firstChild.data
        # Get all the chapter data for each book
        c = book.getElementsByTagName("c")
        chapters = []
        for chapter in c:
            chapters.append({
                "chps": chapter.getAttribute("n"),
                "vss": chapter.getElementsByTagName("vs")[0].firstChild.data
            })
        book_info.append({
            "name": name,
            "abbrev": abbrev,
            "filename": filename,
            "chapters": chapters
        })
        
    # return a list of dicts with the following info:
    # name
    # abbrev
    # filename
    # chapters - a list of dicts with the attributes:
    #     chp (which chapter)
    #     vss (which vss)
    return book_info

def get_hebrew_text(book, chapter, firstvs = 1, lastvs = -1):
    # load the index
    index = get_book_index()
    # Get the filename and chapters dict
    filename = None
    for entry in index:
        if entry["name"].lower() == book.lower() or entry["abbrev"].lower() == book.lower() or entry["filename"] == book.replace(" ", "_"):
            filename = entry["filename"]
            chapters = entry["chapters"]
            break
    if not filename:
        print("error: book not found.")
        return(1)
    # Check that the book and chapter numbers make sense
    if int(chapter) < 1 or int(chapter) > len(chapters) + 1:
        print("invalid chapter")
        return(2)
    # If there is an invalid or default verse ranger, just go ahead and give the whole chapter back
    if (firstvs) > (lastvs) or (lastvs) > int(chapters[chapter - 1]["vss"]):
        firstvs = 1
        lastvs = int(chapters[chapter-1]["vss"])
    
    # load the xml of the specific book
    doc = minidom.parse("books/" + filename + ".xml")
    # doc.getElementsByTagName returns the NodeList
    chps = doc.getElementsByTagName("c")
    # get verses in a chapter
    vss = chps[chapter - 1].getElementsByTagName("v")
    # Get each verse
    hebrew_text = []

    for i in range(firstvs - 1,lastvs):
        # Get the list of xml nodes for the verse
        verse = ""
        words = vss[i].getElementsByTagName("w")
        for word in words:
            verse += word.firstChild.data + " "
        hebrew_text.append({"vs": i + 1, "text":verse})
    return hebrew_text

# Get book, chapter, vs based on HULTP
def get_text_HULTP(HULTP):
    # Get entry with correct HULTP (these are unqiue)
    entry = {}
    for datum in data:
        if str(HULTP) == datum["HULTP"]:
            entry = datum
            break
    if not entry:
        return 2
    # Get the info from our entry
    book = entry["book"]
    chapter = entry["ref"].split(':')[0]
    firstvs = entry["ref"].split(':')[1].split('-')[0]
    lastvs = entry["ref"].split(':')[1].split('-')[1]
    # Now, return hebrew text and english text as parts of a single dict
    return {"hebrew": get_hebrew_text(book, int(chapter), int(firstvs), int(lastvs)), "english": get_jps(book, int(chapter), int(firstvs), int(lastvs))}


def search_entries(term):
    # Also, replace spaces with "_" just in case
    results = {
        'entries' : [],
        'cities' : []
    }
    curr_cities = []
    for entry in data:
        # hacky way to check for combined name but it works. In the future would reconfigure JSON file
        if term.lower() in str(entry.values()).lower():
            results["entries"].append(entry)
    # Now, get the relevant cities
    for entry in results["entries"]:
        if entry['city'] not in curr_cities:
            curr_cities.append(entry['city'])
    for city in cities:
        if city['city'] in curr_cities:
            results['cities'].append(city)
    return results

    
def get_jps(book, chapter, firstvs = 0, lastvs = 0):
    # Get info from the index
    doc = minidom.parse("Books\engjps_vpl.xml")
    index = doc.getElementsByTagName("v")
    text = []
    for verse in index:
        if verse.hasAttribute("b") and verse.getAttribute("b") == book_to_abbr(book) \
                and int(verse.getAttribute("c")) == chapter \
                and int(verse.getAttribute("v")) >= firstvs \
                and int(verse.getAttribute("v")) <= lastvs:
            text.append({ "vs": verse.getAttribute("v"), "text": verse.firstChild.data})
    return text