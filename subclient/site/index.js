// some lines for not to restart page when submit
let search_form = document.getElementById("search_form");
function handleForm(event) {
	event.preventDefault(); 
} 
search_form.addEventListener('submit', handleForm);

// main page store
class Store {
	constructor() {
		let documents = [];
	}
}

main_store = new Store()


// work with html inner data
function clearComponent(component) {
	component.innerHTML = ""
}

function fillComponent(component, fill_data) {
	component.appendChild(fill_data);
}

// make cards of documents
function makeCardsFromResponsData() {
	let content = document.createElement('div');
	
	// No results found
	if (!main_store.documents.length || main_store.documents.length === 0) {
		let html = `
			<div class="no_results" style="margin: 2vh 0 1vw 1vw; text-align: center;">` +
				`<img src="/site/imgs/no-results.png" alt="No results" type="image/png" style="width: 20vw">` + 
				`<p> Результатов по вашему запросу не найдено </p>` + 
			`</div>`
		content.innerHTML = html
		return content
	}
	
	// Create cards for results
	let cards = []
	for (const [num_in_queue, document_in_list] of Object.entries(main_store.documents)) {
		// id 
		let document_id = (parseInt(num_in_queue) + 1).toString()
		// docname
		let docname_full = document_in_list.document.replaceAll('\\', '/')
		let docname_short = docname_full.split('/').pop().replaceAll(' ', '_')
		
		// similarity
		let similarity = (document_in_list.similarity * 100).toFixed(2)
		
		// words
		let words_in_document = [] 
		for (const [word_in_document, weight] of Object.entries(document_in_list.weights))
			if (weight !== 0)
				words_in_document.push(word_in_document)
		
		// address
		let document_url = "http://" + document_in_list.server + "/" + docname_full
		// document_url = "http://" + "kruapan.com:3000" + "/" + docname_full
			
		html = `
			<div class="card" style="margin: 2vh 0 1vw 1vw; z-index: 0;">` +
				`<div class="card-body">` + 
					`<h5 class="card-title">` + 
						`<a href="` + document_url + `" class="card-link" target="_blank">` + document_id + ". " + docname_short + `</a>` + 
					`</h5>` + 
					`<p class="card-text" style="margin: 0.4vh;"> Слова: ` + words_in_document.join(', ') + `</p>` + 
					`<p class="card-text" style="margin: 0.4vh 1vw;"> > Совпадение: ` + similarity + `% ` + `</p>` +
					`<p class="card-text" style="margin: 0.4vh 1vw;">` +
						`> Результат является релевантным: <input class="relevant_checkbox" id="checkbox_` + docname_short + `" type="checkbox">` + 
					`</p>` +
				`</div>` +
			`</div>`
		cards.push(html)
	}

	content.innerHTML = cards.join("");
	return content
}

