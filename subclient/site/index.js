let search_form = document.getElementById("search_form");
function handleForm(event) {
	event.preventDefault(); 
} 
search_form.addEventListener('submit', handleForm);


function clearComponent(component) {
	component.innerHTML = ""
}

function fillComponent(component, fill_data) {
	component.appendChild(fill_data);
}

function makeCardsFromResponsData(response) {
	let content = document.createElement('div');
	
	let cards = []
	for (const [num_in_queue, document_in_list] of Object.entries(response)) {
		// docname
		docname = document_in_list.document.replaceAll('\\', '/')
		
		// similarity
		similarity = (document_in_list.similarity * 100).toFixed(2)
		
		// words
		words_in_document = [] 
		for (const [word_in_document, weight] of Object.entries(document_in_list.weights))
			if (weight !== 0)
				words_in_document.push(word_in_document)
		
		// address
		document_url = "http://" + document_in_list.server + "/" + docname
			
		html = `
			<div class="card" style="max-width: 66vw; margin: 1vw 0 1vw 1vw;">` +
				`<div class="card-body">` + 
					`<h5 class="card-title">` + 
						`<a href="` + document_url + `" class="card-link" target="_blank">` + 
							docname.split('/').pop() + 
						`</a>` + 
					`</h5>` + 
					`<p class="card-text" style="margin: 0;"> Совпадение: ` + similarity + `% ` + `</p>` +
					`<p class="card-text" style="margin: 0;"> Слова: ` + words_in_document.join(', ') + `</p>` + 
				`</div>` +
			`</div>`
		cards.push(html)
	}

	content.innerHTML = cards.join("");
	return content
}

function search() {
	let content_div = document.getElementById("content"); 
	clearComponent(content_div)
	
	const search_input = document.getElementById("search_input");
	request_content = search_input.value
	
	const request = "http://" + getCurrentServer() + "/search?request_content=" + "\"" + request_content + "\"" 
	const response = JSON.parse(httpGet(request))
	
	let fill_data = makeCardsFromResponsData(response)
	fillComponent(content_div, fill_data)
	
	// console.log("Search done for " + request_content + "\nResult:\n" + response);
}

function httpGet(theUrl)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", theUrl, false); // false for synchronous request
    xmlHttp.send(null);
    return xmlHttp.responseText;
}

function getCurrentServer() {
	server_address = "127.0.0.1:13000"
	try { server_address = window.location.host } catch {}
	return server_address
}
