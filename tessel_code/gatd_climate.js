// Node requires
var http = require('http');
var tessel = require('tessel');
var climatelib = require('climate-si7005');

var twitterHandle = '@mclarkk';



// module info
var climate = climatelib.use(tessel.port['A']);

climate.on('ready', function () {
  console.log('Connected to si7005');

  // Loop forever
  setImmediate(function loop () {
    climate.readTemperature('f', function (err, temp) {
      climate.readHumidity(function (err, humid) {
        //console.log('Degrees:', temp.toFixed(4) + 'F', 'Humidity:', humid.toFixed(4) + '%RH');
        //post("Report for " + twitterHandle + ' Degrees: ' + temp.toFixed(4) + 'F Humidity: ' + humid.toFixed(4) + '%RH');
        var data = {
          location_str: "dummy",
          temperature: temp.toFixed(4),
          temperature_units: "F",
          humidity: humid.toFixed(4),
          humidity_units: "%RH"
        };
        var dataString = JSON.stringify(data);
        post(dataString);
        setTimeout(loop, 300);
      });
    });
  });
});

function post(status) {
  console.log(status);

  // Timestamp
  var curtime = parseInt(process.env.DEPLOY_TIMESTAMP || Date.now());

  // Set up a request
  var req = http.request({
    host: 'inductor.eecs.umich.edu',
    port: 8081,
    path: '/oBNeydOsio',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    }
  }, function (res) {
    console.log("statusCode: ", res.statusCode);
    console.log("headers: ", res.headers);
    res.on('data', function(d) {
      console.log(' ');
      console.log(' ');
      console.log(String(d));
    });
  });

  // POST to GATD
  req.write(status);
  req.end();
  console.log('Sent!')

  // Log any errors
  req.on('error', function(e) {
    console.error(e);
  });  
}

climate.on('error', function(err) {
  console.log('error connecting module', err);
});