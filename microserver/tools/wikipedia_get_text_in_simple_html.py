import wikipedia
import re
import os
ALLOWED_DICTIONARY="ёйцукенгшщзхъфывапролджэячсмитьибюabcdefghijklmnopqrstuvwxyzàèéìíîòóùú"
WORKING_DIRECTORY=r"C:\Users\Eldar\Documents\GitHub\search-system\microserver\tools"
LANGUAGE = "ru"


##### search page in wikipedia
def search_page(page_name):
    wikipedia.set_lang(LANGUAGE)
    # search for a term
    result = wikipedia.search(page_name)
    print(f"Result search of '{page_name}':", result)
    
    # get the page
    page = wikipedia.page(result[0])
    print(page)

    return page

def keepCharactersInStringWithRegex(input_string, reference_string):
    pattern = f"[^{reference_string.lower()}]"
    filtered_string = re.sub(pattern, "", input_string.lower())
    return filtered_string.lower()

##### make simple html
def create_html(page):
    wikipedia.set_lang(LANGUAGE)
    
    title = ""
    content = ""
    summary = ""

    try: title = page.title
    except: pass
    try: content = page.content
    except: pass
    try: summary = page.summary
    except: pass
    
    # title = keepCharactersInStringWithRegex(input_string=title, reference_string=ALLOWED_DICTIONARY)

    html_text = ""
    html_text += f'<!DOCTYPE html>\n<html class="client" lang="{LANGUAGE}">\n'
    html_text += f'\t<head>\n\t\t<meta charset="UTF-8">\n\t\t<title>\n\t\t\t{title}\n\t\t</title>\n\t</head>\n'
    html_text += f'\t<body>\n\t\t<div class="page_content">'
    html_text += f'\n\t\t\tЛабораторная 2\n\t\t\t<hr/>\n\t\t\t{content}\n\t\t</div>\n\t\t<div class="page_summary" style="margin-top: 3vh;">\n\t\t\t{summary}\n\t\t</div>\n'
    html_text += f'\t</body>\n</html>'
	
    file_name = f"{title}_{LANGUAGE}.html"
    file_path: str = os.path.join(WORKING_DIRECTORY, file_name)
    
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(html_text)

#####
LANGUAGE = "ru"
found_page = search_page("Инкапсуляция (программирование)")
create_html(found_page)

LANGUAGE = "it"
found_page = search_page("Incapsulamento (programmazione)")
create_html(found_page)
