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

	var _ChangeAccountComponent = __webpack_require__(2);

	var _ChangeAccountComponent2 = _interopRequireDefault(_ChangeAccountComponent);

	function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

	var _window$marathonPlugi = window.marathonPluginInterface,
	    PluginHelper = _window$marathonPlugi.PluginHelper,
	    PluginMountPoints = _window$marathonPlugi.PluginMountPoints;


	PluginHelper.registerMe();
	_SessionCheckerAction2.default.init();

	PluginHelper.injectComponent(_ChangeAccountComponent2.default, PluginMountPoints.NAVBAR_TOP_RIGHT);

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

/***/ }),
/* 2 */
/***/ (function(module, exports, __webpack_require__) {

	"use strict";

	Object.defineProperty(exports, "__esModule", {
	  value: true
	});

	var _addons = __webpack_require__(3);

	var _addons2 = _interopRequireDefault(_addons);

	var _jwtDecode = __webpack_require__(4);

	var _jwtDecode2 = _interopRequireDefault(_jwtDecode);

	function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

	/* eslint-enable camelcase */

	var _window$marathonPlugi = window.marathonPluginInterface,
	    PluginActions = _window$marathonPlugi.PluginActions,
	    PluginHelper = _window$marathonPlugi.PluginHelper,
	    Sieve = _window$marathonPlugi.Sieve,
	    ajaxWrapper = _window$marathonPlugi.ajaxWrapper,
	    config = _window$marathonPlugi.config;
	/* eslint-disable camelcase */

	function showErrorDialog(title, message) {

	  PluginHelper.callAction(PluginActions.DIALOG_ALERT, [{
	    title: title,
	    message: message,
	    actionButtonLabel: "OK"
	  }]);
	}

	var ChangeAccountComponent = _addons2.default.createClass({
	  displayName: "ChangeAccountComponent",

	  handleMenuClick: function handleMenuClick() {
	    PluginHelper.callAction(PluginActions.DIALOG_ALERT, [{
	      title: "Trocar de conta",
	      message: "Por favor escolha a conta",
	      actionButtonLabel: "OK",
	      myid: "session-account-change"
	    }]);
	  },

	  getInitialState: function getInitialState() {
	    return {
	      User: {},
	      CurrentAccount: {}
	    };
	  },

	  acceptChangeAccountDialog: function acceptChangeAccountDialog(dialog) {
	    var _this = this;

	    if (dialog.myid === "session-account-change") {
	      ajaxWrapper({
	        url: config.apiURL + "hollow/account/next",
	        method: "POST"
	      }).error(function (error) {
	        showErrorDialog("Erro ao trocar de conta", error.body.msg);
	      }).success(function (response) {
	        _this.setState({
	          User: response.body.user,
	          CurrentAccount: response.body.current_account
	        });
	        localStorage.setItem("auth_token", response.body.jwt_token);
	      });
	      Sieve.navigateTo("/#/apps");
	    }
	  },

	  componentDidMount: function componentDidMount() {
	    this.startPolling();
	  },

	  whoAmI: function whoAmI() {
	    var _this2 = this;

	    /* eslint-disable no-unused-vars */
	    ajaxWrapper({ url: config.apiURL + "hollow/account/me", method: "GET" }).error(function (error) {
	      /* Não temos muito o que fazer aqui. Se retornar erro,
	       * já estamos deslogados e isso já é tratado por outra
	       * parte desse plugin. E se estamos deslogados,
	       * não temos o que exiibir nesse componente.
	        */
	    }).success(function (response) {
	      _this2.setState({
	        User: response.body.user,
	        CurrentAccount: response.body.current_account
	      });
	    });
	    /* eslint-enable no-unused-vars */
	  },

	  componentWillMount: function componentWillMount() {
	    Sieve.DialogStore.on("DIALOG_EVENTS_ACCEPT_DIALOG", this.acceptChangeAccountDialog);
	    this.whoAmI();
	  },

	  render: function render() {
	    return _addons2.default.createElement(
	      "div",
	      { className: "help-menu active",
	        onClick: this.handleMenuClick },
	      _addons2.default.createElement(
	        "span",
	        null,
	        " ",
	        this.state.User.name,
	        "@",
	        this.state.CurrentAccount.name,
	        " "
	      )
	    );
	  },

	  reReadToken: function reReadToken() {
	    /* eslint-disable no-empty */
	    try {
	      var token = (0, _jwtDecode2.default)(localStorage.getItem("auth_token"));
	      this.setState({
	        User: token.user,
	        CurrentAccount: token.current_account
	      });
	    } catch (e) {}
	    /* eslint-enable no-empty */
	  },

	  startPolling: function startPolling() {
	    if (this.interval == null) {
	      this.interval = setInterval(this.reReadToken, 5000);
	    }
	  }
	});

	exports.default = ChangeAccountComponent;

/***/ }),
/* 3 */
/***/ (function(module, exports) {

	"use strict";

	// This is a direct replacement for React and used to automatically substitute
	// React with the injected instance.
	// This is necessary, as using a different React instance will result in
	// various "Invariant Violation" errors.
	// It's getting the injected instance from the marathon plugin interface and
	// provide it to the plugin using the CommonJS syntax export for greater
	// compatibility with old modules.
	var React = window.marathonPluginInterface.React;

	module.exports = React;

/***/ }),
/* 4 */
/***/ (function(module, exports, __webpack_require__) {

	'use strict';

	var base64_url_decode = __webpack_require__(5);

	function InvalidTokenError(message) {
	  this.message = message;
	}

	InvalidTokenError.prototype = new Error();
	InvalidTokenError.prototype.name = 'InvalidTokenError';

	module.exports = function (token,options) {
	  if (typeof token !== 'string') {
	    throw new InvalidTokenError('Invalid token specified');
	  }

	  options = options || {};
	  var pos = options.header === true ? 0 : 1;
	  try {
	    return JSON.parse(base64_url_decode(token.split('.')[pos]));
	  } catch (e) {
	    throw new InvalidTokenError('Invalid token specified: ' + e.message);
	  }
	};

	module.exports.InvalidTokenError = InvalidTokenError;


/***/ }),
/* 5 */
/***/ (function(module, exports, __webpack_require__) {

	var atob = __webpack_require__(6);

	function b64DecodeUnicode(str) {
	  return decodeURIComponent(atob(str).replace(/(.)/g, function (m, p) {
	    var code = p.charCodeAt(0).toString(16).toUpperCase();
	    if (code.length < 2) {
	      code = '0' + code;
	    }
	    return '%' + code;
	  }));
	}

	module.exports = function(str) {
	  var output = str.replace(/-/g, "+").replace(/_/g, "/");
	  switch (output.length % 4) {
	    case 0:
	      break;
	    case 2:
	      output += "==";
	      break;
	    case 3:
	      output += "=";
	      break;
	    default:
	      throw "Illegal base64url string!";
	  }

	  try{
	    return b64DecodeUnicode(output);
	  } catch (err) {
	    return atob(output);
	  }
	};


/***/ }),
/* 6 */
/***/ (function(module, exports) {

	/**
	 * The code was extracted from:
	 * https://github.com/davidchambers/Base64.js
	 */

	var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=';

	function InvalidCharacterError(message) {
	  this.message = message;
	}

	InvalidCharacterError.prototype = new Error();
	InvalidCharacterError.prototype.name = 'InvalidCharacterError';

	function polyfill (input) {
	  var str = String(input).replace(/=+$/, '');
	  if (str.length % 4 == 1) {
	    throw new InvalidCharacterError("'atob' failed: The string to be decoded is not correctly encoded.");
	  }
	  for (
	    // initialize result and counters
	    var bc = 0, bs, buffer, idx = 0, output = '';
	    // get next character
	    buffer = str.charAt(idx++);
	    // character found in table? initialize bit storage and add its ascii value;
	    ~buffer && (bs = bc % 4 ? bs * 64 + buffer : buffer,
	      // and if not first of each 4 characters,
	      // convert the first 8 bits to one ascii character
	      bc++ % 4) ? output += String.fromCharCode(255 & bs >> (-2 * bc & 6)) : 0
	  ) {
	    // try to find character in table (0-63, not found => -1)
	    buffer = chars.indexOf(buffer);
	  }
	  return output;
	}


	module.exports = typeof window !== 'undefined' && window.atob && window.atob.bind(window) || polyfill;


/***/ })
/******/ ]);