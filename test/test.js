var assert = require('assert');
var sys = require('sys');
var account = require('../account');
var spotify = require('../spotify');

// make these modules available to any module which require()s this module
GLOBAL.sys = sys;
GLOBAL.assert = assert;
GLOBAL.spotify = spotify;

GLOBAL.createSession = function(dontForwardLogging, onsession) {
  if (typeof dontForwardLogging === 'function') {
    onsession = dontForwardLogging;
    dontForwardLogging = false;
  }
  var session = new spotify.Session({applicationKey: account.applicationKey});
  if (!dontForwardLogging) {
    session.addListener('logMessage', function(m){
      sys.log(m.substr(0,m.length-1));
    });
  }
  session.login(account.username, account.password, function (err) {
    assert.ifError(err);
    onsession(session);
  });
}
