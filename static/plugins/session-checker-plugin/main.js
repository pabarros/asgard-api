/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};

/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {

/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId])
/******/ 			return installedModules[moduleId].exports;

/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			exports: {},
/******/ 			id: moduleId,
/******/ 			loaded: false
/******/ 		};

/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);

/******/ 		// Flag the module as loaded
/******/ 		module.loaded = true;

/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}


/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;

/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;

/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";

/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(0);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ (function(module, exports, __webpack_require__) {

	"use strict";

	var _SessionCheckerAction = __webpack_require__(1);

	var _SessionCheckerAction2 = _interopRequireDefault(_SessionCheckerAction);

	function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

	var PluginHelper = window.marathonPluginInterface.PluginHelper;


	PluginHelper.registerMe();
	_SessionCheckerAction2.default.init();

/***/ }),
/* 1 */
/***/ (function(module, exports) {

	"use strict";

	Object.defineProperty(exports, "__esModule", {
	  value: true
	});
	var _window$marathonPlugi = window.marathonPluginInterface,
	    PluginActions = _window$marathonPlugi.PluginActions,
	    PluginHelper = _window$marathonPlugi.PluginHelper,
	    ajaxWrapper = _window$marathonPlugi.ajaxWrapper,
	    config = _window$marathonPlugi.config,
	    Sieve = _window$marathonPlugi.Sieve;


	var acceptDialog = function acceptDialog(dialog) {
	  if (dialog.myid === "session-expired") {
	    Sieve.navigateTo("/login");
	  }
	};

	function checkStatusCode(statusCode) {
	  if (statusCode === 401) {
	    PluginHelper.callAction(PluginActions.DIALOG_ALERT, [{
	      title: "Sua sessão expirou",
	      message: "Por favor faça login novamente",
	      actionButtonLabel: "Login",
	      myid: "session-expired"
	    }]);
	  }
	}

	Sieve.DialogStore.on("DIALOG_EVENTS_ACCEPT_DIALOG", acceptDialog);

	function checkSession() {
	  ajaxWrapper({
	    url: config.apiURL + "v2/deployments",
	    concurrent: true
	  }).error(function (error) {
	    checkStatusCode(error.status);
	  });
	}

	var SessionCheckerAction = {
	  init: function init() {
	    setInterval(checkSession, 5000);
	  }
	};

	exports.default = SessionCheckerAction;

/***/ })
/******/ ]);