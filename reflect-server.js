var express = require('express');
var morgan = require('morgan');
var app = express();
var fs = require('fs');
var compression = require('compression');

var http = require('http').createServer(app);

var PORT = 31257;

app.use(morgan('combined'));
app.use(compression());

/* ------------------------ TEST URLS ------------------------*/
app.get('/', function(req, res) {
	res.send('Hello World!');
});
/* -------------------- END OF TEST URLS --------------------*/

app.use('/reflect/?', express.static('./reflect.json'));

app.get('/file/?', function(req, res) {
	var query = req.query;
	console.log("Received request for file: " + JSON.stringify(query));

	var reflect = JSON.parse(fs.readFileSync('./reflect.json', 'utf8'));

	if(reflect[query.id] !== undefined && reflect[query.id].path === query.path) {
		// Replace '~' if needed
		var path = reflect[query.id].path.replace('~', process.env.HOME);
		res.write(fs.readFileSync(path, 'utf8'));
	}
	else {
		console.log('---------------------------------------------------------------------');
		console.log('WARNING: Reflect JSON does not match request! Potential hack attempt?');
		console.log('Reflect: \n' + JSON.stringify(reflect[query.id]) + '\n');
		console.log('Query:   \n' + JSON.stringify(query) + '\n');
		console.log('---------------------------------------------------------------------');
	}
});


http.listen(PORT, function () {
	console.log('Example app listening on port ' + PORT);
});