// make card of metrics
function metrics(relevant_count_in_db=-1) {
	
	let metrics_div = document.getElementById("metrics");
	clearComponent(metrics_div)
	
	let content = document.createElement('div');
	let html = ""
	
	// No results found
	if (!main_store.documents  || !main_store.documents.length || main_store.documents.length === 0) {
		html = `
			<div class="no_results" style="margin: 2vh 0 1vw 1vw; text-align: center;">` +
				`<img src="/site/imgs/no-results.png" alt="No results" type="image/png" style="width: 20vw">` + 
				`<p> Невозможно рассчитать метрики </p>` + 
			`</div>`
		content.innerHTML = html
		fillComponent(metrics_div, content)
		return;
	}
	
	let relevant_documents = []
	for (const [num_in_queue, document_in_list] of Object.entries(main_store.documents)) {
		// id 
		// document_id = (parseInt(num_in_queue) + 1).toString()
		// docname
		let docname_full = document_in_list.document.replaceAll('\\', '/')
		let docname_short = docname_full.split('/').pop().replaceAll(' ', '_')
		
		let checkbox_relevant = document.getElementById("checkbox_" + docname_short)

		if (checkbox_relevant.checked) {relevant_documents.push({num_in_queue: document_in_list})}
	}
	
	// console.log(relevant_documents)
	
	// calculate metrics 
	let count = main_store.documents.length
	let unrelevant_count = main_store.documents.length - relevant_documents.length
	let relevant_count = relevant_documents.length
	
	let recall = relevant_count / Math.max(relevant_count_in_db, 1)
	let precision_request = relevant_count / Math.max(count, 1)
	let error = unrelevant_count /  Math.max(count, 1)
	let f_measure = 2 / ((1 / Math.max(precision_request, 1)) + (1 / Math.max(error, 1)))
	
	let n = 10
	let precision = 0
	let n_precision = 0
	let r_precision = 0
	
	// let precisions = new Array(Math.max(n, count)).fill(0);
	let precisions_sum = 0
	
	for (const [num_in_queue, document_in_list] of Object.entries(relevant_documents)) {
		
		let num_in_queue_id = parseInt(num_in_queue)
		if (num_in_queue_id + 1 <= n)
			n_precision += 1;		
		
		if (num_in_queue_id + 1 <= relevant_count)
			r_precision += 1;
		
		precision += 1
		precisions_sum += (precision / Math.max((num_in_queue_id + 1), 1))
		// precisions[num_in_queue] = precision / Math.max(num_in_queue, 1) 
	}
	
	n_precision /= Math.max(n, 1)
	r_precision /= Math.max(relevant_count, 1)
	
	let average_precision = (1 / Math.max(relevant_count_in_db, 1) * precisions_sum)
	
	html = `
		<div class="card" style="width: auto;">` +
			`<div class="card-body">` + 
				`<h5 class="card-title"> Метрики для полученных результатов </h5>` + 
				`<p id="metrics_1" class="card-text" style="margin: 0.4vh;"> Общее количество документов: ` + count + `</p>` + 
				`<p id="metrics_2" class="card-text" style="margin: 0.4vh;"> Количество релевантных документов: ` + relevant_count + `</p>` + 
				`<p id="metrics_3" class="card-text" style="margin: 0.4vh;"> Количество нерелевантных документов: ` + unrelevant_count + `</p>`
				
				if (!relevant_count_in_db || relevant_count_in_db < relevant_count) {
					html += 
					`<p id="metrics_4" class="card-text" style="margin: 0.4vh;"> Полнота [recall]: ` + "Не хватает информации" + ` </p>`
				}
				else {
					html += 
					`<p id="metrics_4" class="card-text" style="margin: 0.4vh;"> Полнота [recall]: ` + recall.toFixed(5) * 100 + `% </p>`
				}
				
				html += 
				`<p id="metrics_5" class="card-text" style="margin: 0.4vh;"> Точность [precision]: ` + precision_request.toFixed(5) * 100 + `%</p>` + 
				`<p id="metrics_6" class="card-text" style="margin: 0.4vh;"> Ошибка [error]: ` + error.toFixed(5) * 100 + `%</p>` +
				`<p id="metrics_7" class="card-text" style="margin: 0.4vh;"> F-Мера [F-measure]: ` + f_measure.toFixed(5) * 100 + `%</p>` +
				`<p id="metrics_8" class="card-text" style="margin: 0.4vh;"> Точность(10) [precision(n)]: ` + n_precision.toFixed(5) * 100 + `%</p>` +
				`<p id="metrics_9" class="card-text" style="margin: 0.4vh;"> R-Точность [R-precision]: ` + r_precision.toFixed(5) * 100 + `%</p>`
				
				if (!relevant_count_in_db || relevant_count_in_db < relevant_count) {
					html += 
					`<p id="metrics_10" class="card-text" style="margin: 0.4vh;"> Средняя точность [average precision]: ` + "Не хватает ифнормации" + `</p>`
				}
				else {
					html += 
					`<p id="metrics_10" class="card-text" style="margin: 0.4vh;"> Средняя точность [average precision]: ` + average_precision.toFixed(5) * 100 + `%</p>`
				}
				
				if (!relevant_count_in_db || relevant_count_in_db < relevant_count) {
					html += 
					`<p id="metrics_11" class="card-text" style="margin: 0.4vh;">` +
						`11-точечный график полноты/точности, измеренный по методике TREC [11-point matrix (TREC)]: ` + "Не хватает ифнормации" + 
					`</p>`
				}
				else {
					html += 
					`<p id="metrics_11" class="card-text" style="margin: 0.4vh;">` +
						`11-точечный график полноты/точности, измеренный по методике TREC [11-point matrix (TREC)]: ` +
						`<div id="curve_chart" style="width: auto; height: 500px"></div>` + 
					`</p>`
				}
				
				html +=
				`<hr style="margin: 1vh 0;"/>`+
				`<p style="margin: 0.4vh;>` + 
					`<label for="dataForMetricsRecalculate" class="form-label">Количество релевантных документов в базе данных:</label>` +
					`<input type="text" class="form-control" id="dataForMetricsRecalculate" placeholder="Количество релевантных документов" style="margin: 1vh 0 1vh 0;">` +
					
					`<button id="metricsRecalculate"` + 
							`type="submit"` + 
							`class="btn btn-outline-dark"` + 
							`on_click="metricsRecalculate()"` + 
							`style="width: 100%; margin: 1vh 0 0 0;">` +
						`Пересчитать`+
					`</button>` +
				`</p>` +
			`</div>` +
		`</div>`
	
	
	content.innerHTML = html
	fillComponent(metrics_div, content)
	
	let button_recalculate = document.getElementById("metricsRecalculate")
	button_recalculate.addEventListener("click", (event) => metricsRecalculate());
	
	// chart
	if (relevant_count_in_db || relevant_count_in_db > relevant_count) 
	{
		drawChart(data)
	}
}

function drawChart() {
	try {
		let data = google.visualization.arrayToDataTable([
			['Recall', 'Sales', 'Expenses'],
			['2004',  1000,      400],
			['2005',  1170,      460],
			['2006',  660,       1120],
			['2007',  1030,      540]
		]);

		let options = {
			title: 'Company Performance',
			legend: { position: 'bottom' }
		};

		let chart = new google.visualization.LineChart(document.getElementById('curve_chart'));

		chart.draw(data, options);
	}
	catch {}
}


function metricsRecalculate() {
	let relevant_count_in_db = parseInt(document.getElementById("dataForMetricsRecalculate").value)
	metrics(relevant_count_in_db)
}

// search main function
function search() {
	main_store.documents = []
	let content_div = document.getElementById("content"); 
	clearComponent(content_div)
	
	const search_input = document.getElementById("search_input");
	request_content = search_input.value
	
	const request = "http://" + getCurrentServer() + "/search?request_content=" + "\"" + request_content + "\"" 
	let response = {}
	try { response = JSON.parse(httpGet(request)) } catch {}
	main_store.documents = response
	
	let fill_data = makeCardsFromResponsData()
	fillComponent(content_div, fill_data)
}

// function to make requests
function httpGet(theUrl)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", theUrl, false); // false for synchronous request
    // xmlHttp.open("GET", theUrl); // false for synchronous request
    xmlHttp.send(null);
    return xmlHttp.responseText;
}

// define current server address
function getCurrentServer() {
	server_address = "127.0.0.1:13000"
	try { server_address = window.location.host } catch {}
	return server_address
}
