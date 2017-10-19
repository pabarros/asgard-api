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

	function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

	var _window$marathonPlugi = window.marathonPluginInterface,
	    PluginActions = _window$marathonPlugi.PluginActions,
	    PluginHelper = _window$marathonPlugi.PluginHelper,
	    Sieve = _window$marathonPlugi.Sieve,
	    ajaxWrapper = _window$marathonPlugi.ajaxWrapper,
	    config = _window$marathonPlugi.config;


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

	  componentWillMount: function componentWillMount() {
	    var _this2 = this;

	    Sieve.DialogStore.on("DIALOG_EVENTS_ACCEPT_DIALOG", this.acceptChangeAccountDialog);

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

/***/ })
/******/ ]);