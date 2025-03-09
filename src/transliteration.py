import os
import tqdm
import string 
from src.az_openai import create_client, generate_response

INSTRUCTIONS_AR_HB = """
Task:
Perform romanization of Arabic or Hebrew song lyrics.
Convert Arabic or Hebrew song lyrics into a phonetic transliteration using only the english alphabet, an apostrophe ('), spaces, and new lines. 
The goal is to preserve the original phonology as closely as possible while using only the english writing system.

Guidelines:
No numbers – Avoid using numbers like "2," "3," or "7" for Arabic or Hebrew sounds. Instead, use the closest english letters.
Preserve pronunciation – The transliteration should reflect how the lyrics are sung, maintaining the phonetic structure of the original language.
Use apostrophes ('') – Represent sounds like:
Arabic: ع (ʿayn) and ء (hamza) → '
Hebrew: ע (ʿayin) and א (aleph) → ' when pronounced
Words must start with a letter – Do not start words with apostrophes. Use the closest english letter instead.
No extra characters – Do not use diacritics, underscores, or special symbols beyond apostrophes.
Keep word boundaries – Maintain spacing similar to the original lyrics.
Use lowercase letters for the transliteration.

Examples (Arabic):
Input:
حبيبي يا نور العين يا ساكن خيالي
عاشق بقالي سنين ولا غيرك في بالي
أجمل عيون فى الكون أنا شفتها
الله عليك، الله على سحرها

Output:
habibi ya nour el-ain, ya sakhen khayali
aashiq ba'ali seneen wala ghayrak fi bali
ajmal a'yun fil kawn ana shuftuha
allah aalayk, allah ala sahriha

Input:
مسيطرة، همشيك مسطرة
هخليك لو شوفت في شارع بنت تبص لورا
أيوه أنا مسيطرة، يا حتة سكرة
طول ما أنت معايا تمشي على هوايا أنا متكبرة

Output:
mesytara, hamshek mastara
hakhlek law shoft fi share'a bent tebos le-wara
aywa ana mesytara ya hetet sokra
toul ma enta ma’aya temshi aala hawaya, ana motakabera

Input:
مافيش حاجه تيجي كده
إهدا حبيبي كده وإرجع زي زمان
يابني اسمعني هتدلعني
تاخد عيني كمان

Output:
ma feesh haga teggy keda
ihda habiby keda, w ergaa' zay zaman
ya ebni isma'ni, hatdala'any
takhod einy kaman

Examples (Hebrew):
Input:
טמפרטורה הזיה, השמש עושה לה טוב
אמא שלה, ממרוקו
אבא מצפון הים, אפשר להרגיש את הקור
משאללה, איך יצא לו טוב

Output:
temperatura haziya, hashemesh osa la tov
ima shela, me'marocco
aba mitzafon hayam, efshar lehargish ta'kor
mashallah, eich yatz’a lo tov

Input:
שמור וזכור בדיבור אחד
השמיענו אל המיוחד
אדוני אחד ושמו אחד
לשם ולתפארת ולתהילה
לכה דודי לקראת כלה
פני שבת נקבלה

Output:
shamor v’zachor b’dibur echad
hishmi’anu el ha’myuchad
adonai echad u’shmo echad
l’shem u’l’tiferet v’lit’hillah
lecha dodi likrat kallah
p'nei shabbat n'kabela

Input:
היא מרגישה שנפתח לה המזל
פגשה אחד, גבר-גבר ורג'אל
והיא תלחש לו, מה היא תלחש לו-
"קח אותי על הגמל"

Output:
hi margisha sheniftach la hamazal
pagsha echad, gever gever verajal
vehi tilchash lo, ma hi tilchash lo
"kach oti al hagamal"

I repeat, do not start words with apostrophes. If a word starts with ع or ע, use the closest english letter.
For example: 
Input:
عينيك
Output:
ainayk

Input:
עיניים
Output:
ayinayim

Input:
على
Output:
ala

Input:
על
Output:
al

Input:
عنب
Output:
anab

Input:
عليك
Output:
alayk

Input:
عليه
Output:
alayh
"""

INSTRUCTIONS_FR = """
Task:
Perform romanization of French song lyrics.
Convert French song lyrics into a phonetic transliteration using only the english alphabet, an apostrophe ('), spaces, and new lines.
The goal is to preserve the original phonology as closely as possible while using only the english writing system.

Guidelines:


Examples:

"""

def filter_content(content):
    # Convert content to lowercase and filter only ASCII lowercase letters, apostrophes, or spaces, keeping newlines
    filtered_content = ''.join([char if char in string.ascii_lowercase + " '\n" else '' for char in content.lower()])
    # Remove apostrophes at the beginning of words or after newlines
    filtered_content = '\n'.join([' '.join([word[1:] if word.startswith("'") else word for word in line.split()]) for line in filtered_content.split('\n')])
    return filtered_content

def save_lyrics_files(dst_folder, filename, filtered_content):
    # Create the .txt filename
    file_path = os.path.join(dst_folder, filename)
    with open(file_path, 'w') as output_file:
        output_file.write(filtered_content)
    
    # Split the filtered content by spaces and newlines, then join with newlines
    words = filtered_content.split()
    words_content = '\n'.join(words)
    
    # Create the .words.txt filename
    words_file_path = os.path.join(dst_folder, filename.replace('.txt', '.words.txt'))
    
    # Write the processed content to the new file
    with open(words_file_path, 'w') as words_file:
        words_file.write(words_content)

def process_lyrics(lyrics_src_folder, lang):
    translations = {
        'sem': INSTRUCTIONS_AR_HB,
        'fr': INSTRUCTIONS_FR
    }
    instructions = translations.get(lang)
    if instructions is None:
        raise ValueError(f'Language {lang} not supported. Please provide instructions for the language.')
    
    client = create_client()
    dst_lyrics_folder = 'lyrics'
    lyrics_rom_folder = "lyrics_rom"

    # Create the destination folders if they do not exist
    if not os.path.exists(dst_lyrics_folder):
        os.makedirs(dst_lyrics_folder)
    if not os.path.exists(lyrics_rom_folder):
        os.makedirs(lyrics_rom_folder)

    for filename in tqdm.tqdm(os.listdir(lyrics_src_folder)):
        if filename.endswith(".txt"):
            file_path = os.path.join(lyrics_src_folder, filename)
            with open(file_path, "r") as f:
                lyrics = f.read()

            # Generate romanized lyrics
            romanized_lyrics = generate_response(client, lyrics, instructions)
            rom_file_path = os.path.join(lyrics_rom_folder, filename)
            with open(rom_file_path, "w") as f:
                f.write(romanized_lyrics)

            # Filter and save structured lyrics
            filtered_content = filter_content(romanized_lyrics)
            save_lyrics_files(dst_lyrics_folder, filename, filtered_content)

    print("Lyrics processing complete.")

